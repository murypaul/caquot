from . import db
import sqlite3
import os
import csv
from . import thesaurus
from . import model
from . import dialogs
from datetime import datetime


def export (connection, cursor):
    print("""+--------+
| Export |
+--------+\n""")

    # Chemin d'export du fichier
    print("Dossier d'export")
    export_path_input = dialogs.ask_directory("Dossier d'export")
    if not export_path_input:
        print("Annulation...\n")
        return
    export_path = os.path.abspath(os.path.expanduser(export_path_input))
    now = datetime.now()
    time = now.strftime("%y%m%d_%H%M")
    file_export_name = os.path.join(export_path, f"caquot_export-{time}.csv")


    while True: # Récupération et jointure des données
        print("Voulez-vous exporter les données d'un modèle ou d'un thésaurus particulier ? (O/N)")
        response = input("CAQUOT> ")

        if response.lower() in ['yes', 'y', 'oui', 'o']: # Récupération selon modèle/thésaurus
            thesaurus_name = thesaurus.select_thesaurus(connection, cursor)
            model_name = model.select_model(connection, cursor)

            cursor.execute("""
                SELECT IMAGE.name AS image_name, COALESCE(IMAGE.idno, IMAGE.name) AS accession_number, THESAURUS.thesaurus_id AS thesaurus_id, IMAGE_THESAURUS.cosinus_similarity AS cosinus_similarity, CLIP_MODEL.name AS clip_model_name, CLIP_MODEL.clip_model_id AS clip_model_id
                FROM IMAGE_THESAURUS
                JOIN IMAGE
                    ON IMAGE_THESAURUS.image_id = IMAGE.image_id
                JOIN THESAURUS
                    ON IMAGE_THESAURUS.thesaurus_id = THESAURUS.thesaurus_id
                JOIN CLIP_MODEL
                    ON IMAGE_THESAURUS.clip_model_id = CLIP_MODEL.clip_model_id
                WHERE THESAURUS.thesaurus_name = ? AND CLIP_MODEL.clip_model_id = ?
                """,
                (thesaurus_name, model_name["model_id"])
            )
            results = cursor.fetchall()

            break


        elif response.lower() in ['no', 'n', 'non']: # Récupération de toutes les données
            cursor.execute("""
                SELECT IMAGE.name AS image_name, COALESCE(IMAGE.idno, IMAGE.name) AS accession_number, THESAURUS.thesaurus_id AS thesaurus_id, IMAGE_THESAURUS.cosinus_similarity AS cosinus_similarity, CLIP_MODEL.name AS clip_model_name, CLIP_MODEL.clip_model_id AS clip_model_id
                FROM IMAGE_THESAURUS
                JOIN IMAGE
                    ON IMAGE_THESAURUS.image_id = IMAGE.image_id
                JOIN THESAURUS
                    ON IMAGE_THESAURUS.thesaurus_id = THESAURUS.thesaurus_id
                JOIN CLIP_MODEL
                    ON IMAGE_THESAURUS.clip_model_id = CLIP_MODEL.clip_model_id
                """
            )
            results = cursor.fetchall()

            break

        else:
            print("/!\\ Entrée invalide. Saisir 'O' ou 'N'.\n")


    # Mise en forme des données
    print("Formatage des données...")

    only_images_name = [] # Récupération du nom des images dans une liste à part
    for row in results:
        only_images_name.append(row["image_name"])

    data = []
    for row in results:
        data_dict = {
            "accession_number": row["accession_number"],
            "thesaurus_id": row["thesaurus_id"],
            "cosinus_similarity": f"{row['cosinus_similarity']:.3f}", # Modifier ':.3f' pour changer le nombre de chiffres après la virgule
            "model_name": row["clip_model_name"]
        }

        data.append(data_dict)

    # Regroupement par numéro d'inventaire
    grouped_data = {}
    for row in data:
        accession_number = row["accession_number"]
        if accession_number not in grouped_data:
            grouped_data[accession_number] = {"thesaurus_id" : [], "cosinus_similarity": [], "model_name": []}
        grouped_data[accession_number]["thesaurus_id"].append(row["thesaurus_id"])
        grouped_data[accession_number]["cosinus_similarity"].append(row["cosinus_similarity"])
        grouped_data[accession_number]["model_name"].append(row["model_name"])

    grouped_data_in_row = [] # Une seule ligne porduite par numéro d'inventaire
    for accession_number, values in grouped_data.items():
        thesaurus_str = ";".join(values["thesaurus_id"])
        similarity_str = ";".join(values["cosinus_similarity"])
        model_str = ";".join(values["model_name"])

        row = {
            "accession_number": accession_number,
            "thesaurus_id": thesaurus_str,
            "cosinus_similarity": similarity_str,
            "model_name": model_str,
        }

        grouped_data_in_row.append(row)

    
    # Production du csv
    print("Ecriture du fichier CSV...\n")

    with open (file_export_name, "w", newline="", encoding="utf-8") as file:
        writer = csv.DictWriter(file, fieldnames=["accession_number", "thesaurus_id", "cosinus_similarity", "model_name"])
        writer.writeheader()
        writer.writerows(grouped_data_in_row)

    print(f"Fichier écrit : ({file_export_name})\n")


    # Changement de la valeur 'exported' sur la table IMAGE_THESAURUS
    for image in only_images_name:
        cursor.execute("""
            UPDATE IMAGE_THESAURUS
            SET exported = ?
            WHERE image_id = (
                SELECT image_id 
                FROM IMAGE 
                WHERE name = ?
            )
        """,
        ("TRUE", image)
        )