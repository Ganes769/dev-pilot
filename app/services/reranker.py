from typing import List, Sequence

from app.config import RERANKER_MODEL, RERANK_ENABLED

_reranker = None


def _get_reranker():
    global _reranker
    if _reranker is None:
        from sentence_transformers import CrossEncoder

        _reranker = CrossEncoder(RERANKER_MODEL)
    return _reranker


def rerank_matches(question: str, matches: Sequence, top_k: int) -> List:
    """Rerank Qdrant matches with a cross-encoder and return the top_k best.

    Matches without payload text are dropped. If reranking is disabled,
    the original retrieval order is kept and simply truncated.
    """
    scored = [m for m in matches if (m.payload or {}).get("text", "").strip()]

    if not RERANK_ENABLED or len(scored) <= 1:
        return list(scored[:top_k])

    pairs = [(question, m.payload["text"]) for m in scored]
    scores = _get_reranker().predict(pairs)

    ranked = sorted(zip(scored, scores), key=lambda pair: pair[1], reverse=True)
    return [match for match, _ in ranked[:top_k]]
