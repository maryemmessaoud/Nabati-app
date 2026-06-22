# model/evaluate.py
from ultralytics import YOLO
from pathlib import Path

MODEL_PATH   = "runs/nabati/v1/weights/best.pt"
DATASET_YAML = "PlantDoc-1/data.yaml"

model = YOLO(MODEL_PATH)

# Évaluation sur le set de test
metrics = model.val(data=DATASET_YAML, split="test")

print("\n📊 Résultats Nabati :")
print(f"   mAP@50     : {metrics.box.map50:.3f}")
print(f"   mAP@50-95  : {metrics.box.map:.3f}")
print(f"   Précision  : {metrics.box.mp:.3f}")
print(f"   Rappel     : {metrics.box.mr:.3f}")