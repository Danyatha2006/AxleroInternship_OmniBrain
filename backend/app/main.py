from pathlib import Path

from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles

from app.api.documents import router as documents_router
from app.api.chat import router as chat_router


app = FastAPI(
    title="OmniBrain API",
    description="Backend API for the OmniBrain Agentic Multi-Modal RAG System",
    version="1.0.0",
)


BASE_DIR = Path(__file__).resolve().parents[1]
EXTRACTED_IMAGES_DIR = BASE_DIR / "extracted_images"

EXTRACTED_IMAGES_DIR.mkdir(
    parents=True,
    exist_ok=True,
)


app.mount(
    "/extracted_images",
    StaticFiles(directory=str(EXTRACTED_IMAGES_DIR)),
    name="extracted_images",
)


app.include_router(documents_router)
app.include_router(chat_router)


@app.get("/")
async def root():
    return {
        "application": "OmniBrain",
        "status": "running",
        "version": "1.0.0",
    }


@app.get("/health")
async def health_check():
    return {
        "status": "healthy",
    }