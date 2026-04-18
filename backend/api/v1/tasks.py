# app/api/v1/tasks.py
from fastapi import APIRouter, UploadFile, File, HTTPException, Depends
from sqlalchemy.orm import Session
from db.session import get_db
from models.document import Document, DocumentStatus
from workers.tasks import process_document_ocr
import os
import uuid
from core.config import settings

router = APIRouter()

# Directory to save uploads locally (for hackathon simplicity)
UPLOAD_DIR = "uploads"
os.makedirs(UPLOAD_DIR, exist_ok=True)

@router.post("/upload")
def upload_document(
    file: UploadFile = File(...),
    db: Session = Depends(get_db)
):
    """
    1. Save file to disk.
    2. Create DB record.
    3. Dispatch Celery Task.
    """
    try:
        # 1. Generate unique filename
        file_extension = file.filename.split(".")[-1]
        unique_filename = f"{uuid.uuid4()}.{file_extension}"
        file_path = os.path.join(UPLOAD_DIR, unique_filename)

        # 2. Save file
        with open(file_path, "wb") as buffer:
            buffer.write(file.file.read())

        # 3. Create DB Record
        new_doc = Document(
            filename=file.filename,
            file_path=file_path,
            status=DocumentStatus.PENDING
        )
        db.add(new_doc)
        db.commit()
        db.refresh(new_doc)

        # 4. Dispatch Async Task
        process_document_ocr.delay(new_doc.id, file_path)

        return {
            "message": "Upload successful. Processing started.",
            "document_id": new_doc.id,
            "status": new_doc.status
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/status/{document_id}")
def get_document_status(document_id: int, db: Session = Depends(get_db)):
    doc = db.query(Document).filter(Document.id == document_id).first()
    if not doc:
        raise HTTPException(status_code=404, detail="Document not found")
    
    response = {
        "id": doc.id,
        "filename": doc.filename,
        "status": doc.status,
        "extracted_text": doc.extracted_text,
        "error": doc.error_message
    }

 
    if doc.status == "COMPLETED" and doc.structured_data:
        response["form"] = doc.structured_data
    
    return response

