from typing import Any, Dict, List, Optional, Tuple

from qdrant_client.models import (
    Distance,
    FieldCondition,
    Filter,
    MatchValue,
    PointStruct,
    VectorParams,
)

from app.config import EMBEDDING_VECTOR_SIZE, SCORE_THRESHOLD
from app.db.qdrant_client import qdrant_client

COLLECTION_NAME = "repo_chunks"
VECTOR_SIZE = EMBEDDING_VECTOR_SIZE


def create_collection() -> None:
    if qdrant_client.collection_exists(COLLECTION_NAME):
        return

    qdrant_client.create_collection(
        collection_name=COLLECTION_NAME,
        vectors_config=VectorParams(
            size=VECTOR_SIZE,
            distance=Distance.COSINE,
        ),
    )


def recreate_collection() -> None:
    if qdrant_client.collection_exists(COLLECTION_NAME):
        qdrant_client.delete_collection(collection_name=COLLECTION_NAME)
    create_collection()


UPSERT_BATCH_SIZE = 500


def upsert_chunks(points: List[Dict[str, Any]]) -> None:
    qdrant_points = [
        PointStruct(
            id=point["id"],
            vector=point["vector"],
            payload=point["payload"],
        )
        for point in points
    ]

    for i in range(0, len(qdrant_points), UPSERT_BATCH_SIZE):
        batch = qdrant_points[i : i + UPSERT_BATCH_SIZE]
        qdrant_client.upsert(
            collection_name=COLLECTION_NAME,
            points=batch,
        )


def search_chunks(
    query_vector: List[float],
    limit: int = 5,
    score_threshold: Optional[float] = SCORE_THRESHOLD,
):
    response = qdrant_client.query_points(
        collection_name=COLLECTION_NAME,
        query=query_vector,
        limit=limit,
        with_payload=True,
        score_threshold=score_threshold,
    )
    return response.points


def fetch_neighbor_chunks(
    file_path: str,
    chunk_indices: List[int],
) -> Dict[Tuple[str, int], str]:
    """Fetch chunks of a file by index (used to pull neighbors of matched chunks).

    Returns a mapping of (file_path, chunk_index) -> chunk text.
    """
    wanted = sorted(set(index for index in chunk_indices if index >= 0))
    if not wanted:
        return {}

    found: Dict[Tuple[str, int], str] = {}
    for index in wanted:
        points, _ = qdrant_client.scroll(
            collection_name=COLLECTION_NAME,
            scroll_filter=Filter(
                must=[
                    FieldCondition(key="file_path", match=MatchValue(value=file_path)),
                    FieldCondition(key="chunk_index", match=MatchValue(value=index)),
                ]
            ),
            limit=1,
            with_payload=True,
        )
        for point in points:
            payload = point.payload or {}
            text = payload.get("text", "")
            if text.strip():
                found[(file_path, index)] = text

    return found
