from sqlalchemy import select, func
from .db import SessionLocal, CancerRecord, IngestionRun, ExternalDatasetRecord, init_db

def summary():
    init_db()
    with SessionLocal() as s:
        total=s.scalar(select(func.count()).select_from(CancerRecord)) or 0
        types=s.execute(select(CancerRecord.cancer_type,func.count()).group_by(CancerRecord.cancer_type).order_by(func.count().desc())).all()
        stages=s.execute(select(CancerRecord.stage,func.count()).group_by(CancerRecord.stage).order_by(CancerRecord.stage)).all()
        outcomes=s.execute(select(CancerRecord.outcome_label,func.count()).group_by(CancerRecord.outcome_label)).all()
        sites=s.execute(select(CancerRecord.site_code,func.count()).where(CancerRecord.site_code.is_not(None)).group_by(CancerRecord.site_code).order_by(func.count().desc())).all()
        runs=s.scalars(select(IngestionRun).order_by(IngestionRun.created_at.desc()).limit(10)).all()
        external_total=s.scalar(select(func.count()).select_from(ExternalDatasetRecord)) or 0
        external_sources=s.execute(select(ExternalDatasetRecord.source_name,func.count()).group_by(ExternalDatasetRecord.source_name).order_by(func.count().desc())).all()
    return {"record_count":total,"by_cancer_type":[{"name":k,"count":v} for k,v in types],
            "by_stage":[{"name":k,"count":v} for k,v in stages],"outcomes":[{"name":k,"count":v} for k,v in outcomes],"by_site":[{"name":k,"count":v} for k,v in sites],
            "recent_ingestion_runs":[{"source":r.source_name,"received":r.received,"accepted":r.accepted,"rejected":r.rejected} for r in runs],
            "external_record_count":external_total,"external_records_by_source":[{"name":name,"count":count} for name,count in external_sources]}
