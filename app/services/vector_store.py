from typing import List, Dict, Any
from qdrant_client.models import Distance, VectorParams, PointStruct
from app.db.qdrant_client import qdrant_client

COLLECTION_NAME = "repo_chunks"
VECTOR_SIZE = 384


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


def upsert_chunks(points: List[Dict[str, Any]]) -> None:
    qdrant_points = [
        PointStruct(
            id=point["id"],
            vector=point["vector"],
            payload=point["payload"],
        )
        for point in points
    ]

    qdrant_client.upsert(
        collection_name=COLLECTION_NAME,
        points=qdrant_points,
    )


def search_chunks(query_vector: List[float], limit: int = 5):
    response = qdrant_client.query_points(
        collection_name=COLLECTION_NAME,
        query=query_vector,
        limit=limit,
        with_payload=True,
    )
    return response.points