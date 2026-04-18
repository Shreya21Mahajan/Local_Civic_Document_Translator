# backend/vector_store/engine.py
import os
import faiss
import numpy as np
import pickle
from sentence_transformers import SentenceTransformer
from typing import List, Dict

# Import local config and utils
from .config import INDEX_PATH, METADATA_PATH, EMBEDDING_MODEL_NAME, DIMENSION
from .utils import chunk_text

class VectorStoreEngine:
    def __init__(self):
        self.model = None
        self.index = None
        self.metadata = []
        self._initialize()

    def _initialize(self):
        """Load model and index."""
        print(f"🤖 Loading Embedding Model: {EMBEDDING_MODEL_NAME}...")
        try:
            self.model = SentenceTransformer(EMBEDDING_MODEL_NAME)
            print("✅ Model loaded.")
        except Exception as e:
            print(f"❌ Error loading model: {e}")
            # Fallback to prevent crash if offline
            self.model = None 

        if os.path.exists(INDEX_PATH) and os.path.exists(METADATA_PATH):
            print(f"📂 Loading existing FAISS index...")
            try:
                self.index = faiss.read_index(INDEX_PATH)
                with open(METADATA_PATH, 'rb') as f:
                    self.metadata = pickle.load(f)
                print(f"✅ Index loaded ({self.index.ntotal} vectors).")
            except Exception as e:
                print(f"⚠️ Failed to load index, creating new one: {e}")
                self.index = faiss.IndexFlatL2(DIMENSION)
                self.metadata = []
        else:
            print("🆕 Creating new FAISS index...")
            self.index = faiss.IndexFlatL2(DIMENSION)
            self.metadata = []
            print("✅ New index created.")

    def add_documents(self, documents: List[Dict[str, str]]):
        if not documents or not self.model:
            return 0
            
        chunks_to_add = []
        for doc in documents:
            text = doc["text"]
            source = doc.get("source", "Unknown")
            chunks = chunk_text(text)
            for chunk in chunks:
                chunks_to_add.append({"text": chunk, "source": source})

        if not chunks_to_add:
            return 0

        texts = [c["text"] for c in chunks_to_add]
        
        try:
            embeddings = self.model.encode(texts, convert_to_numpy=True, normalize=True)
            self.index.add(embeddings.astype('float32'))
            self.metadata.extend(chunks_to_add)
            
            print(f"➕ Added {len(chunks_to_add)} chunks. Total: {self.index.ntotal}")
            self.save()
            return len(chunks_to_add)
        except Exception as e:
            print(f"❌ Error adding documents: {e}")
            return 0

    def search(self, query: str, top_k: int = 3) -> List[Dict]:
        if not self.model or self.index.ntotal == 0:
            return []

        try:
            query_emb = self.model.encode([query], convert_to_numpy=True, normalize=True)
            distances, indices = self.index.search(query_emb.astype('float32'), top_k)
            
            results = []
            for i, idx in enumerate(indices[0]):
                if idx != -1:
                    dist = float(distances[0][i])
                    doc = self.metadata[idx]
                    results.append({
                        "text": doc["text"],
                        "source": doc["source"],
                        "distance": round(dist, 4),
                        "score": round(1 / (1 + dist), 4)
                    })
            return results
        except Exception as e:
            print(f"❌ Search error: {e}")
            return []

    def save(self):
        """Persist index and metadata to disk."""
        if self.index:
            faiss.write_index(self.index, INDEX_PATH)
            with open(METADATA_PATH, 'wb') as f:
                pickle.dump(self.metadata, f)
            print("💾 Index saved.")

# Global Instance
engine = VectorStoreEngine()