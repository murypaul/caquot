from . import db
import open_clip
import torch
import os
from huggingface_hub import scan_cache_dir
from huggingface_hub.utils import logging as hf_logging


# Cache les avertissement HuggingFace
hf_logging.set_verbosity_error()

# Dossier où sont stockés les poids des modèles
MODELS_CACHE_DIR = "data/models"


def load_model(connection, cursor):

    print("""+---------------------------------+
| Chargement d'un modèle OpenCLIP |
+---------------------------------+\n""")

    # Sélection du modèle
    while True:
        print("""MODELES DISPONIBLES
----------------------------------------

 [1] CLIP ViT-B/32 XLM-R BASE - LAION-5B [RECOMMANDE POUR MACHINE LEGERE]
     Rapide / Léger / Multilingue
     GPU : recommandé
     RAM : 8 Go minimum

 [2] CLIP ViT-H/14 F-XLM-R LARGE - LAION-5B
     Haute qualité / Lourd / Multilingue
     GPU : 8 Go VRAM ou plus
     RAM : 16 Go minimum

 [3] Autre...

----------------------------------------""")

        selected_model = input("CAQUOT> ")

        if selected_model == "1":
            print("\nModèle sélectionné :\nCLIP ViT-B/32 XLM-R BASE - LAION-5B")
            model_architecture = "xlm-roberta-base-ViT-B-32"
            model_pretrained_data = "laion5b_s13b_b90k"
            break

        elif selected_model == "2":
            print("\nModèle sélectionné :\nCLIP ViT-H/14 F-XLM-R LARGE - LAION-5B")
            model_architecture = "xlm-roberta-large-ViT-H-14"
            model_pretrained_data = "frozen_laion5b_s13b_b90k"
            break

        elif selected_model == "3":
            print("\nAUTRE...\n")
            model_architecture = input("Architecture (ex. 'xlm-roberta-large-ViT-H-14') : ")
            model_pretrained_data = input("Données de pré-entrainement (ex. 'frozen_laion5b_s13b_b90k') : ")
            break

        elif selected_model.lower() in ['retour', 'quitter', 'cancel', 'quit']:
            return

        else:
            print("/!\\ Entrée invalide. Veuillez réessayer.\n")


    # Inscription du modèle en base
    model_name = f"{model_architecture} - {model_pretrained_data}"

    cursor.execute( # Vérification de l'existence du modèle en base
        "SELECT clip_model_id FROM CLIP_MODEL WHERE name = ?",
        (model_name,)
    )
    model_already_in_base = cursor.fetchone()
    if model_already_in_base is None:
        print("Inscription du modèle en base...")
        cursor.execute(
            "INSERT INTO CLIP_MODEL (name, architecture, pretrained_data) VALUES (?, ?, ?)",
            (model_name, model_architecture, model_pretrained_data)
        )
        clip_model_id = cursor.lastrowid
        print("Données du modèle inscrites en base")
    else:
        clip_model_id = model_already_in_base[0]
        print(f"Modèle '{model_name}' déjà présent en base")

    # Téléchargement du modèle
    while True:
        print(f"\nTélécharger le modèle '{model_name}' ? (O/N)")
        input_download_model = input("CAQUOT> ")
        if input_download_model.lower() in ["yes", "y", "oui", "o"]:
            weights_path = download_model(model_architecture, model_pretrained_data)
            
            if not weights_path:
                print(f"Aucune configuration connue pour : '{model_architecture}' / '{model_pretrained_data}'\nVérifiez les noms et réessayez\nS'il s'agit d'un modèle local : *[WIP]*") #TODO Gérer modèle local
                return
            else:
                cursor.execute(
                    "UPDATE CLIP_MODEL SET weights_path = ? WHERE name = ?",
                    (weights_path, model_name)
                )
            return
        elif input_download_model.lower() in ["no", "n", "non"]:
            print("Retour...")
            return
        else:
            print("Entrée invalide. Saisir 'O' ou 'N'.")


def download_model(model_architecture, model_pretrained_data):
    # Récupère la config du modèle
    cfg = open_clip.get_pretrained_cfg(model_architecture, model_pretrained_data)

    if not cfg:
        weights_path = None
        return weights_path

    weights_path = open_clip.download_pretrained(cfg, cache_dir=MODELS_CACHE_DIR)
    return weights_path


def list_model(connection, cursor): 
    print("""+-------------------+
| Liste des modèles |
+-------------------+\n""")

    # Sélection des données de la table CLIP_MODEL
    cursor.execute(
        """SELECT name AS model_name, clip_model_id AS model_id FROM CLIP_MODEL"""
    )
    results = cursor.fetchall()

    # Mise en forme des données
    data = []
    for row in results:
        data_dict = {
            "model_name": row["model_name"],
            "model_id": row["model_id"]
        }
        data.append(data_dict)
    if len(data) == 0:
        print("Aucun modèle enregistré\nRetour...\n")
        return

    # Print des entrées
    print(f"{len(data)} MODELES\n----------------------------------------\n")
    for index, row in enumerate(data, start=1):
        print(f"   {index}. {row["model_name"]}")
    print("\n----------------------------------------\n")


def delete_model(connection, cursor):
    print("""+---------------------+
| Supprimer un modèle |
+---------------------+\n""")

    # Sélection des données de la table CLIP_MODEL
    cursor.execute("SELECT name AS model_name FROM CLIP_MODEL")
    results = cursor.fetchall()

    # Mise en forme des données
    data = []
    for row in results:
        data_dict = {
            "model_name": row["model_name"],
        }
        data.append(data_dict)
    if len(data) == 0:
        print("Aucun modèle enregistré\nRetour...\n")
        return

    # Sélection du modèle à supprimer
    while True:
        print(f"""MODELE A SUPPRIMER
----------------------------------------""")
        model_list = []
        for index, row in enumerate(data, start=1):
            model_list_dict = {
                "i": index,
                "model_name": row["model_name"]
            }
            print(f"    {index}. {row["model_name"]}")
            model_list.append(model_list_dict)
        print("\n----------------------------------------")
        user_input = input("CAQUOT> ")
        try:
            model_to_delete_int = int(user_input)
        except ValueError:
            model_to_delete_int = None

        model_found = False
        for row in model_list:
            if row["i"] == model_to_delete_int:
                model_to_delete = row["model_name"]
                model_found = True
                break
        if user_input.lower() in ['retour', 'quitter', 'cancel', 'quit']:
            return
        else:
            print("/!\\ Entrée invalide. Veuillez réessayer\n")
        if model_found:
            break
    
    # Vérification du modèle à supprimer
    while True:
        print(f"""----------------------------------------
       
Modèle sélectionné : '{model_to_delete}'
Confirmer la suppression ? (O/N)
Le modèle et toutes les données associées seront supprimés.

----------------------------------------""")
        delete_this_model = input("CAQUOT> ")
        if delete_this_model.lower() in ["yes", "y", "oui", "o"]:
            print("Suppression...\n")
            break
        elif delete_this_model.lower() in ["no", "n", "non"]:
            print("Annulation...\n")
            return
        else:
            print("/!\\ Entrée invalide. Saisir 'O' ou 'N'.\n")


    # Récupération du chemin des poids du modèle
    cursor.execute("""
        SELECT weights_path
        FROM CLIP_MODEL
        WHERE name = ?
        """,
        (model_to_delete,)
    )
    result_weights_path = cursor.fetchone()
    if result_weights_path:
        weights_path = result_weights_path[0]
        delete_model_weights(weights_path)


    # Suppression du modèle
    cursor.execute("""
        DELETE
        FROM CLIP_MODEL
        WHERE name = ?
        """,
        (model_to_delete,)
    )

    print(f"Modèle '{model_to_delete}' et données associées supprimées.\n")


def delete_model_weights(weights_path):
    if not weights_path:
        return

    cache_dir_abs = os.path.abspath(MODELS_CACHE_DIR)
    weights_path_abs = os.path.abspath(weights_path)

    # Ne supprime pas le cache si en dehors du dossier de Caquot
    if not weights_path_abs.startswith(cache_dir_abs): 
        return

    # Cas HuggingFaceHub : utilise l'API HuggingFace pour supprimer les symlinks et blobs
    cache_info = scan_cache_dir(cache_dir_abs)
    for repo in cache_info.repos:
        for revision in repo.revisions:
            for file in revision.files:
                if os.path.abspath(file.file_path) == weights_path_abs:
                    strategy = cache_info.delete_revisions(revision.commit_hash)
                    strategy.execute()
                    return

    # Cas 'fichier plat' : téléchargement par URL directe
    if os.path.isfile(weights_path_abs):
        os.remove(weights_path_abs)


def select_model(connection, cursor):
    # Sélection des données de la table CLIP_MODEL
    cursor.execute(
        """SELECT clip_model_id AS model_id, name AS model_name, architecture AS model_architecture, pretrained_data AS model_pretrained_data
        FROM CLIP_MODEL"""
    )
    results = cursor.fetchall()

    # Retourne 'model = None' si pas de données
    if not results:
        model = None
        print("""Aucun modèle OpenCLIP enregistré en base.
Veuillez suivre la procédure pour intégrer un modèle et réessayer.
Retour...""")
        return model

    # Mise en forme des données
    data = []
    for row in results:
        data_dict = {
            "model_id": row["model_id"],
            "model_name": row["model_name"],
            "model_architecture": row["model_architecture"],
            "model_pretrained_data": row["model_pretrained_data"]
        }
        data.append(data_dict)
    
    # Sélection du modèle
    print(f"SELECTION D'UN MODELE OPENCLIP\n----------------------------------------\n")
    model_list = []
    for index, row in enumerate(data, start=1):
        print(f"   {index}. {row["model_name"]}")
        model_list_dict = {
            "i": index,
            "model_id": row["model_id"],
            "model_name": row["model_name"],
            "model_architecture": row["model_architecture"],
            "model_pretrained_data": row["model_pretrained_data"]
        }
        model_list.append(model_list_dict)
    print("\n----------------------------------------")

    if len(model_list) == 1: # Si un seul modèle disponible alors sélection de celui-ci
        print("Un seul modèle enregistré")
        print(f"Modèle sélectionné '{model_list[0]["model_name"]}'\n")
        model = {
            "model_id": model_list[0]["model_id"],
            "model_name": model_list[0]["model_name"],
            "model_architecture": model_list[0]["model_architecture"],
            "model_pretrained_data": model_list[0]["model_pretrained_data"]
        }
        return model

    while True:        
        user_input = input("CAQUOT> ")
        try:
            selected_model_int = int(user_input)
        except ValueError:
            selected_model_int = None

        model_found = False
        for row in model_list:
            if row["i"] == selected_model_int:
                model = {
                    "model_id": row["model_id"],
                    "model_name": row["model_name"],
                    "model_architecture": row["model_architecture"],
                    "model_pretrained_data": row["model_pretrained_data"]
                }
                print(f"Modèle sélectionné '{row["model_name"]}'\n")
                model_found = True
                break
        else:
            print("/!\\ Entrée invalide. Veuillez réessayer.\n")
        if model_found:
            break

    return model


def model_loading(connection, cursor, model):
    # Définition des variables
    model_id = model["model_id"]
    model_name = model["model_name"]
    model_architecture = model["model_architecture"]
    model_pretrained_data = model["model_pretrained_data"]

    device = "cuda" if torch.cuda.is_available() else "cpu"

    model, _, preprocess = open_clip.create_model_and_transforms(
        model_architecture, pretrained=model_pretrained_data, device=device, cache_dir=MODELS_CACHE_DIR
    )

    tokenizer = open_clip.get_tokenizer(model_architecture)

    # Return des variables
    return model, preprocess, tokenizer, device, model_name, model_id