# app/main.py
import streamlit as st
from PIL import Image
import sys
from pathlib import Path

sys.path.append(str(Path(__file__).parent))
from llm import get_treatment_advice
from database import init_db, log_detection, get_user_detections, get_user_stats, get_global_stats
from auth import show_auth_page

sys.path.append(str(Path(__file__).parent.parent))
from model.predict import predict_disease

# --- Init DB ---
init_db()

# --- Config page ---
st.set_page_config(
    page_title="Nabati — نباتي",
    page_icon="🌿",
    layout="wide",
    initial_sidebar_state="expanded"
)

# --- Session state ---
if "authenticated" not in st.session_state:
    st.session_state.authenticated = False
if "user" not in st.session_state:
    st.session_state.user = None
if "lang" not in st.session_state:
    st.session_state.lang = "fr"
if "messages" not in st.session_state:
    st.session_state.messages = []

# --- Traductions ---
T = {
    "fr": {
        "diagnostic": "🔍 Diagnostic",
        "chatbot": "💬 Chatbot",
        "dashboard": "📊 Dashboard",
        "monjardin": "🌱 Mon Jardin",
        "logout": "🚪 Déconnexion",
        "upload": "Uploader une image de plante",
        "result": "Résultat du diagnostic",
        "confidence": "Niveau de confiance",
        "advice": "💡 Conseils de traitement",
        "top3": "🏆 Top 3 des prédictions",
        "healthy": "Plante saine !",
        "low_conf": "Confiance faible — Essayez une image plus nette",
        "analyzing": "🔬 Analyse en cours...",
        "generating": "🤖 Génération des conseils...",
        "total": "Total Diagnostics",
        "saines": "Plantes Saines",
        "malades": "Plantes Malades",
        "conf_moy": "Confiance Moyenne",
        "bienvenue": "Bienvenue",
    },
    "ar": {
        "diagnostic": "🔍 التشخيص",
        "chatbot": "💬 المساعد",
        "dashboard": "📊 الإحصائيات",
        "monjardin": "🌱 حديقتي",
        "logout": "🚪 خروج",
        "upload": "رفع صورة النبتة",
        "result": "نتيجة التشخيص",
        "confidence": "مستوى الثقة",
        "advice": "💡 نصائح العلاج",
        "top3": "🏆 أفضل 3 تنبؤات",
        "healthy": "النبتة سليمة !",
        "low_conf": "ثقة منخفضة — جرب صورة أوضح",
        "analyzing": "🔬 جاري التحليل...",
        "generating": "🤖 جاري إنشاء النصائح...",
        "total": "إجمالي التشخيصات",
        "saines": "نباتات سليمة",
        "malades": "نباتات مريضة",
        "conf_moy": "متوسط الثقة",
        "bienvenue": "مرحباً",
    }
}

# --- CSS ---
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Tajawal:wght@400;700;800&display=swap');
    html, body, [class*="css"] { font-family: 'Tajawal', sans-serif; }
    .stApp { background: linear-gradient(160deg, #f0faf4 0%, #ffffff 100%); }
    [data-testid="stSidebar"] { background: linear-gradient(180deg, #1b4332 0%, #2d6a4f 100%); }
    [data-testid="stSidebar"] * { color: #d8f3dc !important; }
    .nabati-title {
        font-size: 2.8rem; font-weight: 800;
        background: linear-gradient(90deg, #1b4332, #40916c);
        -webkit-background-clip: text; -webkit-text-fill-color: transparent;
        text-align: center;
    }
    .nabati-subtitle { font-size: 1rem; color: #74c69d; text-align: center; margin-bottom: 1.5rem; }
    .result-card {
        background: linear-gradient(135deg, #d8f3dc, #b7e4c7);
        border-radius: 20px; padding: 1.5rem 2rem;
        border-left: 6px solid #2d6a4f;
        box-shadow: 0 4px 15px rgba(45,106,79,0.15);
    }
    .kpi-card {
        border-radius: 16px; padding: 1.2rem;
        text-align: center; color: white;
        box-shadow: 0 4px 12px rgba(0,0,0,0.1);
    }
    .advice-card {
        background: white; border-radius: 16px; padding: 1.5rem;
        border: 1px solid #b7e4c7;
        box-shadow: 0 2px 10px rgba(0,0,0,0.05);
    }
    .user-badge {
        background: rgba(255,255,255,0.15); border-radius: 12px;
        padding: 0.8rem; text-align: center; margin-bottom: 1rem;
    }
    .stButton button {
        background: linear-gradient(90deg, #2d6a4f, #40916c);
        color: white; border: none; border-radius: 25px;
        font-weight: 700;
    }
    [data-testid="stFileUploader"] {
        border: 2px dashed #52b788 !important; border-radius: 16px !important;
    }
</style>
""", unsafe_allow_html=True)

# ==================== AUTH ====================
if not st.session_state.authenticated:
    lang_col1, lang_col2 = st.columns([4, 1])
    with lang_col2:
        if st.button("🌍 FR / عر"):
            st.session_state.lang = "ar" if st.session_state.lang == "fr" else "fr"
            st.rerun()

    show_auth_page(st.session_state.lang)
    st.stop()

# ==================== APP PRINCIPALE ====================
lang = st.session_state.lang
t = T[lang]
user = st.session_state.user

# --- Sidebar ---
with st.sidebar:
    st.markdown(f"""
    <div style='text-align:center; padding:1rem 0;'>
        <div style='font-size:2.5rem;'>🌿</div>
        <div style='font-size:1.5rem; font-weight:800; color:white;'>Nabati — نباتي</div>
    </div>
    <div class='user-badge'>
        <div style='font-size:1.5rem;'>👤</div>
        <div style='font-weight:700; color:white;'>{user['prenom']} {user['nom']}</div>
        <div style='font-size:0.8rem; color:#95d5b2;'>{user.get('region','')}</div>
    </div>
    """, unsafe_allow_html=True)

    lang = st.selectbox(
        "🌍 Langue / اللغة",
        ["fr", "ar"],
        format_func=lambda x: "🇫🇷 Français" if x == "fr" else "🇹🇳 العربية",
        key="lang",
        label_visibility="collapsed"
    )
    t = T[lang]

    st.markdown("---")
    page = st.radio("", [
        t["diagnostic"], t["chatbot"],
        t["dashboard"], t["monjardin"]
    ], label_visibility="collapsed")

    st.markdown("---")
    if st.button(t["logout"], use_container_width=True):
        st.session_state.authenticated = False
        st.session_state.user = None
        st.session_state.messages = []
        st.rerun()

    st.markdown(f"""
    <div style='font-size:0.75rem; color:#52b788; text-align:center; margin-top:1rem;'>
        FST Tunis — Cycle Ingénieur Data Science
    </div>
    """, unsafe_allow_html=True)

# ==================== PAGE DIAGNOSTIC ====================
if page == t["diagnostic"]:
    st.markdown('<div class="nabati-title">🌿 Nabati — نباتي</div>', unsafe_allow_html=True)
    st.markdown('<div class="nabati-subtitle">Diagnostic intelligent des maladies des plantes | تشخيص ذكي لأمراض النباتات</div>',
                unsafe_allow_html=True)
    st.markdown("---")

    col1, col2 = st.columns([1, 1], gap="large")

    with col1:
        st.markdown(f"#### 📸 {t['upload']}")
        uploaded_file = st.file_uploader(
            "", type=["jpg", "jpeg", "png"],
            label_visibility="collapsed"
        )
        if uploaded_file:
            image = Image.open(uploaded_file)
            st.image(image, caption=uploaded_file.name, use_column_width=True)
            st.markdown(f"""
            <div style='font-size:0.8rem; color:#74c69d;'>
                📐 {image.size[0]}×{image.size[1]}px &nbsp;|&nbsp; 📦 {uploaded_file.size/1024:.1f} KB
            </div>
            """, unsafe_allow_html=True)
        else:
            st.markdown("""
            <div style='background:#f0faf4; border:2px dashed #74c69d;
                        border-radius:16px; padding:3rem; text-align:center; color:#74c69d;'>
                <div style='font-size:3rem;'>🌱</div>
                <div>Glissez une photo de plante ici</div>
                <div style='font-size:0.85rem; color:#95d5b2;'>اسحب صورة النبتة هنا</div>
            </div>
            """, unsafe_allow_html=True)

    with col2:
        st.markdown(f"#### 🤖 {t['result']}")

        if not uploaded_file:
            st.markdown("""
            <div style='background:#f8fffe; border:1px solid #b7e4c7;
                        border-radius:16px; padding:2rem; text-align:center; color:#52b788;'>
                <div style='font-size:2rem;'>👈</div>
                <div>Uploadez une image pour démarrer</div>
            </div>
            """, unsafe_allow_html=True)
        else:
            with st.spinner(t["analyzing"]):
                result = predict_disease(image)

            if result["success"]:
                disease_raw = result["disease"]
                confidence = result["confidence"]
                parts = disease_raw.split("__")
                plant = parts[0].replace("_", " ")
                disease = parts[1].replace("_", " ") if len(parts) > 1 else disease_raw
                is_healthy = "healthy" in disease.lower()

                if is_healthy:
                    st.markdown(f"""
                    <div style='background:linear-gradient(135deg,#d8f3dc,#b7e4c7);
                                border-radius:20px; padding:2rem; text-align:center;'>
                        <div style='font-size:3rem;'>✅</div>
                        <div style='font-size:1.8rem; font-weight:800; color:#1b4332;'>{plant}</div>
                        <div style='color:#2d6a4f;'>{t["healthy"]}</div>
                        <div style='color:#52b788;'>Confiance : {confidence:.1%}</div>
                    </div>
                    """, unsafe_allow_html=True)
                else:
                    st.markdown(f"""
                    <div class='result-card'>
                        <div style='color:#52b788; font-size:0.9rem; font-weight:600;
                                    text-transform:uppercase;'>🌱 {plant}</div>
                        <div style='font-size:2rem; font-weight:800; color:#1b4332;'>🦠 {disease}</div>
                        <div style='background:#2d6a4f; color:white; border-radius:20px;
                                    padding:0.2rem 0.8rem; display:inline-block;
                                    font-size:0.9rem; margin-top:0.3rem;'>
                            {confidence:.1%}
                        </div>
                    </div>
                    """, unsafe_allow_html=True)

                # Barre de confiance
                color = "#2d6a4f" if confidence > 0.7 else "#f4a261" if confidence > 0.4 else "#e63946"
                st.markdown(f"""
                <div style='margin:1rem 0;'>
                    <div style='display:flex; justify-content:space-between;
                                font-size:0.85rem; color:#74c69d; margin-bottom:4px;'>
                        <span>{t["confidence"]}</span><span>{confidence:.1%}</span>
                    </div>
                    <div style='background:#e9f5ee; border-radius:10px; height:10px;'>
                        <div style='background:{color}; width:{confidence*100:.0f}%;
                                    height:10px; border-radius:10px;'></div>
                    </div>
                </div>
                """, unsafe_allow_html=True)

                # Top 3
                if "top3" in result:
                    st.markdown(f"**{t['top3']}**")
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

                if confidence < 0.5:
                    st.warning(f"⚠️ {t['low_conf']}")

                # ===== MODIFICATION : Conseils + log avec image =====
                st.markdown("---")
                st.markdown(f"#### {t['advice']}")

                # Générer les conseils
                with st.spinner(t["generating"]):
                    advice = get_treatment_advice(plant, disease, confidence)

                # Sauvegarder image en bytes
                import io
                img_bytes = io.BytesIO()
                image.save(img_bytes, format="JPEG")
                img_bytes = img_bytes.getvalue()

                # Logger avec image et conseils
                log_detection(
                    user["user_id"],
                    plant,
                    disease,
                    confidence,
                    img_bytes,
                    advice
                )

                # Afficher conseils
                st.markdown(f'<div class="advice-card">{advice.replace(chr(10),"<br>")}</div>',
                            unsafe_allow_html=True)
                # ===== FIN MODIFICATION =====

            else:
                st.error(f"❌ {result['error']}")

# ==================== PAGE CHATBOT ====================
elif page == t["chatbot"]:
    st.markdown('<div class="nabati-title">💬 Chatbot Nabati</div>', unsafe_allow_html=True)
    st.markdown('<div class="nabati-subtitle">Posez vos questions | اطرح أسئلتك</div>',
                unsafe_allow_html=True)
    st.markdown("---")

    from rag import answer_question

    @st.cache_resource(show_spinner="📚 Chargement de la base de connaissances...")
    def load_rag():
        from rag import get_vectorstore
        return get_vectorstore()

    load_rag()

    if not st.session_state.messages:
        st.session_state.messages = [{
            "role": "assistant",
            "content": f"🌿 {t['bienvenue']} {user['prenom']} ! Je suis votre assistant agricole Nabati.\n\nمرحباً ! أنا مساعدك الزراعي نباتي. كيف أستطيع مساعدتك اليوم؟ 🌱"
        }]

    for msg in st.session_state.messages:
        if msg["role"] == "user":
            st.markdown(f"""
            <div style='display:flex; justify-content:flex-end; margin:0.5rem 0;'>
                <div style='background:#2d6a4f; color:white; border-radius:18px 18px 4px 18px;
                            padding:0.8rem 1.2rem; max-width:75%;'>{msg["content"]}</div>
                <div style='margin-left:0.5rem; font-size:1.5rem;'>👤</div>
            </div>
            """, unsafe_allow_html=True)
        else:
            st.markdown(f"""
            <div style='display:flex; justify-content:flex-start; margin:0.5rem 0;'>
                <div style='margin-right:0.5rem; font-size:1.5rem;'>🌿</div>
                <div style='background:#f0faf4; border:1px solid #b7e4c7;
                            border-radius:18px 18px 18px 4px;
                            padding:0.8rem 1.2rem; max-width:75%;'>
                    {msg["content"].replace(chr(10), "<br>")}
                </div>
            </div>
            """, unsafe_allow_html=True)

    st.markdown("---")

    suggestions = {
        "fr": [
            "Comment traiter le mildiou de la tomate ?",
            "Quels fongicides utiliser contre l'alternariose ?",
            "Comment prévenir les maladies fongiques ?",
            "Où contacter un agronome en Tunisie ?"
        ],
        "ar": [
            "كيف أعالج مرض البياض الزغبي للطماطم؟",
            "ما هي المبيدات الفطرية الموصى بها؟",
            "كيف أتجنب الأمراض الفطرية؟",
            "كيف أتواصل مع مهندس زراعي في تونس؟"
        ]
    }

    lang_chat = st.radio(
        "Langue du chat",
        ["fr", "ar"],
        format_func=lambda x: "🇫🇷 Français" if x == "fr" else "🇹🇳 العربية",
        horizontal=True,
        key="chat_lang"
    )

    cols = st.columns(2)
    for i, s in enumerate(suggestions[lang_chat]):
        if cols[i % 2].button(s, key=f"sug_{i}"):
            st.session_state.messages.append({"role": "user", "content": s})
            with st.spinner("🔬 Recherche..."):
                response = answer_question(s)
            st.session_state.messages.append({"role": "assistant", "content": response})
            st.rerun()

    placeholder = "Posez votre question..." if lang_chat == "fr" else "اكتب سؤالك..."
    user_input = st.chat_input(placeholder)

    if user_input:
        st.session_state.messages.append({"role": "user", "content": user_input})
        with st.spinner("🔬 Recherche..."):
            response = answer_question(user_input)
        st.session_state.messages.append({"role": "assistant", "content": response})
        st.rerun()

    if st.button("🗑️ Effacer | مسح"):
        st.session_state.messages = []
        st.rerun()

# ==================== PAGE MON JARDIN ====================
elif page == t["monjardin"]:
    import pandas as pd
    from PIL import Image as PILImage
    import io

    st.markdown(f'<div class="nabati-title">🌱 {t["monjardin"]}</div>',
                unsafe_allow_html=True)
    st.markdown('<div class="nabati-subtitle">Album de vos plantes diagnostiquées | ألبوم نباتاتك</div>',
                unsafe_allow_html=True)
    st.markdown("---")

    rows = get_user_detections(user["user_id"])

    if not rows:
        st.markdown("""
        <div style='background:#f0faf4; border:2px dashed #74c69d;
                    border-radius:16px; padding:3rem; text-align:center; color:#74c69d;'>
            <div style='font-size:3rem;'>🌱</div>
            <div>Aucun diagnostic encore.<br>Allez dans <b>🔍 Diagnostic</b> pour commencer !</div>
        </div>
        """, unsafe_allow_html=True)

    else:
        stats = get_user_stats(user["user_id"])
        k1, k2, k3 = st.columns(3)
        kpis = [
            (k1, stats["total"],   t["total"],   "#1b4332", "#2d6a4f", "#95d5b2"),
            (k2, stats["saines"],  t["saines"]+" ✅", "#52b788", "#74c69d", "#d8f3dc"),
            (k3, stats["malades"], t["malades"]+" 🦠", "#e63946", "#f4a261", "#ffe8e8"),
        ]
        for col, val, label, c1, c2, tc in kpis:
            with col:
                st.markdown(f"""
                <div class='kpi-card' style='background:linear-gradient(135deg,{c1},{c2});
                            margin-bottom:1rem;'>
                    <div style='font-size:2rem; font-weight:800;'>{val}</div>
                    <div style='font-size:0.85rem; color:{tc};'>{label}</div>
                </div>""", unsafe_allow_html=True)

        st.markdown("### 🔎 Filtrer")
        col_f1, col_f2 = st.columns(2)
        with col_f1:
            filtre_sante = st.selectbox(
                "État de santé",
                ["Tous", "🦠 Malades uniquement", "✅ Saines uniquement"]
            )
        with col_f2:
            plantes_dispo = list(set([r[3] for r in rows]))
            filtre_plante = st.selectbox("Plante", ["Toutes"] + plantes_dispo)

        filtered = rows
        if filtre_sante == "🦠 Malades uniquement":
            filtered = [r for r in filtered if r[6] == 0]
        elif filtre_sante == "✅ Saines uniquement":
            filtered = [r for r in filtered if r[6] == 1]
        if filtre_plante != "Toutes":
            filtered = [r for r in filtered if r[3] == filtre_plante]

        st.markdown(f"**{len(filtered)} résultat(s)**")
        st.markdown("---")

        st.markdown("### 📸 Album")
        cols_per_row = 3
        for i in range(0, len(filtered), cols_per_row):
            cols = st.columns(cols_per_row)
            for j, col in enumerate(cols):
                if i + j < len(filtered):
                    row = filtered[i + j]
                    rid, date, heure, plante, maladie, confiance, saine, img_data, conseils = row

                    with col:
                        if img_data:
                            img = PILImage.open(io.BytesIO(img_data))
                            st.image(img, use_column_width=True)
                        else:
                            st.markdown("""
                            <div style='background:#e9f5ee; border-radius:12px;
                                        height:160px; display:flex; align-items:center;
                                        justify-content:center; font-size:3rem;'>
                                🌿
                            </div>
                            """, unsafe_allow_html=True)

                        status_color = "#52b788" if saine else "#e63946"
                        status_icon  = "✅" if saine else "🦠"
                        maladie_clean = maladie.replace("_", " ")
                        plante_clean  = plante.replace("_", " ")

                        st.markdown(f"""
                        <div style='background:white; border-radius:12px; padding:0.8rem;
                                    border:1px solid #b7e4c7; margin-bottom:0.5rem;
                                    box-shadow:0 2px 8px rgba(0,0,0,0.05);'>
                            <div style='font-weight:700; color:#1b4332;
                                        font-size:1rem;'>🌱 {plante_clean}</div>
                            <div style='color:{status_color}; font-size:0.9rem;
                                        margin:0.2rem 0;'>{status_icon} {maladie_clean}</div>
                            <div style='display:flex; justify-content:space-between;
                                        font-size:0.78rem; color:#74c69d; margin-top:0.3rem;'>
                                <span>📅 {date}</span>
                                <span>⏰ {heure}</span>
                            </div>
                            <div style='background:#e9f5ee; border-radius:8px;
                                        padding:0.2rem 0.5rem; margin-top:0.4rem;
                                        font-size:0.78rem; color:#2d6a4f; text-align:center;'>
                                Confiance : {confiance:.1%}
                            </div>
                        </div>
                        """, unsafe_allow_html=True)

                        with st.expander("📋 Voir les conseils"):
                            if conseils:
                                st.markdown(conseils)
                            else:
                                st.info("Aucun conseil enregistré pour ce diagnostic.")

# ==================== PAGE DASHBOARD ====================
elif page == t["dashboard"]:
    import pandas as pd
    import plotly.express as px
    import plotly.graph_objects as go

    st.markdown('<div class="nabati-title">📊 Dashboard Nabati</div>', unsafe_allow_html=True)
    st.markdown('<div class="nabati-subtitle">Statistiques globales de la plateforme</div>',
                unsafe_allow_html=True)
    st.markdown("---")

    stats = get_global_stats()

    if stats["total"] == 0:
        st.info("Aucun diagnostic encore effectué.")
    else:
        k1, k2, k3, k4, k5 = st.columns(5)
        kpis = [
            (k1, stats["total"], t["total"], "#1b4332", "#2d6a4f", "#95d5b2"),
            (k2, stats["saines"], t["saines"]+" ✅", "#52b788", "#74c69d", "#d8f3dc"),
            (k3, stats["malades"], t["malades"]+" 🦠", "#e63946", "#f4a261", "#ffe8e8"),
            (k4, f"{stats['confiance_moyenne']:.0%}", t["conf_moy"], "#3a86ff", "#48cae4", "#e0f4ff"),
            (k5, stats["total_users"], "Agriculteurs 👥", "#6a0572", "#b5179e", "#f8d7ff"),
        ]
        for col, val, label, c1, c2, tc in kpis:
            with col:
                st.markdown(f"""
                <div class='kpi-card' style='background:linear-gradient(135deg,{c1},{c2});'>
                    <div style='font-size:1.8rem; font-weight:800;'>{val}</div>
                    <div style='font-size:0.8rem; color:{tc};'>{label}</div>
                </div>""", unsafe_allow_html=True)

        st.markdown("<br>", unsafe_allow_html=True)
        col1, col2 = st.columns(2)

        with col1:
            fig = go.Figure(data=[go.Pie(
                labels=["Saines ✅", "Malades 🦠"],
                values=[stats["saines"], stats["malades"]],
                hole=0.6, marker_colors=["#52b788", "#e63946"]
            )])
            fig.update_layout(title="Répartition Sain / Malade", height=300,
                              paper_bgcolor="rgba(0,0,0,0)")
            st.plotly_chart(fig, use_container_width=True)

        with col2:
            if stats["top_maladies"]:
                maladies = [m[0].replace("_", " ") for m in stats["top_maladies"]]
                counts = [m[1] for m in stats["top_maladies"]]
                fig2 = px.bar(x=counts, y=maladies, orientation="h",
                              title="🦠 Top Maladies",
                              color=counts, color_continuous_scale=["#b7e4c7","#2d6a4f"])
                fig2.update_layout(height=300, paper_bgcolor="rgba(0,0,0,0)",
                                   coloraxis_showscale=False)
                st.plotly_chart(fig2, use_container_width=True)

        if stats["par_jour"] and len(stats["par_jour"]) > 1:
            dates = [d[0] for d in reversed(stats["par_jour"])]
            counts = [d[1] for d in reversed(stats["par_jour"])]
            fig3 = px.line(x=dates, y=counts, markers=True,
                           title="📅 Évolution des diagnostics",
                           color_discrete_sequence=["#2d6a4f"])
            fig3.update_layout(height=280, paper_bgcolor="rgba(0,0,0,0)")
            st.plotly_chart(fig3, use_container_width=True)