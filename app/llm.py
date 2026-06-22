# app/llm.py
import os
import requests
from dotenv import load_dotenv

load_dotenv()

def get_treatment_advice(plant: str, disease: str, confidence: float) -> str:
    """Génère des conseils de traitement via Groq API."""

    if "healthy" in disease.lower():
        return f"✅ Votre **{plant}** est en bonne santé ! Continuez vos bonnes pratiques agricoles."

    prompt = f"""Tu es un expert agronome. Un agriculteur a soumis une photo de sa plante.

Résultat du diagnostic :
- Plante : {plant}
- Maladie détectée : {disease}
- Niveau de confiance : {confidence:.1%}

Donne des conseils pratiques en français avec ces sections :
1. 🔍 Description rapide de la maladie (2-3 phrases)
2. ⚠️ Symptômes à surveiller (3 points)
3. 💊 Traitement recommandé (3-4 points concrets)
4. 🛡️ Prévention (2-3 points)
5. ⏰ Urgence : Bas / Moyen / Élevé
"""

    headers = {
        "Authorization": f"Bearer {os.getenv('GROQ_API_KEY')}",
        "Content-Type": "application/json"
    }

    payload = {
        "model": "llama-3.1-8b-instant",
        "messages": [{"role": "user", "content": prompt}],
        "max_tokens": 600,
        "temperature": 0.7
    }

    response = requests.post(
        "https://api.groq.com/openai/v1/chat/completions",
        headers=headers,
        json=payload
    )

    if response.status_code == 200:
        return response.json()["choices"][0]["message"]["content"]
    else:
        return f"❌ Erreur API : {response.status_code} — {response.text}"