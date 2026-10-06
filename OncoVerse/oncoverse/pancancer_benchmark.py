"""Published pan-cancer evidence used by the presentation dashboard.

This module intentionally stores only study-level cohort metadata from the published
CancerSEEK work. It does not invent patient-level observations or pretend that the
CancerSEEK individual-level supplementary workbook is bundled.
"""
from __future__ import annotations

from pathlib import Path
import json
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
PATH = ROOT / "data" / "processed" / "pancancer_benchmark.json"

CANCER_TYPES = ["Breast", "Colorectum", "Esophagus", "Liver", "Lung", "Ovary", "Pancreas", "Stomach"]


def load_benchmark() -> dict:
    if not PATH.exists():
        raise FileNotFoundError(PATH)
    return json.loads(PATH.read_text())


def cohort_table() -> pd.DataFrame:
    rows = load_benchmark()["cancer_cohort"]
    return pd.DataFrame(rows)


def stage_table() -> pd.DataFrame:
    rows = load_benchmark()["stage_distribution"]
    return pd.DataFrame(rows)


def sex_age_table() -> pd.DataFrame:
    rows = load_benchmark()["demographics"]
    return pd.DataFrame(rows)
