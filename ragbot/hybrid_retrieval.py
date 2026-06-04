# hybrid_retrieval.py
# Combines BM25 + Vector Search + Reranker

from vector_store import vector_search
from bm25_search  import bm25_search
from reranker     import rerank


def hybrid_search(query: str, top_k: int = 5) -> list:

    # Get candidates from both
    vector_results = vector_search(query, top_k=20)
    bm25_results   = bm25_search(query,   top_k=20)

    # Merge and deduplicate
    seen, merged = set(), []
    for r in vector_results + bm25_results:
        key = r["text"][:100]
        if key not in seen:
            seen.add(key)
            merged.append(r)

    # Reranker picks best ones
    final = rerank(query, merged, top_k=top_k)
    return final