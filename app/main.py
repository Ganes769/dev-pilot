from fastapi import FastAPI
from app.api.routes.repo import router as repos_router
from app.api.routes.chunck import router as chunks_router

app = FastAPI(title="Backend AI Assistant",redoc_url="/redocs")


@app.get("/health")
def health_check():
    return {"status": "ok"}


app.include_router(repos_router)
app.include_router(chunks_router)