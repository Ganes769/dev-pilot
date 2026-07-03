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

# Code edit / agent settings
AGENT_MAX_STEPS: int = int(os.getenv("AGENT_MAX_STEPS", "10"))
AGENT_RUN_TTL_SECONDS: int = int(os.getenv("AGENT_RUN_TTL_SECONDS", "3600"))
MAX_FILE_READ_BYTES: int = int(os.getenv("MAX_FILE_READ_BYTES", "524288"))
MAX_FILE_WRITE_BYTES: int = int(os.getenv("MAX_FILE_WRITE_BYTES", "262144"))
BLOCKED_FILE_PATTERNS: str = os.getenv(
    "BLOCKED_FILE_PATTERNS", ".env,*.pem,credentials*,*.key,*.p12"
)
DEFAULT_CHUNK_SIZE: int = int(os.getenv("DEFAULT_CHUNK_SIZE", "2000"))
DEFAULT_CHUNK_OVERLAP: int = int(os.getenv("DEFAULT_CHUNK_OVERLAP", "200"))
