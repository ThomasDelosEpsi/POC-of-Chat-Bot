import streamlit as st
from src.data_loader import verify_user

def show():
    """ Affiche la page de connexion """
    st.title("🔑 Connexion")

    # ✅ Initialisation des variables de session
    if "logged_in" not in st.session_state:
        st.session_state.logged_in = False
        st.session_state.username = ""
        st.session_state.role = ""
        st.session_state.folders = []

    if "show_signup" not in st.session_state:
        st.session_state.show_signup = False  # ✅ Ajout de l'initialisation

    if st.session_state.logged_in:
        st.success(f"✅ Connecté en tant que {st.session_state.username} ({st.session_state.role})")
        return  # ✅ Ne pas afficher le formulaire si l'utilisateur est connecté

    # 📝 Champs de connexion
    username = st.text_input("Nom d'utilisateur", key="login_username")
    password = st.text_input("Mot de passe", type="password", key="login_password")

    if st.button("Se connecter", key="login_button"):
        user = verify_user(username, password)
        if user:
            st.session_state.logged_in = True
            st.session_state.username = user["username"]
            st.session_state.role = user["role"]
            st.session_state.folders = user["folders"]
            st.success(f"Bienvenue {username} ! 🎉")
            st.rerun()
        else:
            st.error("Nom d'utilisateur ou mot de passe incorrect.")

    # 📌 Lien vers l'inscription (sans duplication de bouton)
    st.markdown("Vous n'avez pas de compte ?")

    if st.button("👉 S'inscrire ici", key="signup_button"):  # ✅ Ajout d'un key unique
        st.session_state.show_signup = True
        st.rerun()
