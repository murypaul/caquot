from . import db
import sqlite3
import os
import csv
from . import thesaurus
from . import model
from tkinter import filedialog
from datetime import datetime


def export (connection, cursor):
    print("""+---------+
| Export |
+--------+\n""")

    # Chemin d'export du fichier
    print("DOSSIER D'EXPORT")
    export_path_input = filedialog.askdirectory(mustexist=True, title='Dossier d''export')
    export_path = os.path.abspath(os.path.expanduser(export_path_input))
    now = datetime.now()
    time = now.strftime("%y%m%d_%H%M")
    file_export_name = os.path.join(export_path, f"caquot_export-{time}.csv")


    while True: # Récupération et jointure des données
        print("EXPORTER LES DONNEES D'UN MODELE OU D'UN THESAURUS PARTICULIER ? (O/N)")
        response = input("CAQUOT> ")

        if response.lower() in ['yes', 'y', 'oui', 'o']: # Récupération selon modèle/thésaurus
            thesaurus_name = thesaurus.select_thesaurus(connection, cursor)
            model_name = model.select_model(connection, cursor)

            cursor.execute("""
                SELECT IMAGE.name AS image_name, THESAURUS.thesaurus_id AS thesaurus_id, IMAGE_THESAURUS.confidence_level AS confidence_level, CLIP_MODEL.name AS clip_model_name, CLIP_MODEL.clip_model_id AS clip_model_id
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
                SELECT IMAGE.name AS image_name, THESAURUS.thesaurus_id AS thesaurus_id, IMAGE_THESAURUS.confidence_level AS confidence_level, CLIP_MODEL.name AS clip_model_name, CLIP_MODEL.clip_model_id AS clip_model_id
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
            print("/!\\ ENTREE INVALIDE. SAISIR 'O' ou 'N'.\n")


    # Mise en forme des données
    print("FORMATAGE DES DONNEES...")

    only_images_name = [] # Récupération du nom des images dans une liste à part
    for row in results:
        only_images_name.append(row["image_name"])

    data = []
    for row in results:
        # Mise en forme du nom de l'image sur le modèle du numéro d'inventaire Musée de France "[année].[lot].[bien](.[sous-inventaire])"
        image_without_path = os.path.basename(row["image_name"]) # Retire le chemin du nom de l'image
        image_without_extension = os.path.splitext(image_without_path) # Retire l'extension
        image_without_last_part = image_without_extension[0].removesuffix("-POS") # Retire le suffixe
        image_final_name = image_without_last_part.replace("_", ".") # Remplace les '_' par des '.'

        data_dict = {
            "accession_number": image_final_name,
            "thesaurus_id": row["thesaurus_id"],
            "confidence_level": f"{row['confidence_level']:.3f}", # Modifier ':.4f' pour changer le nombre de chiffres après la virgule
            "model_name": row["clip_model_name"]
        }

        data.append(data_dict)

    # Regroupement par numéro d'inventaire
    grouped_data = {}
    for row in data:
        accession_number = row["accession_number"]
        if accession_number not in grouped_data:
            grouped_data[accession_number] = {"thesaurus_id" : [], "confidence_level": [], "model_name": []}
        grouped_data[accession_number]["thesaurus_id"].append(row["thesaurus_id"])
        grouped_data[accession_number]["confidence_level"].append(row["confidence_level"])
        grouped_data[accession_number]["model_name"].append(row["model_name"])

    grouped_data_in_row = [] # Une seule ligne porduite par numéro d'inventaire
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

    
    # Production du csv
    print("ECRITURE DU FICHIER CSV...\n")

    with open (file_export_name, "w", newline="", encoding="utf-8") as file:
        writer = csv.DictWriter(file, fieldnames=["accession_number", "thesaurus_id", "confidence_level", "model_name"])
        writer.writeheader()
        writer.writerows(grouped_data_in_row)

    print(f"FICHIER ECRIT : ({file_export_name})")


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