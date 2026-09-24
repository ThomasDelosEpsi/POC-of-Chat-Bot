import os
import xml.etree.ElementTree as ET
import json

# 📂 Dossier principal où se trouvent tous les bots (À MODIFIER)
BOTS_FOLDER = r"C:\Users\tdelos\OneDrive - LYRECO MANAGEMENT\Documents\UiPath"

# 📚 Dictionnaire contenant les documentations et exemples UiPath pour chaque activité
UIPATH_DOCS = {
    "ForEachRow": {
        "url": "https://docs.uipath.com/activities/docs/for-each-row-in-data-table",
        "example": "Utilisation: `For Each Row in dtExample -> row(\"Nom\").ToString` pour accéder aux valeurs."
    },
    "Assign": {
        "url": "https://docs.uipath.com/activities/docs/assign",
        "example": "Utilisation: `myVariable = 10` pour assigner une valeur à une variable."
    },
    "Click": {
        "url": "https://docs.uipath.com/activities/docs/click",
        "example": "Utilisation: Cliquer sur un bouton web en indiquant un sélecteur."
    },
    "TryCatch": {
        "url": "https://docs.uipath.com/activities/docs/try-catch",
        "example": "Utilisation: Encapsule un bloc de code pour gérer les exceptions."
    },
    "SendMail": {
        "url": "https://docs.uipath.com/activities/docs/send-mail",
        "example": "Utilisation: Envoi d’un email via Outlook ou SMTP."
    }
}

# Liste des activités à exclure
EXCLUDED_ACTIVITIES = [
    "Property", "Members", "Boolean", "Dictionary", "WorkflowViewStateService.ViewState",
    "AssemblyReference", "String", "Collection", "NamespacesForImplementation", "ReferencesForImplementation"
]

# Liste pour stocker les activités extraites
activities_data = []

def extract_activities_from_xaml(file_path, bot_name):
    """Parse un fichier .xaml et extrait uniquement les activités visibles dans Studio."""
    try:
        tree = ET.parse(file_path)
        root = tree.getroot()

        # Espaces de noms utilisés dans les fichiers XAML de UiPath
        ns = {
            'x': 'http://schemas.microsoft.com/winfx/2006/xaml',
            'd': 'http://schemas.microsoft.com/expression/blend/2008',
            'mc': 'http://schemas.openxmlformats.org/markup-compatibility/2006',
            'sap': 'http://schemas.microsoft.com/netfx/2009/xaml/activities/presentation',
            'sap2010': 'http://schemas.microsoft.com/netfx/2010/xaml/activities/presentation'
        }

        for elem in root.iter():
            activity_type = elem.tag.split("}")[-1]  # Récupérer le type de l'activité
            display_name = elem.attrib.get("{http://schemas.microsoft.com/winfx/2006/xaml}Name", None)  # Nom affiché
            annotation = elem.attrib.get("{http://schemas.microsoft.com/netfx/2010/xaml/activities/presentation}Annotation.AnnotationText", None)

            # 📌 Ne garder que les activités ayant un DisplayName ou une Annotation
            if activity_type not in EXCLUDED_ACTIVITIES and (display_name or annotation):
                activity_entry = {
                    "bot_name": bot_name,  # 🔥 Ajout du nom du bot
                    "file": os.path.relpath(file_path, BOTS_FOLDER),
                    "activity_type": activity_type
                }

                # Ajouter uniquement les champs utiles
                if display_name:
                    activity_entry["display_name"] = display_name
                if annotation:
                    activity_entry["annotation"] = annotation
                
                # Ajouter documentation officielle et exemple si disponible
                if activity_type in UIPATH_DOCS:
                    activity_entry["documentation"] = UIPATH_DOCS[activity_type]["url"]
                    activity_entry["example"] = UIPATH_DOCS[activity_type]["example"]

                activities_data.append(activity_entry)

    except Exception as e:
        print(f"⚠️ Erreur lors du parsing de {file_path}: {e}")

def scan_all_xaml_files(directory):
    """Parcourt tous les fichiers .xaml et extrait uniquement les activités utiles en ajoutant le bot_name."""
    for bot_name in os.listdir(directory):
        bot_path = os.path.abspath(os.path.normpath(os.path.join(directory, bot_name)))
        
        if os.path.isdir(bot_path):  # Vérifie si c'est bien un dossier (un bot)
            for root, _, files in os.walk(bot_path):
                for file in files:
                    if file.endswith(".xaml"):
                        extract_activities_from_xaml(os.path.join(root, file), bot_name)

# 🔍 Lancer l'extraction
scan_all_xaml_files(BOTS_FOLDER)

# 📁 Sauvegarde des activités dans un fichier JSON
output_file = "bots_activities.json"
with open(output_file, "w", encoding="utf-8") as f:
    json.dump(activities_data, f, indent=4, ensure_ascii=False)

print(f"✅ Extraction terminée ! {len(activities_data)} activités enrichies enregistrées dans '{output_file}'.")
