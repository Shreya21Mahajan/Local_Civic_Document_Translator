# backend/main.py
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from core.config import settings

# ✅ IMPORTS: Ensure 'forms' is plural here
from api.v1 import auth, tasks, rag, face_auth, nlp, ocr, forms

app = FastAPI(title=settings.PROJECT_NAME)

# Allow Frontend to connect (CORS)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], 
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include Routers
app.include_router(auth.router, prefix="/api/v1/auth", tags=["Auth"])
app.include_router(tasks.router, prefix="/api/v1/tasks", tags=["Tasks"])
app.include_router(face_auth.router, prefix="/api/v1", tags=["Face Auth"]) 
app.include_router(rag.router, prefix="/api/v1", tags=["RAG"])
app.include_router(nlp.router, prefix="/api/v1", tags=["NLP"])
app.include_router(ocr.router, prefix="/api/v1", tags=["OCR"])


app.include_router(forms.router, prefix="/api/v1", tags=["Forms"])

@app.get("/")
def read_root():
    return {
        "message": "AITR All-Service Backend Running",
        "modules": [
            "Authentication", "Tasks (OCR+NLP+Form)", 
            "Face Auth", "RAG", "Standalone NLP", 
            "Standalone OCR", "Form Engine"
        ]
    }

@app.get("/health")
def health_check():
    return {"status": "healthy", "service": "backend"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)