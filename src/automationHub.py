import os
import requests
import json

api_key = ""
auth_token = "4113c3ea-7a71-43db-b122-b8c46fb5028f/f029b82b-45a1-41f7-a577-5b317c240cd7"

def get_proxy():
    """
    Récupère la configuration du proxy depuis les variables d'environnement ou retourne None.
    """
    proxy_host = os.getenv("PROXY_HOST", "http://proxy.lyreco.com")  # Adresse du proxy
    proxy_port = os.getenv("PROXY_PORT", "8080")  # Port du proxy

    if proxy_host and proxy_port:
        proxy_url = f"{proxy_host}:{proxy_port}"
        return {
            "http": proxy_url,
            "https": proxy_url
        }
    
    return None  # Pas de proxy configuré

def fetch_automations(api_key: str, auth_token: str):
    """ Récupère les automatisations depuis AutomationHub et les stocke dans un JSON """
    url = "https://cloud.uipath.com/lyrecomanagement/DefaultTenant/automationhub_/api/v1/openapi/automations?limit=30000&offset=0"

    headers = {
        "x-ah-openapi-app-key": api_key,
        "x-ah-openapi-auth": "openapi-token",
        "Authorization": f"Bearer {auth_token}"
    }

    proxy = get_proxy()  # Récupérer le proxy configuré

    try:
        print("🔄 Envoi de la requête à AutomationHub...")  # ✅ Indication avant l'envoi
        response = requests.get(url, headers=headers, proxies=proxy)  # ✅ Ajout du proxy

        print(f"📡 Statut HTTP : {response.status_code}")  # ✅ Affiche le statut de la réponse
        response.raise_for_status()  # Lève une erreur pour les codes HTTP 4xx/5xx

        # ✅ Convertir la réponse en JSON
        data = response.json()

        # ✅ Vérifier si les données sont bien présentes
        if "data" in data and "processes" in data["data"]:
            automations = data["data"]["processes"]

            # ✅ Enregistrer dans un fichier JSON
            with open("automations.json", "w", encoding="utf-8") as f:
                json.dump(automations, f, indent=4, ensure_ascii=False)

            print(f"✅ Données enregistrées dans automations.json ({len(automations)} automatisations)")
            return automations
        else:
            print("⚠️ Aucun résultat trouvé dans la réponse API.")
            return None

    except requests.exceptions.RequestException as e:
        print(f"❌ Erreur lors de la requête API : {e}")
        return None


data = fetch_automations(api_key, auth_token)

if data:
    print("\n🎯 Nombre d'automatisations trouvées :", len(data))
