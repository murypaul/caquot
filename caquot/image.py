from . import db
import re
import os


MDF_PATTERN = re.compile(r"^(\d{4}(?:_\d+){2,3})(?:-[A-Za-z0-9]+)?$")


def delete_images(connection, cursor):
    print("""+------------------------+
| Suppression des images |
+------------------------+\n""")

    while True:
        print("""----------------------------------------

 [1] Supprimer les images déjà exportées (tous modèles confondus)
 [2] Supprimer toutes les images en base

 [0] Retour

----------------------------------------
""")
        response = input("CAQUOT> ")

        if response == "1":
            cursor.execute("""
                SELECT IMAGE.image_id
                FROM IMAGE_THESAURUS
                JOIN IMAGE
                    ON IMAGE_THESAURUS.image_id = IMAGE.image_id
                WHERE IMAGE_THESAURUS.exported = ?
            """,
            ("TRUE",)
            )
            results = cursor.fetchall()

            images_to_delete = []
            for row in results:
                images_to_delete.append(row["image_id"])

            break
        
        elif response == "2":
            cursor.execute("""
                SELECT IMAGE.image_id
                FROM IMAGE
            """)
            results = cursor.fetchall()

            images_to_delete = []
            for row in results:
                images_to_delete.append(row["image_id"])
            
            break

        elif response == "0":
            return

        else:
            print("/!\\ Entrée invalide. Veuillez réessayer.")

    for image_to_delete in images_to_delete:
        cursor.execute("""
            DELETE
            FROM IMAGE
            WHERE image_id = ?
        """,
        (image_to_delete,)
        )

    print(f"{len(images_to_delete)} images supprimées de la base.")


def filename_to_idno(name):
    name = name.strip()
    match = MDF_PATTERN.match(name)
    if match:
        return match.group(1).replace("_", "."), "mdf"
    return name, "fichier"


def list_image_files(path_to_list: str) -> tuple[list[str], list[str]]: # Liste les fichiers d'un dossier
    files_list = os.listdir(path_to_list)
    images = []
    ignored = []
    for file in files_list:
        file_path = os.path.join(path_to_list, file)
        
        if not os.path.isfile(file_path):
            continue

        if not file.lower().endswith(('.jpg', '.png', '.jpeg', '.tif', '.tiff')):
            ignored.append(file)
            continue

        images.append(file_path)
    
    return images, ignored


def register_images(cursor, images: list[str]) -> tuple[list[dict], dict]:
    images_to_return = []
    name_counter = {
        "mdf_counter": 0,
        "file_counter": 0,
        "example_files": []
    }

    for image in images:
        image_no_path = os.path.basename(image)
        image_name, _ = os.path.splitext(image_no_path)
        idno, origin = filename_to_idno(image_name)

        if origin == "mdf":
            name_counter["mdf_counter"] += 1
        else:
            name_counter["file_counter"] += 1
            if len(name_counter["example_files"]) < 3:
                name_counter["example_files"].append(image_name)

        cursor.execute(
            """INSERT INTO IMAGE (path, name, idno) VALUES (?, ?, ?)
                ON CONFLICT(path) DO UPDATE SET name = excluded.name, idno = COALESCE(IMAGE.idno, excluded.idno)
                RETURNING image_id""",
            (image, image_name, idno)
        )

        image_id = cursor.fetchone()["image_id"]

        images_to_return_dict = {
            "image_id": image_id,
            "image_path": image
        }

        images_to_return.append(images_to_return_dict)

    return images_to_return, name_counter


def get_images_from_db(cursor) -> tuple[list[dict], list[str]]:
    # Récupération des images
    cursor.execute(
        "SELECT * FROM IMAGE"
    )
    images_in_db = cursor.fetchall()

    # Insertion des images dans la variable 'images_to_tokenize' et vérification des liens morts
    images_to_return = []
    dead_paths = []
    for image in images_in_db:
        image_path = image["path"]

        if not os.path.exists(image_path):
            dead_paths.append(image_path)
            continue

        images_to_return_dict = {
            "image_id": image["image_id"],
            "image_path": image_path
        }

        images_to_return.append(images_to_return_dict)
    
    return images_to_return, dead_paths


def purge_images(cursor, paths: list[str]):
    for path in paths:
        cursor.execute("""
            DELETE
            FROM IMAGE
            WHERE path = ?
            """,
            (path,)
        )
    

def smoke_test_filename_to_idno():
    cases = [
        ("2026_1_5", "2026.1.5", "mdf"),
        ("2026_1_5_1-POS", "2026.1.5.1", "mdf"),
        ("2026_1_5_1-pos", "2026.1.5.1", "mdf"),
        ("2026_1_5-NEG", "2026.1.5", "mdf"),
        ("IMG_0042", "IMG_0042", "fichier"),
        ("scan_0001", "scan_0001", "fichier"),
        ("MHS_2012_3_14_recto", "MHS_2012_3_14_recto", "fichier"),
        ("2026_1_5 (2)", "2026_1_5 (2)", "fichier"),
        ("2026-1-5", "2026-1-5", "fichier"),
    ]
    for name, expected_idno, expected_origine in cases:
        idno, origine = filename_to_idno(name)
        statut = "OK" if (idno, origine) == (expected_idno, expected_origine) else "ECHEC"
        print(f"{statut} : {name!r} -> ({idno!r}, {origine!r})")

if __name__ == '__main__':
    smoke_test_filename_to_idno()