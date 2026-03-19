from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field
from typing import List

from app.services.embedding_service import embed_text
from app.services.vector_store import search_chunks
from app.services.llm_service import generate_repo_answer


router = APIRouter(prefix="", tags=["ask"])

SIMILARITY_THRESHOLD = 0.4
MAX_LIMIT = 5


class AskRequest(BaseModel):
    question: str = Field(..., min_length=1)
    limit: int = Field(default=3, ge=1, le=MAX_LIMIT)


class AskSource(BaseModel):
    file_path: str
    chunk_index: int
    score: float


class AskResponse(BaseModel):
    question: str
    answer: str
    sources: List[AskSource]


@router.post("/ask", response_model=AskResponse)
def ask_repo(payload: AskRequest):
    try:
        question = payload.question.strip()

        # Step 1: embed the user question
        query_vector = embed_text(question)

        # Step 2: retrieve relevant chunks from Qdrant
        matches = search_chunks(query_vector=query_vector, limit=payload.limit)

        sources: List[AskSource] = []
        context_parts: List[str] = []
        seen = set()

        # Step 3: use stored payload text directly
        for match in matches:
            data = match.payload or {}
            score = float(match.score)

            if score < SIMILARITY_THRESHOLD:
                continue

            file_path = data.get("file_path", "")
            chunk_index = data.get("chunk_index", -1)
            text = data.get("text", "")

            key = (file_path, chunk_index)
            if key in seen:
                continue
            seen.add(key)

            if not text.strip():
                continue

            sources.append(
                AskSource(
                    file_path=file_path,
                    chunk_index=chunk_index,
                    score=round(score, 4),
                )
            )

            context_parts.append(
                f"File: {file_path}\n"
                f"Chunk Index: {chunk_index}\n"
                f"Code:\n{text}"
            )

        # Step 4: fallback if retrieval found nothing useful
        if not context_parts:
            return AskResponse(
                question=question,
                answer="I could not find enough evidence in the retrieved code.",
                sources=[],
            )

        # Step 5: build one context string from stored chunk text
        context = "\n\n---\n\n".join(context_parts)

        # Step 6: send that context to the LLM
        answer = generate_repo_answer(question=question, context=context)

        # Step 7: return final answer + sources
        return AskResponse(
            question=question,
            answer=answer,
            sources=sources,
        )

    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"Unexpected error: {exc}")