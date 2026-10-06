from pathlib import Path
import json
import numpy as np
import pandas as pd
from fastapi.testclient import TestClient

from oncoverse.api import app
from oncoverse.pancancer_benchmark import load_benchmark, cohort_table
from oncoverse.real_survival import kaplan_meier_from_metabric

ROOT = Path(__file__).resolve().parents[1]


def test_pancancer_benchmark_is_published_summary_only():
    b = load_benchmark()
    assert b["cohort_totals"]["cancer_patients"] == 1005
    assert b["cohort_totals"]["healthy_controls"] == 812
    assert len(cohort_table()) == 8
    assert b["interpretation"].startswith("These values describe the published")


def test_real_assets_exist():
    assert (ROOT / "data/raw/wisconsin/breast_cancer_wisconsin_diagnostic.csv").exists()
    assert (ROOT / "data/raw/metabric/Breast Cancer METABRIC.csv").exists()
    assert (ROOT / "models/real/wisconsin_xgb.joblib").exists()
    assert (ROOT / "models/real/metabric_5y_xgb.joblib").exists()


def test_wisconsin_metrics_include_baseline():
    m = json.loads((ROOT / "models/real/wisconsin_metrics.json").read_text())
    assert "majority_class_baseline_accuracy" in m
    assert m["accuracy"] >= 0
    assert 0 <= m["roc_auc"] <= 1


def test_survival_uses_real_metabric_data():
    path = ROOT / "data/raw/metabric/Breast Cancer METABRIC.csv"
    result = kaplan_meier_from_metabric(str(path))
    assert result["dataset"].startswith("Breast Cancer METABRIC")
    assert result["curves"][0]["n"] > 1000
    assert result["curves"][0]["points"][0]["survival"] == 1.0


def test_api_health_and_real_routes():
    with TestClient(app) as client:
        assert client.get("/health").status_code == 200
        assert client.get("/health").json()["clinical_use"] is False
        assert client.get("/analytics/pancancer-benchmark").status_code == 200
        assert client.get("/analytics/survival?group_by=wrong").status_code == 400


def test_dashboard_has_no_demo_mode():
    text = (ROOT / "dashboard/app.py").read_text()
    assert "Demo mode" not in text
    assert "Load Example Patient" not in text
    assert "from oncoverse.survival" not in text
