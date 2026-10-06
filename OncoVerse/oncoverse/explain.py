"""Explainability helpers for active real XGBoost models."""
from pathlib import Path
import joblib, numpy as np, pandas as pd

ROOT=Path(__file__).resolve().parents[1]
MODEL_DIR=ROOT/"models/real"

def explain_real(model_file: str, values: dict, top_n: int=10):
    bundle=joblib.load(MODEL_DIR/model_file)
    X=pd.DataFrame([{f:values.get(f,np.nan) for f in bundle['features']}])
    Xi=bundle['preprocess'].transform(X[bundle['features']])
    from xgboost import DMatrix
    contrib=bundle['model'].get_booster().predict(DMatrix(Xi),pred_contribs=True)[0]
    vals=np.asarray(contrib[:-1],dtype=float)
    out=pd.DataFrame({'feature':bundle['features'],'shap_value':vals,'abs_shap':np.abs(vals)})
    return out.sort_values('abs_shap',ascending=False).head(top_n).to_dict('records')
