"""Explicit column mapping and downloads for authorized CSV data."""
import json
import subprocess
import tempfile
import urllib.request
from pathlib import Path

import pandas as pd
from sqlalchemy import select

from ..db import ExternalDatasetRecord, IngestionRun, SessionLocal, init_db
from ..etl import REQUIRED, ingest_csv


def map_and_ingest_csv(path: str, mapping_path: str) -> dict:
    source = Path(path)
    mapping = json.loads(Path(mapping_path).read_text())
    if not isinstance(mapping, dict):
        raise ValueError("Mapping must map canonical field names to source field names")
    supported = set(REQUIRED) | {"site_code"}
    unknown = sorted(set(mapping) - supported)
    if unknown:
        raise ValueError("Unsupported canonical fields: " + ", ".join(unknown))
    frame = pd.read_csv(source)
    missing = [mapping.get(col) for col in REQUIRED if not mapping.get(col) or mapping[col] not in frame.columns]
    if missing:
        raise ValueError("Mapping missing required source columns: " + ", ".join(map(str, missing)))
    mapped_required = [mapping[col] for col in REQUIRED]
    if len(set(mapped_required)) != len(mapped_required):
        raise ValueError("Each required canonical field must map to a distinct source column")
    if mapping.get("site_code") and mapping["site_code"] not in frame.columns:
        raise ValueError("Mapped site_code source column is not present in the CSV")
    canonical = frame.rename(columns={source_col: field for field, source_col in mapping.items()})
    columns = REQUIRED + (["site_code"] if "site_code" in mapping else [])
    with tempfile.TemporaryDirectory(prefix="oncoverse-mapped-") as temp_dir:
        output = Path(temp_dir) / "canonical.csv"
        canonical[columns].to_csv(output, index=False)
        return ingest_csv(str(output), source_name=source.name)


def download_csv(url: str, destination: str) -> str:
    if not url.startswith("https://"):
        raise ValueError("Dataset URL must use HTTPS")
    target = Path(destination)
    target.parent.mkdir(parents=True, exist_ok=True)
    request = urllib.request.Request(url, headers={"User-Agent": "OncoVerseAcademicPrototype/1.0"})
    with urllib.request.urlopen(request, timeout=60) as response, target.open("wb") as output:
        output.write(response.read())
    if target.suffix.lower() != ".csv":
        raise ValueError("Downloaded file is not a .csv; extract/convert it first")
    return str(target)


def kaggle_download(dataset: str, destination: str = "data/external/kaggle") -> str:
    target = Path(destination)
    target.mkdir(parents=True, exist_ok=True)
    try:
        subprocess.run(["kaggle", "datasets", "download", "-d", dataset, "-p", str(target), "--unzip"],
                       check=True, capture_output=True, text=True)
    except FileNotFoundError as exc:
        raise RuntimeError("Install/configure Kaggle CLI and authorize dataset access first") from exc
    except subprocess.CalledProcessError as exc:
        detail = exc.stderr[-1000:] if exc.stderr else ""
        raise RuntimeError("Kaggle download failed; check credentials, dataset ID, and terms. " + detail) from exc
    files = sorted(target.rglob("*.csv"))
    if not files:
        raise RuntimeError("No top-level CSV found in downloaded dataset")
    return str(files[0])


def uci_download(dataset_id: int, destination: str = "data/external/uci") -> dict:
    """Download one public UCI dataset without guessing its canonical meaning."""
    try:
        from ucimlrepo import fetch_ucirepo
    except ImportError as exc:
        raise RuntimeError("Install the UCI connector with: pip install -r requirements-optional.txt") from exc
    dataset = fetch_ucirepo(id=int(dataset_id))
    features = dataset.data.features.copy()
    targets = dataset.data.targets.copy()
    feature_names = set(map(str, features.columns))
    targets.columns = [f"target__{column}" if str(column) in feature_names else str(column) for column in targets.columns]
    frame = pd.concat([features, targets], axis=1)
    target = Path(destination)
    if target.suffix.lower() != ".csv":
        target.mkdir(parents=True, exist_ok=True)
        target = target / f"uci_{int(dataset_id)}.csv"
    target.parent.mkdir(parents=True, exist_ok=True)
    frame.to_csv(target, index=False)
    source = dataset.metadata
    metadata = {
        "uci_id": getattr(source, "uci_id", int(dataset_id)),
        "name": getattr(source, "name", ""),
        "repository_url": getattr(source, "repository_url", ""),
        "dataset_doi": getattr(source, "dataset_doi", ""),
        "rows": int(len(frame)),
        "feature_columns": list(map(str, features.columns)),
        "target_columns": list(map(str, targets.columns)),
        "notice": "Review dataset terms and semantics. Downloaded columns are not automatically mapped to the OncoVerse canonical schema.",
    }
    target.with_suffix(".metadata.json").write_text(json.dumps(metadata, indent=2, default=str))
    return {"csv": str(target), "metadata": str(target.with_suffix(".metadata.json")), **metadata}


def ingest_external_csv(path: str, source_name: str, id_column: str | None = None) -> dict:
    """Store source-specific rows without coercing them into the canonical clinical schema."""
    source = Path(path)
    if source.stat().st_size > 100 * 1024 * 1024:
        raise ValueError("External CSV exceeds the 100 MB academic-demo limit")
    frame = pd.read_csv(source)
    if len(frame) > 100_000:
        raise ValueError("External CSV exceeds the 100,000-row academic-demo limit")
    if not source_name or len(source_name) > 120:
        raise ValueError("source_name must contain 1 to 120 characters")
    if id_column and id_column not in frame.columns:
        raise ValueError(f"ID column not found in CSV: {id_column}")
    init_db()
    accepted = rejected = skipped = 0
    seen: set[str] = set()
    clean_frame = frame.astype(object).where(pd.notna(frame), None)
    with SessionLocal() as session:
        for index, row in enumerate(clean_frame.to_dict(orient="records")):
            raw_id = row.get(id_column) if id_column else f"row-{index + 1}"
            if raw_id is None or str(raw_id).strip() == "":
                rejected += 1
                continue
            external_id = str(raw_id).strip()
            if len(external_id) > 160:
                rejected += 1
                continue
            if external_id in seen:
                skipped += 1
                continue
            seen.add(external_id)
            exists = session.scalar(select(ExternalDatasetRecord.id).where(
                ExternalDatasetRecord.source_name == source_name,
                ExternalDatasetRecord.external_id == external_id,
            ))
            if exists:
                skipped += 1
                continue
            session.add(ExternalDatasetRecord(
                source_name=source_name,
                external_id=external_id,
                payload_json=json.dumps(row, default=str, allow_nan=False),
            ))
            accepted += 1
        details = {"source": source_name, "received": len(frame), "accepted": accepted,
                   "rejected": rejected, "skipped_existing": skipped, "id_column": id_column}
        session.add(IngestionRun(source_name=source_name, received=len(frame), accepted=accepted,
                                 rejected=rejected, details=json.dumps(details)))
        session.commit()
    return details
