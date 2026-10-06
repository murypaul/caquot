from caquot import db
from caquot import model
from caquot import thesaurus

import platform
import os
import sqlite3
import torch
import numpy as np
import subprocess


def open_image(image_path):
    if platform.system() == "Linux":
        subprocess.Popen(
            ["xdg-open", image_path],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL    
        )

    elif platform.system() == "Windows":
        os.startfile(image_path)

    elif platform.system() == "Darwin":
        subprocess.Popen(
            ["open", image_path],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL
        )


def nlp_image_text(connection, cursor):
    print("""+---------------------------------------------------------------+
| Recherche 'texte <> images' par Traitement du Langage Naturel |
+---------------------------------------------------------------+\n""")

        # Sélection du modèle
    model_dict = model.select_model(connection, cursor)
    if model_dict is None:
        print("Annulation...\n")
        return

        # Récupération des vecteurs "Images"
    cursor.execute("""
        SELECT IMAGE_VECTORS.image_vectors_id, IMAGE_VECTORS.image_id, IMAGE_VECTORS.vectors, IMAGE_VECTORS.clip_model_id, IMAGE.name, IMAGE.path
        FROM IMAGE_VECTORS
        JOIN IMAGE
            ON IMAGE_VECTORS.image_id = IMAGE.image_id
        WHERE IMAGE_VECTORS.clip_model_id = ?
        """,
        (model_dict["model_id"],)
    )
    img_results = cursor.fetchall()

    images_vectors = []
    for row in img_results:
        img_vectors_blob = row["vectors"]
        img_vectors = db.blob_to_vector(img_vectors_blob)
        
        images_vectors_dict = {
            "image_vectors_id": row["image_vectors_id"],
            "image_id": row["image_id"],
            "image_name": row["name"],
            "image_path": row["path"],
            "vectors": img_vectors,
            "clip_model_id": row["clip_model_id"]
        }
        images_vectors.append(images_vectors_dict)
    print(f"{len(images_vectors)} vecteurs 'IMAGES' récupérés\n")
    if not images_vectors:
        print("Aucune image vectorisée pour le moment. Lancez d'abord Vectorisation -> Vectoriser des images")
        return

    # Chargement du modèle
    print("Chargement du modèle OpenCLIP...")
    result = model.model_loading(connection, cursor, model_dict)
    if result is None:
        print("Annulation...\n")
        return
    clip_model, preprocess, tokenizer, device, model_name, model_id = result

    print("SYSTEME PRÊT")
    print("| ATTENTION :\n| un résultat n'équivaut pas à une correspondance exacte, cela est dû à\n| la méthode de rapprochement (cf. README).\n| cos. sim. = Similarité Cosinus\n")

    while True:
        print("Entrez un mot ou une phrase à comparer aux images :\n'RETOUR' pour arrêter la saisie\n----------------------------------------")

        input_to_tokenize = input("CAQUOT> ")
        if input_to_tokenize.lower() in ["", "cancel", "annuler", "retour"]:
            break

        # Vectorisation
        term_to_tokenize = tokenizer(input_to_tokenize).to(device)
        with torch.no_grad():
            tokenized_term = clip_model.encode_text(term_to_tokenize)

        vector_numpy_term = tokenized_term.cpu().numpy()[0]
        term = {
            "term": input_to_tokenize,
            "vectors": vector_numpy_term
        }

        # Comparaison
        all_candidates = []
        for img in images_vectors:
            similarity_value = np.dot(img["vectors"], term["vectors"]) / (
                np.linalg.norm(img["vectors"]) * np.linalg.norm(term["vectors"])
            )
            all_candidates_dict = {
                "image_id": img["image_id"],
                "image_name": img["image_name"],
                "image_path": img["image_path"],
                "similarity": similarity_value
            }
            all_candidates.append(all_candidates_dict)

        all_candidates.sort(
            key=lambda candidate: candidate["similarity"],
            reverse=True
        )

        candidates_indexed_list = [] 
        rows = []
        for index, candidat in enumerate(all_candidates, start=1):
            candidates_indexed_list_dict = {
                "index": index,
                "image_id": candidat["image_id"],
                "image_name": candidat["image_name"],
                "image_path": candidat["image_path"],
                "similarity": candidat["similarity"]
            }

            candidates_indexed_list.append(candidates_indexed_list_dict)

            row = f"{index}. {candidat["image_name"]} (cos. sim. : {candidat["similarity"]:.2f})"
            rows.append(row)

        print(" ")
        i = 1
        for row in rows:
            i = i+1
            print(row)

            if i > 10:
                break
        print("\n----------------------------------------\n")

        open_image(candidates_indexed_list[0]["image_path"])


def nlp_text_text(connection, cursor):
    print("""+--------------------------------------------------------------+
| Recherche 'texte <> texte' par Traitement du Langage Naturel |
+--------------------------------------------------------------+\n""")

    # Sélection du modèle
    model_dict = model.select_model(connection, cursor)
    if model_dict is None:
        print("Annulation...\n")
        return
    # Sélection du thésaurus
    thesaurus_name = thesaurus.select_thesaurus(connection, cursor)
    if thesaurus_name is None:
        print("Annulation...\n")
        return

    # Récupération des vecteurs "thésaurus"
    cursor.execute("""
        SELECT THESAURUS_VECTORS.thesaurus_vectors_id, THESAURUS_VECTORS.thesaurus_id, THESAURUS_VECTORS.vectors, THESAURUS_VECTORS.clip_model_id, THESAURUS.name
        FROM THESAURUS_VECTORS
        JOIN THESAURUS
            ON THESAURUS_VECTORS.thesaurus_id = THESAURUS.thesaurus_id
        WHERE THESAURUS_VECTORS.clip_model_id = ?
            AND THESAURUS.thesaurus_name = ?
    """,
    (model_dict["model_id"], thesaurus_name)
    )
    th_results = cursor.fetchall()

    thesaurus_vectors = []
    for row in th_results:
        th_vectors_blob = row["vectors"]
        th_vectors = db.blob_to_vector(th_vectors_blob)

        thesaurus_vectors_dict = {
            "thesaurus_vectors_id": row["thesaurus_vectors_id"],
            "thesaurus_id": row["thesaurus_id"],
            "thesaurus_term": row["name"],
            "vectors": th_vectors,
            "clip_model_id": row["clip_model_id"]
        }
        thesaurus_vectors.append(thesaurus_vectors_dict)
    print(f"{len(thesaurus_vectors)} vecteurs 'THESAURUS' récupérés")
    if not thesaurus_vectors:
        print("Aucun thésaurus vectorisé pour le moment. Lancez d'abord Vectorisation -> Vectoriser les thesauri")
        return

    # Chargement du modèle
    print("Chargement du modèle OpenCLIP...")
    result = model.model_loading(connection, cursor, model_dict)
    if result is None:
        print("Annulation...\n")
        return
    clip_model, preprocess, tokenizer, device, model_name, model_id = result

    print("SYSTEME PRÊT")
    print("| ATTENTION :\n| un résultat n'équivaut pas à une correspondance exacte, cela est dû à\n| la méthode de rapprochement (cf. README).\n| cos. sim. = Similarité Cosinus\n")
    
    while True:
        print("Entrez un mot ou une phrase à comparer aux termes du thésaurus :\n'RETOUR' pour arrêter la saisie\n----------------------------------------")

        input_to_tokenize = input("CAQUOT> ")
        if input_to_tokenize.lower() in ["", "cancel", "annuler", "retour"]:
            break

        # Vectorisation
        term_to_tokenize = tokenizer(input_to_tokenize).to(device)
        with torch.no_grad():
            tokenized_term = clip_model.encode_text(term_to_tokenize)

        vector_numpy_term = tokenized_term.cpu().numpy()[0]
        input_term = {
            "term": input_to_tokenize,
            "vectors": vector_numpy_term
        }

        # Comparaison
        all_candidates = []
        for th_term in thesaurus_vectors:
            similarity_value = np.dot(th_term["vectors"], input_term["vectors"]) / (
                np.linalg.norm(th_term["vectors"]) * np.linalg.norm(input_term["vectors"])
            )
            all_candidates_dict = {
                "thesaurus_id": th_term["thesaurus_id"],
                "thesaurus_term": th_term["thesaurus_term"],
                "similarity": similarity_value
            }
            all_candidates.append(all_candidates_dict)

        all_candidates.sort(
            key=lambda candidate: candidate["similarity"],
            reverse=True 
        )
        
        candidates_indexed_list = []
        rows = []
        for index, candidate in enumerate(all_candidates, start=1):
            candidates_indexed_list_dict = {
                "index": index,
                "thesaurus_id": candidate["thesaurus_id"],
                "thesaurus_term": candidate["thesaurus_term"],
                "similarity": candidate["similarity"]
            }

            candidates_indexed_list.append(candidates_indexed_list_dict)

            row = f"{index}. {candidate["thesaurus_term"]} (cos. sim. : {candidate["similarity"]:.2f})"
            rows.append(row)

        print(" ")
        i = 1
        for row in rows:
            i = i+1
            print(row)

            if i > 10:
                break
        print("\n----------------------------------------\n")


if __name__ == '__main__':
    connection, cursor = db.get_connection()

    while True:
        input = ("image ou texte : ")
        if input == "image":
            nlp_image(connection, cursor)
        elif input == "texte":
            nlp_texte(connection, cursor)
        elif input == "q":
            break

    db.release_connection(connection)