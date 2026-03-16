from fastapi import APIRouter, HTTPException
from app.services.vector_store import create_collection

router=APIRouter(prefix="/vector",tags=["vector"])
@router.post("/setup")
def setup_vector_db():
    try:
        create_collection()
        return {
            "message":"Vector datbase connected successfully"}
    except Exception as exc:
        raise HTTPException(status_code=500,detail=str(exc))