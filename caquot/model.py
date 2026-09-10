from . import db
import open_clip
import torch


def load_model(connection, cursor):

    print("""+---------------------------------+
| CHARGEMENT D'UN MODELE OPENCLIP |
+---------------------------------+\n""")

    # Sélection du modèle
    while True:
        print("""MODELES DISPONIBLES
----------------------------------------

 [1] CLIP ViT-B/32 XLM-R BASE - LAION-5B [RECOMMANDE POUR MACHINE LEGERE]
     RAPIDE / LEGER / MULTILINGUE
     GPU : RECOMMANDE
     RAM : 8 GO MINIMUM

 [2] CLIP ViT-H/14 F-XLM-R LARGE - LAION-5B
     HAUTE QUALITE / LOURD / MULTILINGUE
     GPU : 8 GO VRAM OU PLUS
     RAM : 16 GO MINIMUM

 [3] AUTRE...

----------------------------------------""")

        selected_model = input("CAQUOT> ")

        if selected_model == "1":
            print("\nMODELE SELECTIONNE :\nCLIP ViT-B/32 XLM-R BASE - LAION-5B")
            model_architecture = "xlm-roberta-base-ViT-B-32"
            model_pretrained_data = "laion5b_s13b_b90k"
            break

        elif selected_model == "2":
            print("\nMODELE SELECTIONNE :\nCLIP ViT-H/14 F-XLM-R LARGE - LAION-5B")
            model_architecture = "xlm-roberta-large-ViT-H-14"
            model_pretrained_data = "frozen_laion5b_s13b_b90k"
            break

        elif selected_model == "3":
            print("\nAUTRE...\n")
            model_architecture = input("ARCHITECTURE (EX. 'XLM-ROBERTA-LARGE-VIT-H-14') : ")
            model_pretrained_data = input("DONNEES DE PRE-ENTRAINEMENT (EX. 'FROZEN_LAION5B_S13B_B90K') : ")
            break

        else:
            print("\n/!\\ ENTREE INVALIDE. REESSAYER.\n")


    # Inscription du modèle en base
    model_name = f"{model_architecture} - {model_pretrained_data}"

    cursor.execute( # Vérification de l'existence du modèle en base
        "SELECT clip_model_id FROM CLIP_MODEL WHERE name = ?",
        (model_name,)
    )
    model_already_in_base = cursor.fetchone()
    if model_already_in_base is None:
        print("INSCRIPTION DU MODELE EN BASE...")
        cursor.execute(
            "INSERT INTO CLIP_MODEL (name, architecture, pretrained_data) VALUES (?, ?, ?)",
            (model_name, model_architecture, model_pretrained_data)
        )
        clip_model_id = cursor.lastrowid
        print("DONNEES DU MODELE INSCRITES EN BASE")
    else:
        clip_model_id = model_already_in_base[0]
        print(f"MODELE '{model_name}' DEJA PRESENT EN BASE")

    # Téléchargement du modèle
    while True:
        print(f"\nTELECHARGER LE MODELE '{model_name}' ? (O/N)")
        download_model = input("CAQUOT> ")
        if download_model.lower() in ["yes", "y", "oui", "o"]:
            break
        elif download_model.lower() in ["no", "n", "non"]:
            print("RETOUR...")
            return
        else:
            print("ENTREE INVALIDE. SAISIR 'O' ou 'N'.")
    
    device = "cuda" if torch.cuda.is_available() else "cpu"
    model, _, preprocess = open_clip.create_model_and_transforms(model_architecture, pretrained=model_pretrained_data, device=device)


def list_model(connection, cursor): 
    print("""+-------------------+
| LISTE DES MODELES |
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
        print("AUCUN MODELE ENREGISTRE\nRETOUR...\n")
        return

    # Print des entrées
    print(f"{len(data)} MODELES\n----------------------------------------\n")
    for index, row in enumerate(data, start=1):
        print(f"   {index}. {row["model_name"]}")
    print("\n----------------------------------------\n")


def delete_model(connection, cursor):
    print("""+---------------------+
| SUPPRIMER UN MODELE |
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
        print("AUCUN MODELE ENREGISTRE\nRETOUR...\n")
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
        model_to_delete_int = int(input("CAQUOT> "))

        model_found = False
        for row in model_list:
            if row["i"] == model_to_delete_int:
                model_to_delete = row["model_name"]
                model_found = True
                break
        else:
            print("/!\\ ENTREE INVALIDE. REESSAYER.\n")
        if model_found:
            break
    
    # Vérification du modèle à supprimer
    while True:
        print(f"""----------------------------------------
       
MODELE SELECTIONNE : '{model_to_delete}'
CONFIRMER LA SUPPRESSION ? (O/N)
LE MODELE ET TOUTES LES DONNEES ASSOCIEES SERONT SUPPRIMES.

----------------------------------------""")
        delete_this_model = input("CAQUOT> ")
        if delete_this_model.lower() in ["yes", "y", "oui", "o"]:
            print("SUPPRESSION...\n")
            break
        elif delete_this_model.lower() in ["no", "n", "non"]:
            print("ANNULATION...\n")
            return
        else:
            print("/!\\ ENTREE INVALIDE. SAISIR 'O' ou 'N'.\n")

    # Suppression du modèle
    cursor.execute("""
        DELETE
        FROM CLIP_MODEL
        WHERE name = ?
        """,
        (model_to_delete,)
    )

    print(f"MODELE '{model_to_delete}' ET DONNEES ASSOCIEES SUPPRIMES.\n")

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
        print("""AUCUN MODELE OPENCLIP ENREGISTRE EN BASE.
VEUILLEZ INTEGRER UN MODELE PUIS REESSAYER.
RETOUR...""")
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
                print(f"MODELE SELECTIONNE '{row["model_name"]}'\n")
                model_found = True
                break
        else:
            print("/!\\ ENTREE INVALIDE. REESSAYER.\n")
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
        model_architecture, pretrained=model_pretrained_data, device=device
    )

    tokenizer = open_clip.get_tokenizer(model_architecture)

    # Return des variables
    return model, preprocess, tokenizer, device, model_name, model_id