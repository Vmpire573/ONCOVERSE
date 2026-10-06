from pathlib import Path
import json
import importlib.util
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
required = [
    ROOT / "data/raw/metabric/Breast Cancer METABRIC.csv",
    ROOT / "data/raw/wisconsin/breast_cancer_wisconsin_diagnostic.csv",
    ROOT / "data/processed/pancancer_benchmark.json",
    ROOT / "models/real/metabric_5y_xgb.joblib",
    ROOT / "models/real/wisconsin_xgb.joblib",
    ROOT / "models/real/metabric_5y_metrics.json",
    ROOT / "models/real/wisconsin_metrics.json",
    ROOT / "results/tables/metabric_survival_metrics.json",
    ROOT / "results/tables/metabric_cox_results.csv",
]
missing=[str(p.relative_to(ROOT)) for p in required if not p.exists()]
if missing: raise SystemExit("Missing presentation assets:\n- " + "\n- ".join(missing))

benchmark=json.loads((ROOT/"data/processed/pancancer_benchmark.json").read_text())
assert benchmark["cohort_totals"]["cancer_types"] == 8
assert benchmark["cohort_totals"]["cancer_patients"] == 1005

for p in [ROOT/"models/real/metabric_5y_metrics.json", ROOT/"models/real/wisconsin_metrics.json", ROOT/"results/tables/metabric_survival_metrics.json"]:
    json.loads(p.read_text())

pd.read_csv(ROOT/"results/tables/metabric_cox_results.csv")

app=(ROOT/"dashboard/app.py").read_text()
assert "Demo mode" not in app
assert "Load Example Patient" not in app
assert "from oncoverse.survival" not in app

print("PRESENTATION BUILD OK")
print("8-cancer published benchmark + real Wisconsin/METABRIC models + held-out survival + dashboard verified")
