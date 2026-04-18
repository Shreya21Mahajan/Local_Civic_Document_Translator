# backend/api/v1/rag.py
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import List, Optional

# Import from your services folder (Flat structure)
from services.rag_service import add_knowledge_base_documents, query_knowledge_base, get_stats

router = APIRouter(prefix="/rag", tags=["RAG"])

class DocumentInput(BaseModel):
    text: str
    source: Optional[str] = "General"

class QueryInput(BaseModel):
    question: str
    top_k: int = 3

@router.post("/add-documents")
async def add_docs_endpoint(docs: List[DocumentInput]):
    formatted = [{"text": d.text, "source": d.source} for d in docs]
    count = add_knowledge_base_documents(formatted)
    return {"message": f"Added {count} chunks to vector database."}
# Seed FAISS with common government forms/rules
government_documents = [
    {
        "title": "Aadhar Registration",
        "content": "Complete guide to Aadhar registration...",
        "language": "en",
        "form_fields": ["name", "dob", "phone", "address"]
    },
    {
        "title": "आधार पंजीकरण",
        "content": "आधार पंजीकरण के लिए पूर्ण गाइड...",
        "language": "hi",
        "form_fields": ["name", "dob", "phone", "address"]
    }
]

@router.post("/query")
async def query_endpoint(data: QueryInput):
    results = query_knowledge_base(data.question, data.top_k)
    if not results:
        return {"answer": "No information found.", "sources": []}
    
    context = "\n".join([f"[{r['source']}]: {r['text']}" for r in results])
    answer = f"Based on retrieved context:\n{context}"
    
    return {"question": data.question, "answer": answer, "sources": results}

@router.get("/stats")
async def stats_endpoint():
    return get_stats()