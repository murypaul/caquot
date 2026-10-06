from . import db
import open_clip
import torch
import os
import shutil
from pathlib import Path

from huggingface_hub import scan_cache_dir
from huggingface_hub.utils import logging as hf_logging
from huggingface_hub import constants as hf_constants

from . import MODELS_DIR

# Cache les avertissement HuggingFace
hf_logging.set_verbosity_error()


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

    # Vérification que la configuration existe réellement
    cfg = open_clip.get_pretrained_cfg(model_architecture, model_pretrained_data)
    if not cfg:
        print(f"Aucune configuration connue pour : '{model_architecture}' / '{model_pretrained_data}'\nVérifiez les noms et réessayez\nS'il s'agit d'un modèle local : *[WIP]*")
        return    

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

    weights_path = open_clip.download_pretrained(cfg, cache_dir=MODELS_DIR)
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

        if model_found:
            break
        if user_input.lower() in ['retour', 'quitter', 'cancel', 'quit']:
            return
        print("/!\\ Entrée invalide. Veuillez réessayer\n")
    
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

    cache_dir_abs = os.path.abspath(MODELS_DIR)
    weights_path_abs = os.path.abspath(weights_path)

    # Ne supprime pas le cache si en dehors du dossier de Caquot
    if not Path(weights_path_abs).is_relative_to(cache_dir_abs):
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


def pick_device(): # Vérifie si le GPU est utilisable
    if torch.cuda.is_available():
        try:
            torch.zeros(1, device="cuda")  # test réel : pilote trop ancien, carte non prise en charge...
            name = torch.cuda.get_device_name(0)
            vram = torch.cuda.get_device_properties(0).total_memory / 1024**3
            print(f"Calcul sur la carte graphique : {name} ({vram:.0f} Go)")
            return "cuda"
        except Exception as error:
            print(f"/!\\ Carte graphique détectée mais inutilisable : {error}")
    print("Calcul sur le processeur (plus lent).")
    if torch.__version__.endswith("+cpu") and shutil.which("nvidia-smi"):
        print("| Une carte NVIDIA est présente, mais la version de PyTorch installée")
        print("| ne sait pas l'utiliser. Voir le README, « Carte graphique NVIDIA ».")
    return "cpu"


def _load_clip_components(model_architecture, model_pretrained_data, device):
    clip_model, _, preprocess = open_clip.create_model_and_transforms(
        model_architecture, pretrained=model_pretrained_data, device=device, cache_dir=MODELS_DIR
    )
    clip_model.eval()
    tokenizer = open_clip.get_tokenizer(model_architecture, cache_dir=MODELS_DIR)
    return clip_model, preprocess, tokenizer


def model_loading(connection, cursor, model):
    # Définition des variables
    model_id = model["model_id"]
    model_name = model["model_name"]
    model_architecture = model["model_architecture"]
    model_pretrained_data = model["model_pretrained_data"]

    device = pick_device()

    # 1er essai : sans accès réseau, vérification de présence du modèle sur le disque
    hf_constants.HF_HUB_OFFLINE = True
    try:
        clip_model, preprocess, tokenizer = _load_clip_components(
            model_architecture, model_pretrained_data, device
        )
    except Exception:
        # 2e essai : modèle absent du disque, on autorise son téléchargement
        hf_constants.HF_HUB_OFFLINE = False
        print("Modèle absent du disque : téléchargement en cours...")
        try:
            clip_model, preprocess, tokenizer = _load_clip_components(
                model_architecture, model_pretrained_data, device
            )
        except Exception as error:
            print("/!\\ Le modèle n'a pas pu être chargé.")
            print("| Vérifiez la connexion internet. Sur un réseau d'établissement, le site")
            print("| huggingface.co est peut-être bloqué.")
            print(f"| Erreur : {error}")
            return None

    # Return des variables
    return clip_model, preprocess, tokenizer, device, model_name, model_id