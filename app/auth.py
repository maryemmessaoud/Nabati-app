# app/auth.py
import streamlit as st
from database import register_user, login_user

TRANSLATIONS = {
    "fr": {
        "welcome": "Bienvenue sur Nabati 🌿",
        "subtitle": "Connectez-vous pour accéder à votre espace agricole",
        "login": "Se connecter",
        "register": "Créer un compte",
        "email": "Email",
        "password": "Mot de passe",
        "nom": "Nom",
        "prenom": "Prénom",
        "region": "Région (optionnel)",
        "confirm_password": "Confirmer le mot de passe",
        "login_btn": "🔐 Se connecter",
        "register_btn": "✅ Créer mon compte",
        "password_mismatch": "Les mots de passe ne correspondent pas",
        "fill_fields": "Veuillez remplir tous les champs obligatoires",
    },
    "ar": {
        "welcome": "مرحباً بك في نباتي 🌿",
        "subtitle": "سجّل دخولك للوصول إلى مساحتك الزراعية",
        "login": "تسجيل الدخول",
        "register": "إنشاء حساب",
        "email": "البريد الإلكتروني",
        "password": "كلمة المرور",
        "nom": "اللقب",
        "prenom": "الاسم",
        "region": "المنطقة (اختياري)",
        "confirm_password": "تأكيد كلمة المرور",
        "login_btn": "🔐 تسجيل الدخول",
        "register_btn": "✅ إنشاء حسابي",
        "password_mismatch": "كلمتا المرور غير متطابقتين",
        "fill_fields": "يرجى ملء جميع الحقول الإلزامية",
    }
}

REGIONS_TUNISIE = [
    "", "Tunis", "Ariana", "Ben Arous", "Manouba",
    "Nabeul", "Zaghouan", "Bizerte", "Béja", "Jendouba",
    "Kef", "Siliana", "Sousse", "Monastir", "Mahdia",
    "Sfax", "Kairouan", "Kasserine", "Sidi Bouzid",
    "Gabès", "Medenine", "Tataouine", "Gafsa", "Tozeur", "Kébili"
]

def init_form_state():
    """Initialise les valeurs du formulaire dans session_state."""
    defaults = {
        "form_nom": "", "form_prenom": "", "form_email": "",
        "form_pass1": "", "form_pass2": "", "form_region": "",
        "login_email": "", "login_password": "",
        "reg_success": False, "reg_error": "", "login_error": ""
    }
    for k, v in defaults.items():
        if k not in st.session_state:
            st.session_state[k] = v

def show_auth_page(lang="fr"):
    t = TRANSLATIONS[lang]
    init_form_state()

    st.markdown(f"""
    <div style='text-align:center; padding:2rem 0 1rem 0;'>
        <div style='font-size:4rem;'>🌿</div>
        <div style='font-size:2.5rem; font-weight:800;
                    background:linear-gradient(90deg,#1b4332,#40916c);
                    -webkit-background-clip:text;
                    -webkit-text-fill-color:transparent;'>
            Nabati — نباتي
        </div>
        <div style='color:#74c69d; margin-top:0.3rem;'>{t["subtitle"]}</div>
    </div>
    """, unsafe_allow_html=True)

    tab1, tab2 = st.tabs([f"🔐 {t['login']}", f"✨ {t['register']}"])

    # ---- CONNEXION ----
    with tab1:
        st.markdown(f"### {t['login']}")

        email_login = st.text_input(
            t["email"], placeholder="votre@email.com",
            autocomplete="email", key="input_login_email"
        )
        pass_login = st.text_input(
            t["password"], type="password",
            autocomplete="current-password", key="input_login_pass"
        )

        if st.session_state.login_error:
            st.error(st.session_state.login_error)

        if st.button(t["login_btn"], use_container_width=True, key="btn_login"):
            if email_login and pass_login:
                result = login_user(email_login, pass_login)
                if result["success"]:
                    st.session_state.user = result
                    st.session_state.authenticated = True
                    st.session_state.login_error = ""
                    st.rerun()
                else:
                    st.session_state.login_error = f"❌ {result['error']}"
                    st.rerun()
            else:
                st.warning(t["fill_fields"])

    # ---- INSCRIPTION ----
    with tab2:
        st.markdown(f"### {t['register']}")

        # Champs sans autocomplete pour éviter les popups navigateur
        nom = st.text_input(
            t["nom"], placeholder="Ex: Messaoud",
            autocomplete="off", key="input_reg_nom"
        )
        prenom = st.text_input(
            t["prenom"], placeholder="Ex: Mariam",
            autocomplete="off", key="input_reg_prenom"
        )
        email_r = st.text_input(
            t["email"], placeholder="votre@email.com",
            autocomplete="off", key="input_reg_email"
        )
        region = st.selectbox(
            t["region"], REGIONS_TUNISIE, key="input_reg_region"
        )
        pass1 = st.text_input(
            t["password"], type="password",
            autocomplete="new-password", key="input_reg_pass1"
        )
        pass2 = st.text_input(
            t["confirm_password"], type="password",
            autocomplete="new-password", key="input_reg_pass2"
        )

        # Afficher résultat précédent
        if st.session_state.reg_success:
            st.success("✅ Compte créé ! Connectez-vous dans l'onglet 'Se connecter'.")
        if st.session_state.reg_error:
            st.error(st.session_state.reg_error)

        if st.button(t["register_btn"], use_container_width=True, key="btn_register"):
            # Sauvegarder dans session_state
            st.session_state.form_nom    = nom
            st.session_state.form_prenom = prenom
            st.session_state.form_email  = email_r
            st.session_state.form_pass1  = pass1
            st.session_state.form_pass2  = pass2
            st.session_state.form_region = region

            # Validation
            if not all([nom, prenom, email_r, pass1, pass2]):
                st.session_state.reg_error = t["fill_fields"]
                st.session_state.reg_success = False
                st.rerun()
            elif pass1 != pass2:
                st.session_state.reg_error = t["password_mismatch"]
                st.session_state.reg_success = False
                st.rerun()
            elif len(pass1) < 6:
                st.session_state.reg_error = "⚠️ Mot de passe trop court (min. 6 caractères)"
                st.session_state.reg_success = False
                st.rerun()
            else:
                result = register_user(nom, prenom, email_r, pass1, region)
                if result["success"]:
                    st.session_state.reg_success = True
                    st.session_state.reg_error = ""
                    # Vider le formulaire
                    for k in ["form_nom","form_prenom","form_email","form_pass1","form_pass2"]:
                        st.session_state[k] = ""
                    st.rerun()
                else:
                    st.session_state.reg_error = f"❌ {result['error']}"
                    st.session_state.reg_success = False
                    st.rerun()