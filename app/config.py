import os

from dotenv import load_dotenv

load_dotenv()

QDRANT_URL: str = os.getenv("QDRANT_URL", "http://localhost:6333")
OLLAMA_MODEL: str = os.getenv("OLLAMA_MODEL", "gemma3")
SCORE_THRESHOLD: float = float(os.getenv("SCORE_THRESHOLD", "0.4"))
DEVPILOT_EXTRA_CONTEXT: str = os.getenv("DEVPILOT_EXTRA_CONTEXT", "")
DEVPILOT_EXTRA_CONTEXT_FILE: str = os.getenv("DEVPILOT_EXTRA_CONTEXT_FILE", "")
DEVPILOT_SYSTEM_PROMPT: str = os.getenv("DEVPILOT_SYSTEM_PROMPT", "")

# Embedding model (bi-encoder). bge-small-en-v1.5 outperforms all-MiniLM-L6-v2
# on retrieval while keeping the same 384-dim vectors.
EMBEDDING_MODEL: str = os.getenv("EMBEDDING_MODEL", "BAAI/bge-small-en-v1.5")
EMBEDDING_VECTOR_SIZE: int = int(os.getenv("EMBEDDING_VECTOR_SIZE", "384"))

# Cross-encoder used to rerank retrieved candidates before they reach the LLM.
RERANKER_MODEL: str = os.getenv("RERANKER_MODEL", "cross-encoder/ms-marco-MiniLM-L-6-v2")
RERANK_ENABLED: bool = os.getenv("RERANK_ENABLED", "true").lower() in ("1", "true", "yes")

# How many candidates to pull from Qdrant before reranking down to the requested limit.
RETRIEVAL_CANDIDATES: int = int(os.getenv("RETRIEVAL_CANDIDATES", "25"))
