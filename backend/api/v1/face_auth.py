# backend/api/v1/face_auth.py
import os 
import sys
from fastapi import APIRouter, UploadFile, File, Form, HTTPException
current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir) # Goes from api/v1 -> api -> backend
if parent_dir not in sys.path:
    sys.path.insert(0, parent_dir)
from services.face_auth_services import (
    load_known_faces_from_disk, 
    register_new_face, 
    authenticate_face
)

router = APIRouter(prefix="/face-auth", tags=["Face Authentication"])

# Load faces on startup (optional: can also be done in main.py lifespan)
@router.on_event("startup")
async def load_faces_event():
    load_known_faces_from_disk()

@router.post("/register")
async def register_face_endpoint(
    image: UploadFile = File(...),
    name: str = Form(...)
):
    """Register a new child/user face."""
    if not name:
        raise HTTPException(status_code=400, detail="Name is required")
    
    result = register_new_face(image, name)
    
    if not result["success"]:
        raise HTTPException(status_code=400, detail=result["message"])
    
    return result

@router.post("/authenticate")
async def authenticate_face_endpoint(
    image: UploadFile = File(...)
):
    """Authenticate a selfie against registered faces."""
    result = authenticate_face(image)
    
    if result["status"] == "error":
        raise HTTPException(status_code=500, detail=result["message"])
    
    return result