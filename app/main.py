# app/main.py
import streamlit as st
from PIL import Image
import sys
from pathlib import Path
sys.path.append(str(Path(__file__).parent))
from llm import get_treatment_advice
sys.path.append(str(Path(__file__).parent.parent))
from model.predict import predict_disease

from database import log_detection, init_db
init_db()

# --- Configuration ---
st.set_page_config(
    page_title="Nabati — نباتي",
    page_icon="🌿",
    layout="wide",
    initial_sidebar_state="expanded"
)

# --- CSS Global ---
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Tajawal:wght@400;700;800&display=swap');

    html, body, [class*="css"] {
        font-family: 'Tajawal', sans-serif;
    }

    /* Fond général */
    .stApp {
        background: linear-gradient(160deg, #f0faf4 0%, #ffffff 100%);
    }

    /* Sidebar */
    [data-testid="stSidebar"] {
        background: linear-gradient(180deg, #1b4332 0%, #2d6a4f 100%);
    }
    [data-testid="stSidebar"] * {
        color: #d8f3dc !important;
    }
    [data-testid="stSidebar"] .stRadio label {
        color: white !important;
        font-size: 1rem;
        padding: 0.4rem 0;
    }

    /* Titre principal */
    .nabati-title {
        font-size: 3rem;
        font-weight: 800;
        background: linear-gradient(90deg, #1b4332, #40916c);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        text-align: center;
        margin-bottom: 0;
    }
    .nabati-arabic {
        font-size: 2rem;
        color: #40916c;
        text-align: center;
        direction: rtl;
        margin-bottom: 0.2rem;
    }
    .nabati-subtitle {
        font-size: 1rem;
        color: #74c69d;
        text-align: center;
        margin-bottom: 2rem;
    }

    /* Carte résultat */
    .result-card {
        background: linear-gradient(135deg, #d8f3dc, #b7e4c7);
        border-radius: 20px;
        padding: 1.5rem 2rem;
        border-left: 6px solid #2d6a4f;
        box-shadow: 0 4px 15px rgba(45,106,79,0.15);
        margin-bottom: 1rem;
    }
    .plant-name {
        font-size: 1.1rem;
        color: #52b788;
        font-weight: 600;
        text-transform: uppercase;
        letter-spacing: 1px;
    }
    .disease-name {
        font-size: 2rem;
        font-weight: 800;
        color: #1b4332;
        margin: 0.3rem 0;
    }
    .confidence-badge {
        display: inline-block;
        background: #2d6a4f;
        color: white;
        border-radius: 20px;
        padding: 0.2rem 0.8rem;
        font-size: 0.9rem;
        margin-top: 0.3rem;
    }

    /* Carte conseil */
    .advice-card {
        background: white;
        border-radius: 16px;
        padding: 1.5rem;
        border: 1px solid #b7e4c7;
        box-shadow: 0 2px 10px rgba(0,0,0,0.05);
        margin-top: 1rem;
    }

    /* Warning */
    .warning-card {
        background: #fff8e6;
        border-radius: 12px;
        padding: 1rem 1.2rem;
        border-left: 5px solid #f4a261;
        margin: 0.5rem 0;
    }

    /* Healthy */
    .healthy-card {
        background: linear-gradient(135deg, #d8f3dc, #b7e4c7);
        border-radius: 16px;
        padding: 1.5rem;
        text-align: center;
        border: 2px solid #52b788;
    }

    /* Bouton */
    .stButton button {
        background: linear-gradient(90deg, #2d6a4f, #40916c);
        color: white;
        border: none;
        border-radius: 25px;
        padding: 0.5rem 2rem;
        font-weight: 700;
        transition: all 0.3s;
    }
    .stButton button:hover {
        transform: translateY(-2px);
        box-shadow: 0 4px 15px rgba(45,106,79,0.3);
    }

    /* Divider */
    hr {
        border-color: #b7e4c7;
        margin: 1.5rem 0;
    }

    /* Upload zone */
    [data-testid="stFileUploader"] {
        border: 2px dashed #52b788 !important;
        border-radius: 16px !important;
        padding: 1rem !important;
    }
</style>
""", unsafe_allow_html=True)

# --- Sidebar ---
with st.sidebar:
    st.markdown("""
    <div style='text-align:center; padding: 1rem 0;'>
        <div style='font-size:3rem'>🌿</div>
        <div style='font-size:1.8rem; font-weight:800; color:white;'>Nabati</div>
        <div style='font-size:1.2rem; color:#74c69d; direction:rtl;'>نباتي</div>
        <div style='font-size:0.8rem; color:#95d5b2; margin-top:0.3rem;'>
            Diagnostic Agricole Intelligent
        </div>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("---")
    st.markdown("<div style='color:#95d5b2; font-size:0.85rem; margin-bottom:0.5rem;'>NAVIGATION</div>",
                unsafe_allow_html=True)

    page = st.radio("", [
        "🔍 Diagnostic",
        "💬 Chatbot",
        "📊 Dashboard"
    ], label_visibility="collapsed")

    st.markdown("---")

    st.markdown("""
    <div style='font-size:0.8rem; color:#74c69d; text-align:center;'>
        <div>🌱 Comment ça marche ?</div>
        <div style='margin-top:0.5rem; line-height:1.8;'>
            📸 Uploader une photo<br>
            🤖 Détection YOLOv8<br>
            💡 Conseils par LLM<br>
            📚 Questions via RAG
        </div>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("---")
    st.markdown("""
    <div style='font-size:0.75rem; color:#52b788; text-align:center;'>
        FST Tunis<br>Cycle Ingénieur Data Science
    </div>
    """, unsafe_allow_html=True)

# ==================== PAGE DIAGNOSTIC ====================
if page == "🔍 Diagnostic":

    # Titre
    st.markdown('<div class="nabati-title">🌿 Nabati</div>', unsafe_allow_html=True)
    st.markdown('<div class="nabati-arabic">منصة ذكية لتشخيص أمراض النباتات</div>', unsafe_allow_html=True)
    st.markdown('<div class="nabati-subtitle">Plateforme intelligente de diagnostic des maladies des plantes</div>',
                unsafe_allow_html=True)

    st.markdown("---")

    col1, col2 = st.columns([1, 1], gap="large")

    with col1:
        st.markdown("#### 📸 Uploader une image de plante")
        uploaded_file = st.file_uploader(
            "Formats acceptés : JPG, JPEG, PNG",
            type=["jpg", "jpeg", "png"],
            label_visibility="collapsed"
        )

        if uploaded_file:
            image = Image.open(uploaded_file)
            st.image(image, caption=f"📁 {uploaded_file.name}", use_column_width=True)

            # Infos image
            st.markdown(f"""
            <div style='font-size:0.8rem; color:#74c69d; margin-top:0.5rem;'>
                📐 Dimensions : {image.size[0]} × {image.size[1]} px &nbsp;|&nbsp;
                📦 Taille : {uploaded_file.size/1024:.1f} KB
            </div>
            """, unsafe_allow_html=True)
        else:
            # Placeholder
            st.markdown("""
            <div style='background:#f0faf4; border:2px dashed #74c69d; border-radius:16px;
                        padding:3rem; text-align:center; color:#74c69d;'>
                <div style='font-size:3rem;'>🌱</div>
                <div style='font-size:1rem; margin-top:0.5rem;'>
                    Glissez une photo de plante ici
                </div>
                <div style='font-size:0.85rem; margin-top:0.3rem; color:#95d5b2;'>
                    Prenez une photo claire de la feuille malade
                </div>
            </div>
            """, unsafe_allow_html=True)

    with col2:
        st.markdown("#### 🤖 Résultat du diagnostic")

        if uploaded_file is None:
            st.markdown("""
            <div style='background:#f8fffe; border:1px solid #b7e4c7; border-radius:16px;
                        padding:2rem; text-align:center; color:#52b788;'>
                <div style='font-size:2rem;'>👈</div>
                <div style='margin-top:0.5rem;'>
                    Uploadez une image pour démarrer le diagnostic
                </div>
            </div>
            """, unsafe_allow_html=True)

        else:
            with st.spinner("🔬 Analyse de la plante en cours..."):
                result = predict_disease(image)

            if result["success"]:
                disease_raw = result["disease"]
                confidence = result["confidence"]

                parts = disease_raw.split("__")
                plant = parts[0].replace("_", " ") if len(parts) > 0 else ""
                disease = parts[1].replace("_", " ") if len(parts) > 1 else disease_raw
                # Logger la détection
                log_detection(plant, disease, confidence)
                is_healthy = "healthy" in disease.lower()

                if is_healthy:
                    st.markdown(f"""
                    <div class="healthy-card">
                        <div style='font-size:3rem;'>✅</div>
                        <div style='font-size:1.5rem; font-weight:800; color:#1b4332;
                                    margin-top:0.5rem;'>{plant}</div>
                        <div style='font-size:1.2rem; color:#2d6a4f;'>Plante saine !</div>
                        <div style='font-size:0.9rem; color:#52b788; margin-top:0.5rem;'>
                            Confiance : {confidence:.1%}
                        </div>
                    </div>
                    """, unsafe_allow_html=True)
                else:
                    st.markdown(f"""
                    <div class="result-card">
                        <div class="plant-name">🌱 {plant}</div>
                        <div class="disease-name">🦠 {disease}</div>
                        <div class="confidence-badge">Confiance : {confidence:.1%}</div>
                    </div>
                    """, unsafe_allow_html=True)

                # Barre de confiance colorée
                color = "#2d6a4f" if confidence > 0.7 else "#f4a261" if confidence > 0.4 else "#e63946"
                st.markdown(f"""
                <div style='margin:0.5rem 0 1rem 0;'>
                    <div style='display:flex; justify-content:space-between;
                                font-size:0.8rem; color:#74c69d; margin-bottom:4px;'>
                        <span>Niveau de confiance</span>
                        <span>{confidence:.1%}</span>
                    </div>
                    <div style='background:#e9f5ee; border-radius:10px; height:10px;'>
                        <div style='background:{color}; width:{confidence*100:.0f}%;
                                    height:10px; border-radius:10px; transition:all 0.5s;'></div>
                    </div>
                </div>
                """, unsafe_allow_html=True)

                # Top 3
                if "top3" in result:
                    st.markdown("**🏆 Top 3 des prédictions**")
                    for i, (name, conf) in enumerate(result["top3"]):
                        p = name.split("__")
                        label = f"{p[0].replace('_',' ')} — {p[1].replace('_',' ')}" if len(p) > 1 else name
                        icon = "🥇" if i == 0 else "🥈" if i == 1 else "🥉"
                        st.markdown(f"""
                        <div style='display:flex; justify-content:space-between;
                                    padding:0.4rem 0.8rem; margin:0.2rem 0;
                                    background:{"#e8f5e9" if i==0 else "#f9fafb"};
                                    border-radius:8px; font-size:0.9rem;'>
                            <span>{icon} {label}</span>
                            <span style='color:#2d6a4f; font-weight:700;'>{conf:.1%}</span>
                        </div>
                        """, unsafe_allow_html=True)

                # Alerte confiance faible
                if confidence < 0.5:
                    st.markdown("""
                    <div class="warning-card">
                        ⚠️ <b>Confiance faible</b> — Pour un meilleur résultat :<br>
                        • Prenez la photo en pleine lumière<br>
                        • Centrez la feuille malade dans le cadre<br>
                        • Évitez les reflets et le flou
                    </div>
                    """, unsafe_allow_html=True)

                # Conseils LLM
                st.markdown("---")
                st.markdown("#### 💡 Conseils de traitement")

                with st.spinner("🤖 Génération des recommandations par IA..."):
                    advice = get_treatment_advice(plant, disease, confidence)

                st.markdown(f"""
                <div class="advice-card">
                    {advice.replace(chr(10), '<br>')}
                </div>
                """, unsafe_allow_html=True)

            else:
                st.error(f"❌ Erreur lors du diagnostic : {result['error']}")

# ==================== PAGE CHATBOT ====================
elif page == "💬 Chatbot":

    st.markdown('<div class="nabati-title">💬 Chatbot Nabati</div>', unsafe_allow_html=True)
    st.markdown('<div class="nabati-subtitle">Posez vos questions sur les maladies des plantes</div>',
                unsafe_allow_html=True)
    st.markdown("---")

    # Import RAG
    from rag import answer_question, get_vectorstore

    # Initialiser le vectorstore au démarrage
    with st.spinner("📚 Chargement de la base de connaissances..."):
        get_vectorstore()

    # Initialiser l'historique du chat
    if "messages" not in st.session_state:
        st.session_state.messages = [
            {
                "role": "assistant",
                "content": "🌿 Bonjour ! Je suis **Nabati**, votre assistant agricole intelligent.\n\nPosez-moi vos questions sur les maladies des plantes, les traitements, ou la prévention. Je suis là pour vous aider ! 🌱"
            }
        ]

    if "last_disease" not in st.session_state:
        st.session_state.last_disease = ""

    # Contexte maladie détectée
    col1, col2 = st.columns([3, 1])
    with col2:
        disease_context = st.text_input(
            "🔍 Contexte (maladie détectée)",
            value=st.session_state.last_disease,
            placeholder="Ex: Tomato Early blight",
            help="Optionnel : renseigne la maladie détectée pour des réponses plus précises"
        )

    # Afficher l'historique
    chat_container = st.container()
    with chat_container:
        for msg in st.session_state.messages:
            if msg["role"] == "user":
                st.markdown(f"""
                <div style='display:flex; justify-content:flex-end; margin:0.5rem 0;'>
                    <div style='background:#2d6a4f; color:white; border-radius:18px 18px 4px 18px;
                                padding:0.8rem 1.2rem; max-width:75%; font-size:0.95rem;'>
                        {msg["content"]}
                    </div>
                    <div style='margin-left:0.5rem; font-size:1.5rem;'>👤</div>
                </div>
                """, unsafe_allow_html=True)
            else:
                st.markdown(f"""
                <div style='display:flex; justify-content:flex-start; margin:0.5rem 0;'>
                    <div style='margin-right:0.5rem; font-size:1.5rem;'>🌿</div>
                    <div style='background:#f0faf4; border:1px solid #b7e4c7;
                                border-radius:18px 18px 18px 4px;
                                padding:0.8rem 1.2rem; max-width:75%; font-size:0.95rem;'>
                        {msg["content"].replace(chr(10), "<br>")}
                    </div>
                </div>
                """, unsafe_allow_html=True)

    st.markdown("---")

    # Questions suggérées
    st.markdown("**💡 Questions fréquentes :**")
    suggestions = [
        "Comment traiter le mildiou de la tomate ?",
        "Quels fongicides utiliser contre l'alternariose ?",
        "Comment prévenir les maladies fongiques ?",
        "Où contacter un agronome en Tunisie ?"
    ]

    cols = st.columns(2)
    for i, suggestion in enumerate(suggestions):
        if cols[i % 2].button(suggestion, key=f"sug_{i}"):
            st.session_state.messages.append({"role": "user", "content": suggestion})
            with st.spinner("🤖 Recherche dans la base de connaissances..."):
                response = answer_question(suggestion, disease_context)
            st.session_state.messages.append({"role": "assistant", "content": response})
            st.rerun()

    # Zone de saisie
    user_input = st.chat_input("Posez votre question ici...")

    if user_input:
        st.session_state.messages.append({"role": "user", "content": user_input})
        with st.spinner("🔬 Analyse en cours..."):
            response = answer_question(user_input, disease_context)
        st.session_state.messages.append({"role": "assistant", "content": response})
        st.rerun()

    # Bouton reset
    if st.button("🗑️ Effacer la conversation"):
        st.session_state.messages = [
            {
                "role": "assistant",
                "content": "🌿 Conversation réinitialisée. Comment puis-je vous aider ?"
            }
        ]
        st.rerun()
# ==================== PAGE DASHBOARD ====================
elif page == "📊 Dashboard":
    import pandas as pd
    import plotly.express as px
    import plotly.graph_objects as go
    from database import get_stats, get_all_detections

    st.markdown('<div class="nabati-title">📊 Dashboard Nabati</div>', unsafe_allow_html=True)
    st.markdown('<div class="nabati-subtitle">Statistiques et analyses des diagnostics</div>',
                unsafe_allow_html=True)
    st.markdown("---")

    stats = get_stats()

    # Vérifier si des données existent
    if stats["total"] == 0:
        st.markdown("""
        <div style='background:#f0faf4; border:2px dashed #74c69d; border-radius:16px;
                    padding:3rem; text-align:center; color:#52b788;'>
            <div style='font-size:3rem;'>📊</div>
            <div style='font-size:1.1rem; margin-top:0.5rem;'>
                Aucun diagnostic encore effectué.<br>
                Allez dans <b>🔍 Diagnostic</b> pour commencer !
            </div>
        </div>
        """, unsafe_allow_html=True)

    else:
        # --- KPIs ---
        k1, k2, k3, k4 = st.columns(4)

        with k1:
            st.markdown(f"""
            <div style='background:linear-gradient(135deg,#1b4332,#2d6a4f);
                        border-radius:16px; padding:1.2rem; text-align:center; color:white;'>
                <div style='font-size:2.5rem; font-weight:800;'>{stats["total"]}</div>
                <div style='font-size:0.9rem; color:#95d5b2;'>Total Diagnostics</div>
            </div>
            """, unsafe_allow_html=True)

        with k2:
            st.markdown(f"""
            <div style='background:linear-gradient(135deg,#52b788,#74c69d);
                        border-radius:16px; padding:1.2rem; text-align:center; color:white;'>
                <div style='font-size:2.5rem; font-weight:800;'>{stats["saines"]}</div>
                <div style='font-size:0.9rem; color:#d8f3dc;'>Plantes Saines ✅</div>
            </div>
            """, unsafe_allow_html=True)

        with k3:
            st.markdown(f"""
            <div style='background:linear-gradient(135deg,#e63946,#f4a261);
                        border-radius:16px; padding:1.2rem; text-align:center; color:white;'>
                <div style='font-size:2.5rem; font-weight:800;'>{stats["malades"]}</div>
                <div style='font-size:0.9rem; color:#ffe8e8;'>Plantes Malades 🦠</div>
            </div>
            """, unsafe_allow_html=True)

        with k4:
            st.markdown(f"""
            <div style='background:linear-gradient(135deg,#3a86ff,#48cae4);
                        border-radius:16px; padding:1.2rem; text-align:center; color:white;'>
                <div style='font-size:2.5rem; font-weight:800;'>
                    {stats["confiance_moyenne"]:.0%}
                </div>
                <div style='font-size:0.9rem; color:#e0f4ff;'>Confiance Moyenne</div>
            </div>
            """, unsafe_allow_html=True)

        st.markdown("<br>", unsafe_allow_html=True)

        # --- Graphiques ---
        col1, col2 = st.columns(2)

        with col1:
            # Donut Sain vs Malade
            if stats["total"] > 0:
                fig_donut = go.Figure(data=[go.Pie(
                    labels=["Saines ✅", "Malades 🦠"],
                    values=[stats["saines"], stats["malades"]],
                    hole=0.6,
                    marker_colors=["#52b788", "#e63946"]
                )])
                fig_donut.update_layout(
                    title="Répartition Sain / Malade",
                    showlegend=True,
                    height=320,
                    paper_bgcolor="rgba(0,0,0,0)",
                    plot_bgcolor="rgba(0,0,0,0)",
                    font=dict(family="Tajawal")
                )
                st.plotly_chart(fig_donut, use_container_width=True)

        with col2:
            # Top maladies
            if stats["top_maladies"]:
                maladies = [m[0].replace("_", " ") for m in stats["top_maladies"]]
                counts = [m[1] for m in stats["top_maladies"]]
                fig_bar = px.bar(
                    x=counts, y=maladies,
                    orientation="h",
                    title="🦠 Top Maladies Détectées",
                    color=counts,
                    color_continuous_scale=["#b7e4c7", "#2d6a4f"]
                )
                fig_bar.update_layout(
                    height=320,
                    paper_bgcolor="rgba(0,0,0,0)",
                    plot_bgcolor="rgba(0,0,0,0)",
                    showlegend=False,
                    coloraxis_showscale=False,
                    font=dict(family="Tajawal")
                )
                st.plotly_chart(fig_bar, use_container_width=True)

        # Évolution temporelle
        if stats["par_jour"] and len(stats["par_jour"]) > 1:
            dates = [d[0] for d in reversed(stats["par_jour"])]
            counts = [d[1] for d in reversed(stats["par_jour"])]
            fig_line = px.line(
                x=dates, y=counts,
                title="📅 Évolution des diagnostics (7 derniers jours)",
                markers=True,
                color_discrete_sequence=["#2d6a4f"]
            )
            fig_line.update_layout(
                height=280,
                paper_bgcolor="rgba(0,0,0,0)",
                plot_bgcolor="rgba(0,0,0,0)",
                xaxis_title="Date",
                yaxis_title="Nombre de diagnostics",
                font=dict(family="Tajawal")
            )
            st.plotly_chart(fig_line, use_container_width=True)

        # Tableau des dernières détections
        st.markdown("### 📋 Dernières détections")
        rows = get_all_detections()
        if rows:
            df = pd.DataFrame(rows, columns=[
                "ID", "Date", "Heure", "Plante", "Maladie", "Confiance", "Saine"
            ])
            df["Confiance"] = df["Confiance"].apply(lambda x: f"{x:.1%}")
            df["Saine"] = df["Saine"].apply(lambda x: "✅" if x == 1 else "🦠")
            df = df.drop("ID", axis=1)
            st.dataframe(df.head(10), use_container_width=True, hide_index=True)