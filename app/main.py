from fastapi import FastAPI
from app.api.routes.repo import router as repos_router
from app.api.routes.chunck import router as chunks_router
from app.api.routes.vector import  router as vector_router
from app.api.routes.embed import router as embed_router
from app.api.routes.search import router as search_router
from app.api.routes.ask import router as ask_router
app = FastAPI(title="Backend AI Assistant",redoc_url="/redocs")


@app.get("/health")
def health_check():
    return {"status": "ok"}


app.include_router(repos_router)
app.include_router(chunks_router)
app.include_router(vector_router)
app.include_router(embed_router)
app.include_router(search_router)
app.include_router(ask_router)