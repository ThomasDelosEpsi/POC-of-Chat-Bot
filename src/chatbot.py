from src.utils import check_predefined_responses, search_activity

# 🔹 Réponses aux phrases courantes
PREDEFINED_RESPONSES = {
    "bonjour": "Bonjour ! Comment puis-je vous aider avec UiPath ? 😊",
    "salut": "Salut ! Besoin d'aide sur UiPath ?",
    "merci": "Avec plaisir ! N'hésitez pas si vous avez d'autres questions. 🚀",
    "au revoir": "Au revoir ! Bonne automatisation avec UiPath ! 👋",
    "comment ça va": "Je vais bien, merci ! Et vous ? 😊",
    "que fais-tu": "Je vous aide à trouver des informations sur UiPath ! 🤖",
    "aide-moi": "Bien sûr ! Posez-moi une question sur UiPath et je chercherai la réponse.",
    "je suis perdu": "Pas de souci ! Dites-moi ce que vous cherchez et je vous guiderai.",
    "help": "Je peux vous aider à trouver des informations sur UiPath. Posez-moi une question !"
}

def get_chat_response(user_input, activities):
    """ Génère une réponse en fonction de la question posée. """
    user_input = user_input.lower().strip()

    # Vérifier les réponses pré-enregistrées
    predefined_response = check_predefined_responses(user_input, PREDEFINED_RESPONSES)
    if predefined_response:
        return f"🤖 **Chatbot** : {predefined_response}"

    # Chercher une activité UiPath
    result = search_activity(user_input, activities)
    if result:
        response = f"🤖 **Chatbot** : {result['summary']}\n"
        response += f"\n💡 **Comment l'utiliser ?** {result['usage']}\n"
        response += f"\n✅ **Exemple** :\n{result['example']}"

        if result.get("bots"):
            bot_list = "\n".join([f"- {bot}" for bot in result["bots"]])
            response += f"\n🤖 **Bots utilisant cette activité :**\n{bot_list}"

        return response

    return "🤖 **Chatbot** : Désolé, aucune activité trouvée."
