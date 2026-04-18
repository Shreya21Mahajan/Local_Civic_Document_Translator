import faiss
from app.vector_store.embeddings import get_embedding_model

class RAGEngine:
    def __init__(self):
        self.index = faiss.read_index("data/faiss_index/govt_rules.index")
        self.embedder = get_embedding_model()

    def retrieve(self, query: str, k=3):
        embedding = self.embedder.encode([query])
        distances, indices = self.index.search(embedding, k)
        return indices 