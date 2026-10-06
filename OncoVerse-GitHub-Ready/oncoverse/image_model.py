"""Train a generic educational image classifier from labeled subfolders."""
import json
from pathlib import Path
import joblib,numpy as np
from PIL import Image
from sklearn.ensemble import RandomForestClassifier,ExtraTreesClassifier,VotingClassifier
from sklearn.metrics import accuracy_score,classification_report
from sklearn.model_selection import train_test_split
from .config import MODEL_DIR
MODEL=MODEL_DIR/"image_demo_model.joblib"; METRICS=MODEL_DIR/"image_demo_metrics.json"; EXT={".png",".jpg",".jpeg",".tif",".tiff",".dcm"}
def _features(path):
    if path.suffix.lower()==".dcm":
        try: import pydicom
        except ImportError as exc: raise ValueError("DICOM support requires pip install -r requirements-optional.txt") from exc
        pixels=np.squeeze(pydicom.dcmread(str(path)).pixel_array.astype(np.float32))
        if pixels.ndim!=2: raise ValueError("Expected one grayscale DICOM image per file")
        low,high=np.percentile(pixels,[1,99]); pixels=np.clip((pixels-low)/max(float(high-low),1e-6),0,1)
        return np.asarray(Image.fromarray((pixels*255).astype(np.uint8)).resize((32,32)),dtype=np.float32).reshape(-1)/255.
    with Image.open(path) as im: return np.asarray(im.convert("L").resize((32,32)),dtype=np.float32).reshape(-1)/255.
def train_image_demo(root):
    base=Path(root); classes=sorted(p for p in base.iterdir() if p.is_dir()) if base.is_dir() else []
    if len(classes)<2: raise ValueError("Need at least two class subfolders of authorized labeled images")
    X=[]; y=[]
    for folder in classes:
        for f in sorted(folder.rglob("*")):
            if f.is_file() and f.suffix.lower() in EXT: X.append(_features(f)); y.append(folder.name)
    if len(X)<10 or len(set(y))<2: raise ValueError("Need 10+ readable images across at least two classes")
    counts={label:y.count(label) for label in set(y)}; strat=y if min(counts.values())>=2 else None
    xtr,xte,ytr,yte=train_test_split(np.asarray(X),y,test_size=.25,random_state=42,stratify=strat)
    model=VotingClassifier([("rf",RandomForestClassifier(n_estimators=100,max_depth=8,class_weight="balanced",random_state=42,n_jobs=2)),("extra",ExtraTreesClassifier(n_estimators=100,max_depth=8,class_weight="balanced",random_state=43,n_jobs=2))],voting="soft",n_jobs=1)
    model.fit(xtr,ytr); pred=model.predict(xte)
    metrics={"purpose":"generic image pipeline demonstration only","records":len(X),"holdout_records":len(yte),"classes":sorted(set(y),),"accuracy":float(accuracy_score(yte,pred)),"classification_report":classification_report(yte,pred,zero_division=0,output_dict=True),"warning":"Not a tumor detector or clinically validated model."}
    MODEL_DIR.mkdir(parents=True,exist_ok=True); joblib.dump(model,MODEL); METRICS.write_text(json.dumps(metrics,indent=2)); return metrics
def predict_image_demo(path):
    if not MODEL.exists(): raise FileNotFoundError("Train image model first with python -m oncoverse.cli train-image <folder>")
    model=joblib.load(MODEL); probs=model.predict_proba(_features(Path(path))[None,:])[0]
    return {"class":str(model.classes_[int(probs.argmax())]),"class_probabilities":{str(k):float(v) for k,v in zip(model.classes_,probs)},"warning":"Toy classifier output only; not a cancer diagnosis."}
