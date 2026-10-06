"""Observed METABRIC survival analysis: Kaplan-Meier and Cox PH."""
from pathlib import Path
import json
import numpy as np, pandas as pd
import matplotlib.pyplot as plt
from sklearn.impute import SimpleImputer
from sklearn.preprocessing import StandardScaler
import statsmodels.api as sm

RESULTS=Path("results"); FIG=RESULTS/"figures"; TAB=RESULTS/"tables"
FIG.mkdir(parents=True,exist_ok=True); TAB.mkdir(parents=True,exist_ok=True)

def _load(path):
    d=pd.read_csv(path)
    t=pd.to_numeric(d["Overall Survival (Months)"],errors="coerce")
    status=d["Overall Survival Status"].astype(str).str.lower()
    e=status.eq("deceased").astype(int)
    keep=t.notna() & status.isin(["deceased","living"])
    d=d.loc[keep].copy(); t=t.loc[keep]; e=e.loc[keep]
    return d,t,e

def _km(g):
    times=np.sort(g["_time"].unique()); n=len(g); at=n; s=1.; pts=[{"time_months":0.,"survival":1.,"at_risk":n}]
    for t in times:
        d=int(((g["_time"]==t)&(g["_event"]==1)).sum()); c=int(((g["_time"]==t)&(g["_event"]==0)).sum())
        if d:
            s*=1-d/at; pts.append({"time_months":float(t),"survival":float(s),"at_risk":int(at)})
        at-=d+c
    med=next((p["time_months"] for p in pts if p["survival"]<=.5),None)
    return pts,med

def kaplan_meier_from_metabric(csv_path,group_col=None):
    df,t,e=_load(csv_path); df["_time"]=t; df["_event"]=e
    aliases={"tumor_stage":"Tumor Stage","neoplasm_histologic_grade":"Neoplasm Histologic Grade",
             "er_status":"ER Status","her2_status":"HER2 Status"}
    if group_col: group_col=aliases.get(group_col,group_col)
    if group_col and group_col not in df: raise ValueError(f"Unknown grouping column: {group_col}")
    if not group_col:
        groups=[("All",df)]
    else:
        # Some METABRIC columns are pandas categoricals containing missing values.
        # groupby(..., dropna=False) can fail with "Categorical categories cannot be null"
        # on those columns. Convert the grouping values to plain object strings and
        # give missing observations an explicit research label.
        # Normalize every grouping value to text before grouping. METABRIC mixes
        # numeric categorical values with missing values, and pandas can otherwise
        # raise a categorical/null or mixed-type sorting error.
        group_values=df[group_col].astype("string").fillna("Missing")
        groups=list(df.assign(_km_group=group_values).groupby("_km_group", sort=True, dropna=False))
    curves=[]
    for name,g in groups:
        pts,med=_km(g); curves.append({"group":str(name),"n":len(g),"events":int(g._event.sum()),"median_months":med,"points":pts})
    return {"dataset":"Breast Cancer METABRIC (Kaggle)","curves":curves,
            "warning":"Descriptive research analysis only; uses observed overall-survival follow-up."}

def _features(df):
    # Deliberately avoid Nottingham prognostic index because it is constructed
    # from tumour size, nodes and grade; including both creates direct collinearity.
    x=pd.DataFrame(index=df.index)
    for new,old in {"Age at Diagnosis":"age_at_diagnosis","Tumor Stage":"tumor_stage",
                    "Neoplasm Histologic Grade":"grade","Mutation Count":"mutation_count"}.items():
        x[old]=pd.to_numeric(df[new],errors="coerce")
    x["er_positive"]=df["ER Status"].astype(str).str.lower().eq("positive").astype(float)
    x["her2_positive"]=df["HER2 Status"].astype(str).str.lower().eq("positive").astype(float)
    x["pr_positive"]=df["PR Status"].astype(str).str.lower().eq("positive").astype(float)
    return x

def concordance_index(time,event,risk):
    time=np.asarray(time); event=np.asarray(event).astype(bool); risk=np.asarray(risk)
    concordant=tied=permissible=0.
    for i in range(len(time)):
        if not event[i]: continue
        for j in range(len(time)):
            if time[j] <= time[i] or i==j: continue
            permissible+=1
            if risk[i]>risk[j]: concordant+=1
            elif risk[i]==risk[j]: tied+=1
    return float((concordant+.5*tied)/permissible) if permissible else float("nan")

def run_metabric_survival(csv_path):
    df,t,e=_load(csv_path); X=_features(df)
    from sklearn.model_selection import train_test_split
    idx=np.arange(len(df))
    tr_idx,te_idx=train_test_split(idx,test_size=0.25,random_state=42,stratify=e)
    imp=SimpleImputer(strategy="median")
    scaler=StandardScaler()
    Xtr=scaler.fit_transform(imp.fit_transform(X.iloc[tr_idx]))
    Xte=scaler.transform(imp.transform(X.iloc[te_idx]))
    model=sm.duration.PHReg(t.iloc[tr_idx].values, Xtr, status=e.iloc[tr_idx].values)
    fit=model.fit()
    risk=np.asarray(fit.predict(Xte).predicted_values).reshape(-1)
    cidx=concordance_index(t.iloc[te_idx].values,e.iloc[te_idx].values,risk)
    rows=[]
    cols=list(X.columns)
    for name,b,se,pval in zip(cols,fit.params,fit.bse,fit.pvalues):
        rows.append({"feature":name,"hazard_ratio":float(np.exp(b)),"coef":float(b),"p_value":float(pval)})
    cox=pd.DataFrame(rows).sort_values("p_value")
    cox.to_csv(TAB/"metabric_cox_results.csv",index=False)
    curves=kaplan_meier_from_metabric(csv_path)["curves"]
    plt.figure()
    for c in curves:
        pts=pd.DataFrame(c["points"]); plt.step(pts.time_months,pts.survival,where="post",label=f"All (n={c['n']})")
    plt.xlabel("Overall survival (months)"); plt.ylabel("Survival probability"); plt.title("METABRIC Kaplan–Meier")
    plt.ylim(0,1.05); plt.legend(); plt.tight_layout(); plt.savefig(FIG/"metabric_kaplan_meier.png",dpi=180); plt.close()
    res=kaplan_meier_from_metabric(csv_path,"er_status")
    plt.figure()
    for c in res["curves"]:
        pts=pd.DataFrame(c["points"]); plt.step(pts.time_months,pts.survival,where="post",label=f"{c['group']} (n={c['n']})")
    plt.xlabel("Overall survival (months)"); plt.ylabel("Survival probability"); plt.title("METABRIC Kaplan–Meier by ER Status")
    plt.ylim(0,1.05); plt.legend(); plt.tight_layout(); plt.savefig(FIG/"metabric_kaplan_meier_er.png",dpi=180); plt.close()
    metrics={"dataset":"Breast Cancer METABRIC","records_analyzed":len(df),"events":int(e.sum()),
             "median_followup_months":float(t.median()),"cox_concordance_index_test":cidx,
             "cox_train_records":len(tr_idx),"cox_test_records":len(te_idx),"cox_features":cols,
             "warning":"C-index is evaluated on a held-out test partition; this is a research discrimination statistic, not clinical validation."}
    (TAB/"metabric_survival_metrics.json").write_text(json.dumps(metrics,indent=2))
    return {"metrics":metrics,"cox":cox.to_dict("records"),"km_all":curves,"km_er":res["curves"]}

