import gensim
from gensim.models import Word2Vec
import os
import json
from nltk.corpus import wordnet
import spacy
import streamlit as st
import difflib

MODEL_PATH = "data/synonym_model.bin"
SYNONYM_CACHE = "data/synonym_cache.json"
SYNONYM_CACHE_PATH = "data/synonym_cache.json"

def get_filtered_synonyms(word, automations):
    """Retourne uniquement les synonymes qui apparaissent dans les automatisations."""
    
    synonyms = set()

    # Récupérer les synonymes de WordNet
    for syn in wordnet.synsets(word):
        for lemma in syn.lemmas():
            synonyms.add(lemma.name().lower())

    # ✅ Filtrer pour ne garder que les mots qui existent dans le JSON AutomationHub
    all_automation_keywords = set()
    for automation in automations:
        all_automation_keywords.update(automation.get("keywords", []))

    filtered_synonyms = {syn for syn in synonyms if syn in all_automation_keywords}

    return list(filtered_synonyms)

def filter_valid_keywords(user_keywords, automations):
    """ Filtre les mots-clés utilisateur pour ne garder que ceux qui existent aussi dans les sujets AutomationHub, en autorisant des correspondances proches. """

    filtered_keywords = set()
    
    # Récupérer tous les mots-clés existants dans le JSON AutomationHub
    all_automation_keywords = set()
    for automation in automations:
        all_automation_keywords.update(automation.get("keywords", []))

    # Vérifier chaque mot utilisateur
    for word in user_keywords:
        if word in all_automation_keywords:
            filtered_keywords.add(word)  # ✅ Correspondance exacte
        else:
            # 🔍 Trouver la meilleure correspondance proche
            closest_match = difflib.get_close_matches(word, all_automation_keywords, n=1, cutoff=0.7)
            if closest_match:
                filtered_keywords.add(closest_match[0])  # ✅ Ajout du mot le plus proche

    print(f"✅ Debug: Mots-clés utilisateur (après filtrage amélioré avec fuzzy matching) -> {filtered_keywords}")
    return filtered_keywords

def load_spacy_model():
    """Charge le modèle spaCy une seule fois et l'enregistre en mémoire"""
    if "nlp_model" not in st.session_state:
        try:
            st.session_state.nlp_model = spacy.load("en_core_web_sm")
            print("✅ Modèle NLP chargé en mémoire.")
        except OSError:
            print("📥 Téléchargement du modèle spaCy en cours...")
            spacy.cli.download("en_core_web_sm")  # Téléchargement si absent
            st.session_state.nlp_model = spacy.load("en_core_web_sm")
            print("✅ Modèle NLP téléchargé et chargé.")


def load_synonym_cache():
    """Charge les synonymes stockés depuis un fichier JSON."""
    if os.path.exists(SYNONYM_CACHE_PATH):
        with open(SYNONYM_CACHE_PATH, "r", encoding="utf-8") as file:
            return json.load(file)
    return {}

def train_word2vec(descriptions):
    """ Entraîne un modèle Word2Vec à partir des descriptions des sujets AutomationHub. """
    tokenized_sentences = [desc.split() for desc in descriptions]
    model = Word2Vec(sentences=tokenized_sentences, vector_size=100, window=5, min_count=1, workers=4)
    model.save(MODEL_PATH)
    print("✅ Modèle Word2Vec entraîné et sauvegardé.")
    return model

def load_word2vec():
    """ Charge le modèle Word2Vec s'il existe, sinon l'entraîne. """
    if os.path.exists(MODEL_PATH):
        print("🔄 Chargement du modèle Word2Vec existant...")
        return Word2Vec.load(MODEL_PATH)
    else:
        print("⚠️ Aucun modèle Word2Vec trouvé. Il faut d'abord l'entraîner.")
        return None

def get_learned_synonyms(word, model):
    """ Retourne des mots similaires à un mot donné en utilisant le modèle Word2Vec. """
    try:
        similar_words = model.wv.most_similar(word, topn=5)
        return [w[0] for w in similar_words]
    except KeyError:
        return []  # Si le mot n'est pas connu, retourne une liste vide

def update_synonym_cache(word, synonyms):
    """ Stocke les nouveaux synonymes dans un cache JSON. """
    if os.path.exists(SYNONYM_CACHE):
        with open(SYNONYM_CACHE, "r", encoding="utf-8") as file:
            synonym_data = json.load(file)
    else:
        synonym_data = {}

    synonym_data[word] = synonyms

    with open(SYNONYM_CACHE, "w", encoding="utf-8") as file:
        json.dump(synonym_data, file, indent=4)


def save_synonym_cache(cache):
    """Sauvegarde les synonymes dans un fichier JSON."""
    with open(SYNONYM_CACHE_PATH, "w", encoding="utf-8") as file:
        json.dump(cache, file, indent=4)

synonym_cache = load_synonym_cache()

def get_synonyms(word, model=None):
    """Retourne les synonymes d'un mot en utilisant WordNet + Word2Vec + Cache"""
    
    # ✅ Vérifier si le mot est déjà dans le cache
    if word in synonym_cache:
        return synonym_cache[word]

    synonyms = set()

    # 1️⃣ D'abord, chercher dans WordNet
    for syn in wordnet.synsets(word):
        for lemma in syn.lemmas():
            synonyms.add(lemma.name().lower())

    # 2️⃣ Ensuite, chercher avec Word2Vec si un modèle est disponible
    if model:
        learned_synonyms = get_learned_synonyms(word, model)
        synonyms.update(learned_synonyms)

    # 3️⃣ Mettre à jour le cache et sauvegarder
    if synonyms:
        synonym_cache[word] = list(synonyms)
        save_synonym_cache(synonym_cache)  # ✅ Sauvegarde immédiate

    return list(synonyms)

def filter_synonyms(synonyms):
    """
    Filtre les synonymes inutiles en supprimant les verbes, adjectifs et mots trop génériques.
    Utilise spaCy pour analyser la nature des mots.
    """
    nlp = st.session_state.nlp_model  # ✅ Récupérer le modèle chargé
    filtered_synonyms = set()

    for word in synonyms:
        doc = nlp(word)
        for token in doc:
            if token.pos_ in {"NOUN", "PROPN"} and len(token.text) > 2:  # Garde seulement les noms propres et communs
                filtered_synonyms.add(token.text.lower())

    return filtered_synonyms

load_spacy_model()