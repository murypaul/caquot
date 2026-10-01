from . import db


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