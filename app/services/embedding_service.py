from typing import List

from sentence_transformers import SentenceTransformer

from app.config import EMBEDDING_MODEL

_model = SentenceTransformer(EMBEDDING_MODEL)

# BGE models are trained with an instruction prefix on the query side only.
_QUERY_PREFIX = (
    "Represent this sentence for searching relevant passages: "
    if "bge" in EMBEDDING_MODEL.lower()
    else ""
)


def embed_text(text: str) -> List[float]:
    """Embed a single passage (document chunk)."""
    vector = _model.encode(text, normalize_embeddings=True)
    return vector.tolist()


def embed_texts(texts: List[str]) -> List[List[float]]:
    """Embed a batch of passages (document chunks)."""
    if not texts:
        return []
    vectors = _model.encode(texts, normalize_embeddings=True)
    return [vector.tolist() for vector in vectors]


def embed_query(text: str) -> List[float]:
    """Embed a search query. Applies the model's query instruction prefix if needed."""
    return embed_text(f"{_QUERY_PREFIX}{text}")
