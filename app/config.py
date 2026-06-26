# app/config.py
import os
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()

# Chemins
BASE_DIR    = Path(__file__).parent.parent
MODEL_PATH  = BASE_DIR / "model" / "best.pt"
KB_PATH     = BASE_DIR / "data" / "knowledge_base"
FAISS_PATH  = BASE_DIR / "data" / "faiss_index"
DB_PATH     = BASE_DIR / "data" / "detections.db"

# API
GROQ_API_KEY = os.getenv("GROQ_API_KEY", "")
GROQ_MODEL   = "llama-3.1-8b-instant"

# Modèle
IMG_SIZE     = 224
CONFIDENCE_THRESHOLD = 0.3