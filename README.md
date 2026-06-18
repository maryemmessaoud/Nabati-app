# 🌿 Nabati — Plateforme intelligente de diagnostic agricole

Nabati (نباتي) est une application web qui permet à un agriculteur de :
- 📸 Uploader une photo de plante
- 🤖 Détecter la maladie via YOLOv8
- 💡 Recevoir des recommandations via LLM
- 📚 Poser des questions via un chatbot RAG
- 📊 Consulter un dashboard de statistiques

## Stack technique
- **Détection** : YOLOv8 (Ultralytics)
- **LLM** : Groq (Llama 3)
- **RAG** : LangChain + FAISS
- **Interface** : Streamlit
- **Déploiement** : Docker + Cloud

## Installation
\```bash
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
streamlit run app/main.py
\```

## Projet académique
FST Tunis — Cycle Ingénieur Data Science