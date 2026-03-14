from pathlib import Path
from typing import List

SUPPORTED_EXTENSIONS = {".py", ".md", ".json", ".yaml", ".yml"}
IGNORED_DIRS = {
    ".git",
    "venv",
    ".venv",
    "__pycache__",
    ".pytest_cache",
    "node_modules",
    "."
}

def scan_repository(repo_path: str) -> List[str]:
    root = Path(repo_path)

    if not root.exists():
        raise FileNotFoundError(f"Path does not exist: {repo_path}")

    if not root.is_dir():
        raise NotADirectoryError(f"Path is not a directory: {repo_path}")

    indexed_files = []

    for file_path in root.rglob("*"):
        if not file_path.is_file():
            continue

        relative_parts = file_path.relative_to(root).parts
        if any(part in IGNORED_DIRS for part in relative_parts):
            continue

        if file_path.suffix.lower() in SUPPORTED_EXTENSIONS:
            relative_path = file_path.relative_to(root).as_posix()
            print("ADDING:", relative_path)
            indexed_files.append(relative_path)

    print("FINAL INDEXED FILES:", indexed_files)
    return sorted(indexed_files)