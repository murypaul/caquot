import os
import sqlite3

import numpy as np

DB_PATH = "data/data.db"


def get_connection(db_path=DB_PATH):
    os.makedirs(os.path.dirname(db_path), exist_ok=True)
    conn = sqlite3.connect(db_path)
    conn.execute("PRAGMA foreign_keys = ON")
    return conn


def init_schema(conn):
    conn.execute("""
        CREATE TABLE IF NOT EXISTS THESAURUS (
            thesaurus_id VARCHAR(255) PRIMARY KEY,
            name VARCHAR(255) NOT NULL,
            parent_id VARCHAR(255),
            path TEXT,
            note TEXT
        )
    """)
    conn.execute("""
        CREATE TABLE IF NOT EXISTS IMAGE (
            image_id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL UNIQUE
        )
    """)
    conn.execute("""
        CREATE TABLE IF NOT EXISTS CLIP_MODEL (
            clip_model_id INTEGER PRIMARY KEY AUTOINCREMENT,
            name VARCHAR(255) NOT NULL,
            publication_date DATE
        )
    """)
    conn.execute("""
        CREATE TABLE IF NOT EXISTS IMAGE_VECTORS (
            image_vectors_id INTEGER PRIMARY KEY AUTOINCREMENT,
            image_id INTEGER NOT NULL,
            vectors BLOB NOT NULL,
            clip_model_id INTEGER NOT NULL,
            FOREIGN KEY (image_id) REFERENCES IMAGE(image_id),
            FOREIGN KEY (clip_model_id) REFERENCES CLIP_MODEL(clip_model_id),
            UNIQUE (image_id, clip_model_id)
        )
    """)
    conn.execute("""
        CREATE TABLE IF NOT EXISTS THESAURUS_VECTORS (
            thesaurus_vectors_id INTEGER PRIMARY KEY AUTOINCREMENT,
            thesaurus_id VARCHAR(255) NOT NULL,
            vectors BLOB NOT NULL,
            clip_model_id INTEGER NOT NULL,
            FOREIGN KEY (thesaurus_id) REFERENCES THESAURUS(thesaurus_id),
            FOREIGN KEY (clip_model_id) REFERENCES CLIP_MODEL(clip_model_id),
            UNIQUE (thesaurus_id, clip_model_id)
        )
    """)
    conn.execute("""
        CREATE TABLE IF NOT EXISTS IMAGE_THESAURUS (
            image_thesaurus_id INTEGER PRIMARY KEY AUTOINCREMENT,
            image_id INTEGER NOT NULL,
            thesaurus_id VARCHAR(255) NOT NULL,
            clip_model_id INTEGER NOT NULL,
            confidence_level FLOAT NOT NULL,
            statut VARCHAR(32) NOT NULL DEFAULT 'to_be_checked'
                CHECK (statut IN ('to_be_checked', 'selected', 'rejected', 'manually_selected', 'manually_rejected')),
            FOREIGN KEY (image_id) REFERENCES IMAGE(image_id),
            FOREIGN KEY (thesaurus_id) REFERENCES THESAURUS(thesaurus_id),
            FOREIGN KEY (clip_model_id) REFERENCES CLIP_MODEL(clip_model_id),
            UNIQUE (image_id, thesaurus_id, clip_model_id)
        )
    """)
    conn.commit()


def vector_to_blob(vector):
    return np.asarray(vector, dtype=np.float32).tobytes()


def blob_to_vector(blob):
    return np.frombuffer(blob, dtype=np.float32)


if __name__ == "__main__":
    connection = get_connection()
    init_schema(connection)
    connection.close()
