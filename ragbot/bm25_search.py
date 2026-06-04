# bm25_search.py
# Keyword search using BM25 algorithm

from rank_bm25 import BM25Okapi

_bm25_index  = None
_bm25_chunks = None


def build_bm25_index(chunks: list):
    global _bm25_index, _bm25_chunks
    _bm25_chunks = chunks
    tokenized    = [c["text"].lower().split() for c in chunks]
    _bm25_index  = BM25Okapi(tokenized)
    print(f"✅ BM25 index built with {len(chunks)} chunks")


def bm25_search(query: str, top_k: int = 20) -> list:
    if _bm25_index is None:
        return []

    query_tokens = query.lower().split()
    scores       = _bm25_index.get_scores(query_tokens)
    top_indices  = sorted(
        range(len(scores)),
        key     = lambda i: scores[i],
        reverse = True
    )[:top_k]

    results = []
    for idx in top_indices:
        if scores[idx] > 0:
            results.append({
                "text":     _bm25_chunks[idx]["text"],
                "filename": _bm25_chunks[idx]["filename"],
                "filepath": _bm25_chunks[idx].get("filepath", ""),
                "score":    float(scores[idx]),
                "source":   "bm25"
            })
    return results