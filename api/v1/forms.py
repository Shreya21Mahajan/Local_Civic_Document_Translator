# backend/api/v1/forms.py
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Dict, Any, Optional, List
from services.form_engine import FormEngine

router = APIRouter(prefix="/forms", tags=["Forms - Data Mapping"])

class FormFillRequest(BaseModel):
    form_id: str
    # This should contain the extracted entities from NLP/OCR
    extracted_data: Dict[str, Any] 

@router.post("/fill")
async def fill_form(request: FormFillRequest):
    """
    Maps extracted entities to a specific form definition.
    """
    try:
        engine = FormEngine()
        
        # Process the form
        result = engine.process(request.form_id, request.extracted_data)
        
        if not result:
            raise HTTPException(status_code=404, detail=f"Form ID '{request.form_id}' not found.")

        return {
            "status": "success",
            "form_id": request.form_id,
            "filled_data": result
        }
    except ValueError as ve:
        raise HTTPException(status_code=400, detail=str(ve))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/definitions")
async def list_forms():
    """
    Lists all available form definitions.
    """
    try:
        # Returning a static list for demo purposes
        # If your engine has a method to list IDs, use it here
        return {
            "available_forms": [
                {"id": "govt_id_application", "name": "Government ID Application"},
                {"id": "passport_renewal", "name": "Passport Renewal Form"}
            ]
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
