from contextlib import asynccontextmanager
from pathlib import Path
import os
import joblib
from fastapi import FastAPI, HTTPException, Header
from pydantic import BaseModel, Field
from .db import init_db
from .analytics import summary
from .real_survival import kaplan_meier_from_metabric
from .pancancer_benchmark import load_benchmark

ROOT = Path(__file__).resolve().parents[1]
MODEL_DIR = ROOT / "models" / "real"
METABRIC = ROOT / "data/raw/metabric/Breast Cancer METABRIC.csv"
API_KEY = os.getenv("ONCOVERSE_API_KEY")

@asynccontextmanager
async def lifespan(_app):
    init_db()
    yield

app=FastAPI(title="OncoVerse Multi-Cancer Research API",version="2.0.0",description="Academic cancer research analytics API. Not for clinical use.",lifespan=lifespan)

def guard(x_api_key: str|None):
    if API_KEY and x_api_key != API_KEY:
        raise HTTPException(status_code=401,detail="Invalid or missing API key")

@app.get("/health")
def health():
    return {"status":"ok","clinical_use":False,"pan_cancer_benchmark":True,"real_patient_models":True}

@app.get("/analytics/summary")
def get_summary(x_api_key: str|None=Header(default=None)): guard(x_api_key); return summary()

@app.get("/analytics/pancancer-benchmark")
def pancancer_benchmark(x_api_key: str|None=Header(default=None)):
    guard(x_api_key); return load_benchmark()

@app.get("/analytics/survival")
def get_survival(group_by: str = "all", x_api_key: str|None=Header(default=None)):
    guard(x_api_key)
    if not METABRIC.exists(): raise HTTPException(status_code=503,detail="METABRIC source file is missing")
    aliases={"all":None,"tumor_stage":"tumor_stage","neoplasm_histologic_grade":"neoplasm_histologic_grade","er_status":"er_status","her2_status":"her2_status"}
    if group_by not in aliases: raise HTTPException(status_code=400,detail="Unsupported grouping field")
    return kaplan_meier_from_metabric(str(METABRIC),aliases[group_by])

class WisconsinRecord(BaseModel):
    values: dict[str,float]

class MetabricRecord(BaseModel):
    age_at_diagnosis: float=Field(ge=0)
    tumor_size: float=Field(ge=0)
    tumor_stage: float=Field(ge=0)
    neoplasm_histologic_grade: float=Field(ge=0)
    lymph_nodes_examined_positive: float=Field(ge=0)
    mutation_count: float=Field(ge=0)
    nottingham_prognostic_index: float=Field(ge=0)
    er_positive: float=Field(ge=0,le=1)
    her2_positive: float=Field(ge=0,le=1)
    pr_positive: float=Field(ge=0,le=1)

def _predict(bundle_name, values):
    path=MODEL_DIR/bundle_name
    if not path.exists(): raise HTTPException(status_code=503,detail="Trained model artifact is missing")
    bundle=joblib.load(path)
    import pandas as pd
    X=pd.DataFrame([values])
    Xi=bundle["preprocess"].transform(X[bundle["features"]])
    probs=bundle["model"].predict_proba(Xi)[0]
    return {"classes":getattr(bundle["model"],"classes_",[0,1]).tolist(),"probabilities":[float(x) for x in probs],"features":bundle["features"],"notice":"Research model output only; not a diagnosis or prognosis."}

@app.post("/model/wisconsin")
def predict_wisconsin(payload: WisconsinRecord,x_api_key: str|None=Header(default=None)):
    guard(x_api_key); return _predict("wisconsin_xgb.joblib",payload.values)

@app.post("/model/metabric-5y")
def predict_metabric(payload: MetabricRecord,x_api_key: str|None=Header(default=None)):
    guard(x_api_key); return _predict("metabric_5y_xgb.joblib",payload.model_dump())

@app.get("/research/trials")
def search_trials(q: str,limit: int=10,x_api_key: str|None=Header(default=None)):
    guard(x_api_key)
    try:
        from .integrations.public_sources import clinical_trials
        return clinical_trials(q,limit)
    except Exception as exc: raise HTTPException(status_code=502,detail=f"Registry request failed: {exc}")

@app.get("/research/pubmed")
def search_pubmed(q: str,limit: int=10,x_api_key: str|None=Header(default=None)):
    guard(x_api_key)
    try:
        from .integrations.public_sources import pubmed_search
        return {"articles":pubmed_search(q,limit),"notice":"Literature retrieval only; not medical advice."}
    except Exception as exc: raise HTTPException(status_code=502,detail=f"PubMed request failed: {exc}")
