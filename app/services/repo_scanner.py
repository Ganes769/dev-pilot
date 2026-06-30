from pathlib import Path
from typing import List


SUPPORTED_EXTENSIONS = {
    # Python
    ".py",
    # JavaScript / TypeScript
    ".js", ".jsx", ".ts", ".tsx", ".mjs", ".cjs",
    # Web
    ".html", ".htm", ".css", ".scss", ".sass",
    # Data / config
    ".json", ".yaml", ".yml", ".toml", ".env",
    # Docs / text
    ".md", ".mdx", ".rst", ".txt",
    # Go
    ".go",
    # Java / Kotlin
    ".java", ".kt", ".kts",
    # Ruby
    ".rb",
    # Rust
    ".rs",
    # C / C++
    ".c", ".cpp", ".h", ".hpp",
    # Shell
    ".sh", ".bash", ".zsh",
    # SQL
    ".sql",
    # Dockerfile
    ".dockerfile",
}

IGNORED_DIRS = {
    ".git",
    "venv",
    ".venv",
    "__pycache__",
    ".pytest_cache",
    "node_modules",
    "dist",
    "build",
    ".next",
    ".nuxt",
    "coverage",
    ".mypy_cache",
    ".ruff_cache",
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
            indexed_files.append(relative_path)

    return sorted(indexed_files)
