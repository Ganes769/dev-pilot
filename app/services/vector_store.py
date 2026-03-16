from qdrant_client.models import Distance, VectorParams
from app.db.qdrant_client import qdrant_client

COLLECTION_NAME = "repo_chunks"
VECTOR_SIZE = 384
def create_collection()-> None:
    colletion_resposne=qdrant_client.get_collections()
    print(colletion_resposne)
    exsisting_collections=[c for c in colletion_resposne.collections]
    print(exsisting_collections)
    if COLLECTION_NAME not in exsisting_collections:
        qdrant_client.create_collection(
            collection_name=COLLECTION_NAME,
            vectors_config=VectorParams(
                size=VECTOR_SIZE,
                distance=Distance.COSINE,
            ),
        )