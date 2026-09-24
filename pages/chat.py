import streamlit as st
import time
from src.chatbot import get_chat_response
from src.data_loader import load_activities, load_automations, find_similar_subjects, generate_response

def show():
    """ Affiche la page du chatbot """
    st.title("🤖 Chatbot UiPath - Mode Chat")

    # ✅ Vérifier si l'utilisateur est bien connecté
    if "logged_in" not in st.session_state or not st.session_state.logged_in:
        st.warning("🚨 Vous devez être connecté pour accéder au chatbot.")
        st.stop()

    # ✅ Vérifier si l'utilisateur peut accéder à AutomationHub
    can_access_automationhub = st.session_state.role in ["Business", "Admin", "SuperAdmin"]

    # ✅ Charger les données nécessaires une seule fois
    if "activities" not in st.session_state:
        st.session_state.activities = load_activities()

    if "automations" not in st.session_state:
        st.session_state.automations = load_automations()

    # ✅ Initialiser l'historique du chat si non présent
    if "history" not in st.session_state:
        st.session_state.history = []

    # ✅ Initialiser la variable pour l'input utilisateur
    if "user_input" not in st.session_state:
        st.session_state.user_input = ""

    # ✅ Afficher l'historique du chat
    st.subheader("🕒 Chat en cours")
    for interaction in st.session_state.history:
        st.markdown(interaction)

    # ✅ Déterminer dynamiquement la hauteur du champ input
    text_length = len(st.session_state.user_input)
    min_height = 70  # Hauteur minimale du champ de saisie
    max_height = 200  # Hauteur maximale avant d'afficher un scroll
    dynamic_height = min(min_height + text_length // 3, max_height)  # Ajustement progressif

    # ✅ Champ de saisie utilisateur avec une hauteur dynamique
    user_input = st.text_area(
        "Pose ta question sur UiPath ou proposez une idée pour AutomationHub",
        value=st.session_state.user_input,
        key="chat_input",
        height=dynamic_height  # 📌 Ajustement automatique de la hauteur
    )

    # ✅ Bouton d'envoi
    if st.button("Envoyer", key="send_button_chat"):
        if user_input.strip():  # Vérifie que l'entrée n'est pas vide
            # ✅ Ajouter la question à l'historique
            st.session_state.history.append(f"🧑‍💻 **Vous** : {user_input}")

            response = ""

            # 🔹 **1️⃣ Vérification des activités UiPath**
            ui_response = get_chat_response(user_input, st.session_state.activities)
            print(f"🔍 Debug: Réponse UiPath -> {ui_response}")

            # ✅ Vérifier que la réponse UiPath n'est pas vide et n'est pas un message d'erreur
            if ui_response and ui_response.strip() and "Désolé, aucune activité trouvée." not in ui_response:
                response = ui_response
            else:
                # 🔹 **2️⃣ Vérification des idées RPA dans AutomationHub**
                if can_access_automationhub:
                    print(f"🔎 Debug: Recherche AutomationHub activée pour '{user_input}'")
                    similar_subjects = find_similar_subjects(user_input, st.session_state.automations)

                    if similar_subjects:
                        print(f"✅ {len(similar_subjects)} sujet(s) trouvé(s) avec un score élevé.")
                        response = generate_response(user_input, similar_subjects)
                    else:
                        print("⚠️ Aucun sujet RPA trouvé dans AutomationHub.")
                        response = "🤖 **Chatbot** : Aucun sujet similaire trouvé, vous pouvez proposer une nouvelle idée !"
                else:
                    response = "🤖 **Chatbot** : Je ne trouve pas de réponse à votre question."

            # ✅ Ajouter la réponse du chatbot à l'historique
            st.session_state.history.append(f"🤖 **Chatbot** : {response}")

            # ✅ Effacer proprement l'input après envoi
            st.session_state.user_input = ""

            # ✅ Rafraîchir l'affichage
            time.sleep(0.1)
            st.rerun()
