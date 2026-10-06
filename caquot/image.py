from . import db
import re


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