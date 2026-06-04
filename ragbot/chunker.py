# chunker.py
# Splits documents into smart overlapping chunks

from langchain_text_splitters import RecursiveCharacterTextSplitter


def get_splitter(ext: str):
    if ext == ".py":
        separators = [
            "\nclass ", "\ndef ",
            "\n    def ", "\n\n", "\n", " ", ""
        ]
    elif ext in [".js", ".ts"]:
        separators = [
            "\nfunction ", "\nconst ",
            "\nclass ", "\n\n", "\n", " ", ""
        ]
    elif ext == ".md":
        separators = [
            "\n## ", "\n### ",
            "\n\n", "\n", " ", ""
        ]
    else:
        separators = ["\n\n", "\n", " ", ""]

    return RecursiveCharacterTextSplitter(
        chunk_size    = 500,
        chunk_overlap = 50,
        separators    = separators
    )


def chunk_all_documents(documents: list) -> list:
    all_chunks = []

    for doc in documents:
        splitter   = get_splitter(doc.get("extension", ".txt"))
        raw_chunks = splitter.split_text(doc["content"])

        for index, text in enumerate(raw_chunks):
            if not text.strip():
                continue

            all_chunks.append({
                "chunk_id":    f"{doc['filepath']}__chunk_{index}",
                "text":        text,
                "filename":    doc["filename"],
                "filepath":    doc["filepath"],
                "extension":   doc.get("extension", ".txt"),
                "chunk_index": index,
                "chunk_size":  len(text)
            })

    print(f"✅ Created {len(all_chunks)} chunks")
    return all_chunks
