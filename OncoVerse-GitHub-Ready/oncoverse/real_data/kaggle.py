"""Download public Kaggle datasets used by the real-data OncoVerse pipeline.

Authentication is handled by kagglehub. The project never stores Kaggle
credentials in source control.
"""
from pathlib import Path
import json

DATASETS = {
    "wisconsin": {
        "slug": "uciml/breast-cancer-wisconsin-data",
        "purpose": "Breast tumor diagnosis classification",
        "source": "UCI Machine Learning / Kaggle",
        "license_note": "Check the current Kaggle data card before redistribution",
    },
    "metabric": {
        "slug": "gunesevitan/breast-cancer-metabric",
        "purpose": "Breast cancer clinical survival analysis",
        "source": "METABRIC / Kaggle",
        "license_note": "Check the current Kaggle data card before redistribution",
    },
    "tcga_brca": {
        "slug": "samdemharter/brca-multiomics-tcga",
        "purpose": "TCGA-BRCA multi-omics research integration",
        "source": "TCGA-BRCA / Kaggle",
        "license_note": "Check the current Kaggle data card before redistribution",
    },
    "lc25000": {
        "slug": "andrewmvd/lung-and-colon-cancer-histopathological-images",
        "purpose": "Histopathology image classification",
        "source": "LC25000 / Kaggle",
        "license_note": "CC BY-SA 4.0 per Kaggle data card; verify current terms",
    },
}


def download_dataset(name: str, output_root: str = "data/raw") -> dict:
    if name not in DATASETS:
        raise ValueError(f"Unknown dataset: {name}. Choose from {', '.join(DATASETS)}")
    try:
        import kagglehub
    except ImportError as exc:
        raise RuntimeError("Install kagglehub first: pip install kagglehub") from exc

    spec = DATASETS[name]
    path = kagglehub.dataset_download(spec["slug"])
    dest = Path(output_root) / name
    dest.mkdir(parents=True, exist_ok=True)
    manifest = {**spec, "local_cache": str(path), "downloaded_to": str(dest)}
    (dest / "manifest.json").write_text(json.dumps(manifest, indent=2))
    return manifest


def download_all(output_root: str = "data/raw") -> list[dict]:
    return [download_dataset(name, output_root) for name in DATASETS]
