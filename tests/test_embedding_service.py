import pytest

from app.services.embedding_service import embed_query, embed_text, embed_texts

VECTOR_SIZE = 384


def test_embed_text_returns_correct_size():
    vector = embed_text("where is the ask API?")
    assert isinstance(vector, list)
    assert len(vector) == VECTOR_SIZE
    assert all(isinstance(v, float) for v in vector)


def test_embed_text_different_inputs_differ():
    v1 = embed_text("where is the ask API?")
    v2 = embed_text("how does chunking work?")
    assert v1 != v2


def test_embed_texts_batch_matches_single():
    texts = ["hello world", "how does qdrant work?"]
    batch = embed_texts(texts)

    assert len(batch) == 2
    for vec in batch:
        assert isinstance(vec, list)
        assert len(vec) == VECTOR_SIZE

    single_0 = embed_text(texts[0])
    single_1 = embed_text(texts[1])
    # Batched encoding can differ from single encoding by float rounding noise
    assert batch[0] == pytest.approx(single_0, abs=1e-5)
    assert batch[1] == pytest.approx(single_1, abs=1e-5)


def test_embed_texts_empty_list():
    result = embed_texts([])
    assert result == []


def test_embed_query_returns_correct_size():
    vector = embed_query("where is the ask API?")
    assert isinstance(vector, list)
    assert len(vector) == VECTOR_SIZE
