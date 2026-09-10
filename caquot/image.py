from . import db


def delete_images(connection, cursor):
    print("""+------------------------+
    | SUPPRESSION DES IMAGES |
    +------------------------+\n""")

    while True:
        print("""----------------------------------------

 [1] SUPPRIMER LES IMAGES DEJA EXPORTEES (TOUS MODELES)
 [2] SUPPRIMER TOUTES LES IMAGES EN BASE

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

        else:
            print("/!\\ ENTREE INVALIDE. REESSAYER.")

    for image_to_delete in images_to_delete:
        cursor.execute("""
            DELETE
            FROM IMAGE
            WHERE image_id = ?
        """,
        (image_to_delete,)
        )

    print(f"{len(images_to_delete)} IMAGES SUPPRIMEES DE LA BASE")