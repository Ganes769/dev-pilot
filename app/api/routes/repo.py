from fastapi import APIRouter, HTTPException
from pathlib import Path

from app.models.schema   import RepoIndexRequest, RepoIndexResponse
from app.services.repo_scanner import scan_repository


router = APIRouter(prefix="/repos", tags=["repos"])


@router.post("/index", response_model=RepoIndexResponse)
def index_repository(payload: RepoIndexRequest):
    try:
        files = scan_repository(payload.repo_path)
        repo_name = Path(payload.repo_path).name

        return RepoIndexResponse(
            repo_name=repo_name,
            files_indexed=len(files),
            files=files,
        )

    except FileNotFoundError as exc:
        raise HTTPException(status_code=404, detail=str(exc))
    except NotADirectoryError as exc:
        raise HTTPException(status_code=400, detail=str(exc))
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"Unexpected error: {exc}")