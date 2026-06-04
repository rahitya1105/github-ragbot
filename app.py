# app.py

import os
import sys
import stat
import shutil
import subprocess

sys.path.append(os.path.join(os.path.dirname(__file__), 'ragbot'))

from ragbot.repo_loader      import load_repo_files
from ragbot.chunker          import chunk_all_documents
from ragbot.vector_store     import embed_and_store
from ragbot.bm25_search      import build_bm25_index
from ragbot.ragbot           import ask_ragbot, set_chunks, find_file_path
import gradio as gr

# Global state
repo_info = {
    "loaded":     False,
    "name":       "",
    "github_url": ""
}
chunks = []


def remove_readonly(func, path, excinfo):
    os.chmod(path, stat.S_IWRITE)
    func(path)


def clone_repo(github_url: str,
               clone_dir: str = "./cloned_repo"):
    if os.path.exists(clone_dir):
        shutil.rmtree(clone_dir, onerror=remove_readonly)
    subprocess.run(
        ["git", "clone", "--depth", "1",
         github_url, clone_dir],
        capture_output=True
    )
    print(f"✅ Cloned: {github_url}")


def load_repository(github_url: str):
    global chunks

    if not github_url.strip():
        yield "Please enter a GitHub URL!"
        return

    github_url = github_url.strip()
    repo_info["github_url"] = github_url
    repo_info["name"]       = github_url.split("/")[-1]

    yield "⏳ Cloning repository..."
    clone_repo(github_url)

    yield "⏳ Loading files..."
    docs = load_repo_files("./cloned_repo")

    if not docs:
        yield "❌ No supported files found!"
        return

    yield f"⏳ Chunking {len(docs)} files..."
    chunks = chunk_all_documents(docs)

    yield "⏳ Creating embeddings (please wait)..."
    embed_and_store(chunks)

    yield "⏳ Building search index..."
    build_bm25_index(chunks)
    set_chunks(chunks)

    repo_info["loaded"] = True

    yield (
        f"🚀 Repository Ready!\n"
        f"   Repo   : {repo_info['name']}\n"
        f"   Files  : {len(docs)}\n"
        f"   Chunks : {len(chunks)}\n\n"
        f"Now ask questions below!"
    )


def build_github_link(filename: str) -> str:
    file_path = find_file_path(filename)
    if not file_path:
        return None
    relative = file_path\
        .replace("./cloned_repo/", "")\
        .replace(".\\cloned_repo\\", "")\
        .replace("\\", "/")
    return f"{repo_info['github_url']}/blob/main/{relative}"


def chat(message, history):
    if not repo_info["loaded"]:
        return "Please load a repository first!"

    result  = ask_ragbot(message)
    answer  = result["answer"]
    sources = list(set(result["sources"]))

    source_lines = []
    for source in sources:
        link = build_github_link(source)
        if link:
            source_lines.append(f"  • [{source}]({link})")
        else:
            source_lines.append(f"  • {source}")

    source_text = "\n".join(source_lines)

    return (
        f"{answer}\n\n"
        f"---\n"
        f"📁 **Sources — Click to open on GitHub:**\n"
        f"{source_text}"
    )


# ── Gradio UI ──────────────────────────────────────────
with gr.Blocks(theme=gr.themes.Soft()) as demo:

    gr.Markdown("""
    # 🤖 GitHub RAGBot
    ### Ask anything about any GitHub repository
    **How to use:**
    1. Paste a GitHub URL and click Load Repository
    2. Wait for indexing to complete
    3. Ask questions!
    """)

    gr.Markdown("## 📂 Step 1 — Load Repository")
    with gr.Row():
        url_input = gr.Textbox(
            placeholder = "https://github.com/pallets/flask",
            label       = "GitHub URL",
            scale       = 4
        )
        load_btn = gr.Button(
            "Load Repository",
            variant = "primary",
            scale   = 1
        )

    status_box = gr.Textbox(
        label       = "Status",
        value       = "No repository loaded yet.",
        lines       = 4,
        interactive = False
    )

    load_btn.click(
        fn      = load_repository,
        inputs  = [url_input],
        outputs = [status_box]
    )

    gr.Markdown("## 💬 Step 2 — Ask Questions")
    gr.ChatInterface(
        fn             = chat,
        examples       = [
            "What does this project do?",
            "What are the main functions?",
            "How is authentication handled?",
            "Explain the project structure",
        ],
        cache_examples = False
    )

    gr.Markdown("""
    <center>
    Built with LangChain • ChromaDB • BM25 •
    CrossEncoder Reranker • Groq • Gradio
    </center>
    """)

if __name__ == "__main__":
    demo.launch(share=True)