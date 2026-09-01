import db
import sqlite3
import os
import csv
from datetime import datetime


print("=== Export des données ===\n")


# Ouverture de la connexion
connexion = db.get_connection()
connexion.row_factory = sqlite3.Row
curseur = connexion.cursor()


# Liste des modèles CLIP
curseur.execute("SELECT * FROM CLIP_MODEL")
results_clip = curseur.fetchall()

print("Modèle(s) CLIP disponible(s) :")
for row in results_clip:
    print(f"({row["clip_model_id"]}) {row["name"]} - {row["publication_date"]}")


# Modèle CLIP à utiliser pour l'export
clip_model_id_for_export = int(input("\nIdentifiant du modèle à utiliser : "))

# Chemin d'export
export_path = input("\nDossier d'export : ")
now = datetime.now()
export_time = now.strftime("%y%m%d_%H%M")
export_file = os.path.join(export_path, f"caquot_export-{export_time}.csv")


# Récupération et jointure des données depuis la base
curseur.execute(
    """SELECT IMAGE.name AS image_name, THESAURUS.thesaurus_id AS thesaurus_id, IMAGE_THESAURUS.confidence_level AS confidence_level, CLIP_MODEL.name AS clip_model_name, CLIP_MODEL.publication_date AS clip_model_date, CLIP_MODEL.clip_model_id AS clip_model_id
    FROM IMAGE_THESAURUS
    JOIN IMAGE ON IMAGE_THESAURUS.image_id = IMAGE.image_id
    JOIN THESAURUS ON IMAGE_THESAURUS.thesaurus_id = THESAURUS.thesaurus_id
    JOIN CLIP_MODEL ON IMAGE_THESAURUS.clip_model_id = CLIP_MODEL.clip_model_id"""
)
join_result = curseur.fetchall()


# Mise en forme des formes des données
data = []
for row in join_result:
    image_without_path = os.path.basename(row["image_name"])
    image_without_extension = os.path.splitext(image_without_path)
    image_without_last_part = image_without_extension[0].removesuffix("-POS")
    image_final_name = image_without_last_part.replace("_", ".")

    if row["clip_model_id"] != clip_model_id_for_export:
        continue
    
    data_dict = {
        "accession_number": str(image_final_name),
        "thesaurus_id": str(row["thesaurus_id"]),
        "confidence_level": f"{row['confidence_level']:.4f}",
        "model_name": str(f"{row["clip_model_name"]} - {row["clip_model_date"]}")
    }

    data.append(data_dict)


# Regroupement par numéro d'inventaire
grouped_data = {}
for row in data:
    accession_number = row["accession_number"]
    if accession_number not in grouped_data:
        grouped_data[accession_number] = {"thesaurus_id": [], "confidence_level": [], "model_name": []}
    grouped_data[accession_number]["thesaurus_id"].append(row["thesaurus_id"])
    grouped_data[accession_number]["confidence_level"].append(row["confidence_level"])
    grouped_data[accession_number]["model_name"].append(row["model_name"])


grouped_data_in_row = []
for accession_number, values in grouped_data.items():
    thesaurus_str = ";".join(values["thesaurus_id"])
    confidence_str = ";".join(values["confidence_level"])
    model_str = ";".join(values["model_name"])

    row = {
        "accession_number": accession_number,
        "thesaurus_id": thesaurus_str,
        "confidence_level": confidence_str,
        "model_name": model_str,
    }

    grouped_data_in_row.append(row)


# Production du '.csv'
with open (export_file, "w", newline="", encoding="utf-8") as file:
    writer = csv.DictWriter(file, fieldnames=["accession_number", "thesaurus_id", "confidence_level", "model_name"])
    writer.writeheader()
    writer.writerows(grouped_data_in_row)

print(f"Fichier écrit ({export_file})")


# Fermeture de la connexion
connexion.close()

print("\nProgramme terminé")