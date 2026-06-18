# data/verify_annotations.py
import cv2
import yaml
import random
from pathlib import Path

DATASET_PATH = Path("PlantDoc-1")

with open(DATASET_PATH / "data.yaml") as f:
    config = yaml.safe_load(f)
classes = config["names"]

# Prendre une image au hasard dans train
images = list((DATASET_PATH / "train" / "images").glob("*.jpg"))
img_path = random.choice(images)
label_path = DATASET_PATH / "train" / "labels" / (img_path.stem + ".txt")

# Lire l'image
img = cv2.imread(str(img_path))
h, w = img.shape[:2]

# Dessiner les bounding boxes
with open(label_path) as f:
    for line in f:
        parts = line.strip().split()
        class_id = int(parts[0])
        cx, cy, bw, bh = map(float, parts[1:])

        x1 = int((cx - bw / 2) * w)
        y1 = int((cy - bh / 2) * h)
        x2 = int((cx + bw / 2) * w)
        y2 = int((cy + bh / 2) * h)

        cv2.rectangle(img, (x1, y1), (x2, y2), (0, 255, 0), 2)
        cv2.putText(img, classes[class_id], (x1, y1 - 8),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 0), 2)

# ✅ Sauvegarder au lieu d'afficher
output_path = Path("data/sample_annotation.jpg")
cv2.imwrite(str(output_path), img)
print(f"✅ Image sauvegardée : {output_path}")
print(f"   Image source : {img_path.name}")
print(f"   Classes détectées : {classes}")