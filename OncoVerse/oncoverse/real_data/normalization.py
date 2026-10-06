"""Canonical schema and normalization for heterogeneous cancer datasets."""
from pathlib import Path
import re
import pandas as pd

CANONICAL_COLUMNS = [
    "patient_id", "source_dataset", "age", "sex", "cancer_type", "stage",
    "tumor_size_mm", "grade", "smoking_status", "diagnosis_label",
    "survival_months", "survival_event", "site_code", "treatment",
]


def _find(df, candidates):
    lookup = {str(c).strip().lower(): c for c in df.columns}
    for candidate in candidates:
        if candidate.lower() in lookup:
            return lookup[candidate.lower()]
    for c in df.columns:
        normalized = re.sub(r"[^a-z0-9]", "", str(c).lower())
        for candidate in candidates:
            if re.sub(r"[^a-z0-9]", "", candidate.lower()) == normalized:
                return c
    return None


def normalize_wisconsin(df: pd.DataFrame) -> pd.DataFrame:
    id_col = _find(df, ["id"])
    diagnosis = _find(df, ["diagnosis", "diagnosis_label"])
    if not diagnosis:
        raise ValueError("Wisconsin dataset: diagnosis column not found")
    out = pd.DataFrame()
    out["patient_id"] = df[id_col].astype(str) if id_col else [f"WDBC-{i}" for i in range(len(df))]
    out["source_dataset"] = "kaggle_wisconsin"
    out["age"] = pd.NA
    out["sex"] = "Female/Not specified"
    out["cancer_type"] = "Breast"
    out["stage"] = pd.NA
    out["tumor_size_mm"] = pd.NA
    out["grade"] = pd.NA
    out["smoking_status"] = pd.NA
    out["diagnosis_label"] = df[diagnosis].astype(str).str.upper().map({"M":"Malignant","B":"Benign"})
    out["survival_months"] = pd.NA
    out["survival_event"] = pd.NA
    out["site_code"] = "WDBC"
    out["treatment"] = pd.NA
    return out


def normalize_metabric(df: pd.DataFrame) -> pd.DataFrame:
    id_col = _find(df, ["patient_id", "patient id"])
    age = _find(df, ["age_at_diagnosis", "age at diagnosis"])
    stage = _find(df, ["tumor_stage", "tumor stage"])
    size = _find(df, ["tumor_size", "tumor size"])
    grade = _find(df, ["neoplasm_histologic_grade", "grade"])
    survival_months = _find(df, [
        "overall_survival_months", "overall survival (months)",
        "overall survival months", "survival_months", "survival months"
    ])
    survival_status = _find(df, ["overall survival status", "overall_survival_status"])
    death = _find(df, ["death_from_cancer", "death from cancer"])
    sex = _find(df, ["sex"])
    cancer_type = _find(df, ["cancer_type", "cancer_type_detailed"])
    treatment = _find(df, ["chemotherapy", "hormone_therapy"])
    if not id_col or not survival_months:
        raise ValueError("METABRIC dataset: required patient_id/survival_months columns were not found")

    out = pd.DataFrame()
    out["patient_id"] = df[id_col].astype(str)
    out["source_dataset"] = "kaggle_metabric"
    out["age"] = pd.to_numeric(df[age], errors="coerce") if age else pd.NA
    out["sex"] = df[sex].astype(str) if sex else "Female"
    out["cancer_type"] = df[cancer_type].astype(str) if cancer_type else "Breast"
    out["stage"] = df[stage].astype(str) if stage else pd.NA
    out["tumor_size_mm"] = pd.to_numeric(df[size], errors="coerce") if size else pd.NA
    out["grade"] = pd.to_numeric(df[grade], errors="coerce") if grade else pd.NA
    out["smoking_status"] = pd.NA
    out["diagnosis_label"] = "Cancer"
    out["survival_months"] = pd.to_numeric(df[survival_months], errors="coerce")
    if survival_status:
        status = df[survival_status].astype(str).str.strip().str.lower()
        out["survival_event"] = status.eq("deceased").astype("Int64")
    elif death:
        out["survival_event"] = df[death].astype(str).str.lower().str.contains("died of disease", na=False).astype("Int64")
    else:
        out["survival_event"] = pd.NA
    out["site_code"] = "METABRIC"
    out["treatment"] = df[treatment].astype(str) if treatment else pd.NA
    return out


def normalize_file(path: str, dataset: str) -> pd.DataFrame:
    df = pd.read_csv(path)
    if dataset == "wisconsin":
        return normalize_wisconsin(df)
    if dataset == "metabric":
        return normalize_metabric(df)
    raise ValueError(f"No tabular normalizer for {dataset}")
