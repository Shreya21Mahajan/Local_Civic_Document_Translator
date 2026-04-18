# backend/vector_store/config.py
import os

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
INDEX_PATH = os.path.join(BASE_DIR, "faiss_index.index")
METADATA_PATH = os.path.join(BASE_DIR, "faiss_metadata.pkl")

EMBEDDING_MODEL_NAME = "all-MiniLM-L6-v2"
DIMENSION = 384

# 👇 THIS VARIABLE MUST EXIST 👇
TOP_K_DEFAULT = 3