from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field
from typing import List

from app.services.embedding_service import embed_text
from app.services.vector_store import search_chunks


router = APIRouter(prefix="", tags=["search"])

SIMILARITY_THRESHOLD = 0.4
MAX_LIMIT = 10


class SearchRequest(BaseModel):
    query: str = Field(..., min_length=1)
    limit: int = Field(default=5, ge=1, le=MAX_LIMIT)


class SearchResult(BaseModel):
    file_path: str
    chunk_index: int
    score: float
    text_preview: str


class SearchResponse(BaseModel):
    query: str
    results: List[SearchResult]


@router.post("/search", response_model=SearchResponse)
def semantic_search(payload: SearchRequest):
    try:
        query = payload.query.strip()
        query_vector = embed_text(query)
        matches = search_chunks(query_vector=query_vector, limit=payload.limit)

        results: List[SearchResult] = []
        seen = set()

        for match in matches:
            data = match.payload or {}

            score = float(match.score)
            file_path = data.get("file_path", "")
            chunk_index = data.get("chunk_index", -1)
            text = data.get("text", "")

            if score < SIMILARITY_THRESHOLD:
                continue

            unique_key = (file_path, chunk_index)
            if unique_key in seen:
                continue
            seen.add(unique_key)

            results.append(
                SearchResult(
                    file_path=file_path,
                    chunk_index=chunk_index,
                    score=round(score, 4),
                    text_preview=text[:200],
                )
            )

        return SearchResponse(
            query=query,
            results=results,
        )

    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"Unexpected error: {exc}")