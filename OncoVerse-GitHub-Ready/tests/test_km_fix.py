from pathlib import Path

from oncoverse.real_survival import kaplan_meier_from_metabric

METABRIC = Path(__file__).resolve().parents[1] / "data" / "raw" / "metabric" / "Breast Cancer METABRIC.csv"


def test_kaplan_meier_handles_missing_categorical_groups():
    result = kaplan_meier_from_metabric(str(METABRIC), "tumor_stage")
    assert result["curves"]
    assert all(curve["n"] > 0 for curve in result["curves"])
    assert any(curve["group"] == "Missing" for curve in result["curves"])
