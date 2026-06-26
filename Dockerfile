# Dockerfile
FROM python:3.10-slim

# Métadonnées
LABEL maintainer="Nabati - FST Tunis"
LABEL description="Plateforme intelligente de diagnostic agricole"

# Variables d'environnement
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV STREAMLIT_SERVER_PORT=8501
ENV STREAMLIT_SERVER_ADDRESS=0.0.0.0

# Dossier de travail
WORKDIR /app

# Installer les dépendances système
RUN apt-get update && apt-get install -y \
    libgl1 \
    libglib2.0-0 \
    libsm6 \
    libxext6 \
    libxrender1 \
    && rm -rf /var/lib/apt/lists/*

# Copier et installer les dépendances Python
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copier le projet
COPY app/ ./app/
COPY model/ ./model/
COPY data/knowledge_base/ ./data/knowledge_base/

# Créer les dossiers nécessaires
RUN mkdir -p data/faiss_index data/images_test

# Port exposé
EXPOSE 8501

# Lancer l'application
CMD ["streamlit", "run", "app/main.py", \
     "--server.port=8501", \
     "--server.address=0.0.0.0", \
     "--server.headless=true"]