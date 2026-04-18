# backend/api/v1/nlp.py
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Optional
from services.nlp_services import process_document_text

router = APIRouter(prefix="/nlp", tags=["NLP - Text Analysis"])

class TextAnalysisRequest(BaseModel):
    text: str
    # Optional: Add fields if your service supports language selection later
    # language: str = "en"

@router.post("/analyze")
async def analyze_text( request: TextAnalysisRequest):
    """
    Analyzes raw text to extract entities (Email, Phone, Date, Names) 
    and clean OCR noise.
    """
    try:
        if not request.text.strip():
            raise HTTPException(status_code=400, detail="Text cannot be empty")
            
        result = process_document_text(request.text)
        
        return {
            "status": "success",
            "data": result
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/health")
async def nlp_health():
    return {"status": "healthy", "service": "NLP Engine"}
