import os
import sqlite3
import numpy as np

from . import DB_PATH


def get_connection(db_path=DB_PATH):
    os.makedirs(os.path.dirname(db_path), exist_ok=True)
    
    connection = sqlite3.connect(db_path)
    connection.execute("PRAGMA foreign_keys = ON") # Active la vérification des FK
    connection.row_factory = sqlite3.Row
    init_schema(connection)

    cursor = connection.cursor()

    return connection, cursor

def release_connection(connection):
    connection.commit()
    connection.close()


def init_schema(connection):
    connection.execute("""
        CREATE TABLE IF NOT EXISTS THESAURUS (
            thesaurus_name VARCHAR(255),
            thesaurus_id VARCHAR(255) PRIMARY KEY,
            name VARCHAR(255) NOT NULL,
            parent_id VARCHAR(255),
            path TEXT,
            note TEXT
        )
    """)
    connection.execute("""
        CREATE TABLE IF NOT EXISTS IMAGE (
            image_id INTEGER PRIMARY KEY AUTOINCREMENT,
            path TEXT NOT NULL UNIQUE,
            name TEXT NOT NULL,
            idno VARCHAR(255)
        )
    """)
    connection.execute("""
        CREATE TABLE IF NOT EXISTS CLIP_MODEL (
            clip_model_id INTEGER PRIMARY KEY AUTOINCREMENT,
            name VARCHAR(255) NOT NULL,
            architecture VARCHAR(255) NOT NULL,
            pretrained_data VARCHAR(255) NOT NULL,
            weights_path VARCHAR(255)
        )
    """)
    connection.execute("""
        CREATE TABLE IF NOT EXISTS IMAGE_VECTORS (
            image_vectors_id INTEGER PRIMARY KEY AUTOINCREMENT,
            image_id INTEGER NOT NULL,
            vectors BLOB NOT NULL,
            clip_model_id INTEGER NOT NULL,
            FOREIGN KEY (image_id) REFERENCES IMAGE(image_id) ON DELETE CASCADE,
            FOREIGN KEY (clip_model_id) REFERENCES CLIP_MODEL(clip_model_id) ON DELETE CASCADE,
            UNIQUE (image_id, clip_model_id)
        )
    """)
    connection.execute("""
        CREATE TABLE IF NOT EXISTS THESAURUS_VECTORS (
            thesaurus_vectors_id INTEGER PRIMARY KEY AUTOINCREMENT,
            thesaurus_id VARCHAR(255) NOT NULL,
            vectors BLOB NOT NULL,
            clip_model_id INTEGER NOT NULL,
            FOREIGN KEY (thesaurus_id) REFERENCES THESAURUS(thesaurus_id) ON DELETE CASCADE,
            FOREIGN KEY (clip_model_id) REFERENCES CLIP_MODEL(clip_model_id) ON DELETE CASCADE,
            UNIQUE (thesaurus_id, clip_model_id)
        )
    """)
    connection.execute("""
        CREATE TABLE IF NOT EXISTS IMAGE_THESAURUS (
            image_thesaurus_id INTEGER PRIMARY KEY AUTOINCREMENT,
            image_id INTEGER NOT NULL,
            thesaurus_id VARCHAR(255) NOT NULL,
            clip_model_id INTEGER NOT NULL,
            cosinus_similarity FLOAT NOT NULL,
            confidence_level FLOAT,
            exported VARCHAR(32) NOT NULL DEFAULT 'FALSE'
                CHECK (exported IN ('FALSE', 'TRUE')),
            FOREIGN KEY (image_id) REFERENCES IMAGE(image_id) ON DELETE CASCADE,
            FOREIGN KEY (thesaurus_id) REFERENCES THESAURUS(thesaurus_id) ON DELETE CASCADE,
            FOREIGN KEY (clip_model_id) REFERENCES CLIP_MODEL(clip_model_id) ON DELETE CASCADE,
            UNIQUE (image_id, thesaurus_id, clip_model_id)
        )
    """)
    connection.commit()


def vector_to_blob(vector):
    return np.asarray(vector, dtype=np.float32).tobytes()


def blob_to_vector(blob):
    return np.frombuffer(blob, dtype=np.float32)


if __name__ == "__main__":
    connection, cursor = get_connection()
    release_connection(connection)