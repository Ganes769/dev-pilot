import os
from pathlib import Path


def load_extra_context() -> str:
    """
    Optional text merged into LLM prompts (identity, greetings, product facts).

    Set either:
      - DEVPILOT_EXTRA_CONTEXT_FILE — path to a UTF-8 text/markdown file
      - DEVPILOT_EXTRA_CONTEXT — inline string (use quotes in shell for newlines)

    If the file path is set and the file exists, its contents are used.
    Otherwise the env string is used.
    """
    path = os.environ.get("DEVPILOT_EXTRA_CONTEXT_FILE", "").strip()
    if path:
        p = Path(path).expanduser()
        if p.is_file():
            return p.read_text(encoding="utf-8").strip()
    return os.environ.get("DEVPILOT_EXTRA_CONTEXT", "").strip()
