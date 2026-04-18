# backend/api/v1/ocr.py
import os
import tempfile
import shutil
from fastapi import APIRouter, UploadFile, File, HTTPException
from services.ocr_services import extract_text_from_image

router = APIRouter(prefix="/ocr", tags=["OCR - Image to Text"])

@router.post("/extract")
async def extract_text( image: UploadFile = File(...)):
    """
    Extracts text from an uploaded image (JPG, PNG) using PaddleOCR.
    Returns the raw extracted text.
    """
    # Validate file type
    allowed_extensions = [".jpg", ".jpeg", ".png", ".bmp"]
    file_ext = os.path.splitext(image.filename)[1].lower()
    
    if file_ext not in allowed_extensions:
        raise HTTPException(status_code=400, detail=f"Invalid file type. Allowed: {allowed_extensions}")

    temp_file_path = None
    
    try:
        # Create a temporary file to save the upload
        with tempfile.NamedTemporaryFile(delete=False, suffix=file_ext) as tmp_file:
            content = await image.read()
            tmp_file.write(content)
            temp_file_path = tmp_file.name

        # Call the service
        extracted_text = extract_text_from_image(temp_file_path)
        
        if not extracted_text:
            return {
                "status": "warning",
                "message": "Image processed but no text detected.",
                "text": ""
            }

        return {
            "status": "success",
            "filename": image.filename,
            "text": extracted_text,
            "char_count": len(extracted_text)
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"OCR Processing Failed: {str(e)}")
    
    finally:
        # Cleanup temp file
        if temp_file_path and os.path.exists(temp_file_path):
            try:
                os.remove(temp_file_path)
            except:
                pass

@router.get("/health")
async def ocr_health():
    return {"status": "healthy", "service": "PaddleOCR Engine"}
