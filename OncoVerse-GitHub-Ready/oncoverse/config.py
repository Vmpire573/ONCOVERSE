import os
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DATA_DIR = ROOT / "data"
MODEL_DIR = ROOT / "models"
DATABASE_URL = os.getenv("DATABASE_URL", f"sqlite:///{DATA_DIR / 'oncoverse.db'}")
MODEL_PATH = MODEL_DIR / "demo_model.joblib"
FEATURES = ["age", "sex", "stage", "tumor_size_mm", "grade", "smoking_status"]
