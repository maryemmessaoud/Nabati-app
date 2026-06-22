# model/train.py
from ultralytics import YOLO
import yaml
from pathlib import Path

# --- Config ---
DATASET_YAML = "PlantDoc-1/data.yaml"
MODEL_BASE   = "yolov8n.pt"   # nano = léger, idéal pour commencer
EPOCHS       = 50
IMG_SIZE     = 640
BATCH        = 8             # réduis à 8 si ton PC manque de RAM
PROJECT_NAME = "runs/nabati"
RUN_NAME     = "v1"

def train():
    print("🌿 Nabati — Démarrage de l'entraînement YOLOv8")
    print(f"   Modèle  : {MODEL_BASE}")
    print(f"   Dataset : {DATASET_YAML}")
    print(f"   Epochs  : {EPOCHS}")

    # Charger le modèle pré-entraîné
    model = YOLO(MODEL_BASE)

    # Lancer l'entraînement
    results = model.train(
        data    = DATASET_YAML,
        epochs  = EPOCHS,
        imgsz   = IMG_SIZE,
        batch   = BATCH,
        project = PROJECT_NAME,
        name    = RUN_NAME,
        patience= 10,          # arrêt si pas d'amélioration pendant 10 epochs
        save    = True,
        plots   = True,        # génère les courbes de perte
        verbose = True,
    )

    print("\n✅ Entraînement terminé !")
    best_model = Path(PROJECT_NAME) / RUN_NAME / "weights" / "best.pt"
    print(f"   Meilleur modèle : {best_model}")
    return results

if __name__ == "__main__":
    train()