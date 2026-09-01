import db
import csv
import open_clip
import torch
import sqlite3
import os

from PIL import Image


# Initialisation
print("=== Vectorisation 'image/thésaurus' ===\n")

thesaurus_path = input("Chemin du thésaurus : ")
images_path = input("Chemin des images : ")

print("\n------")

# Chargement du modèle
device = "cuda" if torch.cuda.is_available() else "cpu"

model, _, preprocess = open_clip.create_model_and_transforms(
    "xlm-roberta-large-ViT-H-14", pretrained="frozen_laion5b_s13b_b90k", device=device
)
tokenizer = open_clip.get_tokenizer("xlm-roberta-large-ViT-H-14")


# Ouverture de la connexion
connexion = db.get_connection()
connexion.row_factory = sqlite3.Row
db.init_schema(connexion)
curseur = connexion.cursor()


# Vérification de l'existence du modèle CLIP dans la base de données
clip_model_name = "xlm-roberta-large-ViT-H-14 / frozen_laion5b_s13b_b90k"

curseur.execute(
    "SELECT clip_model_id FROM CLIP_MODEL WHERE name = ?",
    (clip_model_name,)
)
clip_in_db = curseur.fetchone()
if clip_in_db == None:
    curseur.execute("INSERT INTO CLIP_MODEL (name, publication_date) VALUES (?, ?)",
    (clip_model_name, "2021")
    )
    clip_model_id = curseur.lastrowid
else:
    clip_model_id = clip_in_db[0]

print(f"Modèle CLIP : {clip_model_name} (id {clip_model_id})\n")


# Insertion des lignes du csv dans une variable 'thesaurus'
print("Récupération du thésaurus...")

thesaurus = []
with open(thesaurus_path, encoding="utf-8") as fichier:
    reader = csv.DictReader(fichier)
    for row in reader:
        thesaurus.append(row)


# Inscription des lignes de la variable 'thesaurus' dans la commande d'insertion SQLite
for row in thesaurus:
    if row["parent_id"] == "":
        row["parent_id"] = None
    curseur.execute(
        "INSERT OR REPLACE INTO THESAURUS (thesaurus_id, name, parent_id, path, note) VALUES (?, ?, ?, ?, ?)",
        (row["id"], row["label"], row["parent_id"], row["path"], row["notes"]),
    )


# Sélection de toutes les données de la table THESAURUS et print du nombre d'entrées
curseur.execute("SELECT * FROM THESAURUS")
resultats = curseur.fetchall()
print(f"{len(resultats)} termes dans le thésaurus")


# Récupération des termes du thésaurus et insertion dans un dictionnaire
curseur.execute("SELECT thesaurus_id, name, note, path FROM THESAURUS")
results = curseur.fetchall()

thesaurus_to_tokenize = []
for row in results:
    if row['note'] and str(row['note']).strip():
        note = f" : {row['note']}"
    else:
        note = ""

    thesaurus_dict = {
        "thesaurus_id": row['thesaurus_id'],
        "text": (f"{row['name']}{note} ({row['path']})")
    }

    thesaurus_to_tokenize.append(thesaurus_dict)


# Vectorisation des termes du vocabulaire
for term in thesaurus_to_tokenize:
    text_to_tokenize = tokenizer([term["text"]]).to(device)

    with torch.no_grad():
        tokenized_text = model.encode_text(text_to_tokenize)
    
    vecteur_numpy_text = tokenized_text.cpu().numpy()[0]
    blobed_tokenized_text = db.vector_to_blob(vecteur_numpy_text)

    curseur.execute(
        "INSERT OR REPLACE INTO THESAURUS_VECTORS (thesaurus_id, vectors, clip_model_id) VALUES (?, ?, ?)",
        (term['thesaurus_id'], blobed_tokenized_text, clip_model_id)
    )

curseur.execute("SELECT * FROM THESAURUS_VECTORS")
resultats = curseur.fetchall()
print(f"{len(resultats)} termes du thésaurus vectorisés\n")


# Liste des fichiers images et création d'une liste
print("Récupération des images...")

images_list = os.listdir(images_path)

images = []
for image in images_list:
    image_path = f"{images_path}/{image}"
    images.append(image_path)

print(f"{len(images)} fichiers dans le dossier")

# Insertion des références des images dans la base de données
for file in images:
    if not file.endswith(('.jpg', '.png', '.jpeg')):
        continue

    curseur.execute(
        "INSERT OR IGNORE INTO IMAGE (name) VALUES (?)",
        (file,)
    )

curseur.execute("SELECT * FROM IMAGE")
results_images = curseur.fetchall()


# Récupération des images et insertion dans un dictionnaire
curseur.execute("SELECT * FROM IMAGE")
results_images_in_db = curseur.fetchall()

images_to_tokenize = []
for image in results_images_in_db:
    image_dict = {
        "image_id": image["image_id"],
        "name": image["name"]
    }

    images_to_tokenize.append(image_dict)


# Vectorisation des images
for file in images_to_tokenize:
    image = Image.open(file["name"])
    preprocessed_image = preprocess(image).unsqueeze(0).to(device)

    with torch.no_grad():
        tokenized_image = model.encode_image(preprocessed_image)
    
    vecteur_numpy_image = tokenized_image.cpu().numpy()[0]
    blobed_tokenized_image = db.vector_to_blob(vecteur_numpy_image)

    curseur.execute(
        "INSERT OR REPLACE INTO IMAGE_VECTORS (image_id, vectors, clip_model_id) VALUES (?, ?, ?)",
        (file['image_id'], blobed_tokenized_image, clip_model_id)
    )

curseur.execute("SELECT * FROM IMAGE_VECTORS")
resultats = curseur.fetchall()
print(f"{len(resultats)} images vectorisées")


# Publication des résultats dans la base de données
connexion.commit()


# Fermeture de la connexion
connexion.close()


print("\nProgramme terminé")