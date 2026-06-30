import pytest

from app.services.chuncker import chunk_text


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
