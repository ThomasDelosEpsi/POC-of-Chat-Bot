import streamlit as st
import json
import os
import hashlib
import secrets
from src.data_loader import load_users, save_user, AVAILABLE_FOLDERS, ROLES, USERS_PATH

def reset_password(username):
    """ Réinitialise le mot de passe d'un utilisateur """
    users = load_users()
    for user in users:
        if user["username"] == username:
            salt = user.get("salt", secrets.token_hex(16))
            user["password"] = hashlib.sha256(("new_password" + salt).encode()).hexdigest()
            save_user(username=user["username"], password=user["password"], salt=salt)  # ✅ Correction ici
            return True
    return False

def delete_user(username):
    """ Supprime un utilisateur de `users.json` """
    users = load_users()
    updated_users = [user for user in users if user["username"] != username]
    with open(USERS_PATH, "w", encoding="utf-8") as f:
        json.dump(updated_users, f, indent=4)

def show():
    """ Affiche le dashboard d'administration """
    st.title("📊 Dashboard Administratif")

    if "logged_in" not in st.session_state or not st.session_state.logged_in:
        st.warning("🚨 Vous devez être connecté pour accéder au dashboard.")
        st.stop()

    if st.session_state.role not in ["Admin", "SuperAdmin"]:
        st.warning("⛔ Accès refusé : Seuls les Admins et SuperAdmins peuvent accéder à cette page.")
        st.stop()

    users = [user for user in load_users() if user["username"] != st.session_state.username]

    if st.session_state.role == "Admin":
        users = [user for user in users if user["role"] not in ["Admin", "SuperAdmin"]]

    st.subheader("👥 Liste des utilisateurs")

    modified_users = []
    for user in users:
        st.markdown("---")
        container = st.container()
        with container:
            col1, col2, col3, col4, col5, col6 = st.columns([1.5, 2, 3, 1.5, 1, 1])

            with col1:
                st.markdown(f"👤 **{user['username']}**")

            with col2:
                new_role = st.selectbox(
                    "Rôle",
                    options=ROLES,
                    index=ROLES.index(user["role"]),
                    key=f"role_{user['username']}"
                )

            with col3:
                new_folders = st.multiselect(
                    "Pays associés",
                    options=AVAILABLE_FOLDERS,
                    default=user["folders"],
                    key=f"folders_{user['username']}"
                )

            with col4:
                if st.button("✏️", key=f"reset_{user['username']}"):
                    if reset_password(user["username"]):
                        st.success(f"✅ Mot de passe réinitialisé pour {user['username']} (nouveau: `new_password`)")
                        st.rerun()

            with col5:
                if st.button("❌", key=f"delete_{user['username']}"):
                    delete_user(user["username"])
                    st.success(f"✅ Utilisateur {user['username']} supprimé avec succès !")
                    st.rerun()

            with col6:
                if user["role"] != new_role or user["folders"] != new_folders:
                    if st.button("💾", key=f"save_{user['username']}"):
                        save_user(username=user["username"], role=new_role, folders=new_folders)  # ✅ Correction ici
                        st.success(f"✅ Modifications enregistrées pour {user['username']} !")
                        st.rerun()
