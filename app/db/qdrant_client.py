from qdrant_client import QdrantClient

from app.config import QDRANT_URL

qdrant_client = QdrantClient(url=QDRANT_URL)
