import os
from . import db
from . import embed
from . import thesaurus
from . import model
from . import alignment
from . import export
from . import image


# Initialisation
def clear_screen(): # Nettoyer la console
    os.system('cls' if os.name == 'nt' else 'clear')


clear_screen()
print("""+------------------------------------------+
| CAQUOT - INDEXATION AUTOMATISEE D'IMAGES |
+------------------------------------------+\n""")

# Définition des menus
def main_menu(): # Menu principal
    while True: # Boucle infinie pour maintenir le menu actif
        print("""MENU PRINCIPAL
----------------------------------------

 [1] GERER LES THESAURI
 [2] GERER LES MODELES OPENCLIP
 [3] VECTORISATION
 [4] RAPPROCHEMENT / EXPORT
    
 [0] QUITTER
 
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

        elif menu == "0":
            print("\nAU REVOIR !\n****************************************\n")
            break # Casse la boucle while et ferme propremennt le programme
        else:
            clear_screen()

            print("OPTION INVALIDE. VEUILLEZ RECOMMENCER.")

def manage_thesauri(): # Menu de gestion des thésauri
    while True:
        print("""GERER LES THESAURI
----------------------------------------

 [1] CHARGER
 [2] SUPPRIMER
 [3] LISTER
        
 [0] RETOUR
 
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
            
            print("OPTION INVALIDE. VEUILLEZ RECOMMENCER.")

def manage_models(): # Menu de gestion des modèles openCLIP
    while True:
        print("""GERER LES MODELES OPENCLIP
----------------------------------------

 [1] CHARGER
 [2] SUPPRIMER
 [3] LISTER
        
 [0] RETOUR
 
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
            
            print("OPTION INVALIDE. VEUILLEZ RECOMMENCER.")

def embedding_menu(): # Menu de vectorisation
    while True:
        print("""VECTORISER
----------------------------------------

 [1] VECTORISER LES THESAURI
 [2] VECTORISER DES IMAGES
        
 [0] RETOUR
 
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
            
            print("OPTION INVALIDE. VEUILLEZ RECOMMENCER.")


def alignment_and_export(): # Menu de rapprochement et d'export
    while True:
        print("""RAPPROCHEMENT / EXPORT
----------------------------------------

 [1] RAPPROCHEMENT
 [2] EXPORTER
 [3] SUPPRIMER LES IMAGES
        
 [0] RETOUR

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
            
            print("OPTION INVALIDE. VEUILLEZ RECOMMENCER.")


main_menu()