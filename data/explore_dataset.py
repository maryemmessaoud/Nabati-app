# data/explore_dataset.py
import os
from pathlib import Path
from collections import Counter
import matplotlib.pyplot as plt

DATASET_PATH = Path("PlantDoc-1")

# --- Compter les images par split ---
for split in ["train", "valid", "test"]:
    images = list((DATASET_PATH / split / "images").glob("*.jpg"))
    images += list((DATASET_PATH / split / "images").glob("*.png"))
    print(f"{split:6} : {len(images)} images")

# --- Lire les classes depuis data.yaml ---
import yaml
with open(DATASET_PATH / "data.yaml", "r") as f:
    config = yaml.safe_load(f)

classes = config["names"]
print(f"\n{len(classes)} classes détectées :")
for i, name in enumerate(classes):
    print(f"  {i:2}. {name}")

# --- Compter les annotations par classe ---
label_counts = Counter()
for label_file in (DATASET_PATH / "train" / "labels").glob("*.txt"):
    with open(label_file) as f:
        for line in f:
            class_id = int(line.split()[0])
            label_counts[classes[class_id]] += 1

# --- Afficher un graphique ---
sorted_counts = dict(sorted(label_counts.items(), key=lambda x: x[1], reverse=True))

plt.figure(figsize=(14, 6))
plt.bar(sorted_counts.keys(), sorted_counts.values(), color="green", alpha=0.7)
plt.xticks(rotation=45, ha="right", fontsize=9)
plt.title("Distribution des classes dans le dataset Nabati")
plt.ylabel("Nombre d'annotations")
plt.tight_layout()
plt.savefig("data/distribution_classes.png")
plt.show()
print("\nGraphique sauvegardé dans data/distribution_classes.png")