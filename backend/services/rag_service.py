# backend/services/rag_service.py
from vector_store import engine, TOP_K_DEFAULT
from typing import List, Dict

def add_knowledge_base_documents(documents: List[Dict]):
    return engine.add_documents(documents)

def query_knowledge_base(question: str, top_k: int = None):
    if top_k is None:
        top_k = TOP_K_DEFAULT
    return engine.search(question, top_k)

def get_stats():
    return {
        "total_vectors": engine.index.ntotal,
        "model": "all-MiniLM-L6-v2"
    }