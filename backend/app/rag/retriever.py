from .embedder import embed
from .collection import get_collection


def retrieve(query: str, top_k=5, threshold=0.0):
    """
    Retrieve relevant document chunks from Milvus.
    
    Args:
        query: User's question
        top_k: Number of top results to retrieve (default: 5)
        threshold: Minimum similarity score (0.0-1.0, default: 0.05)
                  Lower = more lenient, Higher = stricter matching
    """
    col = get_collection()
    q_emb = embed([query])[0]

    results = col.search(
        [q_emb],
        "embedding",
        param={"metric_type": "IP", "params": {"nprobe": 10}},
        limit=top_k,
        output_fields=["content"]
    )

    matches = []
    for hit in results[0]:
        print(f"[DEBUG] Match score: {hit.score:.4f} (threshold: {threshold})")
        if hit.score >= threshold:
            matches.append(hit.entity.get("content"))
    
    if not matches:
        print(f"[WARNING] No matches found above threshold {threshold}. Try lowering the threshold in retriever.py")

    return matches
