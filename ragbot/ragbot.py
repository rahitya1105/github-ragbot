# ragbot/ragbot.py

import os
import sys
sys.path.append(os.path.dirname(__file__))

from groq import Groq
from hybrid_retrieval import hybrid_search

GROQ_API_KEY = os.environ.get("GROQ_API_KEY", "")

_chunks = []

def set_chunks(chunks: list):
    global _chunks
    _chunks = chunks

def find_file_path(filename: str) -> str:
    for chunk in _chunks:
        if chunk["filename"] == filename:
            return chunk["filepath"]
    return None

def ask_ragbot(question: str) -> dict:
    if not question.strip():
        return {"question": question,
                "answer": "Please ask a valid question.",
                "context": "", "sources": []}

    relevant_chunks = hybrid_search(question, top_k=5)

    if not relevant_chunks:
        return {"question": question,
                "answer": "No relevant info found.",
                "context": "", "sources": []}

    context_parts, sources = [], []
    for i, chunk in enumerate(relevant_chunks):
        label = f"[SOURCE {i+1}: {chunk['filename']}]"
        context_parts.append(f"{label}\n{chunk['text']}")
        sources.append(chunk["filename"])

    context = "\n\n".join(context_parts)

    prompt = f"""You are an expert code assistant
for a GitHub repository.

STRICT RULES:
1. Answer ONLY using sources below.
2. Reference sources using [SOURCE 1], [SOURCE 2] etc.
3. If not in sources say:
   'This information is not in the repository.'
4. End with Sources Used: section.

SOURCES:
{context}

QUESTION: {question}
ANSWER:"""

    try:
        client   = Groq(api_key=GROQ_API_KEY)
        response = client.chat.completions.create(
            model       = "llama-3.1-8b-instant",
            messages    = [{"role": "user", "content": prompt}],
            max_tokens  = 1000,
            temperature = 0.1
        )
        answer = response.choices[0].message.content

    except Exception as e:
        answer = f"Error: {str(e)}"

    return {
        "question": question,
        "answer":   answer,
        "context":  context,
        "sources":  list(set(sources))
    }