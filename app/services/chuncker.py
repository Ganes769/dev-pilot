import ast
from pathlib import Path
from typing import List


def chunk_text(text: str, chunk_size: int = 1000, overlap: int = 100) -> List[str]:
    if chunk_size <= 0:
        raise ValueError("chunk_size must be greater than 0")

    if overlap < 0:
        raise ValueError("overlap cannot be negative")

    if overlap >= chunk_size:
        raise ValueError("overlap must be smaller than chunk_size")

    text = text.strip()
    if not text:
        return []

    chunks = []
    start = 0
    step = chunk_size - overlap

    while start < len(text):
        end = start + chunk_size
        chunk = text[start:end].strip()

        if chunk:
            chunks.append(chunk)

        start += step

    return chunks


def _top_level_segments(text: str, tree: ast.Module) -> List[str]:
    """Split a module into source segments, one per top-level statement.

    Decorators and comments between statements stay attached to the
    statement that follows them, so functions/classes remain intact.
    """
    lines = text.splitlines()
    if not tree.body:
        return [text]

    # Start line of each top-level statement (0-based), including decorators.
    starts = []
    for node in tree.body:
        start = node.lineno - 1
        for decorator in getattr(node, "decorator_list", []):
            start = min(start, decorator.lineno - 1)
        starts.append(start)

    segments = []
    for i, start in enumerate(starts):
        # Pull leading comment/blank lines into this segment.
        prev_end = starts[i - 1] if i > 0 else 0
        while start > prev_end and (
            not lines[start - 1].strip() or lines[start - 1].lstrip().startswith("#")
        ):
            start -= 1
        end = starts[i + 1] if i + 1 < len(starts) else len(lines)
        segment = "\n".join(lines[start:end]).strip()
        if segment:
            segments.append(segment)

    return segments


def chunk_python_text(text: str, chunk_size: int = 2000, overlap: int = 200) -> List[str]:
    """Chunk Python source on syntax boundaries (functions, classes, top-level code).

    Small adjacent statements (imports, constants) are packed together up to
    chunk_size. Oversized definitions fall back to overlapping text chunks.
    Falls back entirely to chunk_text if the source does not parse.
    """
    stripped = text.strip()
    if not stripped:
        return []

    try:
        tree = ast.parse(text)
    except SyntaxError:
        return chunk_text(text, chunk_size=chunk_size, overlap=overlap)

    segments = _top_level_segments(text, tree)

    chunks: List[str] = []
    buffer: List[str] = []
    buffer_len = 0

    def flush():
        nonlocal buffer, buffer_len
        if buffer:
            chunks.append("\n\n".join(buffer))
            buffer = []
            buffer_len = 0

    for segment in segments:
        if len(segment) > chunk_size:
            flush()
            chunks.extend(chunk_text(segment, chunk_size=chunk_size, overlap=overlap))
            continue

        if buffer_len + len(segment) > chunk_size:
            flush()

        buffer.append(segment)
        buffer_len += len(segment) + 2

    flush()
    return chunks


def chunk_file(
    file_path: str,
    text: str,
    chunk_size: int = 2000,
    overlap: int = 200,
) -> List[str]:
    """Chunk file content, using syntax-aware chunking for Python files."""
    if Path(file_path).suffix.lower() == ".py":
        return chunk_python_text(text, chunk_size=chunk_size, overlap=overlap)
    return chunk_text(text, chunk_size=chunk_size, overlap=overlap)
