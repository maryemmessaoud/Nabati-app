# app/main.py
import streamlit as st
from PIL import Image
import sys
from pathlib import Path

# Ajouter le dossier racine au path
sys.path.append(str(Path(__file__).parent.parent))
from model.predict import predict_disease

# --- Configuration de la page ---
st.set_page_config(
    page_title="Nabati — Diagnostic Agricole",
    page_icon="🌿",
    layout="wide",
    initial_sidebar_state="expanded"
)

# --- CSS personnalisé ---
st.markdown("""
<style>
    .main-title {
        font-size: 2.5rem;
        font-weight: 800;
        color: #2d6a4f;
        text-align: center;
        margin-bottom: 0.2rem;
    }
    .subtitle {
        font-size: 1.1rem;
        color: #74c69d;
        text-align: center;
        margin-bottom: 2rem;
    }
    .result-box {
        background: linear-gradient(135deg, #d8f3dc, #b7e4c7);
        border-radius: 16px;
        padding: 1.5rem;
        border-left: 5px solid #2d6a4f;
        margin-top: 1rem;
    }
    .disease-name {
        font-size: 1.8rem;
        font-weight: 700;
        color: #1b4332;
    }
    .confidence-text {
        font-size: 1rem;
        color: #40916c;
        margin-top: 0.3rem;
    }
    .warning-box {
        background: #fff3cd;
        border-radius: 12px;
        padding: 1rem;
        border-left: 5px solid #ffc107;
        margin-top: 1rem;
    }
</style>
""", unsafe_allow_html=True)

# --- Sidebar ---
with st.sidebar:
    st.image("https://em-content.zobj.net/source/apple/354/seedling_1f331.png", width=80)
    st.markdown("## 🌿 Nabati")
    st.markdown("**Plateforme intelligente de diagnostic agricole**")
    st.markdown("---")
    st.markdown("### Navigation")
    page = st.radio("", [
        "🔍 Diagnostic",
        "💬 Chatbot",
        "📊 Dashboard"
    ])
    st.markdown("---")
    st.markdown("*FST Tunis — Cycle Ingénieur Data Science*")

# --- Page Diagnostic ---
if page == "🔍 Diagnostic":
    st.markdown('<div class="main-title">🌿 Nabati</div>', unsafe_allow_html=True)
    st.markdown('<div class="subtitle">Diagnostic intelligent des maladies des plantes</div>',
                unsafe_allow_html=True)

    col1, col2 = st.columns([1, 1], gap="large")

    with col1:
        st.markdown("### 📸 Uploader une image")
        uploaded_file = st.file_uploader(
            "Choisissez une photo de plante",
            type=["jpg", "jpeg", "png"],
            help="Prenez une photo claire de la feuille ou de la plante"
        )

        if uploaded_file:
            image = Image.open(uploaded_file)
            st.image(image, caption="Image uploadée", use_column_width=True)

    with col2:
        st.markdown("### 🤖 Résultat du diagnostic")

        if uploaded_file is None:
            st.info("👈 Uploadez une image pour commencer le diagnostic")
            st.markdown("#### Comment ça marche ?")
            st.markdown("""
            1. 📸 **Uploadez** une photo de votre plante
            2. 🤖 **YOLOv8** analyse et détecte la maladie
            3. 💡 **Le LLM** génère des recommandations
            4. 📚 **Posez vos questions** au chatbot
            """)
        else:
            with st.spinner("🔍 Analyse en cours..."):
                result = predict_disease(image)

            if result["success"]:
                # Afficher le résultat
                disease_raw = result["disease"]
                confidence = result["confidence"]

                # Formater le nom : "Tomato__Late_blight" → "Tomate — Mildiou tardif"
                parts = disease_raw.split("__")
                plant = parts[0].replace("_", " ") if len(parts) > 0 else ""
                disease = parts[1].replace("_", " ") if len(parts) > 1 else disease_raw

                st.markdown(f"""
                <div class="result-box">
                    <div class="disease-name">🌱 {plant}</div>
                    <div class="disease-name">🦠 {disease}</div>
                    <div class="confidence-text">Confiance : {confidence:.1%}</div>
                </div>
                """, unsafe_allow_html=True)

                # Barre de confiance
                st.markdown("#### Niveau de confiance")
                st.progress(confidence)

                # Top 3 des prédictions
                if "top3" in result:
                    st.markdown("#### Top 3 des prédictions")
                    for i, (name, conf) in enumerate(result["top3"]):
                        parts = name.split("__")
                        label = f"{parts[0]} — {parts[1].replace('_', ' ')}" if len(parts) > 1 else name
                        st.write(f"{i+1}. **{label}** ({conf:.1%})")

                # Alerte si confiance faible
                if confidence < 0.5:
                    st.markdown("""
                    <div class="warning-box">
                        ⚠️ <b>Confiance faible</b> — Essayez avec une image plus nette et mieux éclairée.
                    </div>
                    """, unsafe_allow_html=True)

                # Bouton vers chatbot
                st.success("✅ Diagnostic terminé !")
                st.markdown("💬 **Allez dans le Chatbot** pour des recommandations de traitement !")

            else:
                st.error(f"❌ Erreur : {result['error']}")

# --- Page Chatbot (placeholder) ---
elif page == "💬 Chatbot":
    st.markdown("## 💬 Chatbot Nabati")
    st.info("🚧 Cette fonctionnalité sera disponible à l'étape 6 !")

# --- Page Dashboard (placeholder) ---
elif page == "📊 Dashboard":
    st.markdown("## 📊 Dashboard Nabati")
    st.info("🚧 Cette fonctionnalité sera disponible à l'étape 9 !")