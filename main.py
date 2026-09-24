import streamlit as st
from pages import login, signup, chat, profile, dashboard

st.set_page_config(page_title="Chatbot UiPath", page_icon="🤖", layout="centered")

# ✅ Masquer le menu de navigation par défaut
st.markdown("""
    <style>
        [data-testid="stSidebarNav"] {
            display: none;
        }
    </style>
""", unsafe_allow_html=True)

# ✅ Initialisation des variables de session
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False
    st.session_state.username = ""
    st.session_state.role = ""
    st.session_state.folders = []

if "show_signup" not in st.session_state:
    st.session_state.show_signup = False

if "show_dashboard" not in st.session_state:
    st.session_state.show_dashboard = False

if "show_profile" not in st.session_state:
    st.session_state.show_profile = False

if "show_chatbot" not in st.session_state:
    st.session_state.show_chatbot = True  # ✅ Toujours afficher le Chatbot par défaut après connexion

# 🔄 Gestion automatique de la navigation
if st.session_state.logged_in:

    # ✅ Affichage de l'interface utilisateur connectée
    st.sidebar.write(f"👤 Connecté en tant que **{st.session_state.username}**")

    # ✅ Bouton pour accéder au Chatbot
    if st.sidebar.button("💬 Aller au Chatbot", key="chatbot_button"):
        st.session_state.show_chatbot = True
        st.session_state.show_dashboard = False
        st.session_state.show_profile = False
        st.rerun()

    # ✅ Vérification du rôle et affichage du bouton Dashboard
    if st.session_state.role in ["Admin", "SuperAdmin"]:
        if st.sidebar.button("📊 Gérer les utilisateurs", key="dashboard_button"):
            st.session_state.show_dashboard = True
            st.session_state.show_chatbot = False
            st.session_state.show_profile = False
            st.rerun()

    # ✅ Bouton pour accéder au profil utilisateur
    if st.sidebar.button("🔄 Modifier mon profil", key="profile_button"):
        st.session_state.show_profile = True
        st.session_state.show_chatbot = False
        st.session_state.show_dashboard = False
        st.rerun()

    # ✅ Bouton de déconnexion
    if st.sidebar.button("🚪 Se déconnecter", key="logout_button_sidebar"):
        for key in list(st.session_state.keys()):
            del st.session_state[key]
        st.session_state.logged_in = False
        st.session_state.username = ""
        st.session_state.role = ""
        st.session_state.folders = []
        st.session_state.show_signup = False
        st.session_state.show_profile = False
        st.session_state.show_dashboard = False
        st.session_state.show_chatbot = False
        st.rerun()

    # ✅ Affichage de la bonne page
    if st.session_state.show_dashboard:
        dashboard.show()
    elif st.session_state.show_profile:
        profile.show()
    else:
        chat.show()  # ✅ Par défaut, affiche le Chatbot

elif st.session_state.show_signup:
    signup.show()

else:
    login.show()
