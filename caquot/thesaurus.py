from . import db
import csv
import os
from tkinter import filedialog


def load_thesaurus(connection, cursor):
    print("""+---------------------------+
| CHARGEMENT D'UN THESAURUS |
+---------------------------+\n""")
    print("|  /!\\ FORMAT ACTUELLEMENT ACCEPTE :")
    print(f"|  {'{:<10} {:<10} {:<10} {:<10} {:<10}'.format('ID', 'LABEL', 'PARENT_ID', 'PATH', 'NOTES')}\n")

    print("CHEMIN DU THESAURUS : ")
    thesaurus_path = filedialog.askopenfilename()
    thesaurus_name = input("NOM DU THESAURUS : ")
    print("\n----------------------------------------\n")

    # Insertion des lignes du csv dans une variable 'thesaurus'
    print(f"RECUPERATION DE '{thesaurus_name}'...")

    thesaurus = []
    with open(thesaurus_path, encoding="utf-8") as file:
        reader = csv.DictReader(file)
        for row in reader:
            thesaurus.append(row)
    

    print(f"\nVERIFIER LE THESAURUS SELECTIONNE. CONFIRMER ? (O/N)")
    
    # Création dynamique du tableau
    keys = ["id", "label", "parent_id", "path", "notes"]
    headers = ["ID", "LABEL", "PARENT_ID", "PATH", "NOTES"]
    list_widths = []
    for key, header in zip(keys, headers):
        lengths = [len(header)] + [len(str(thesaurus_row[key])) for thesaurus_row in thesaurus[:5]]
        list_widths.append(max(lengths))
    widths = [4] + list_widths
    def table_separator(widths):
        bit = ["--" + "-" * w for w in widths]
        return "+" + "+".join(bit) + "+"
    def table_content(values, widths):
        box = []
        for value, w in zip(values, widths):
            box.append("{:<{}}".format(value, w))
        return "| " + " | ".join(box) + " |"
    # Print du tableau
    print(table_separator(widths))
    print(table_content(["RANK", "ID", "LABEL", "PARENT_ID", "PATH", "NOTES"], widths))
    print(table_separator(widths))
    for index, thesaurus_row in enumerate(thesaurus[:5], start=1):
        print(table_content([index, thesaurus_row['id'], thesaurus_row['label'], thesaurus_row['parent_id'], thesaurus_row['path'], thesaurus_row['notes']], widths))
    print(table_content(["6", "...", "", "", "", ""], widths))
    print(table_separator(widths))
    print("\n")

    while True:
        good_thesaurus = input("CAQUOT> ")
        if good_thesaurus.lower() in ["yes", "y", "oui", "o"]:
            print("INSCRIPTION DU THESAURUS EN BASE...")
            break
        elif good_thesaurus.lower() in ["no", "n", "non"]:
            print("ANNULATION...")
            return
        else:
            print("ENTREE INVALIDE. SAISIR 'O' ou 'N'.")

    # Ecriture de 'thesaurus' dans l'insertion SQLite
    for row in thesaurus:
        if row["parent_id"] == "":
           row["parent_id"] = None
        cursor.execute(
            "INSERT OR REPLACE INTO THESAURUS (thesaurus_name, thesaurus_id, name, parent_id, path, note) VALUES (?, ?, ?, ?, ?, ?)",
            (thesaurus_name, row["id"], row["label"], row["parent_id"], row["path"], row["notes"]),
        )

    # Sélection des données de la table THESAURUS et print du nombre d'entrées
    cursor.execute(
        "SELECT * FROM THESAURUS WHERE thesaurus_name = ?",
        (thesaurus_name,)
    )
    resultats = cursor.fetchall()
    print(f"\nENREGISTREMENT TERMINE : {len(resultats)} TERMES AJOUTES EN BASE.\n")
    

def list_thesaurus(connection, cursor):
    print("""+--------------------+
| LISTE DES THESAURI |
+--------------------+\n""")

    # Sélection des données de la table THESAURUS
    cursor.execute(
        """SELECT thesaurus_name AS thesaurus_name, thesaurus_id AS thesaurus_id
        FROM THESAURUS"""
    )
    results = cursor.fetchall()

    # Mise en forme des données
    data = []
    for row in results:
        data_dict = {
            "thesaurus_name": row["thesaurus_name"],
            "thesaurus_id": row["thesaurus_id"]
        }
        data.append(data_dict)
    # Regroupement par nom de thésaurus
    grouped_data = {}
    for row in data:
        thesaurus_name = row["thesaurus_name"]
        if thesaurus_name not in grouped_data:
            grouped_data[thesaurus_name] = {"thesaurus_id": []}
        grouped_data[thesaurus_name]["thesaurus_id"].append(row["thesaurus_id"])
    # Print des entrées par nom de thésaurus
    list_data = []
    for row in grouped_data:
        data_dict = {
            "thesaurus_name": row,
            "thesaurus_sum": len(grouped_data[row]["thesaurus_id"])
        }
        list_data.append(data_dict)
    print(f"{len(grouped_data)} THESAURI\n----------------------------------------\n")
    for index, row in enumerate(list_data, start=1):
        print(f"   {index}. {row["thesaurus_name"]} ({row["thesaurus_sum"]} termes)")
    print("\n----------------------------------------\n")


def delete_thesaurus(connection, cursor):
    print("""+------------------------+
| Supprimer un thésaurus |
+------------------------+\n""")

    # Sélection des données de la table THESAURUS
    cursor.execute(
        """SELECT thesaurus_name AS thesaurus_name, thesaurus_id AS thesaurus_id
        FROM THESAURUS"""
    )
    results = cursor.fetchall()

    # Mise en forme des données
    data = []
    for row in results:
        data_dict = {
            "thesaurus_name": row["thesaurus_name"],
            "thesaurus_id": row["thesaurus_id"]
        }
        data.append(data_dict)
    # Regroupement par nom de thésaurus
    grouped_data = {}
    for row in data:
        thesaurus_name = row["thesaurus_name"]
        if thesaurus_name not in grouped_data:
            grouped_data[thesaurus_name] = {"thesaurus_id": []}
        grouped_data[thesaurus_name]["thesaurus_id"].append(row["thesaurus_id"])
    # Print des entrées par nom de thésaurus
    list_data = []
    for row in grouped_data:
        data_dict = {
            "thesaurus_name": row,
            "thesaurus_sum": len(grouped_data[row]["thesaurus_id"])
        }
        list_data.append(data_dict)
    if len(grouped_data) == 0:
        print("AUCUN THESAURUS ENREGISTRE\nANNULATION...\n")
        return
    while True:
        print(f"THESAURUS A SUPPRIMER\n----------------------------------------\n")
        thesaurus_list = []
        for index, row in enumerate(list_data, start=1):
            thesaurus_list_dict = {
                "i": index,
                "thesaurus_name": row["thesaurus_name"]
            }
            print(f"   {index}. {row["thesaurus_name"]} ({row["thesaurus_sum"]} TERMES)")
            thesaurus_list.append(thesaurus_list_dict)   
        print("\n----------------------------------------")
        thesaurus_to_delete_int = int(input("CAQUOT> "))

        thesaurus_found = False
        for row in thesaurus_list:
            if row["i"] == thesaurus_to_delete_int:
                thesaurus_to_delete = row["thesaurus_name"]
                thesaurus_found = True
                break
        else:
            print("/!\\ ENTREE INVALIDE. REESAYER.\n")
        if thesaurus_found:
            break

    while True:
        print(f"""----------------------------------------

THESAURUS SELECTIONNE : '{thesaurus_to_delete}'
CONFIRMER LA SUPPRESSION ? (O/N)
LE THESAURUS ET TOUTES LES DONNEES ASSOCIEES SERONT SUPPRIMES.

----------------------------------------""")
        delete_this_thesaurus = input("CAQUOT> ")
        if delete_this_thesaurus.lower() in ["yes", "y", "oui", "o"]:
            print("SUPPRESSION...\n")
            break
        elif delete_this_thesaurus.lower() in ["no", "n", "non"]:
            print("ANNULATION...\n")
            return
        else:
            print("/!\\ ENTREE INVALIDE. SAISIR 'O' ou 'N'.\n")

    cursor.execute("""
        DELETE
        FROM THESAURUS
        WHERE thesaurus_name = ?
        """,
        (thesaurus_to_delete,)
    )

    print(f"THESAURUS '{thesaurus_to_delete}' ET DONNEES ASSOCIEES SUPPRIMES.\n")


def select_thesaurus(connection, cursor):
    # Sélection des données de la table THESAURUS
    cursor.execute(
        """SELECT thesaurus_name AS thesaurus_name, thesaurus_id AS thesaurus_id
        FROM THESAURUS"""
    )
    results = cursor.fetchall()

    # Retourne 'thesaurus = None' si pas de données
    if not results:
        thesaurus = None
        print("""AUCUN THESAURUS ENREGISTRE EN BASE.
VEUILLEZ INTEGRER UN THESAURUS PUIS REESSAYER.
RETOUR...""")
        return thesaurus

    # Mise en forme des données
    data = []
    for row in results:
        data_dict = {
            "thesaurus_name": row["thesaurus_name"],
            "thesaurus_id": row["thesaurus_id"]
        }
        data.append(data_dict)
    
    # Regroupement par nom de thésaurus
    grouped_data = {}
    for row in data:
        thesaurus_name = row["thesaurus_name"]
        if thesaurus_name not in grouped_data:
            grouped_data[thesaurus_name] = {"thesaurus_id": []}
        grouped_data[thesaurus_name]["thesaurus_id"].append(row["thesaurus_id"]) 
    
    # Sélection du thésaurus
    print(f"SELECTION D'UN THESAURUS\n----------------------------------------\n")
    thesaurus_list = []
    for index, row in enumerate(grouped_data, start=1):
        print(f"   {index}. {row} ({len(grouped_data[row]['thesaurus_id'])} TERMES)")
        thesaurus_list_dict = {
            "i": index,
            "thesaurus_name": row
        }
        thesaurus_list.append(thesaurus_list_dict)
    print("\n----------------------------------------")

    while True:
        user_input = input("CAQUOT> ")
        try:
            selected_thesaurus_int = int(user_input)
        except ValueError:
            selected_thesaurus_int = None


        thesaurus_found = False
        for row in thesaurus_list:
            if row["i"] == selected_thesaurus_int:
                thesaurus = row["thesaurus_name"]
                print(f"THESAURUS SELECTIONNE : '{thesaurus}'\n")
                thesaurus_found = True
                break
        else:
            print("/!\\ ENTREE INVALIDE. REESSAYER.\n")
        if thesaurus_found:
            break

    return thesaurus