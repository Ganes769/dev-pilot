from fastapi import APIRouter, HTTPException
from pathlib import Path
from pydantic import BaseModel
from typing import List

from app.services.repo_scanner import scan_repository
from app.services.file_reader import read_file_content
from app.services.chuncker import chunk_text
from app.services.embedding_service import embed_texts
from app.services.vector_store import create_collection, upsert_chunks, COLLECTION_NAME


router = APIRouter(prefix="/repos", tags=["embed"])


class RepoEmbedRequest(BaseModel):
    repo_path: str
    chunk_size: int = 1000
    overlap: int = 100


class RepoEmbedResponse(BaseModel):
    repo_name: str
    total_files: int
    total_chunks: int
    vectors_stored: int
    collection: str


@router.post("/embed", response_model=RepoEmbedResponse)
def embed_repository(payload: RepoEmbedRequest):
    try:
        repo_name = Path(payload.repo_path).name
        files = scan_repository(payload.repo_path)

        create_collection()

        chunk_records = []

        point_id = 1

        for relative_file_path in files:
            content = read_file_content(payload.repo_path, relative_file_path)
            chunks = chunk_text(
                text=content,
                chunk_size=payload.chunk_size,
                overlap=payload.overlap,
            )

            for chunk_index, chunk in enumerate(chunks):
                chunk_records.append(
                    {
                        "id": point_id,
                        "file_path": relative_file_path,
                        "chunk_index": chunk_index,
                        "text": chunk,
                    }
                )
                point_id += 1

        texts = [record["text"] for record in chunk_records]
        vectors = embed_texts(texts)

        points = []
        for record, vector in zip(chunk_records, vectors):
            points.append(
                {
                    "id": record["id"],
                    "vector": vector,
                    "payload": {
                        "file_path": record["file_path"],
                        "chunk_index": record["chunk_index"],
                        "text": record["text"],
                    },
                }
            )

        if points:
            upsert_chunks(points)

        return RepoEmbedResponse(
            repo_name=repo_name,
            total_files=len(files),
            total_chunks=len(chunk_records),
            vectors_stored=len(points),
            collection=COLLECTION_NAME,
        )

    except FileNotFoundError as exc:
        raise HTTPException(status_code=404, detail=str(exc))
    except NotADirectoryError as exc:
        raise HTTPException(status_code=400, detail=str(exc))
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc))
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"Unexpected error: {exc}")