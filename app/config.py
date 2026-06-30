import os

from dotenv import load_dotenv

load_dotenv()

QDRANT_URL: str = os.getenv("QDRANT_URL", "http://localhost:6333")
OLLAMA_MODEL: str = os.getenv("OLLAMA_MODEL", "gemma3")
SCORE_THRESHOLD: float = float(os.getenv("SCORE_THRESHOLD", "0.4"))
DEVPILOT_EXTRA_CONTEXT: str = os.getenv("DEVPILOT_EXTRA_CONTEXT", "")
DEVPILOT_EXTRA_CONTEXT_FILE: str = os.getenv("DEVPILOT_EXTRA_CONTEXT_FILE", "")
DEVPILOT_SYSTEM_PROMPT: str = os.getenv("DEVPILOT_SYSTEM_PROMPT", "")
