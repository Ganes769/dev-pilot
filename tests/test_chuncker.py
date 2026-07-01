import pytest

from app.services.chuncker import chunk_file, chunk_python_text, chunk_text


def test_empty_text_returns_empty_list():
    assert chunk_text("") == []


def test_whitespace_only_returns_empty_list():
    assert chunk_text("   \n  ") == []


def test_single_chunk_when_text_fits():
    text = "hello world"
    result = chunk_text(text, chunk_size=100, overlap=10)
    assert len(result) == 1
    assert result[0] == "hello world"


def test_splits_into_multiple_chunks():
    # 5 lines of 50 chars each = 250 chars total, chunk_size=120 → at least 2 chunks
    line = "x" * 49 + "\n"
    text = line * 5
    result = chunk_text(text, chunk_size=120, overlap=20)
    assert len(result) >= 2


def test_no_empty_chunks():
    line = "a" * 30 + "\n"
    text = line * 10
    result = chunk_text(text, chunk_size=100, overlap=20)
    for chunk in result:
        assert chunk.strip() != ""


def test_overlap_carries_content():
    # Two lines that together exceed chunk_size; overlap should carry tail of first chunk
    line_a = "A" * 60 + "\n"
    line_b = "B" * 60 + "\n"
    text = line_a + line_b
    result = chunk_text(text, chunk_size=70, overlap=20)
    assert len(result) >= 2
    # Second chunk should contain overlap from first
    assert "A" in result[1]


def test_invalid_chunk_size_raises():
    with pytest.raises(ValueError):
        chunk_text("hello", chunk_size=0)


def test_negative_overlap_raises():
    with pytest.raises(ValueError):
        chunk_text("hello", chunk_size=100, overlap=-1)


def test_overlap_gte_chunk_size_raises():
    with pytest.raises(ValueError):
        chunk_text("hello", chunk_size=50, overlap=50)


SAMPLE_PYTHON = '''\
import os
from typing import List

CONSTANT = 42


def first_function(x: int) -> int:
    """Docstring."""
    return x + CONSTANT


@property
def decorated_function(self):
    return self._value


class MyClass:
    def method_a(self):
        return "a"

    def method_b(self):
        return "b"
'''


def test_python_chunking_keeps_functions_intact():
    chunks = chunk_python_text(SAMPLE_PYTHON, chunk_size=200, overlap=20)
    joined = "\n\n".join(chunks)

    # Every definition appears whole in exactly one chunk
    assert any("def first_function" in c and "return x + CONSTANT" in c for c in chunks)
    assert any("class MyClass" in c and "method_b" in c for c in chunks)
    assert "import os" in joined


def test_python_chunking_keeps_decorators_with_function():
    chunks = chunk_python_text(SAMPLE_PYTHON, chunk_size=200, overlap=20)
    for chunk in chunks:
        if "def decorated_function" in chunk:
            assert "@property" in chunk
            break
    else:
        pytest.fail("decorated_function not found in any chunk")


def test_python_chunking_packs_small_statements():
    text = "import os\nimport sys\n\nX = 1\nY = 2\n"
    chunks = chunk_python_text(text, chunk_size=500, overlap=50)
    assert len(chunks) == 1


def test_python_chunking_empty_text():
    assert chunk_python_text("") == []
    assert chunk_python_text("   \n  ") == []


def test_python_chunking_invalid_syntax_falls_back():
    broken = "def broken(:\n    pass\n" + ("x" * 300)
    chunks = chunk_python_text(broken, chunk_size=100, overlap=10)
    assert len(chunks) >= 1


def test_python_chunking_splits_oversized_definition():
    body = "\n".join(f"    x{i} = {i}" for i in range(100))
    text = f"def big_function():\n{body}\n"
    chunks = chunk_python_text(text, chunk_size=200, overlap=20)
    assert len(chunks) > 1


def test_chunk_file_dispatches_by_extension():
    python_chunks = chunk_file("app/main.py", SAMPLE_PYTHON, chunk_size=200, overlap=20)
    assert any("def first_function" in c and "return x + CONSTANT" in c for c in python_chunks)

    text_chunks = chunk_file("README.md", "hello world", chunk_size=100, overlap=10)
    assert text_chunks == ["hello world"]
