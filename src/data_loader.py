import json
import os
import hashlib
import secrets
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from TrainningModel.trainningSynonym import get_synonyms, filter_synonyms, filter_valid_keywords, get_filtered_synonyms
import random
import re
import pycountry
import spacy
import nltk
from difflib import SequenceMatcher
from nltk.data import find
from collections import Counter
import difflib

# ✅ Vérifier si spaCy est déjà installé
SPACY_MODEL = "en_core_web_sm"
if not spacy.util.is_package(SPACY_MODEL):
    print(f"📥 Téléchargement du modèle spaCy {SPACY_MODEL}...")
    spacy.cli.download(SPACY_MODEL)

# ✅ Charger spaCy (une seule fois)
nlp = spacy.load(SPACY_MODEL)

# ✅ Vérifier si les données WordNet sont déjà téléchargées
try:
    find("corpora/wordnet.zip")
except LookupError:
    print("📥 Téléchargement de WordNet pour NLTK...")
    nltk.download("wordnet")


def preprocess_text(text):
    """ Nettoie le texte, lemmatise les mots et remplace par des synonymes """
    doc = nlp(text.lower())  # Convertir en minuscule et tokeniser
    processed_tokens = []

    for token in doc:
        if token.is_stop or token.is_punct:  # Ignorer les mots vides et la ponctuation
            continue
        lemma = token.lemma_  # Récupérer le lemme du mot
        synonyms = get_synonyms(lemma)  # Récupérer les synonymes
        processed_tokens.append(synonyms[0] if synonyms else lemma)  # Prendre le premier synonyme si dispo

    return " ".join(processed_tokens) 

# Définir le bon chemin vers le fichier JSON
BASE_DIR = os.path.dirname(os.path.abspath(__file__))  # Récupère le répertoire du fichier actuel
DATA_PATH = os.path.join(BASE_DIR, "../data/bots_activities.json")  # Aller dans le dossier data
AUTOMATION_PATH = os.path.join(BASE_DIR, "../data/automations_with_keywords.json") #Aller dans le dossier dans automations
USERS_PATH = os.path.join(BASE_DIR, "../data/users.json") #Aller dans le dossier data dans user

ROLES = ["User", "Dev RPA", "Admin", "SuperAdmin", "Business"]

AVAILABLE_FOLDERS = [
    "France", "Allemagne", "Italie", "Espagne", "Royaume-Uni", "États-Unis", "Canada",
    "Brésil", "Japon", "Chine", "Inde", "Australie"
]

STOPWORDS = [
    "Hi RPA,", "Can you please", "implement RPA for", "I would like to", "Is there a way to",
    "Would it be possible to", "Can we automate", "Would RPA work for"
]

# Génère une liste de noms de pays
COUNTRIES_LIST = [country.name for country in pycountry.countries]
print(f"🌍 Debug: Liste des pays détectés ({len(COUNTRIES_LIST)} pays) -> {COUNTRIES_LIST[:10]} ...")

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
    sorted_keywords = [word for word, count in keyword_counts.most_common(30)]  # Garde les 10 mots les plus fréquents

    return sorted_keywords

def format_description(description, words_per_line=12):
    """ Formate la description en insérant un retour à la ligne tous les `words_per_line` mots. """
    words = description.split()
    formatted_description = ""
    
    for i in range(0, len(words), words_per_line):
        formatted_description += " ".join(words[i:i+words_per_line]) + "\n"

    return formatted_description.strip()

def remove_countries(text):
    """ Supprime les noms de pays du texte avec une meilleure détection. """
    if not text:
        return ""

    # ✅ Convertir le texte en minuscules pour éviter les erreurs de casse
    text_lower = text.lower()

    for country in COUNTRIES_LIST:
        country_lower = country.lower()

        # ✅ Remplacer les pays par un espace au lieu de juste les supprimer
        text_lower = re.sub(rf"\b{re.escape(country_lower)}\b", " ", text_lower, flags=re.IGNORECASE)

    # ✅ Nettoyer les espaces en trop après suppression
    text_cleaned = re.sub(r'\s+', ' ', text_lower).strip()

    print(f"🔹 Debug: Texte après suppression des pays -> '{text_cleaned}'")  # ✅ Vérifie si `France` est bien supprimé

    return text_cleaned

def clean_text(text):
    """ Nettoie la description en supprimant les phrases inutiles et les noms de pays. """
    if not text:
        return ""

    # Supprimer les mots inutiles
    for stopword in STOPWORDS:
        text = text.replace(stopword, "")

    # Supprimer les noms de pays (⚠️ Vérification supplémentaire)
    text_cleaned = remove_countries(text)

    # Supprimer les espaces en trop après nettoyage
    text_cleaned = re.sub(r'\s+', ' ', text_cleaned).strip()

    print(f"🔹 Debug: Texte nettoyé après suppression des pays -> '{text_cleaned}'")  # ✅ Vérifie si `France` est bien supprimé

    return text_cleaned

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
    
def hash_password(password, salt):
    """ Hache un mot de passe avec SHA-256 et un sel """
    return hashlib.sha256((password + salt).encode()).hexdigest()

def load_activities():
    """ Charge les activités UiPath depuis un fichier JSON. """
    try:
        with open(DATA_PATH, "r", encoding="utf-8") as f:
            data = json.load(f)

        if not data:
            print("⚠️ Aucune donnée trouvée dans automations.json !")
            return []

        # ✅ Extraire et nettoyer les descriptions des champs pertinents
        for automation in data:
            extracted_text = []
            
            # 🔹 Extraction des champs JSON imbriqués
            if "process_description__display" in automation:
                extracted_text.append(extract_text_from_json(automation["process_description__display"]))
            if "process_description" in automation:
                extracted_text.append(extract_text_from_json(automation["process_description"]))
            if "ovr-purpose" in automation:
                extracted_text.append(extract_text_from_json(automation["ovr-purpose"]))

            # 🔹 Fusionner toutes les descriptions extraites en une seule chaîne
            automation["clean_description"] = " ".join([t for t in extracted_text if t])

        return data

    except json.JSONDecodeError as e:
        print(f"❌ Erreur de décodage JSON : {e}")
        return []
    except Exception as e:
        print(f"❌ Erreur inattendue lors du chargement de automations.json : {e}")
        return []

def load_users():
    """ Charge les utilisateurs depuis le fichier JSON. """
    try:
        with open(USERS_PATH, "r", encoding="utf-8") as f:
            return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        return []

def save_user(username, password=None, role="User", folders=None, salt=None):
    """ Enregistre ou met à jour un utilisateur """
    users = load_users()

    # Vérifier si l'utilisateur existe déjà
    for user in users:
        if user["username"] == username:
            # Mise à jour du rôle et des folders si fournis
            if role:
                user["role"] = role
            if folders is not None:
                user["folders"] = folders
            if password:
                user["password"] = password
            if salt:
                user["salt"] = salt

            with open(USERS_PATH, "w", encoding="utf-8") as f:
                json.dump(users, f, indent=4)
            return True

    # Si l'utilisateur n'existe pas, l'ajouter
    salt = salt or secrets.token_hex(16)
    hashed_password = hashlib.sha256((password + salt).encode()).hexdigest() if password else None

    users.append({
        "username": username,
        "password": hashed_password,
        "salt": salt,
        "role": role,
        "folders": folders if folders else []
    })

    with open(USERS_PATH, "w", encoding="utf-8") as f:
        json.dump(users, f, indent=4)

    return True

def verify_user(username, password):
    """ Vérifie si le nom d'utilisateur et le mot de passe haché correspondent """
    users = load_users()

    for user in users:
        if user["username"] == username:
            stored_salt = user.get("salt", "")
            stored_hashed_password = user["password"]

            if stored_hashed_password == hash_password(password, stored_salt):
                return user  # Retourne les infos de l'utilisateur

    return None


def generate_response(user_query, similar_subjects):
    """ Génère une réponse améliorée avec un affichage bien structuré et un retour à la ligne automatique. """
    print(f"📝 Debug: Génération de réponse pour '{user_query}' avec {len(similar_subjects)} sujet(s).")

    if not similar_subjects:
        return "🤖 **Chatbot** : Aucun sujet similaire trouvé."

    subject = similar_subjects[0]  # ✅ Prend uniquement le premier sujet trouvé

    print(f"🔍 Debug: Affichage description pour {subject['process_name']}: {subject['description'][:300]}...") 

    # ✅ Appliquer le formatage de la description avec retour à la ligne automatique
    formatted_description = format_description(subject.get('description', '📌 Aucune description disponible.'))

    # ✅ Mise en page améliorée avec retour à la ligne et markdown
    response = f"""
🔹 **{subject.get('process_name', 'Untitled Automation')}**  

📋 **Détails du processus :**  
📌 **Statut du projet :**   
👕 **Taille du projet :**  
🏢 **Département impliqué :**   
👥 **Process Owner(s) :** 
🤝 **Autres parties prenantes :**   
💻 **Technologie utilisée :**  
🔧 **Maintenance requise :** 

📝 **Description :**  
{formatted_description}  

🔄 **Fréquence d'utilisation :**    

🔎 **Score de pertinence :** 🔥 **{subject['score']:.2f}**
    """

    return response


def clean_synonyms(synonyms):
    """ Filtre les synonymes inutiles comme les noms propres ou expressions incorrectes """
    unwanted_terms = {"kingdom_of_denmark", "nathaniel_currier"}  # Exclusion manuelle
    return {word.replace("_", " ") for word in synonyms if word not in unwanted_terms}

def get_best_match(word, reference_list):
    """ Trouve la meilleure correspondance entre un mot et une liste de mots existants """
    matches = difflib.get_close_matches(word, reference_list, n=1, cutoff=0.75)
    return matches[0] if matches else word

def find_similar_subjects(user_query, automations, threshold=0.1):
    """ Recherche les sujets les plus proches en comparant les mots-clés avec un seuil plus souple. """

    print(f"🔎 Debug: Recherche AutomationHub activée pour '{user_query}'")

    # ✅ Extraction et nettoyage des mots-clés
    user_keywords = extract_keywords(user_query)
    print(f"🔹 Debug: Mots-clés utilisateur (avant filtrage) -> {user_keywords}")

    if not user_keywords:
        print("⚠️ Aucun mot-clé pertinent trouvé dans la requête utilisateur.")
        return []

    # ✅ Ajout des synonymes et application du fuzzy matching
    extended_keywords = set(user_keywords)
    for word in user_keywords:
        synonyms = get_filtered_synonyms(word, automations)  # 🔥 Récupère les synonymes filtrés
        extended_keywords.update(synonyms)

    print(f"🔹 Debug: Mots-clés utilisateur (avec synonymes) -> {extended_keywords}")

    # ✅ Filtrage final pour ne garder que les mots-clés valides
    extended_keywords = filter_valid_keywords(extended_keywords, automations)

    best_matches = []
    best_score = 0
    best_subject = None

    for automation in automations:
        automation_keywords = set(automation.get("keywords", []))
        if not automation_keywords:
            continue

        # ✅ Comparaison des mots-clés
        common_keywords = extended_keywords & automation_keywords
        keyword_match_score = len(common_keywords) / max(len(extended_keywords), len(automation_keywords))

        if keyword_match_score > best_score:
            best_score = keyword_match_score
            best_subject = {
                "process_name": automation.get("process_name", "Untitled Automation"),
                "description": automation.get("clean_description", "Aucune description disponible."),
                "keywords": list(automation_keywords),
                "score": best_score
            }

        # ✅ On garde tous les sujets qui dépassent le seuil défini
        if keyword_match_score > threshold:
            match = {
            "process_name": automation.get("process_name", "Untitled Automation"),
            "description": automation.get("clean_description", "Aucune description disponible."),
            "keywords": list(automation_keywords),
            "score": keyword_match_score
            }
        
            best_matches.append(match)
            
            # ✅ Afficher tous les sujets trouvés dans la console
            print(f"🔹 Sujet trouvé : {match['process_name']} | Score : {match['score']:.2f} | Mots-clés communs : {common_keywords}")


    # ✅ Trier les résultats par score décroissant
    best_matches = sorted(best_matches, key=lambda x: x["score"], reverse=True)

    # ✅ Si aucun sujet ne dépasse le seuil, retourner la meilleure approximation
    if not best_matches and best_subject:
        print("⚠️ Aucun sujet n'a dépassé le seuil, mais on retourne le meilleur trouvé.")
        return [best_subject]

    if best_matches:
        print(f"✅ {len(best_matches)} sujet(s) trouvé(s) avec un score > {threshold}.")
        return best_matches[:3]

    print("⚠️ Aucun sujet pertinent trouvé après analyse.")
    return []




def extract_text_from_json(description_json):
    """ Extrait le texte brut d'une description JSON. """
    try:
        description_data = json.loads(description_json)  # Convertir en dict JSON
        blocks = description_data.get("blocks", [])
        return " ".join(block["text"] for block in blocks if "text" in block)  # Concaténer les textes
    except (json.JSONDecodeError, TypeError):
        return description_json if isinstance(description_json, str) else ""
