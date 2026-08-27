from fastapi import APIRouter, BackgroundTasks, UploadFile, File, HTTPException
from pathlib import Path
from uuid import uuid4

from app.services.document_processor import process_document
from app.services.document_status import (
    DocumentStatus,
    get_document_status,
    set_document_status,
)
from app.services.document_text import get_document_text
from app.services.search_service import search_document

router = APIRouter(
    prefix="/api/v1/documents",
    tags=["Documents"],
)

UPLOAD_DIR = Path(__file__).resolve().parents[2] / "uploads"
UPLOAD_DIR.mkdir(parents=True, exist_ok=True)


@router.post("/upload")
async def upload_document(
    background_tasks: BackgroundTasks,
    file: UploadFile = File(...),
):
    if not file.filename:
        raise HTTPException(
            status_code=400,
            detail="No file was provided.",
        )

    if Path(file.filename).suffix.lower() != ".pdf":
        raise HTTPException(
            status_code=400,
            detail="Only PDF files are allowed.",
        )

    document_id = str(uuid4())
    safe_filename = f"{document_id}.pdf"
    file_path = UPLOAD_DIR / safe_filename

    try:
        contents = await file.read()
        file_path.write_bytes(contents)

        set_document_status(document_id, DocumentStatus.PENDING)

        background_tasks.add_task(
            process_document,
            document_id,
            str(file_path),
        )

    except Exception as exc:
        raise HTTPException(
            status_code=500,
            detail="Failed to save the uploaded document.",
        ) from exc

    return {
        "document_id": document_id,
        "filename": file.filename,
        "status": "pending",
    }


@router.get("/{document_id}/status")
async def get_document_processing_status(document_id: str):
    status = get_document_status(document_id)

    if status is None:
        raise HTTPException(
            status_code=404,
            detail="Document not found.",
        )

    return {
        "document_id": document_id,
        "status": status.value,
    }


@router.get("/{document_id}/text")
async def get_document_extracted_text(document_id: str):
    status = get_document_status(document_id)

    if status is None:
        raise HTTPException(
            status_code=404,
            detail="Document not found.",
        )

    if status != DocumentStatus.COMPLETED:
        raise HTTPException(
            status_code=409,
            detail=f"Document processing is not completed. Current status: {status.value}",
        )

    text = get_document_text(document_id)

    if text is None:
        raise HTTPException(
            status_code=404,
            detail="Extracted text not found.",
        )

    return {
        "document_id": document_id,
        "text": text,
        "character_count": len(text),
    }


@router.get("/{document_id}/search")
async def search_document_content(
    document_id: str,
    query: str,
    top_k: int = 5,
):
    status = get_document_status(document_id)

    if status is None:
        raise HTTPException(
            status_code=404,
            detail="Document not found.",
        )

    if status != DocumentStatus.COMPLETED:
        raise HTTPException(
            status_code=409,
            detail=f"Document processing is not completed. Current status: {status.value}",
        )

    if not query.strip():
        raise HTTPException(
            status_code=400,
            detail="Search query cannot be empty.",
        )

    if top_k < 1 or top_k > 20:
        raise HTTPException(
            status_code=400,
            detail="top_k must be between 1 and 20.",
        )

    results = search_document(
        document_id=document_id,
        query=query,
        top_k=top_k,
    )

    return {
        "document_id": document_id,
        "query": query,
        "results": results,
    }