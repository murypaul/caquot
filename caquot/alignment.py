import sqlite3
import numpy as np
from . import db
from . import thesaurus
from . import model


def similarity(candidate):
    return candidate["similarity"]

def alignement(connection, cursor):
    print("""+-----------------------------+
| Rapprochement des vecteurs |
+-----------------------------+\n""")

    # Sélection du thésaurus / modèle
    thesaurus_name = thesaurus.select_thesaurus(connection, cursor)
    if thesaurus_name is None:
        print("Annulation...\n")
        return
    model_dict = model.select_model(connection, cursor)
    if model_dict is None:
        print("Annulation...\n")
        return
    
    # Récupération des vecteurs images
    cursor.execute("""
        SELECT *
        FROM IMAGE_VECTORS
        WHERE clip_model_id = ?
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
            "vectors": img_vectors,
            "clip_model_id": row["clip_model_id"]
        }
        images_vectors.append(images_vectors_dict)
    print(f"{len(images_vectors)} vecteurs 'IMAGES' récupérés")

    # Récupération des vecteurs 'thesaurus'
    cursor.execute("""
        SELECT THESAURUS_VECTORS.*
        FROM THESAURUS_VECTORS
        JOIN THESAURUS
            ON THESAURUS_VECTORS.thesaurus_id = THESAURUS.thesaurus_id
        WHERE THESAURUS.thesaurus_name = ? AND THESAURUS_VECTORS.clip_model_id = ?
        """,
        (thesaurus_name, model_dict["model_id"])
    )
    th_results = cursor.fetchall()

    thesaurus_vectors = []
    for row in th_results:
        th_vectors_blob = row["vectors"]
        th_vectors = db.blob_to_vector(th_vectors_blob)

        thesaurus_vectors_dict = {
            "thesaurus_vectors_id": row["thesaurus_vectors_id"],
            "thesaurus_id": row["thesaurus_id"],
            "vectors": th_vectors,
            "clip_model_id": row["clip_model_id"]
        }
        thesaurus_vectors.append(thesaurus_vectors_dict)
    print(f"{len(thesaurus_vectors)} vecteurs 'THESAURUS' récupérés")


    # Rapprochement vecteurs
    best_candidates = []
    for img in images_vectors:
        
        results_images = []
        
        for th in thesaurus_vectors:
            similarity_value = np.dot(img["vectors"], th["vectors"]) / (
                np.linalg.norm(img["vectors"]) * np.linalg.norm(th["vectors"])
            )

            results_images.append({
                "image_id": img["image_id"],
                "thesaurus_id": th["thesaurus_id"],
                "clip_model_id": img["clip_model_id"],
                "similarity": similarity_value
            })

        results_images.sort(key=similarity, reverse=True)
        best_candidates.extend(results_images[:10]) # Augmenter/diminuer le nombre de candidats ici

    print(f"\nEnregistrement des candidats...")


    # Insertion des meilleurs candidats en base
    i = 0
    for candidate in best_candidates:
        cursor.execute(
            "INSERT OR REPLACE INTO IMAGE_THESAURUS (image_id, thesaurus_id, clip_model_id, cosinus_similarity) VALUES (?, ?, ?, ?)",
            (candidate["image_id"], candidate["thesaurus_id"], candidate["clip_model_id"], float(candidate["similarity"]))
        )
        i = i+1

    print(f"{i} Rapprochements enregistrés\n")
