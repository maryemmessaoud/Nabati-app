# model/predict.py
from ultralytics import YOLO
from PIL import Image
from pathlib import Path
import torch

# Chemin du modèle
MODEL_PATH = Path(__file__).parent / "best.pt"

# Charger le modèle une seule fois
_model = None

def get_model():
    global _model
    if _model is None:
        _model = YOLO(str(MODEL_PATH))
    return _model

def predict_disease(image: Image.Image) -> dict:
    try:
        model = get_model()

        # Prédiction
        results = model(image, verbose=False)
        probs = results[0].probs

        # Classe prédite
        top1_idx = probs.top1
        top1_conf = float(probs.top1conf)
        disease_name = model.names[top1_idx]

        # Top 3
        top5_idx = probs.top5
        top5_conf = probs.top5conf.tolist()
        top3 = [(model.names[top5_idx[i]], top5_conf[i]) for i in range(3)]

        return {
            "success": True,
            "disease": disease_name,
            "confidence": top1_conf,
            "top3": top3
        }

    except Exception as e:
        return {
            "success": False,
            "error": str(e)
        }