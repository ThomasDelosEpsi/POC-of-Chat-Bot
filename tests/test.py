import sys
import os
import json

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
AUTOMATION_PATH = os.path.join(BASE_DIR, "../data/filtered_automations.json")

sys.path.append(os.path.abspath(os.path.join(BASE_DIR, "..")))

from mistral.Mistral import Mistral

# Initialisation de Mistral avec un token API et un projet nommé "Lyreco_Automation"
mistral = Mistral(api_key=os.environ["MISTRAL_API_KEY"], project_name="Lyreco_AutomationHub", proxy={
    "http": "http://proxy.lyreco.com:8080",
    "https": "http://proxy.lyreco.com:8080"
})

# Envoyer une question avec un fichier JSON en référence
response = mistral.send_request(
    "Tell me about the subject P2P approval matrix",
    AUTOMATION_PATH
)

# Afficher la réponse obtenue
print(json.dumps(response, indent=4, ensure_ascii=False))