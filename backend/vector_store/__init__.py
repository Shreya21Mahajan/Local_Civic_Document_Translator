# backend/vector_store/__init__.py

# 1. Import the config constant
from .config import TOP_K_DEFAULT

# 2. Import the engine instance
from .engine import engine

# 3. Define what gets exported when someone does "from vector_store import ..."
__all__ = ["engine", "TOP_K_DEFAULT"]