"""Institutional-data adapter. Expects de-identified CSV and explicit mapping."""
import json
from pathlib import Path
import pandas as pd
from .normalization import CANONICAL_COLUMNS


def normalize_institutional(csv_path: str, mapping_path: str) -> pd.DataFrame:
    df = pd.read_csv(csv_path)
    mapping = json.loads(Path(mapping_path).read_text())
    missing = [k for k in ["patient_id", "age", "sex", "cancer_type"] if k not in mapping]
    if missing:
        raise ValueError(f"Institutional mapping missing: {missing}")
    out = pd.DataFrame(index=df.index)
    for field in CANONICAL_COLUMNS:
        src = mapping.get(field)
        out[field] = df[src] if src in df.columns else pd.NA
    out["source_dataset"] = "institutional_deidentified"
    return out
