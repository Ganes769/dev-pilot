from fastapi import APIRouter,HTTPException
from pathlib import Path
from app.models.schema import RepoChunckResponse,RepoChunckRequest,ChunckPreview
from app.services.repo_scanner import scan_repository
from app.services.file_reader import read_file_content
from app.services.chuncker import chunk_text

router=APIRouter(prefix="/repo",tags=["chuncks"])
@router.post("/chunck",response_model=RepoChunckResponse)
def chunck_repository(payload:RepoChunckRequest):
    try:
        repo_name=Path(payload.repo_path).name
        files=scan_repository(payload.repo_path)
        previews=[]
        total_chuncks=0
        for relative_file_path in files:
            content=read_file_content(payload.repo_path,relative_file_path)
            chunks=chunk_text(text=content,chunk_size=payload.chunck_size,overlap=payload.overlap)
            total_chuncks += len(chunks)
            for idx, ch in enumerate(chunks[:2]):
                previews.append(
                    ChunckPreview(
                        file_path=relative_file_path,
                        chunck_index=idx,
                        text_preview=ch[:200],
                    )
                )
        return RepoChunckResponse(
            repo_name=repo_name,
            total_files=len(files),
            total_chuncks=total_chuncks,
            chunck_preview=previews[:20],
        )
    except FileNotFoundError as exc:
        raise HTTPException(status_code=404, detail=str(exc))
    except NotADirectoryError as exc:
        raise HTTPException(status_code=400, detail=str (exc))
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc))
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"Unexpected error: {exc}")
