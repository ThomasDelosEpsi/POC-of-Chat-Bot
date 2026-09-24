import streamlit as st
from src.data_loader import save_user, ROLES, AVAILABLE_FOLDERS

def show():
    """ Affiche la page d'inscription """
    st.title("📝 Inscription")

    username = st.text_input("Nom d'utilisateur", key="signup_username")
    password = st.text_input("Mot de passe", type="password", key="signup_password")
    confirm_password = st.text_input("Confirmez le mot de passe", type="password", key="signup_confirm_password")

    # 📌 Choix du rôle
    role = st.selectbox("Choisissez votre rôle", ROLES, index=0)

    # 📌 Sélection des folders (pays) avec des checkbox
    folders = []
    st.write("📁 Sélectionnez les pays associés :")
    for folder in AVAILABLE_FOLDERS:
        if st.checkbox(folder, key=f"folder_{folder}"):
            folders.append(folder)

    if st.button("S'inscrire"):
        if not username or not password:
            st.warning("Veuillez remplir tous les champs.")
        elif password != confirm_password:
            st.error("Les mots de passe ne correspondent pas.")
        else:
            success = save_user(username, password, role, folders)
            if success:
                st.success("Inscription réussie ! Connectez-vous maintenant.")
                st.session_state.show_signup = False
                st.rerun()
            else:
                st.error("Ce nom d'utilisateur existe déjà.")
