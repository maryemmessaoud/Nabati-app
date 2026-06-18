# test_install.py
print("Test des imports...")

try:
    from ultralytics import YOLO
    print("✅ ultralytics (YOLOv8) OK")
except:
    print("❌ ultralytics manquant")

try:
    import streamlit
    print("✅ streamlit OK")
except:
    print("❌ streamlit manquant")

try:
    import groq
    print("✅ groq OK")
except:
    print("❌ groq manquant")

try:
    import langchain
    print("✅ langchain OK")
except:
    print("❌ langchain manquant")

try:
    import faiss
    print("✅ faiss OK")
except:
    print("❌ faiss manquant")

try:
    import plotly
    print("✅ plotly OK")
except:
    print("❌ plotly manquant")

print("\nTout est prêt !")