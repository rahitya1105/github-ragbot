# repo_loader.py
# Loads all supported files from a repository folder

import os

SUPPORTED_EXTENSIONS = [
    ".py", ".md", ".js", ".ts",
    ".txt", ".json", ".yaml", ".yml",
    ".toml", ".cfg", ".rst"
]

SKIP_FOLDERS = [
    ".git", "__pycache__", "node_modules",
    ".venv", "venv", "env", ".env",
    "dist", "build", ".idea", ".vscode"
]


def load_repo_files(repo_path: str) -> list:
    documents = []

    if not os.path.exists(repo_path):
        print(f"ERROR: Path does not exist: {repo_path}")
        return documents

    for root, dirs, files in os.walk(repo_path):
        dirs[:] = [
            d for d in dirs
            if d not in SKIP_FOLDERS
            and not d.startswith('.')
        ]

        for filename in files:
            ext = os.path.splitext(filename)[1].lower()
            if ext not in SUPPORTED_EXTENSIONS:
                continue

            filepath = os.path.join(root, filename)

            try:
                with open(filepath, "r",
                          encoding="utf-8",
                          errors="ignore") as f:
                    content = f.read()

                if not content.strip():
                    continue

                documents.append({
                    "content":   content,
                    "filename":  filename,
                    "filepath":  filepath,
                    "extension": ext,
                    "size":      len(content)
                })

            except Exception as e:
                print(f"Skipped {filepath}: {e}")

    print(f"✅ Loaded {len(documents)} files")
    return documents