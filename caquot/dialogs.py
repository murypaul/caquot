import tkinter as tk
from tkinter import filedialog
import os


def _dialog(function, **options) -> str:
    root = tk.Tk()
    root.withdraw()
    root.attributes("-topmost", True)
    root.update()
    try:
        result = function(
            parent=root,
            **options
        )
    finally:
        root.destroy()
    if result:
        return os.path.normpath(result)

    return ""


def ask_directory(dialog_title: str) -> str:
    return _dialog(
        filedialog.askdirectory,
        mustexist=True,
        title=dialog_title
    )


def ask_csv_file(dialog_title: str) -> str:
    return _dialog(
        filedialog.askopenfilename,
        filetypes=[("Fichier CSV", "*.csv"), ("Tous les fichiers", "*.*")],
        title=dialog_title
    )


# if __name__ == '__main__':