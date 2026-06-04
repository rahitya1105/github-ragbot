# reranker.py
# Reranks retrieved chunks using CrossEncoder

from sentence_transformers import CrossEncoder

print("Loading reranker model...")
RERANKER = CrossEncoder("cross-encoder/ms-marco-MiniLM-L-6-v2")
print("✅ Reranker ready!")


def rerank(query: str,
           chunks: list,
           top_k: int = 5) -> list:

    if not chunks:
        return []

    pairs  = [[query, chunk["text"]] for chunk in chunks]
    scores = RERANKER.predict(pairs)

    for i, chunk in enumerate(chunks):
        chunk["rerank_score"] = float(scores[i])

    reranked = sorted(
        chunks,
        key     = lambda x: x["rerank_score"],
        reverse = True
    )
    return reranked[:top_k]