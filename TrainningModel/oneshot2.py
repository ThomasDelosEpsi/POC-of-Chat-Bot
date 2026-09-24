import json
import os
def filter_json_data(input_file, output_file):
    """
    Filtre les clés spécifiques d'un fichier JSON et enregistre le résultat dans un autre fichier JSON.

    :param input_file: Chemin du fichier JSON d'entrée.
    :param output_file: Chemin du fichier JSON de sortie.
    """
    try:
        with open(input_file, "r", encoding="utf-8") as f:
            data = json.load(f)

        filtered_data = []

        for item in data:
            filtered_item = {
                "process_name": item.get("process_name", "N/A"),
                "clean_description": item.get("clean_description", "N/A"),
                "q2-apps_process__display": item.get("q2-apps_process__display", "N/A"),
                "phase_status_name": item.get("phase_status_name", "N/A"),
                "category_name": item.get("categories", [{}])[0].get("category_name", "N/A")  # Prend la 1ère catégorie si dispo
            }
            filtered_data.append(filtered_item)

        with open(output_file, "w", encoding="utf-8") as f:
            json.dump(filtered_data, f, indent=4, ensure_ascii=False)

        print(f"✅ JSON filtré enregistré avec succès dans {output_file} ({len(filtered_data)} éléments).")

    except Exception as e:
        print(f"❌ Erreur lors du filtrage du JSON : {e}")

# 🔹 Exemple d'utilisation
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
AUTOMATION_PATH = os.path.join(BASE_DIR, "../data/automations_with_keywords.json")
output_json_path = "filtered_automations.json"
filter_json_data(AUTOMATION_PATH, output_json_path)
