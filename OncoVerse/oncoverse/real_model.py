"""Real-data research models for OncoVerse."""
from pathlib import Path
import json, joblib
import numpy as np, pandas as pd
import matplotlib.pyplot as plt
from sklearn.impute import SimpleImputer
from sklearn.metrics import (accuracy_score, roc_auc_score, precision_score, recall_score,
                             f1_score, confusion_matrix, roc_curve, classification_report)
from sklearn.model_selection import train_test_split
from xgboost import XGBClassifier

MODEL_DIR=Path("models/real"); FIG_DIR=Path("results/figures"); TAB_DIR=Path("results/tables")
for d in (MODEL_DIR,FIG_DIR,TAB_DIR): d.mkdir(parents=True,exist_ok=True)

def _fit_xgb(X,y):
    y=pd.Series(y).astype(int); pos=max(1,int(y.sum())); neg=max(1,int((y==0).sum()))
    m=XGBClassifier(n_estimators=350,max_depth=4,learning_rate=.04,subsample=.85,
                    colsample_bytree=.85,objective="binary:logistic",eval_metric="logloss",
                    random_state=42,n_jobs=2,scale_pos_weight=neg/pos)
    m.fit(X,y); return m

def _save_eval_artifacts(prefix,y_test,prob,pred,feature_names,model,X_test):
    stem=prefix.lower().replace(" ","_")
    cm=confusion_matrix(y_test,pred)
    fpr,tpr,_=roc_curve(y_test,prob)
    plt.figure(); plt.plot(fpr,tpr,label=f"AUC={roc_auc_score(y_test,prob):.3f}"); plt.plot([0,1],[0,1],"--")
    plt.xlabel("False Positive Rate"); plt.ylabel("True Positive Rate"); plt.title(f"{prefix} ROC Curve"); plt.legend(); plt.tight_layout()
    plt.savefig(FIG_DIR/f"{stem}_roc_curve.png",dpi=180); plt.close()
    plt.figure(); plt.imshow(cm); plt.title(f"{prefix} Confusion Matrix"); plt.xlabel("Predicted"); plt.ylabel("Actual")
    plt.xticks([0,1],["0","1"]); plt.yticks([0,1],["0","1"])
    for i in range(2):
        for j in range(2): plt.text(j,i,str(cm[i,j]),ha="center",va="center")
    plt.tight_layout(); plt.savefig(FIG_DIR/f"{stem}_confusion_matrix.png",dpi=180); plt.close()
    try:
        import shap
        sv=shap.TreeExplainer(model).shap_values(X_test[:min(200,len(X_test))])
        if isinstance(sv,list): sv=sv[1]
        imp=np.abs(np.asarray(sv)).mean(axis=0)
        sdf=pd.DataFrame({"feature":feature_names,"mean_abs_shap":imp}).sort_values("mean_abs_shap",ascending=False)
        sdf.to_csv(TAB_DIR/f"{stem}_shap_importance.csv",index=False)
        top=sdf.head(12).sort_values("mean_abs_shap")
        plt.figure(); plt.barh(top.feature,top.mean_abs_shap); plt.xlabel("Mean |SHAP value|"); plt.title(f"{prefix} Global SHAP Importance")
        plt.tight_layout(); plt.savefig(FIG_DIR/f"{stem}_shap_importance.png",dpi=180); plt.close()
    except Exception as e:
        (TAB_DIR/f"{stem}_shap_error.txt").write_text(repr(e))

def train_wisconsin(csv_path):
    df=pd.read_csv(csv_path); target=next((c for c in df if str(c).lower()=="diagnosis"),None)
    if not target: raise ValueError("Wisconsin CSV needs diagnosis")
    y=df[target].astype(str).str.upper().map({"M":1,"B":0})
    cols=[c for c in df if c not in {target,"id","Unnamed: 32"}]
    X=df[cols].apply(pd.to_numeric,errors="coerce")
    tr,te,ytr,yte=train_test_split(X,y,test_size=.2,random_state=42,stratify=y)
    imp=SimpleImputer(strategy="median"); trp=imp.fit_transform(tr); tep=imp.transform(te)
    model=_fit_xgb(trp,ytr); prob=model.predict_proba(tep)[:,1]; pred=(prob>=.5).astype(int)
    metrics={"dataset":"Breast Cancer Wisconsin Diagnostic (UCI dataset; bundled source-equivalent copy)","task":"benign_vs_malignant_research_classification",
             "records":len(df),"features":cols,"accuracy":accuracy_score(yte,pred),"roc_auc":roc_auc_score(yte,prob),
             "precision":precision_score(yte,pred),"recall":recall_score(yte,pred),"f1":f1_score(yte,pred),
             "majority_class_baseline_accuracy":float(max((yte==0).mean(),(yte==1).mean())),
             "confusion_matrix":confusion_matrix(yte,pred).tolist(),"warning":"Research prototype; not a clinical diagnostic model."}
    metrics={k:(float(v) if isinstance(v,(np.floating,np.integer)) else v) for k,v in metrics.items()}
    _save_eval_artifacts("Wisconsin XGBoost",yte,prob,pred,cols,model,tep)
    joblib.dump({"preprocess":imp,"model":model,"features":cols,"task":metrics["task"]},MODEL_DIR/"wisconsin_xgb.joblib")
    (MODEL_DIR/"wisconsin_metrics.json").write_text(json.dumps(metrics,indent=2)); (TAB_DIR/"wisconsin_classification_report.csv").write_text(classification_report(yte,pred,output_dict=False))
    return metrics

def _metabric_features(df):
    out=pd.DataFrame(index=df.index)
    mapping={
      "age_at_diagnosis":"Age at Diagnosis","tumor_size":"Tumor Size",
      "tumor_stage":"Tumor Stage","neoplasm_histologic_grade":"Neoplasm Histologic Grade",
      "lymph_nodes_examined_positive":"Lymph nodes examined positive",
      "mutation_count":"Mutation Count","nottingham_prognostic_index":"Nottingham prognostic index"}
    for new,old in mapping.items(): out[new]=pd.to_numeric(df[old],errors="coerce")
    out["er_positive"]=df["ER Status"].astype(str).str.lower().eq("positive").astype(float)
    out["her2_positive"]=df["HER2 Status"].astype(str).str.lower().eq("positive").astype(float)
    out["pr_positive"]=df["PR Status"].astype(str).str.lower().eq("positive").astype(float)
    return out

def train_metabric_5y(csv_path):
    df=pd.read_csv(csv_path)
    time=pd.to_numeric(df["Overall Survival (Months)"],errors="coerce")
    status=df["Overall Survival Status"].astype(str).str.lower()
    event=status.eq("deceased")
    valid=time.notna() & status.isin(["deceased","living"])
    df=df.loc[valid].copy(); time=time.loc[valid]; event=event.loc[valid]
    eligible=(time>=60) | (event & (time<60))
    df=df.loc[eligible].copy(); time=time.loc[eligible]; event=event.loc[eligible]
    y=(event & (time<=60)).astype(int)
    X=_metabric_features(df)
    tr,te,ytr,yte=train_test_split(X,y,test_size=.2,random_state=42,stratify=y)
    imp=SimpleImputer(strategy="median"); trp=imp.fit_transform(tr); tep=imp.transform(te)
    model=_fit_xgb(trp,ytr); prob=model.predict_proba(tep)[:,1]; pred=(prob>=.5).astype(int)
    metrics={"dataset":"Breast Cancer METABRIC (Kaggle)","task":"5_year_overall_survival_research_classification",
             "records_used":len(df),"positive_5y_events":int(y.sum()),"features":list(X.columns),
             "accuracy":accuracy_score(yte,pred),"roc_auc":roc_auc_score(yte,prob),
             "precision":precision_score(yte,pred),"recall":recall_score(yte,pred),"f1":f1_score(yte,pred),
             "majority_class_baseline_accuracy":float(max((yte==0).mean(),(yte==1).mean())),
             "confusion_matrix":confusion_matrix(yte,pred).tolist(),
             "endpoint_definition":"Event=Deceased by 60 months; patients censored before 60 months excluded; patients observed >=60 months without death treated as 5-year survivors.",
             "warning":"Research endpoint derived from observed follow-up; not an individualized clinical risk estimate."}
    metrics={k:(float(v) if isinstance(v,(np.floating,np.integer)) else v) for k,v in metrics.items()}
    _save_eval_artifacts("METABRIC 5Y XGBoost",yte,prob,pred,list(X.columns),model,tep)
    joblib.dump({"preprocess":imp,"model":model,"features":list(X.columns),"task":metrics["task"]},MODEL_DIR/"metabric_5y_xgb.joblib")
    (MODEL_DIR/"metabric_5y_metrics.json").write_text(json.dumps(metrics,indent=2))
    pd.DataFrame(classification_report(yte,pred,output_dict=True)).T.to_csv(TAB_DIR/"metabric_5y_classification_report.csv")
    return metrics
