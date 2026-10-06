"""TCGA-BRCA multi-omics loader with feature capping for local research demos."""
from pathlib import Path
import pandas as pd


def load_tcga_brca(csv_path: str, max_features: int = 150) -> pd.DataFrame:
    df = pd.read_csv(csv_path)
    id_cols = [c for c in df.columns if str(c).lower() in {"patient_id", "patient", "sample", "id"}]
    numeric = df.select_dtypes(include="number")
    if numeric.empty:
        raise ValueError("TCGA file contains no numeric omics columns")
    variances = numeric.var(numeric_only=True).sort_values(ascending=False)
    keep = list(variances.head(max_features).index)
    result = df[id_cols].copy() if id_cols else pd.DataFrame(index=df.index)
    result = pd.concat([result, df[keep]], axis=1)
    return result
