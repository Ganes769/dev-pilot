from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field
from typing import Dict, List, Optional, Tuple

from app.config import RETRIEVAL_CANDIDATES
from app.services.embedding_service import embed_query
from app.services.extra_context import load_extra_context
from app.services.llm_service import generate_answer
from app.services.reranker import rerank_matches
from app.services.vector_store import fetch_neighbor_chunks, search_chunks


router = APIRouter(prefix="", tags=["ask"])

MAX_LIMIT = 15


class AskRequest(BaseModel):
    question: str = Field(..., min_length=1)
    limit: int = Field(default=8, ge=1, le=MAX_LIMIT)
    extra_context: Optional[str] = Field(
        default=None,
        description="Optional text appended to server-configured context for this request only.",
    )


class AskSource(BaseModel):
    file_path: str
    chunk_index: int
    score: float


class AskResponse(BaseModel):
    question: str
    answer: str
    sources: List[AskSource]


def _build_context(matches) -> Tuple[List[AskSource], str]:
    """Turn reranked matches into sources + a context block for the LLM.

    Pulls in the chunks adjacent to each match (chunk_index +/- 1) so the
    model sees complete logic, and orders everything by file and position.
    """
    sources: List[AskSource] = []
    chunks: Dict[Tuple[str, int], str] = {}
    matched_by_file: Dict[str, List[int]] = {}
    seen = set()

    for match in matches:
        data = match.payload or {}
        file_path = data.get("file_path", "")
        chunk_index = data.get("chunk_index", -1)
        text = data.get("text", "")

        key = (file_path, chunk_index)
        if key in seen or not text.strip():
            continue
        seen.add(key)

        sources.append(
            AskSource(
                file_path=file_path,
                chunk_index=chunk_index,
                score=round(float(match.score), 4),
            )
        )
        chunks[key] = text
        matched_by_file.setdefault(file_path, []).append(chunk_index)

    # Fetch neighbors of each matched chunk that we don't already have.
    for file_path, indices in matched_by_file.items():
        neighbor_indices = [
            neighbor
            for index in indices
            for neighbor in (index - 1, index + 1)
            if (file_path, neighbor) not in chunks
        ]
        chunks.update(fetch_neighbor_chunks(file_path, neighbor_indices))

    context_parts = []
    for (file_path, chunk_index), text in sorted(chunks.items()):
        context_parts.append(
            f"File: {file_path}\n"
            f"Chunk Index: {chunk_index}\n"
            f"Code:\n{text}"
        )

    return sources, "\n\n---\n\n".join(context_parts)


@router.post("/ask", response_model=AskResponse)
def ask_repo(payload: AskRequest):
    try:
        question = payload.question.strip()

        # Step 1: embed the user question (query-side embedding)
        query_vector = embed_query(question)

        # Step 2: over-fetch candidates from Qdrant (score threshold applied there)
        candidates = search_chunks(
            query_vector=query_vector,
            limit=max(RETRIEVAL_CANDIDATES, payload.limit),
        )

        # Step 3: rerank with a cross-encoder and keep the best matches
        matches = rerank_matches(question, candidates, top_k=payload.limit)

        # Step 4: build context (matched chunks + their neighbors)
        sources, context = _build_context(matches)

        server_extra = load_extra_context()
        req_extra = (payload.extra_context or "").strip()
        extra_context = "\n\n".join(
            part for part in (server_extra, req_extra) if part
        )

        # Step 5: no retrieval — still answer if optional extra context is configured
        if not context:
            if extra_context:
                answer = generate_answer(
                    question=question,
                    code_context=None,
                    extra_context=extra_context,
                )
                return AskResponse(
                    question=question,
                    answer=answer,
                    sources=[],
                )
            return AskResponse(
                question=question,
                answer="I could not find enough evidence in the retrieved code.",
                sources=[],
            )

        # Step 6: send that context to the LLM
        answer = generate_answer(
            question=question,
            code_context=context,
            extra_context=extra_context,
        )

        # Step 7: return final answer + sources
        return AskResponse(
            question=question,
            answer=answer,
            sources=sources,
        )

    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"Unexpected error: {exc}")
