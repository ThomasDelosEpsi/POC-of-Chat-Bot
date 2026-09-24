import requests
import json
import os
from datetime import datetime

class Mistral:
    def __init__(self, api_key, project_name, proxy=None):
        """
        Initialise la classe avec le token API, un nom de projet et un proxy optionnel.
        
        :param api_key: Clé API pour l'accès à Mistral.
        :param project_name: Nom du projet utilisé pour organiser les logs.
        :param proxy: Dictionnaire contenant les paramètres de proxy si nécessaire.
        """
        self.api_key = api_key
        self.base_url = "https://api.mistral.ai/v1/chat/completions"
        self.project_name = project_name
        self.proxy = proxy if proxy else {}

        # Création du dossier de logs
        self.log_dir = os.path.join("logs", self.project_name)
        os.makedirs(self.log_dir, exist_ok=True)

        # Contexte de base à inclure dans chaque requête
        self.system_prompt = """
        You are **Lyreco's AI assistant**, a multilingual expert in **Robotic Process Automation (RPA)** specializing in **UiPath**.  
        Your primary role is to assist users with **automation processes, workflows, and optimizations** within Lyreco's ecosystem.  

        ### **Your Capabilities**:
        - 🌍 **Multilingual**: You understand and respond in multiple languages.
        - 🤖 **UiPath Expertise**: You provide guidance on RPA implementation, automation strategies, and process optimization.
        - 🏢 **Lyreco Context**: You help improve business efficiency by automating repetitive tasks and streamlining workflows.
        - 📊 **Data-Driven Answers**: Your responses are based on existing Lyreco automation records and best industry practices.

        ### **Response Guidelines**:
        - 🎯 **Be precise & relevant**: Answer concisely and to the point.
        - 🔍 **Base responses on available data**: Do not generate information that is not supported by provided records.
        - 💬 **Use clear, business-friendly language**: Avoid technical jargon unless necessary.
        - 📌 **If a direct answer is not possible**: Suggest alternative automation strategies or process improvements.

        You are here to **assist Lyreco employees** in maximizing their automation potential with UiPath. Answer questions in a helpful, structured, and professional manner.
        """

    def send_request(self, user_question, files=None, max_tokens=3000, temperature=0.3):
        """
        Envoie une requête à l'API Mistral en utilisant le contexte chargé et des fichiers optionnels.
        
        :param user_question: La question de l'utilisateur.
        :param files: Chemin du fichier JSON à transmettre à Mistral.
        :param max_tokens: Nombre maximum de tokens dans la réponse.
        :param temperature: Contrôle la créativité de la réponse.
        :return: Réponse JSON de l'API.
        """
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {self.api_key}"
        }

        # Charger le fichier JSON si fourni
        file_content = ""
        if files and os.path.exists(files):
            with open(files, "r", encoding="utf-8") as f:
                file_content = f"\n\nHere is relevant automation data:\n" + json.dumps(json.load(f), indent=2)

        payload = {
            "model": "mistral-large-latest",
            "messages": [
                {"role": "system", "content": self.system_prompt},
                {"role": "user", "content": user_question + file_content}
            ],
            "temperature": temperature,
            "max_tokens": max_tokens
        }

        response = requests.post(self.base_url, headers=headers, json=payload, proxies=self.proxy)

        if response.status_code == 200:
            result = response.json()
            self.log_interaction(user_question, result)  # Enregistrer la conversation
            return result
        else:
            error_msg = {"error": f"API Error: {response.status_code}", "details": response.text}
            self.log_interaction(user_question, error_msg)  # Enregistrer l'erreur
            return error_msg

    def log_interaction(self, question, response):
        """
        Enregistre les interactions avec l'API dans un fichier JSON sans écraser les logs existants.
        
        :param question: La question posée.
        :param response: La réponse obtenue.
        """
        timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
        log_file = os.path.join(self.log_dir, "log.json")

        log_data = {
            "timestamp": timestamp,
            "question": question,
            "response": response
        }

        # Lire le fichier s'il existe, sinon créer une nouvelle liste
        logs = []
        if os.path.exists(log_file):
            try:
                with open(log_file, "r", encoding="utf-8") as log:
                    logs = json.load(log)  # Charger les logs existants
                    if not isinstance(logs, list):  # Si ce n'est pas une liste, le réinitialiser
                        logs = []
            except (json.JSONDecodeError, IOError):
                logs = []  # En cas d'erreur de lecture, recommencer proprement

        # Ajouter la nouvelle interaction à la liste
        logs.append(log_data)

        # Réécrire tout le fichier avec les logs mis à jour
        with open(log_file, "w", encoding="utf-8") as log:
            json.dump(logs, log, indent=4, ensure_ascii=False)

        print(f"📌 Interaction ajoutée dans {log_file}")


