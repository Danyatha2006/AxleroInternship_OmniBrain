from fastapi import FastAPI

app = FastAPI(
    title="OmniBrain API",
    description="Backend API for the OmniBrain Agentic Multi-Modal RAG System",
    version="1.0.0",
)


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
        "status": "healthy"
    }