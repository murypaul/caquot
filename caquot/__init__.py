from pathlib import Path
import os


BASE_DIR = Path(__file__).resolve().parent.parent

DATA_DIR = BASE_DIR / "data"
MODELS_DIR = DATA_DIR / "models"
DB_PATH = DATA_DIR / "data.db"

os.environ.setdefault("HF_HUB_CACHE", str(MODELS_DIR))
os.environ.setdefault("HF_HUB_DISABLE_SYMLINKS_WARNING", "1")