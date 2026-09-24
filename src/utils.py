# 🔹 Explications détaillées des activités UiPath
ACTIVITY_DESCRIPTIONS = {
    "ForEachRow": {
        "summary": "L'activité **For Each Row** permet de parcourir chaque ligne d'un DataTable.",
        "usage": "Elle est utilisée pour traiter chaque ligne d'un tableau, comme lire des fichiers Excel ou manipuler des bases de données.",
        "example": "```python\nFor Each Row in dtExample:\n    valeur = row(\"Nom\").ToString\n```"
    },
    "Assign": {
        "summary": "L'activité **Assign** sert à affecter une valeur à une variable.",
        "usage": "Utile pour stocker des données temporaires ou manipuler des valeurs numériques et textuelles.",
        "example": "```python\nmyVariable = 10\nmessage = \"Bonjour UiPath!\"\n```"
    },
    "Click": {
        "summary": "L'activité **Click** permet de cliquer sur un élément d'une interface utilisateur.",
        "usage": "Elle est souvent utilisée pour naviguer sur un site web ou interagir avec des applications desktop.",
        "example": "```python\nClick target=button[\"Envoyer\"]\n```"
    },
    "TryCatch": {
        "summary": "L'activité **Try Catch** permet de gérer les erreurs en UiPath.",
        "usage": "Elle exécute un bloc de code et capture les erreurs pour éviter un plantage du robot.",
        "example": "```python\nTry:\n    Ouvrir une application\nCatch:\n    Afficher un message d'erreur\n```"
    }
}

def check_predefined_responses(query, responses):
    """ Vérifie si la question correspond à une réponse pré-enregistrée. """
    return responses.get(query, None)

def search_activity(query, activities):
    """ Recherche une activité et retourne ses détails. """
    query_lower = query.lower().strip()

    for activity_type in ACTIVITY_DESCRIPTIONS.keys():
        if activity_type.lower() in query_lower:
            matching_activity = ACTIVITY_DESCRIPTIONS[activity_type]
            bots_using_activity = {activity.get("bot_name", "Bot inconnu") for activity in activities if activity.get("activity_type", "").lower() == activity_type.lower()}

            return {
                "activity_type": activity_type,
                "summary": matching_activity["summary"],
                "usage": matching_activity["usage"],
                "example": matching_activity["example"],
                "bots": sorted(bots_using_activity)
            }

    return None
