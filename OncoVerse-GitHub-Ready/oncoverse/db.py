from datetime import datetime, timezone
from sqlalchemy import create_engine, String, Float, Integer, DateTime, Text, inspect, text, UniqueConstraint
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, sessionmaker
from .config import DATABASE_URL, DATA_DIR

if DATABASE_URL.startswith("sqlite"):
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
else:
    engine = create_engine(DATABASE_URL, pool_pre_ping=True)
SessionLocal = sessionmaker(bind=engine, autoflush=False, expire_on_commit=False)

class Base(DeclarativeBase):
    pass

class CancerRecord(Base):
    __tablename__ = "cancer_records"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    source_id: Mapped[str] = mapped_column(String(120), unique=True, index=True)
    age: Mapped[int] = mapped_column(Integer)
    sex: Mapped[str] = mapped_column(String(20))
    cancer_type: Mapped[str] = mapped_column(String(80))
    stage: Mapped[str] = mapped_column(String(20))
    tumor_size_mm: Mapped[float] = mapped_column(Float)
    grade: Mapped[int] = mapped_column(Integer)
    smoking_status: Mapped[str] = mapped_column(String(30))
    outcome_label: Mapped[str] = mapped_column(String(30))
    site_code: Mapped[str | None] = mapped_column(String(80), nullable=True, index=True)
    source_name: Mapped[str] = mapped_column(String(120))
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))

class IngestionRun(Base):
    __tablename__ = "ingestion_runs"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    source_name: Mapped[str] = mapped_column(String(120))
    received: Mapped[int] = mapped_column(Integer)
    accepted: Mapped[int] = mapped_column(Integer)
    rejected: Mapped[int] = mapped_column(Integer)
    details: Mapped[str] = mapped_column(Text)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))

class ExternalDatasetRecord(Base):
    __tablename__ = "external_dataset_records"
    __table_args__ = (UniqueConstraint("source_name", "external_id", name="uq_external_source_record"),)
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    source_name: Mapped[str] = mapped_column(String(120), index=True)
    external_id: Mapped[str] = mapped_column(String(160))
    payload_json: Mapped[str] = mapped_column(Text)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))

def init_db():
    Base.metadata.create_all(bind=engine)
    columns = {col["name"] for col in inspect(engine).get_columns("cancer_records")}
    if "site_code" not in columns:
        with engine.begin() as connection:
            connection.execute(text("ALTER TABLE cancer_records ADD COLUMN site_code VARCHAR(80)"))
