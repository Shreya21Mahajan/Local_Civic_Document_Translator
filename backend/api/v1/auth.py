from fastapi import APIRouter, HTTPException, Depends, UploadFile, File
from pydantic import BaseModel
from datetime import datetime, timedelta
from jose import jws, JWTError, jwt
from sqlalchemy.orm import Session
from db.session import get_db
from fastapi.security import OAuth2PasswordBearer
router = APIRouter()


SECRET_KEY = "super-secret-key-change-this"
ALGORITHM = "HS256"

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="api/v1/auth/login")

def verify_token(token: str = Depends(oauth2_scheme)):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")

        if username is None:
            raise HTTPException(status_code=401, detail="Invalid credentials")

        return username

    except JWTError:
        raise HTTPException(status_code=401, detail="Invalid token")
class LoginRequest(BaseModel):
    username: str
    password: str

@router.post("/upload")
def upload_document(
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    current_user: str = Depends(verify_token) 
):
    # Now only users with a valid token can upload
    print(f"User {current_user} is uploading...")

@router.post("/login")
def login(credentials: LoginRequest):
    """
    HACKATHON MODE: Accepts ANY username/password and returns a valid JWT.
    """
    # In a real app, you would check DB for user/password here
    
    # Create token data
    expire = datetime.utcnow() + timedelta(minutes=60)
    to_encode = {
        "sub": credentials.username,
        "exp": expire,
        "role": "user"
    }
    
    # Encode the JWT
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    
    return {
        "access_token": encoded_jwt,
        "token_type": "bearer",
        "username": credentials.username,
        "message": "Login successful (Demo Mode)"
    }

@router.get("/me")
def get_current_user():
    return {"info": "Use the token from /login to access protected routes"}
