import os
from . import db
from . import embed
from . import thesaurus
from . import model
from . import alignment
from . import export
from . import image

from nlp import nlp


# Initialisation
def clear_screen(): # Nettoyer la console
    os.system('cls' if os.name == 'nt' else 'clear')


clear_screen()
print(r"""+ =========================================== +
|        ____                        _        |
|      / ___|__ _  __ _ _   _  ___ | |_       |
|     | |   / _` |/ _` | | | |/ _ \| __|      |
|     | |__| (_| | (_| | |_| | (_) | |_       |
|      \____\__,_|\__, |\__,_|\___/ \__|      |
|                    |_|                      |
|                                             |
| Programme d'indexation automatisée d'images |
+ =========================================== +""")

print("\n")

# Définition des menus
def main_menu(): # Menu principal
    while True: # Boucle infinie pour maintenir le menu actif
        print("""MENU PRINCIPAL
----------------------------------------

 [1] Gérer les thésauri
 [2] Gérer les modèles OpenCLIP
 [3] Vectorisation
 [4] Rapprochement / Export
 [5] Recherche en langage naturel (EXPERIMENTAL)
    
 [0] Quitter
 
----------------------------------------""")
        menu = input("CAQUOT> ")

        if menu == "1":
            clear_screen()
            manage_thesauri()

        elif menu == "2":
            clear_screen()
            manage_models()

        elif menu == "3":
            clear_screen()
            embedding_menu()

        elif menu == "4":
            clear_screen()
            alignment_and_export()

        elif menu == "5":
            clear_screen()          
            natural_language_processing_menu()

        elif menu == "0":
            print("\nAu revoir !\n****************************************\n")
            break # Casse la boucle while et ferme propremennt le programme
        else:
            clear_screen()

            print("Option invalide. Veuillez recommencer.")

def manage_thesauri(): # Menu de gestion des thésauri
    while True:
        print("""GERER LES THESAURI
----------------------------------------

 [1] Charger
 [2] Supprimer
 [3] Lister
        
 [0] Retour
 
----------------------------------------""")
        menu = input("CAQUOT> ")

        if menu == "1":
            clear_screen()

            connection, cursor = db.get_connection()
            
            thesaurus.load_thesaurus(connection, cursor)

            db.release_connection(connection)


        elif menu == "2":
            clear_screen()

            connection, cursor = db.get_connection()
            thesaurus.delete_thesaurus(connection, cursor)
            db.release_connection(connection)


        elif menu == "3":
            clear_screen()

            connection, cursor = db.get_connection()
            thesaurus.list_thesaurus(connection, cursor)
            db.release_connection(connection)


        elif menu == "0":
            clear_screen()
            
            break
        else:
            clear_screen()
            
            print("Option invalide. Veuillez recommencer.")

def manage_models(): # Menu de gestion des modèles openCLIP
    while True:
        print("""GERER LES MODELES OPENCLIP
----------------------------------------

 [1] Charger
 [2] Supprimer
 [3] Lister
        
 [0] Retour
 
----------------------------------------""")
        menu = input("CAQUOT> ")

        if menu == "1":
            clear_screen()

            connection, cursor = db.get_connection()
            
            model.load_model(connection, cursor)

            db.release_connection(connection)


        elif menu == "2":
            clear_screen()
            
            connection, cursor = db.get_connection()

            model.delete_model(connection, cursor)

            db.release_connection(connection)


        elif menu == "3":
            clear_screen()
 
            connection, cursor = db.get_connection()
            
            model.list_model(connection, cursor)

            db.release_connection(connection)

        elif menu == "0":
            clear_screen()
            
            break
        else:
            clear_screen()
            
            print("Option invalide. Veuillez recommencer.")

def embedding_menu(): # Menu de vectorisation
    while True:
        print("""VECTORISER
----------------------------------------

 [1] Vectoriser les thesauri
 [2] Vectoriser des images
        
 [0] Retour
 
----------------------------------------""")
        menu = input("CAQUOT> ")

        if menu == "1":
            clear_screen()

            connection, cursor = db.get_connection()
            
            embed.thesaurus_embedding(connection, cursor)

            db.release_connection(connection)


        elif menu == "2":
            clear_screen()
            
            connection, cursor = db.get_connection()
            
            embed.image_embedding(connection, cursor)

            db.release_connection(connection)


        elif menu == "0":
            clear_screen()
            
            break
        else:
            clear_screen()
            
            print("Option invalide. Veuillez recommencer.")


def alignment_and_export(): # Menu de rapprochement et d'export
    while True:
        print("""RAPPROCHEMENT / EXPORT
----------------------------------------

 [1] Rapprochement
 [2] Exporter
 [3] Supprimer les images
        
 [0] Retour

----------------------------------------""")
        menu = input("CAQUOT> ")

        if menu == "1":
            clear_screen()

            connection, cursor = db.get_connection()
            
            alignment.alignement(connection, cursor)

            db.release_connection(connection)


        elif menu == "2":
            clear_screen()

            connection, cursor = db.get_connection()
            
            export.export(connection, cursor)

            db.release_connection(connection)


        elif menu == "3":
            clear_screen()

            connection, cursor = db.get_connection()
            
            image.delete_images(connection, cursor)

            db.release_connection(connection)

        elif menu == "0":
            clear_screen()
            
            break
        else:
            clear_screen()
            
            print("Option invalide. Veuillez recommencer.")


def natural_language_processing_menu(): # Menu de gestion de le recherche en langage naturel
    while True:
        print("""RECHERCHE EN LANGAGE NATUREL
----------------------------------------

 [1] Image / Texte
 [2] Texte / Texte
 [3] Image / Image [EN COURS DE DEVELOPPEMENT]
        
 [0] Retour
 
----------------------------------------""")
        menu = input("CAQUOT> ")

        if menu == "1":
            clear_screen()

            connection, cursor = db.get_connection()
            
            nlp.nlp_image_text(connection, cursor)

            db.release_connection(connection)


        elif menu == "2":
            clear_screen()

            connection, cursor = db.get_connection()

            nlp.nlp_text_text(connection, cursor)
            
            db.release_connection(connection)


        elif menu == "3":
            clear_screen()

            print("Indisponible actuellement\nDéveloppement en cours...")


        elif menu == "0":
            clear_screen()
            
            break
        else:
            clear_screen()
            
            print("Option invalide. Veuillez recommencer.")


if __name__ == '__main__':
    main_menu()