# data/download_dataset.py
from roboflow import Roboflow
from dotenv import load_dotenv
import os
from pathlib import Path

load_dotenv()

rf = Roboflow(api_key=os.getenv("ROBOFLOW_API_KEY"))
project = rf.workspace("roboflow-universe-projects").project("plantdoc")

# Téléchargement direct sans zip
dataset = project.version(1).download("yolov8", location="PlantDoc-1")

print("✅ Dataset téléchargé !")

# Vérification
for split in ["train", "valid", "test"]:
    folder = Path("PlantDoc-1") / split / "images"
    if folder.exists():
        count = len(list(folder.glob("*.*")))
        print(f"  {split:6} : {count} images")
    else:
        print(f"  {split:6} : dossier introuvable")