import streamlit as st
from src.data_loader import load_users, save_user, AVAILABLE_FOLDERS
import json
import os
import hashlib

# 📌 Définir le chemin vers le fichier JSON
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
USERS_PATH = os.path.join(BASE_DIR, "../data/users.json")

def update_user_data(username, new_password=None, new_folders=None):
    """ Met à jour le mot de passe et/ou les folders de l'utilisateur """
    users = load_users()

    for user in users:
        if user["username"] == username:
            # Mise à jour du mot de passe si fourni
            if new_password:
                salt = user.get("salt", "")
                user["password"] = hashlib.sha256((new_password + salt).encode()).hexdigest()

            # Mise à jour des folders si fournis
            if new_folders is not None:
                user["folders"] = new_folders

            # Sauvegarde des modifications
            with open(USERS_PATH, "w", encoding="utf-8") as f:
                json.dump(users, f, indent=4)
            return True
    return False

def show():
    """ Page de gestion du profil utilisateur """
    st.title("👤 Mon Profil")

    # 📌 Vérifier si l'utilisateur est connecté
    if "logged_in" not in st.session_state or not st.session_state.logged_in:
        st.warning("🚨 Vous devez être connecté pour accéder à cette page.")
        st.stop()

    username = st.session_state.username
    role = st.session_state.role
    current_folders = st.session_state.folders

    st.write(f"**👤 Utilisateur :** {username}")
    st.write(f"**🛠️ Rôle :** {role}")

    # 📌 Modifier les folders
    st.write("📁 **Sélectionnez les pays associés** :")
    new_folders = []
    for folder in AVAILABLE_FOLDERS:
        if st.checkbox(folder, value=(folder in current_folders), key=f"folder_{folder}"):
            new_folders.append(folder)

    # 📌 Modifier le mot de passe
    st.write("🔑 **Changer votre mot de passe**")
    new_password = st.text_input("Nouveau mot de passe", type="password")
    confirm_password = st.text_input("Confirmez le nouveau mot de passe", type="password")

    if st.button("Mettre à jour"):
        if new_password and new_password != confirm_password:
            st.error("❌ Les mots de passe ne correspondent pas.")
        else:
            success = update_user_data(username, new_password if new_password else None, new_folders)
            if success:
                st.success("✅ Profil mis à jour avec succès !")
                st.session_state.folders = new_folders  # Mise à jour immédiate
                st.rerun()
            else:
                st.error("❌ Erreur lors de la mise à jour.")
