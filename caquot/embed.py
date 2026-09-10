from . import db
import csv
import open_clip
import torch
import sqlite3
import os
from . import thesaurus
from . import model
from tkinter import filedialog
from PIL import Image


def thesaurus_embedding(connection, cursor): # Vectorisation du thésaurus
    print("""+---------------------------+
| VECTORISATION 'THESAURUS' |
+---------------------------+\n""")
    
    # Sélection thésaurus/modèle
    thesaurus_name = thesaurus.select_thesaurus(connection, cursor)
    model_name = model.select_model(connection, cursor)

    if thesaurus_name == None:
        return

    if model_name == None:
        return

    # Chargement du modèle
    print("CHARGEMENT DU MODELE OPENCLIP...")
    clip_model, preprocess, tokenizer, device, model_name, model_id = model.model_loading(
        connection, cursor, model_name
    )

    # Récupération des termes du thésaurus et insertion dans un dictionnaire
    print("RECUPERATION DU THESAURUS...")
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
    print("VECTORISATION...")
    total_thesaurus_to_tokenize = len(thesaurus_to_tokenize)
    for index, term in enumerate(thesaurus_to_tokenize, start=1):
        # Vectorisation
        text_to_tokenize = tokenizer([term["text"]]).to(device) # Vectorisation uniquement du texte mis en forme, jamais de l'identifiant

        with torch.no_grad():
            tokenized_text = clip_model.encode_text(text_to_tokenize)
        
        vecteur_numpy_text = tokenized_text.cpu().numpy()[0]
        blobed_tokenized_text = db.vector_to_blob(vecteur_numpy_text)

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
    print(f"{total_thesaurus_vectors} TERMES VECTORISES\n")


def image_embedding(connection, cursor): # Vectorisation des images
    print("""+-----------------------+
| VECTORISATION 'IMAGE' |
+-----------------------+\n""")

    while True:
        print("""----------------------------------------
        
 [1] TRAITER UN NOUVEAU LOT
 [2] TRAITER LES IMAGES EN BASE

----------------------------------------
        """)
        scope_int = int(input("CAQUOT> "))

        if scope_int == 1: # Nouveau lot d'images

            # Sélection images/thésaurus/modèle
            print("""
| /!\\ CONSIDERATIONS TECHNIQUES :
| 
|FORMATS ACCEPTES : JPG / JPEG / PNG
|
| CHEMIN DE L'IMAGE UNIQUEMENT ENREGISTRE EN BASE.
| LE FICHIER ORIGINAL N'EST PAS COPIE.
            """)
            images_path_input = filedialog.askdirectory(mustexist=True, title='Répertoire des images')
            if not images_path_input:
                print("ANNULATION...\n")
                return
            else:
                images_path = f"{images_path_input}/"
            
            # Liste des fichiers images et création d'une liste
            print("RECUPERATION DES IMAGES...")

            images_list = os.listdir(images_path)

            images = []
            for image in images_list:
                image_path = f"{images_path}{image}"
                images.append(image_path)
            
            print(f"DOSSIER : {len(images)} FICHIERS")

            # Enregistrement des liens des images dans la base de données
            images_to_tokenize = []
            for file in images:
                if not file.endswith(('.jpg', '.png', '.jpeg')):
                    continue

                cursor.execute(
                    "INSERT OR REPLACE INTO IMAGE (name) VALUES (?)",
                    (file,)
                )

                image_id = cursor.lastrowid

                images_to_tokenize_dict = {
                    "image_id": image_id,
                    "image_name": file
                }
            
                images_to_tokenize.append(images_to_tokenize_dict)

            break
        
        elif scope_int == 2: # Toutes les images de la base
            print("RECUPERATION DES IMAGES...")

            # Récupération des images
            cursor.execute(
                "SELECT * FROM IMAGE"
            )
            images_in_db = cursor.fetchall()

            # Insertion des images dans la variable 'images_to_tokenize' et vérification des liens morts
            images_to_tokenize = []
            unprocessed_images = []
            for image in images_in_db:
                image_path = image["name"]
                
                if not os.path.exists(image_path):
                    unprocessed_images.append(image_path)
                    continue

                images_to_tokenize_dict = {
                    "image_id": image["image_id"],
                    "image_name": image_path
                }

                images_to_tokenize.append(images_to_tokenize_dict)

            if not images_to_tokenize:
                print("AUCUNE IMAGE EN BASE\nANNULATION...")
                break

            print(f"{len(images_to_tokenize)} IMAGES RECUPERES")

            if unprocessed_images: # Références mortes dans la base
                while True:
                    print(f"{len(unprocessed_images)} IMAGES N'EXISTENT PLUS SUR LE DISQUE.\nLES SUPPRIMER DE LA BASE ? (O/N)")
                    purge = input("CAQUOT> ")

                    if purge.lower() in ['yes', 'y', 'o', 'oui']: # Purge des références mortes
                        for image_name in unprocessed_images:
                            cursor.execute("""
                                DELETE
                                FROM IMAGE
                                WHERE name = ?
                                """,
                                (image_name,)
                            )
                        print("REFERENCES MORTES PURGEES DE LA BASE.\n")
                        break
                    
                    elif purge.lower() in ['no', 'n', 'non']:
                        break

                    else:
                        print("/!\\ ENTREE INVALIDE. SAISIR 'O' ou 'N'.\n")

            break
        

        else:
            print("/!\\ ENTREE INVALIDE. REESSAYER.")

    model_name = model.select_model(connection, cursor)
    if model_name == None:
        return

    # Chargement du modèle
    model_to_use, preprocess, tokenizer, device, model_name, model_id = model.model_loading(connection, cursor, model_name)
    
    # Vectorisation des images
    print(f"VECTORISATION...")
    
    total_images_to_tokenize = len(images_to_tokenize)
    for index, file in enumerate(images_to_tokenize, start=1):
        image = Image.open(file["image_name"])
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
            WHERE IMAGE_VECTORS.clip_model_id = ? AND IMAGE.name = ?
            """,
            (model_id, row["image_name"])
        )
        result = cursor.fetchone()

        if result:
            total += 1
    
    print(f"{total} IMAGES VECTORISEES")