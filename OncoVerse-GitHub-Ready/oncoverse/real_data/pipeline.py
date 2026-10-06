"""End-to-end real/public-data ETL for OncoVerse."""
from pathlib import Path
import json
import pandas as pd
from .kaggle import download_dataset
from .normalization import normalize_file


def locate_csv(root: str):
    return list(Path(root).rglob("*.csv")) + list(Path(root).rglob("*.CSV"))


def download_and_normalize(dataset: str, raw_root="data/raw", processed_root="data/processed") -> dict:
    manifest = download_dataset(dataset, raw_root)
    csvs = locate_csv(manifest["local_cache"])
    if not csvs:
        raise FileNotFoundError(f"No CSV files found in Kaggle cache for {dataset}: {manifest['local_cache']}")
    # Prefer obvious canonical filenames when several files are present.
    names = {p.name.lower(): p for p in csvs}
    preferred = ["data.csv", "breast cancer metabric.csv", "metabric.csv", "breast_cancer_wisconsin_data.csv"]
    csv_path = next((names[n] for n in preferred if n in names), csvs[0])
    normalized = normalize_file(str(csv_path), dataset)
    dest = Path(processed_root)
    dest.mkdir(parents=True, exist_ok=True)
    output = dest / f"{dataset}_canonical.csv"
    normalized.to_csv(output, index=False)
    report = {"dataset": dataset, "source_csv": str(csv_path), "output": str(output), "rows": len(normalized), "columns": list(normalized.columns), "nulls": normalized.isna().sum().to_dict()}
    (dest / f"{dataset}_etl_report.json").write_text(json.dumps(report, indent=2, default=str))
    return report
