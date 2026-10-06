import csv
import open_clip
import torch
import sqlite3
import os

from . import db
from . import thesaurus
from . import model
from . import dialogs
from . import image as img
from PIL import Image


def thesaurus_embedding(connection, cursor): # Vectorisation du thésaurus
    print("""+---------------------------+
| Vectorisation 'THESAURUS' |
+---------------------------+\n""")
    
    # Sélection thésaurus/modèle
    thesaurus_name = thesaurus.select_thesaurus(connection, cursor)
    model_dict = model.select_model(connection, cursor)

    if thesaurus_name == None:
        print("Annulation...\n")
        return

    if model_dict == None:
        print("Annulation...\n")
        return

    # Chargement du modèle
    print("Chargement du modèle OpenCLIP...")
    result = model.model_loading(connection, cursor, model_dict)
    if result is None:
        print("Annulation...\n")
        return
    clip_model, preprocess, tokenizer, device, model_name, model_id = result

    # Récupération des termes du thésaurus et insertion dans un dictionnaire
    print("Récupération du thésaurus...")
    cursor.execute(
        """SELECT thesaurus_name, thesaurus_id, name, note, path
        FROM THESAURUS
        WHERE thesaurus_name = ?""",
        (thesaurus_name,)
    )
    results = cursor.fetchall()

    thesaurus_to_tokenize = []
    for row in results:
        if row['note'] and str(row['note']).strip(): # Mise en forme de la 'note' s'il y en a une
            note = f" : {row['note']}"
        else:
            note = ""

        thesaurus_dict = {
            "thesaurus_id": row['thesaurus_id'],
            "text": (f"{row['name']}{note} ({row['path']})") # Mise en forme du texte tokenizé au format "terme : note (chemin)"
        }

        thesaurus_to_tokenize.append(thesaurus_dict)


    # Vectorisation des termes
    print("Vectorisation...")
    total_thesaurus_to_tokenize = len(thesaurus_to_tokenize)
    for index, term in enumerate(thesaurus_to_tokenize, start=1):
        # Vectorisation
        text_to_tokenize = tokenizer([term["text"]]).to(device) # Vectorisation uniquement du texte mis en forme

        with torch.no_grad():
            tokenized_text = clip_model.encode_text(text_to_tokenize)
        
        vector_numpy_text = tokenized_text.cpu().numpy()[0]
        blobed_tokenized_text = db.vector_to_blob(vector_numpy_text)

        cursor.execute(
            "INSERT OR REPLACE INTO THESAURUS_VECTORS (thesaurus_id, vectors, clip_model_id) VALUES (?, ?, ?)",
            (term['thesaurus_id'], blobed_tokenized_text, model_id)
        )

        # Barre de progression
        progress = index / total_thesaurus_to_tokenize
        bar = "#" * int(progress * 30) # '30' largeur de la barre de progression
        void = "_" * (30 - len(bar))
        percentage = (index / total_thesaurus_to_tokenize) * 100

        print(f"\r[{bar}{void}] {percentage:.1f}% | {index}/{total_thesaurus_to_tokenize}", end="", flush=True)
    print()

    cursor.execute("""
        SELECT COUNT(THESAURUS.thesaurus_id) AS total
        FROM THESAURUS
        JOIN THESAURUS_VECTORS
            ON THESAURUS.thesaurus_id = THESAURUS_VECTORS.thesaurus_id
        WHERE THESAURUS.thesaurus_name = ? AND THESAURUS_VECTORS.clip_model_id = ?
        """,
        (thesaurus_name, model_id)
    )
    total_thesaurus_vectors = cursor.fetchone()["total"]
    print(f"{total_thesaurus_vectors} termes vectorisés\n")


def image_embedding(connection, cursor): # Vectorisation des images
    print("""+-----------------------+
| Vectorisation 'IMAGE' |
+-----------------------+\n""")

    while True:
        print("""----------------------------------------
        
 [1] Traiter un nouveau lot
 [2] Traiter les images en base

----------------------------------------
        """)
        user_input = input("CAQUOT> ")
        try:
            scope_int = int(user_input)
        except ValueError:
            scope_int = None

        if scope_int == 1: # Nouveau lot d'images

            # Sélection images/thésaurus/modèle
            print("""
| /!\\ CONSIDERATIONS TECHNIQUES :
| 
|Formats acceptés : '.jpg' / '.jpeg' / '.png' / '.tif' / '.tiff'
|
| Seul le chemin de l'image est enregistré en base.
| Le fichier original n'est pas copié.
            """)
            images_path_input = dialogs.ask_directory("Répertoire des images")
            if not images_path_input:
                print("Annulation...\n")
                return
            
            # Liste des fichiers images et création d'une liste
            print("Récupération des images...")
            images, ignored = img.list_image_files(images_path_input)         
            print(f"Dossier :\n  {len(images)} images\n  {len(ignored)} fichiers ignorés (extension non prise en charge)\n")

            # Enregistrement des images en base
            images_to_tokenize, name_counter = img.register_images(cursor, images)
            if name_counter["file_counter"] >= 1:
                print(f"\n{name_counter['mdf_counter']} numéros d'inventaire reconnus (norme Musée de France).")
                print(f"{name_counter['file_counter']} noms hors norme : le nom du fichier est utilisé tel quel comme identifiant.")
                print(f"   Exemples : {', '.join(name_counter['example_files'])}")

            break
        
        elif scope_int == 2: # Toutes les images de la base
            print("Récupération des images...")

            # Récupération des images et des références mortes
            images_to_tokenize, dead_paths = img.get_images_from_db(cursor)
            if not images_to_tokenize:
                print("Aucune image en base\nAnnulation...")
                break
            print(f"{len(images_to_tokenize)} images récupérées")

            if dead_paths: # Références mortes dans la base
                while True:
                    print(f"{len(dead_paths)} images n'existent plus sur le disque.\nLes supprimer de la base ? (O/N)")
                    purge = input("CAQUOT> ")

                    if purge.lower() in ['yes', 'y', 'o', 'oui']: # Purge des références mortes
                        img.purge_images(cursor, dead_paths)
                        print("Références mortes purgées de la base.\n")
                        break
                    
                    elif purge.lower() in ['no', 'n', 'non']:
                        break

                    else:
                        print("/!\\ Entrée invalide. Saisir 'O' ou 'N'.\n")

            break
        

        else:
            print("/!\\ Entrée invalide. Veuillez réessayer.")

    model_dict = model.select_model(connection, cursor)
    if model_dict == None:
        return

    # Chargement du modèle
    result = model.model_loading(connection, cursor, model_dict)
    if result is None:
        print("Annulation...\n")
        return
    model_to_use, preprocess, tokenizer, device, model_name, model_id = result
    
    # Vectorisation des images
    print(f"Vectorisation...")
    
    total_images_to_tokenize = len(images_to_tokenize)
    for index, file in enumerate(images_to_tokenize, start=1):
        image = Image.open(file["image_path"])
        preprocessed_image = preprocess(image).unsqueeze(0).to(device)

        with torch.no_grad():
            tokenized_image = model_to_use.encode_image(preprocessed_image)

        numpy_vector_image = tokenized_image.cpu().numpy()[0]
        blobed_tokenized_image = db.vector_to_blob(numpy_vector_image)

        # Insertion des données en base
        cursor.execute("""
            INSERT OR REPLACE
            INTO IMAGE_VECTORS (image_id, vectors, clip_model_id)
            VALUES (?, ?, ?)
            """,
            (file['image_id'], blobed_tokenized_image, model_id)
        )

        # Barre de progression
        progress = index / total_images_to_tokenize
        bar = "#" * int(progress * 30) # '30' largeur de la barre de progression
        void = "_" * (30 - len(bar))
        percentage = (index / total_images_to_tokenize) * 100

        print(f"\r[{bar}{void}] {percentage:.1f}% | {index}/{total_images_to_tokenize}", end="", flush=True)
    print()
    
    # Print du nombre d'images vectorisées
    total = 0
    for row in images_to_tokenize:
        cursor.execute("""
            SELECT IMAGE.image_id
            FROM IMAGE
            JOIN IMAGE_VECTORS
                ON IMAGE.image_id = IMAGE_VECTORS.image_id
            WHERE IMAGE_VECTORS.clip_model_id = ? AND IMAGE.path = ?
            """,
            (model_id, row["image_path"])
        )
        result = cursor.fetchone()

        if result:
            total += 1
    
    print(f"{total} images vectorisées\n")