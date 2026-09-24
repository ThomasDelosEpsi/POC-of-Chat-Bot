# POC of Chat Bot

Preuve de concept d'un chatbot d'aide à l'automatisation (RPA), avec une interface Streamlit multi-pages : authentification (login/signup), profil utilisateur, dashboard d'administration et un chatbot capable de répondre à des questions sur un catalogue d'automatisations existantes, en s'appuyant sur l'API Mistral.

Inclut également des scripts d'entraînement/expérimentation (recherche de synonymes, extraction d'activités UiPath) utilisés pour préparer les données du chatbot.

## Stack

- Python, Streamlit
- API Mistral (LLM)

## Structure

- `main.py` — point d'entrée de l'application Streamlit
- `pages/` — pages de l'application (login, chat, dashboard, profil...)
- `mistralChatbot/` — logique d'appel au modèle de langage
- `src/` — logique métier (chargement de données, chatbot, utilitaires)
- `TrainningModel/` — scripts d'expérimentation / entraînement
- `data/` — jeux de données utilisés par le chatbot

## Usage

```bash
pip install -r requirements.txt
streamlit run main.py
```
