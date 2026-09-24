import requests
import json
import os
import datetime

# 🔑 Clé API Mistral (définie via variable d'environnement MISTRAL_API_KEY)
MISTRAL_API_KEY = os.environ["MISTRAL_API_KEY"]

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
JSON_FILE_PATH = os.path.join(BASE_DIR, "../data/filtered_automations.json")
LOG_FILE_PATH = os.path.join(BASE_DIR, "../data//mistral_responses.json")

# 🔗 URL de l'API Mistral
MISTRAL_API_URL = "https://api.mistral.ai/v1/chat/completions"

system_prompt = """
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

def get_proxy():
    """Récupère les paramètres du proxy Lyreco depuis les variables d'environnement."""
    proxy_host = os.getenv("PROXY_HOST", "http://proxy.lyreco.com")  # Adresse du proxy
    proxy_port = os.getenv("PROXY_PORT", "8080")  # Port du proxy

    if proxy_host and proxy_port:
        proxy_url = f"{proxy_host}:{proxy_port}"
        return {
            "http": proxy_url,
            "https": proxy_url
        }
    
    return None  # Pas de proxy configuré

def load_json(file_path):
    """Charge un fichier JSON en mémoire."""
    try:
        with open(file_path, "r", encoding="utf-8") as file:
            return json.load(file)
    except (FileNotFoundError, json.JSONDecodeError):
        return []

def save_json(data, file_path):
    """Sauvegarde les données dans un fichier JSON."""
    try:
        with open(file_path, "w", encoding="utf-8") as file:
            json.dump(data, file, indent=4, ensure_ascii=False)
    except Exception as e:
        print(f"❌ Erreur lors de la sauvegarde du fichier {file_path}: {e}")

def count_automations(automations):
    """Retourne le nombre total d'automatisations."""
    return len(automations)

def detect_predefined_questions(question, automations):
    """Détecte si la question concerne un comptage et répond immédiatement."""
    question_lower = question.lower()

    if "combien" in question_lower and "process" in question_lower:
        process_count = count_automations(automations)
        return f"Nous avons actuellement **{process_count}** processus d'automatisation enregistrés."

    return None  # Si la question n'est pas reconnue, continuer avec Mistral

def format_context(automations):
    """Construit un contexte en formatant les automatisations sous forme de texte."""
    if not automations:
        return "Aucune automatisation trouvée dans le fichier."

    context_lines = [
        f"- {a.get('process_name', 'Nom inconnu')}: {a.get('clean_description', 'Pas de description disponible')}"
        for a in automations
    ]
    return "\n".join(context_lines)

def call_mistral(question, context):
    """Effectue un appel API à Mistral avec un contexte structuré et un proxy."""
    headers = {
        "Authorization": f"Bearer {MISTRAL_API_KEY}",
        "Content-Type": "application/json",
        "Accept": "application/json"
    }
    
    prompt = (
        f"Voici des automatisations enregistrées :\n{context}\n\n"
        f"Réponds de manière très claire et concise à la question suivante :\n"
        f"{question}\n"
        f"N'invente pas de réponses, base-toi uniquement sur les informations fournies."
    )

    payload = {
        "model": "mistral-large-latest",
        "messages": [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": prompt}
        ],
        "temperature": 0.0,  # Pour éviter les hallucinations
        "max_tokens": 3000
    }

    # ✅ Récupération du proxy
    proxy = get_proxy()

    response = requests.post(MISTRAL_API_URL, headers=headers, json=payload, proxies=proxy)
    
    if response.status_code == 200:
        return response.json()
    else:
        return {"error": f"Erreur API: {response.status_code}", "details": response.text}

def log_interaction(question, response):
    """Stocke chaque question et réponse dans le fichier de log."""
    log_data = load_json(LOG_FILE_PATH)  # Charger l'historique existant

    # ✅ Structuration de la réponse
    new_entry = {
        "timestamp": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "question": question,
        "response": response
    }

    log_data.append(new_entry)  # Ajouter la nouvelle entrée
    save_json(log_data, LOG_FILE_PATH)  # Sauvegarder l'historique

def main():
    """Exécute le programme et gère la logique des réponses."""
    automations = load_json(JSON_FILE_PATH)
    
    question = input("Posez votre question : ")

    # 🔹 Vérification des questions pré-définies (comme le comptage des processus)
    predefined_response = detect_predefined_questions(question, automations)
    if predefined_response:
        print(predefined_response)
        log_interaction(question, predefined_response)  # Log de la réponse immédiate
        return

    # 🔹 Construction du contexte
    context = format_context(automations)
    
    # 🔹 Appel à l'API Mistral avec proxy
    api_response = call_mistral(question, context)
    
    # ✅ Extraction de la réponse de Mistral
    mistral_message = api_response.get("choices", [{}])[0].get("message", {}).get("content", "Pas de réponse.")

    # 🔹 Stocker la réponse
    log_interaction(question, mistral_message)

    final_response = {
        "question": question,
        "mistral_response": mistral_message
    }

    print(json.dumps(final_response, indent=4, ensure_ascii=False))

if __name__ == "__main__":
    main()