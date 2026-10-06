"""Aggregate-only local cohort discovery."""
from sqlalchemy import select,func
from .db import CancerRecord,SessionLocal,init_db

def discover_cohort(cancer_type: str | None=None,stage: str | None=None) -> dict:
    init_db(); query=select(CancerRecord.cancer_type,CancerRecord.stage,func.count()).group_by(CancerRecord.cancer_type,CancerRecord.stage)
    if cancer_type: query=query.where(CancerRecord.cancer_type.ilike(f"%{cancer_type.strip()}%"))
    if stage: query=query.where(CancerRecord.stage==stage.strip().upper())
    with SessionLocal() as session: rows=session.execute(query).all()
    return {"filters":{"cancer_type":cancer_type,"stage":stage},"aggregate_cells":[{"cancer_type":c,"stage":s,"count":int(n) if n>=5 else "<5 suppressed"} for c,s,n in rows],"notice":"Aggregate cohort discovery only; no individual records returned."}
