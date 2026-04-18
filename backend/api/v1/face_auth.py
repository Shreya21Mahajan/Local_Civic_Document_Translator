import os
import sys
from typing import Optional

from fastapi import APIRouter, UploadFile, File, Form, HTTPException, Depends, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session

# --- Path Configuration for Flat Structure ---
current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir) # api/v1 -> api
root_dir = os.path.dirname(parent_dir)    # api -> backend

if root_dir not in sys.path:
    sys.path.insert(0, root_dir)

# --- Imports: Local Services (Legacy/Demo) ---
# These handle in-memory/file-based face storage
from services.face_auth_services import (
    load_known_faces_from_disk, 
    register_new_face as register_local_face, 
    authenticate_face as authenticate_local_face
)

# --- Imports: Database Services (Production) ---
# These handle SQL-based family linking and JWT generation
from services.face_auth_service import FaceAuthService
from services.auth_service import create_access_token
from database.session import get_db
from models.user import User # Ensure your User model is imported

# --- Security Setup ---
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="api/v1/auth/login")

router = APIRouter(prefix="/face-auth", tags=["Face Authentication"])

# Initialize DB Service
db_face_service = FaceAuthService()

# ==========================================
# 🚀 Startup Event
# ==========================================
@router.on_event("startup")
async def load_faces_event():
    """Load existing faces from disk on server start (for Legacy Mode)."""
    print(" Loading known faces from disk...")
    load_known_faces_from_disk()

# ==========================================
# 🔐 Helper: Get Current User
# ==========================================
async def get_current_active_user(
    token: str = Depends(oauth2_scheme), 
    db: Session = Depends(get_db)
):
    """
    Decode JWT and return user object. 
    (Simplified logic - replace with your actual auth dependency)
    """
    from jose import jwt, JWTError
    from core.config import settings # Assuming you have SECRET_KEY in config
    
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        user_id: str = payload.get("sub")
        if user_id is None:
            raise HTTPException(status_code=401, detail="Invalid token")
        
        user = db.query(User).filter(User.id == int(user_id)).first()
        if user is None:
            raise HTTPException(status_code=401, detail="User not found")
        return user
    except JWTError:
        raise HTTPException(status_code=401, detail="Could not validate credentials")

# ==========================================
# 🟢 MODE 1: Legacy / Standalone (No DB Required)
# Best for: Quick demos, single-user kiosk mode
# ==========================================

@router.post("/register")
async def register_face_endpoint(
    image: UploadFile = File(...),
    name: str = Form(...)
):
    """
    [Legacy] Register a new face to local storage.
    Does not require login. Good for initial setup.
    """
    if not name:
        raise HTTPException(status_code=400, detail="Name is required")
    
    # Use local service
    result = register_local_face(image, name)
    
    if not result["success"]:
        raise HTTPException(status_code=400, detail=result["message"])
    
    return result

@router.post("/authenticate")
async def authenticate_face_endpoint(
    image: UploadFile = File(...)
):
    """
    [Legacy] Authenticate against local storage.
    Returns identity name but NO JWT token.
    """
    result = authenticate_local_face(image)
    
    if result["status"] == "error":
        raise HTTPException(status_code=500, detail=result["message"])
    
    if result["status"] == "denied":
        raise HTTPException(status_code=401, detail=result["message"])
    
    return result

# ==========================================
# 🔵 MODE 2: Production (Database + JWT)
# Best for: Multi-user families, secure login
# ==========================================

@router.post("/login")
async def biometric_login(
    image: UploadFile = File(...),
    db: Session = Depends(get_db)
):
    """
    [Production] Login purely by scanning a face.
    Searches ALL family faces in DB. Returns JWT Token if matched.
    """
    # Use DB service to find user by face
    result = db_face_service.authenticate_login_by_face(db, image.file)
    
    if result["status"] == "denied":
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, 
            detail=result["message"],
            headers={"WWW-Authenticate": "FaceAuth"},
        )
    
    user = result["user"]
    
    # Generate JWT
    access_token = create_access_token(data={"sub": str(user.id)})
    
    return {
        "access_token": access_token,
        "token_type": "bearer",
        "user_info": {
            "id": user.id,
            "name": user.full_name,
            "email": user.email,
            "recognized_as": result["identity_name"] # e.g., "Dad", "Mom"
        }
    }

@router.post("/register-family")
async def register_family_member(
    name: str = Form(...),
    image: UploadFile = File(...),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    [Production] Link a new family member's face to the logged-in user's account.
    Requires valid JWT token in header.
    """
    if not name:
        raise HTTPException(status_code=400, detail="Relation/Name is required")
    
    try:
        result = db_face_service.register_family_face(
            db=db, 
            user_id=current_user.id, 
            name=name, 
            image_file=image.file
        )
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/family-members")
async def list_family_members(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    [Production] List all registered faces for the current user.
    """
    faces = db.query(models.FamilyFace).filter(models.FamilyFace.user_id == current_user.id).all()
    return {
        "count": len(faces),
        "members": [{"id": f.id, "name": f.name} for f in faces]
    }
