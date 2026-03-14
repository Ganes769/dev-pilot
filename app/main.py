from fastapi import FastAPI
from app.api.routes.repo import router as repos_router


app = FastAPI(title="Backend AI Assistant")


@app.get("/health")
def health_check():
    return {"status": "ok"}


app.include_router(repos_router)