"""PostgreSQL/SQLite storage for normalized public cancer cohorts."""
import json
from datetime import datetime, timezone
from sqlalchemy import String, Float, Integer, DateTime, Text, create_engine, select, func
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, sessionmaker
from .config import DATABASE_URL, DATA_DIR

if DATABASE_URL.startswith("sqlite"):
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
else:
    engine = create_engine(DATABASE_URL, pool_pre_ping=True)
Session = sessionmaker(bind=engine, autoflush=False, expire_on_commit=False)

class Base(DeclarativeBase): pass

class RealCancerRecord(Base):
    __tablename__ = "real_cancer_records"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    patient_id: Mapped[str] = mapped_column(String(160), index=True)
    source_dataset: Mapped[str] = mapped_column(String(120), index=True)
    age: Mapped[float | None] = mapped_column(Float, nullable=True)
    sex: Mapped[str | None] = mapped_column(String(40), nullable=True)
    cancer_type: Mapped[str | None] = mapped_column(String(120), nullable=True)
    stage: Mapped[str | None] = mapped_column(String(40), nullable=True)
    tumor_size_mm: Mapped[float | None] = mapped_column(Float, nullable=True)
    grade: Mapped[float | None] = mapped_column(Float, nullable=True)
    smoking_status: Mapped[str | None] = mapped_column(String(40), nullable=True)
    diagnosis_label: Mapped[str | None] = mapped_column(String(60), nullable=True)
    survival_months: Mapped[float | None] = mapped_column(Float, nullable=True)
    survival_event: Mapped[int | None] = mapped_column(Integer, nullable=True)
    site_code: Mapped[str | None] = mapped_column(String(100), nullable=True)
    treatment: Mapped[str | None] = mapped_column(String(120), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))

class RealIngestionRun(Base):
    __tablename__ = "real_ingestion_runs"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    source_dataset: Mapped[str] = mapped_column(String(120))
    received: Mapped[int] = mapped_column(Integer)
    inserted: Mapped[int] = mapped_column(Integer)
    rejected: Mapped[int] = mapped_column(Integer)
    details: Mapped[str] = mapped_column(Text)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))


def init_real_db():
    Base.metadata.create_all(bind=engine)


def ingest_canonical_csv(path: str) -> dict:
    import pandas as pd
    init_real_db()
    df = pd.read_csv(path)
    required = ["patient_id", "source_dataset"]
    missing = [c for c in required if c not in df.columns]
    if missing: raise ValueError(f"Missing required columns: {missing}")
    records = 0; rejected = 0
    with Session() as s:
        existing = {x for x, in s.execute(select(RealCancerRecord.patient_id).where(RealCancerRecord.source_dataset == str(df.source_dataset.iloc[0]) if len(df) else "")).all()}
        for row in df.to_dict("records"):
            pid = str(row.get("patient_id", "")).strip()
            src = str(row.get("source_dataset", "")).strip()
            if not pid or not src or pid in existing:
                rejected += 1; continue
            clean = {k: (None if pd.isna(v) else v) for k, v in row.items() if k in RealCancerRecord.__table__.columns.keys()}
            clean["patient_id"] = pid; clean["source_dataset"] = src
            for k in ["age", "tumor_size_mm", "grade", "survival_months"]:
                if clean.get(k) is not None:
                    clean[k] = float(clean[k])
            if clean.get("survival_event") is not None:
                clean["survival_event"] = int(clean["survival_event"])
            s.add(RealCancerRecord(**clean)); existing.add(pid); records += 1
        src_name = str(df.source_dataset.iloc[0]) if len(df) else "unknown"
        s.add(RealIngestionRun(source_dataset=src_name, received=len(df), inserted=records, rejected=rejected, details=json.dumps({"path": path})))
        s.commit()
    return {"source_dataset": src_name, "received": len(df), "inserted": records, "rejected": rejected}


def summary() -> dict:
    init_real_db()
    with Session() as s:
        total = s.scalar(select(func.count()).select_from(RealCancerRecord)) or 0
        sources = s.execute(select(RealCancerRecord.source_dataset, func.count()).group_by(RealCancerRecord.source_dataset)).all()
        cancers = s.execute(select(RealCancerRecord.cancer_type, func.count()).where(RealCancerRecord.cancer_type.is_not(None)).group_by(RealCancerRecord.cancer_type).order_by(func.count().desc())).all()
        labels = s.execute(select(RealCancerRecord.diagnosis_label, func.count()).where(RealCancerRecord.diagnosis_label.is_not(None)).group_by(RealCancerRecord.diagnosis_label)).all()
    return {"records": int(total), "sources": [{"source": a, "count": int(b)} for a,b in sources], "cancers": [{"name": a, "count": int(b)} for a,b in cancers], "diagnoses": [{"name": a, "count": int(b)} for a,b in labels]}
