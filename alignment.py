import sqlite3
import numpy as np
import db


print("=== Rapprochement des vecteurs 'image/thésaurus' ===\n")


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


# Modèle CLIP à utiliser pour l'alignement
clip_model_id_for_alignement = int(input("\nIdentifiant du modèle à utiliser : "))


# Récupération des vecteurs 'images'
curseur.execute("SELECT * FROM IMAGE_VECTORS")
results_image_vectors = curseur.fetchall()

images_vectors = []
for row in results_image_vectors:
    if clip_model_id_for_alignement is not None and row["clip_model_id"] != clip_model_id_for_alignement:
        continue

    img_vectors_blob = row["vectors"]
    img_vectors = db.blob_to_vector(img_vectors_blob)

    image_vectors_dict = {
        "image_vectors_id": row["image_vectors_id"],
        "image_id": row["image_id"],
        "vectors": img_vectors,
        "clip_model_id": row["clip_model_id"]
    }
    images_vectors.append(image_vectors_dict)

print(f"\n{len(images_vectors)} vecteurs 'images' récupérés")


# Récupération des vecteurs 'thésaurus"
curseur.execute("SELECT * FROM THESAURUS_VECTORS")
results_thesaurus_vectors = curseur.fetchall()

thesaurus_vectors = []
for row in results_thesaurus_vectors:
    if clip_model_id_for_alignement is not None and row["clip_model_id"] != clip_model_id_for_alignement:
        continue

    th_vectors_blob = row["vectors"]
    th_vectors = db.blob_to_vector(th_vectors_blob)

    thesaurus_vectors_dict = {
        "thesaurus_vectors_id": row["thesaurus_vectors_id"],
        "thesaurus_id": row["thesaurus_id"],
        "vectors": th_vectors,
        "clip_model_id": row["clip_model_id"]
    }
    thesaurus_vectors.append(thesaurus_vectors_dict)

print(f"{len(thesaurus_vectors)} vecteurs 'thésaurus' récupérés")


# Rapprochement vecteur/image
def similarity(candidat):
    return candidat["similarity"]

best_candidats = []
for img in images_vectors:
    results_image = []
    for th in thesaurus_vectors:
        if img["clip_model_id"] != th["clip_model_id"]:
            continue

        similarity_value = np.dot(img["vectors"], th["vectors"]) / (
            np.linalg.norm(img["vectors"]) * np.linalg.norm(th["vectors"])
        )

        results_image.append({
            "image_id": img["image_id"],
            "thesaurus_id": th["thesaurus_id"],
            "clip_model_id": img["clip_model_id"],
            "similarity": similarity_value
        })

    results_image.sort(key=similarity, reverse=True)
    best_candidats.extend(results_image[:10])

print(f"{len(best_candidats)} candidats trouvés... enregistrement sur la base")


# Insertion des meilleurs candidats dans la base
for candidat in best_candidats:
    curseur.execute(
        "INSERT OR REPLACE INTO IMAGE_THESAURUS (image_id, thesaurus_id, clip_model_id, confidence_level) VALUES (?, ?, ?, ?)",
        (candidat["image_id"], candidat["thesaurus_id"], candidat["clip_model_id"], float(candidat["similarity"]))
    )


# Print des résultats
curseur.execute("SELECT * FROM IMAGE_THESAURUS")
results = curseur.fetchall()
print(f"{len(results)} rapprochements enregistrés sur la base")


# Publication des résultats dans la base de données
connexion.commit()


# Fermeture de la connexion
connexion.close()

print("\nProgramme terminé")