from sentence_transformers import CrossEncoder
from app.core.logger import get_logger

logger = get_logger(__name__)
_reranker = None


def rerank(query: str, chunks: list[str], top_n: int = 5) -> list[str]:
    global _reranker
    if _reranker is None:
        logger.info("Loading reranker: cross-encoder/ms-marco-MiniLM-L-6-v2")
        _reranker = CrossEncoder("cross-encoder/ms-marco-MiniLM-L-6-v2")

    scores = _reranker.predict([(query, chunk) for chunk in chunks])
    ranked = sorted(zip(scores, chunks), reverse=True)
    logger.info(f"Reranked {len(chunks)} → top {top_n} chunks | Best score: {ranked[0][0]:.2f}")
    return [chunk for _, chunk in ranked[:top_n]]
