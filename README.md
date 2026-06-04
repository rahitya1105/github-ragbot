# 🤖 GitHub RAGBot

Ask anything about any GitHub repository using AI!

## 🚀 Live Demo
[Click Here to Try](your_huggingface_link_here)

## ✨ Features
- Load ANY GitHub repository instantly
- Hybrid Retrieval (BM25 + Vector Search)
- Cross Encoder Reranker for precision
- Citation Enforcement (no hallucinations)
- Clickable source file links
- Powered by Groq AI (fast & free)

## 🛠️ Tech Stack
- LangChain + ChromaDB
- Sentence Transformers
- BM25 + CrossEncoder Reranker
- Groq API (llama-3.1-8b)
- Gradio UI

## 📦 Installation
```bash
git clone https://github.com/YOUR_USERNAME/github-ragbot
cd github-ragbot
pip install -r requirements.txt
```

## ⚙️ Setup
Add your Groq API key in .env file

## ▶️ Run
Run python app.py in terminal

## 📁 Project Structure
- ragbot/repo_loader.py      → loads repo files
- ragbot/chunker.py          → smart chunking
- ragbot/vector_store.py     → embeddings + ChromaDB
- ragbot/bm25_search.py      → keyword search
- ragbot/reranker.py         → CrossEncoder reranker
- ragbot/hybrid_retrieval.py → combines all search
- ragbot/ragbot.py           → Groq answer generation
- app.py                     → Gradio UI

## 🏗️ Architecture
GitHub URL → Clone → Load Files → Smart Chunking
→ Embeddings → Vector DB → BM25 Index
→ User Question → Hybrid Search → Reranker
→ Top Chunks → Groq LLM → Cited Answer