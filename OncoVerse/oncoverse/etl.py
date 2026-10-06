"""CSV validation, harmonization, and persistence."""
import json
import pandas as pd
from sqlalchemy import select
from .db import SessionLocal, CancerRecord, IngestionRun, init_db

REQUIRED = ["source_id", "age", "sex", "cancer_type", "stage", "tumor_size_mm", "grade", "smoking_status", "outcome_label"]
STAGES = {"1":"I", "2":"II", "3":"III", "4":"IV", "I":"I", "II":"II", "III":"III", "IV":"IV"}

def ingest_csv(path: str, source_name: str | None = None) -> dict:
    init_db()
    source_name = source_name or path.rsplit("/", 1)[-1]
    frame = pd.read_csv(path)
    missing = sorted(set(REQUIRED) - set(frame.columns))
    if missing:
        raise ValueError(f"CSV is missing required columns: {', '.join(missing)}")
    received = len(frame)
    columns = REQUIRED + (["site_code"] if "site_code" in frame.columns else [])
    frame = frame[columns].drop_duplicates(subset="source_id", keep="first").copy()
    for col in ["age", "tumor_size_mm", "grade"]:
        frame[col] = pd.to_numeric(frame[col], errors="coerce")
    frame["stage"] = frame.stage.astype(str).str.strip().str.upper().str.replace("STAGE ", "", regex=False).map(STAGES)
    for col in ["sex", "cancer_type", "smoking_status", "outcome_label"] + (["site_code"] if "site_code" in frame.columns else []):
        frame[col] = frame[col].astype("string").str.strip()
    frame["sex"] = frame.sex.str.lower().map({"female":"Female", "f":"Female", "male":"Male", "m":"Male", "other":"Other", "unknown":"Unknown"})
    frame["smoking_status"] = frame.smoking_status.str.lower().map({"never":"Never", "former":"Former", "current":"Current", "unknown":"Unknown"})
    frame["outcome_label"] = frame.outcome_label.str.lower().map({"alive":"Alive", "deceased":"Deceased"})
    frame["cancer_type"] = frame.cancer_type.str.title()
    valid = (frame.source_id.notna() & (frame.source_id.astype(str) != "") & frame.age.between(18,110) &
             frame.tumor_size_mm.between(0,500) & frame.grade.isin([1,2,3,4]) & frame.stage.notna() &
             frame.sex.notna() & frame.smoking_status.notna() & frame.outcome_label.notna() &
             frame.cancer_type.notna() & (frame.cancer_type != ""))
    good = frame[valid]
    inserted = skipped = 0
    with SessionLocal() as session:
        for row in good.to_dict(orient="records"):
            sid = str(row["source_id"])
            existing = session.scalar(select(CancerRecord).where(CancerRecord.source_id == sid))
            if existing:
                if existing.site_code is None and row.get("site_code") is not None and pd.notna(row.get("site_code")):
                    existing.site_code = str(row["site_code"]).strip() or None
                skipped += 1
                continue
            row.update(source_id=sid, age=int(row["age"]), grade=int(row["grade"]), tumor_size_mm=float(row["tumor_size_mm"]))
            if row.get("site_code") is not None and pd.notna(row.get("site_code")):
                row["site_code"] = str(row["site_code"]).strip() or None
            else:
                row["site_code"] = None
            session.add(CancerRecord(**row, source_name=source_name))
            inserted += 1
        rejected = received - inserted - skipped
        report = {"source":source_name,"received":received,"accepted":inserted,"rejected":rejected,"skipped_existing":skipped}
        session.add(IngestionRun(source_name=source_name, received=received, accepted=inserted, rejected=rejected, details=json.dumps(report)))
        session.commit()
    return report
