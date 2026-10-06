"""Compatibility entry point for the active real-data survival workflow.

The previous synthetic survival generator has been removed from the active project.
"""
from pathlib import Path
from .real_survival import kaplan_meier_from_metabric

ROOT = Path(__file__).resolve().parents[1]
METABRIC = ROOT / "data/raw/metabric/Breast Cancer METABRIC.csv"

def kaplan_meier(group_by: str = "all"):
    aliases={"all":None,"tumor_stage":"tumor_stage","neoplasm_histologic_grade":"neoplasm_histologic_grade","er_status":"er_status","her2_status":"her2_status"}
    if group_by not in aliases:
        raise ValueError(f"Unsupported grouping field: {group_by}")
    if not METABRIC.exists():
        raise FileNotFoundError(METABRIC)
    return kaplan_meier_from_metabric(str(METABRIC), aliases[group_by])
