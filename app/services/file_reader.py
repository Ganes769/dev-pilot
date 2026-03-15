from pathlib import Path
def read_file_content(repo_path:str,relative_repo_path:str)->str:
    full_path=Path(repo_path)/relative_repo_path
    try:
        return full_path.read_text(encoding="utf-8")
    except UnicodeDecodeError:
        return full_path.read_text(encoding="utf-8",errors="ignore")
