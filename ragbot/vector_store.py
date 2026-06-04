# vector_store.py
# Creates embeddings and stores in ChromaDB

from sentence_transformers import SentenceTransformer
import chromadb

print("Loading embedding model...")
EMBEDDING_MODEL = SentenceTransformer("all-MiniLM-L6-v2")
print("✅ Embedding model ready!")

CHROMA_CLIENT = chromadb.Client()
_collection   = None


def get_collection():
    global _collection
    try:
        CHROMA_CLIENT.delete_collection("github_repo")
    except:
        pass
    _collection = CHROMA_CLIENT.create_collection(
        name     = "github_repo",
        metadata = {"hnsw:space": "cosine"}
    )
    return _collection


def embed_and_store(chunks: list):
    global _collection
    _collection = get_collection()
    batch_size  = 50

    for i in range(0, len(chunks), batch_size):
        batch     = chunks[i:i + batch_size]
        texts     = [c["text"]     for c in batch]
        ids       = [c["chunk_id"] for c in batch]
        metadatas = [{
            "filename":    c["filename"],
            "filepath":    c["filepath"],
            "chunk_index": c["chunk_index"],
        } for c in batch]

        embeddings = EMBEDDING_MODEL.encode(texts).tolist()

        _collection.add(
            ids       = ids,
            documents = texts,
            embeddings= embeddings,
            metadatas = metadatas
        )

    print(f"✅ Stored {len(chunks)} chunks in ChromaDB!")


def vector_search(query: str, top_k: int = 20) -> list:
    global _collection
    if _collection is None:
        return []

    query_vector = EMBEDDING_MODEL.encode([query]).tolist()

    results = _collection.query(
        query_embeddings = query_vector,
        n_results        = min(top_k, _collection.count()),
        include          = ["documents", "metadatas", "distances"]
    )

    hits = []
    for i in range(len(results["documents"][0])):
        hits.append({
            "text":     results["documents"][0][i],
            "filename": results["metadatas"][0][i]["filename"],
            "filepath": results["metadatas"][0][i]["filepath"],
            "score":    1 - results["distances"][0][i],
            "source":   "vector"
        })
    return hits