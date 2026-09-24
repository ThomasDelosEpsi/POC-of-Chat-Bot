import json
import os
import re
import nltk
from nltk.corpus import stopwords
from collections import Counter

# Télécharger les stopwords pour la première fois
nltk.download("stopwords")

# 📂 Chemins des fichiers
OUTPUT_JSON = "data/automations_with_keywords.json"  # Nouveau fichier enrichi
BASE_DIR = os.path.dirname(os.path.abspath(__file__))  # Récupère le répertoire du fichier actuel
AUTOMATION_PATH = os.path.join(BASE_DIR, "../data/automations.json") #Aller dans le dossier dans automations

# 🔍 Stopwords et mots inutiles
STOPWORDS = set(stopwords.words("english"))

def extract_text_from_json(description_json):
    """ Extrait le texte brut d'une description JSON. """
    try:
        description_data = json.loads(description_json)  # Convertir en dict JSON
        blocks = description_data.get("blocks", [])
        return " ".join(block["text"] for block in blocks if "text" in block)  # Concaténer les textes
    except (json.JSONDecodeError, TypeError):
        return description_json if isinstance(description_json, str) else ""

def load_automations():
    """Charge les automatisations depuis le fichier JSON."""

    try:
        with open(AUTOMATION_PATH, "r", encoding="utf-8") as f:
            data = json.load(f)

        if not data:
            print("⚠️ Aucune donnée trouvée dans automations.json !")
            return []

        # ✅ Extraire et nettoyer les descriptions
        for automation in data:
            extracted_text = []

            if "process_description__display" in automation:
                extracted_text.append(extract_text_from_json(automation["process_description__display"]))
            if "process_description" in automation:
                extracted_text.append(extract_text_from_json(automation["process_description"]))
            if "ovr-purpose" in automation:
                extracted_text.append(extract_text_from_json(automation["ovr-purpose"]))

            # ✅ Stocker la description nettoyée
            automation["clean_description"] = " ".join([t for t in extracted_text if t])

        print(f"✅ {len(data)} automatisations traitées avec succès.")
        return data

    except json.JSONDecodeError as e:
        print(f"❌ Erreur de décodage JSON : {e}")
        return []
    
# ✅ Fonction pour nettoyer et extraire des mots-clés
def extract_keywords(text):
    """Transforme une description en un ensemble de mots-clés pertinents"""
    if not text:
        return []

    # 1️⃣ Conversion en minuscule et suppression de la ponctuation
    text = text.lower()
    text = re.sub(r"[^a-z\s]", "", text)  # Supprime tout sauf lettres et espaces

    # 2️⃣ Tokenisation : découpage en mots
    words = text.split()

    # 3️⃣ Suppression des stopwords
    keywords = [word for word in words if word not in STOPWORDS]

    # 4️⃣ Suppression des mots trop courts
    keywords = [word for word in keywords if len(word) > 2]

    # 5️⃣ Suppression des doublons en conservant les mots les plus fréquents
    keyword_counts = Counter(keywords)
    sorted_keywords = [word for word, count in keyword_counts.most_common(100)]  # Garde les 10 mots les plus fréquents

    return sorted_keywords

# ✅ Lecture et transformation des données JSON
def process_automations():
    automations = load_automations()

    for automation in automations:
        description = automation.get("clean_description", "")  # 📌 On utilise la description nettoyée si dispo
        automation["keywords"] = extract_keywords(description)

    # ✅ Sauvegarde dans un nouveau fichier JSON
    with open(OUTPUT_JSON, "w", encoding="utf-8") as file:
        json.dump(automations, file, indent=4, ensure_ascii=False)

    print(f"✅ Transformation terminée ! Nouveau fichier : {OUTPUT_JSON}")

# 🏁 Exécution du script
if __name__ == "__main__":
    process_automations()
