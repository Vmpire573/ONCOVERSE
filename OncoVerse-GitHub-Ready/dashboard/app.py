from __future__ import annotations

import json
import sys
from pathlib import Path

import joblib
import numpy as np
import pandas as pd
import plotly.express as px
import streamlit as st

BASE_DIR = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(BASE_DIR))

from oncoverse.pancancer_benchmark import cohort_table, load_benchmark, sex_age_table, stage_table
from oncoverse.real_survival import kaplan_meier_from_metabric

RESULTS = BASE_DIR / "results"
MODEL_DIR = BASE_DIR / "models" / "real"
METABRIC_CSV = BASE_DIR / "data" / "raw" / "metabric" / "Breast Cancer METABRIC.csv"
WISCONSIN_CSV = BASE_DIR / "data" / "raw" / "wisconsin" / "breast_cancer_wisconsin_diagnostic.csv"

st.set_page_config(page_title="OncoVerse — Multi-Cancer Intelligence", page_icon="🧬", layout="wide")

st.markdown("""
<style>
:root{--ink:#172033;--muted:#667085;--line:#e7eaf1}
.stApp{background:radial-gradient(circle at 8% 0%,rgba(109,93,252,.11),transparent 30%),radial-gradient(circle at 96% 10%,rgba(6,182,212,.10),transparent 28%),linear-gradient(180deg,#f7f9fc,#fff 48%,#f8fafc)}
.block-container{padding-top:1.2rem;max-width:1450px}
.hero{padding:1.7rem 1.8rem;border-radius:24px;color:white;margin-bottom:1rem;background:linear-gradient(120deg,#172554,#4338ca 48%,#0891b2);box-shadow:0 18px 45px rgba(67,56,202,.20)}
.hero h1{margin:0;font-size:2.2rem;letter-spacing:-.04em}.hero p{margin:.25rem 0 0;color:rgba(255,255,255,.86)}
.hero-pill{display:inline-block;margin-top:.8rem;padding:.34rem .72rem;border-radius:999px;background:rgba(255,255,255,.14);border:1px solid rgba(255,255,255,.18);font-size:.78rem}
.notice{border:1px solid #c7d2fe;border-radius:15px;padding:.85rem 1rem;background:#eef2ff;color:#312e81;margin-bottom:1rem}
.card{border:1px solid #e2e8f0;border-radius:18px;padding:1rem;background:rgba(255,255,255,.82);box-shadow:0 10px 28px rgba(15,23,42,.055);height:100%}
.metric{border-radius:18px;padding:1rem 1.05rem;color:white;min-height:105px}.metric .label{font-size:.75rem;opacity:.8;text-transform:uppercase;letter-spacing:.08em}.metric .value{font-size:1.7rem;font-weight:800;margin-top:.2rem}
.p{background:linear-gradient(135deg,#4338ca,#7c3aed)}.c{background:linear-gradient(135deg,#0e7490,#06b6d4)}.g{background:linear-gradient(135deg,#047857,#10b981)}.r{background:linear-gradient(135deg,#be185d,#ec4899)}
.kicker{color:#6366f1;font-size:.74rem;text-transform:uppercase;font-weight:800;letter-spacing:.12em;margin-bottom:.15rem}
</style>
""", unsafe_allow_html=True)


def metric(label: str, value: str, tone: str = "p"):
    st.markdown(f'<div class="metric {tone}"><div class="label">{label}</div><div class="value">{value}</div></div>', unsafe_allow_html=True)


def load_json(path: Path):
    return json.loads(path.read_text()) if path.exists() else {}


benchmark = load_benchmark()
cohort = cohort_table()
stage = stage_table()
demo_note = benchmark["interpretation"]
metabric = pd.read_csv(METABRIC_CSV) if METABRIC_CSV.exists() else pd.DataFrame()
wisconsin = pd.read_csv(WISCONSIN_CSV) if WISCONSIN_CSV.exists() else pd.DataFrame()

st.markdown(f'''<div class="hero"><h1>🧬 OncoVerse</h1><p>AI-powered multi-cancer intelligence platform · research implementation</p><span class="hero-pill">8 cancer types · published pan-cancer benchmark · real breast cohorts · XGBoost · SHAP · Kaplan–Meier</span></div>''', unsafe_allow_html=True)
st.markdown('<div class="notice"><b>Research software:</b> pan-cancer figures in this dashboard are published CancerSEEK study-level evidence. The individual CancerSEEK supplementary workbook is not bundled. OncoVerse does not fabricate patient-level pan-cancer observations. The trained patient-level models bundled here are evaluated on the real Wisconsin Diagnostic and METABRIC cohorts.</div>', unsafe_allow_html=True)

# Headline metrics
cols = st.columns(4)
with cols[0]: metric("Pan-cancer types", "8", "p")
with cols[1]: metric("Published cancer cohort", "1,005", "c")
with cols[2]: metric("Healthy controls", "812", "r")
with cols[3]: metric("Protein biomarkers", "39", "g")

st.caption("CancerSEEK cohort: breast, colorectum, esophagus, liver, lung, ovary, pancreas and stomach. Study-level benchmark values are sourced from the published paper; they are not OncoVerse validation metrics.")

tabs = st.tabs(["Overview", "Pan-Cancer Evidence", "AI Prediction", "Survival", "Data Engineering", "Medical Imaging", "Research", "Governance"])

with tabs[0]:
    st.markdown('<div class="kicker">Platform overview</div>', unsafe_allow_html=True)
    st.subheader("One research workspace across multiple cancer domains")
    a,b,c = st.columns(3)
    with a:
        st.markdown('<div class="card"><h4>🌐 Pan-cancer evidence</h4><b>8 cancer types</b><p>Published CancerSEEK cohort composition, stage distribution and study-level performance are shown without pretending to reproduce unavailable patient-level data.</p></div>', unsafe_allow_html=True)
    with b:
        st.markdown('<div class="card"><h4>🤖 Real ML models</h4><b>2 held-out XGBoost models</b><p>Wisconsin benign/malignant classification and METABRIC 5-year observed-survival endpoint.</p></div>', unsafe_allow_html=True)
    with c:
        st.markdown('<div class="card"><h4>📈 Survival analytics</h4><b>Observed METABRIC follow-up</b><p>Kaplan–Meier curves plus a Cox model whose C-index is evaluated on a held-out test partition.</p></div>', unsafe_allow_html=True)

    fig = px.bar(cohort, x="cancer_type", y="patients", title="Published CancerSEEK cancer cohort", template="plotly_white")
    fig.update_layout(height=420, xaxis_title="Cancer type", yaxis_title="Patients")
    st.plotly_chart(fig, use_container_width=True)

    st.markdown("### Active data assets")
    assets = pd.DataFrame([
        ["Wisconsin Diagnostic", len(wisconsin), "Real bundled cohort", "Benign vs malignant research classification"],
        ["METABRIC", len(metabric), "Real bundled cohort", "Observed survival + 5-year endpoint"],
        ["CancerSEEK", 1817, "Published study summary", "Pan-cancer evidence; individual rows not bundled"],
    ], columns=["Asset","Records","Status","Use"])
    st.dataframe(assets, use_container_width=True, hide_index=True)

with tabs[1]:
    st.markdown('<div class="kicker">Pan-cancer evidence</div>', unsafe_allow_html=True)
    st.subheader("CancerSEEK published cohort — eight cancer types")
    b = benchmark["published_benchmarks"]
    m1,m2,m3,m4 = st.columns(4)
    with m1: metric("Median detection sensitivity", f"{b['median_cancer_detection_sensitivity_percent']}%", "p")
    with m2: metric("Specificity", f">{b['specificity_percent_greater_than']}%", "g")
    with m3: metric("Two-site localization", f"{b['two_site_localization_median_percent']}%", "c")
    with m4: metric("Single-site localization", f"{b['single_site_localization_median_percent']}%", "r")

    st.caption("Published benchmark, not an OncoVerse model result. The original study reported 1,005 nonmetastatic stage I–III cancer patients and 812 healthy controls.")
    st.markdown("### Cohort composition")
    st.dataframe(cohort.rename(columns={"cancer_type":"Cancer type","patients":"Patients"}), use_container_width=True, hide_index=True)
    st.markdown("### Stage distribution")
    st.dataframe(stage.rename(columns={"cancer_type":"Cancer type","stage_I":"Stage I","stage_II":"Stage II","stage_III":"Stage III"}), use_container_width=True, hide_index=True)
    fig = px.bar(stage, x="cancer_type", y=["stage_I","stage_II","stage_III"], barmode="stack", title="Published stage distribution", template="plotly_white")
    fig.update_layout(height=430, xaxis_title="Cancer type", yaxis_title="Patients")
    st.plotly_chart(fig, use_container_width=True)
    st.markdown("### Important distinction")
    st.info("The CancerSEEK source provides the pan-cancer research framing and published benchmark. Because the individual supplementary workbook could not be bundled reliably, this build does not claim to have trained a new eight-class patient-level model on CancerSEEK.")

with tabs[2]:
    st.markdown('<div class="kicker">Explainable AI</div>', unsafe_allow_html=True)
    st.subheader("Real patient-level research models")
    st.write("Choose a real bundled cohort and enter feature values manually. No hidden example patient, true label, or training-row shortcut is used.")
    model_choice = st.radio("Model", ["Wisconsin diagnostic", "METABRIC 5-year endpoint"], horizontal=True)

    if model_choice.startswith("Wisconsin"):
        bundle_path = MODEL_DIR / "wisconsin_xgb.joblib"
        metrics = load_json(MODEL_DIR / "wisconsin_metrics.json")
        if bundle_path.exists() and not wisconsin.empty:
            bundle = joblib.load(bundle_path); features = bundle["features"]
            st.caption(f"Held-out test set: {metrics.get('test_records','available')} records · majority-class baseline accuracy: {metrics.get('majority_class_baseline_accuracy',0):.3f}")
            vals = {}
            grid = st.columns(3)
            for i,f in enumerate(features):
                s = pd.to_numeric(wisconsin[f], errors="coerce").dropna(); lo=float(s.min()); hi=float(s.max()); med=float(s.median())
                with grid[i%3]: vals[f]=st.number_input(f, min_value=lo, max_value=hi, value=med, key=f"w_{f}")
            if st.button("Run Wisconsin research prediction", type="primary"):
                X=pd.DataFrame([vals]); Xi=bundle["preprocess"].transform(X[features]); prob=float(bundle["model"].predict_proba(Xi)[0,1]); pred=int(prob>=0.5)
                label="Malignant research class" if pred else "Benign research class"
                st.success(f"Model output: {label} · probability={prob:.3f}")
                st.caption("This output is a model classification, not a diagnosis.")
                try:
                    from xgboost import DMatrix
                    contrib=bundle["model"].get_booster().predict(DMatrix(Xi),pred_contribs=True)[0][:-1]
                    shap_df=pd.DataFrame({"Feature":features,"SHAP contribution":contrib}).sort_values("SHAP contribution")
                    fig=px.bar(shap_df.tail(10),x="SHAP contribution",y="Feature",orientation="h",title="Individual SHAP contributions",template="plotly_white")
                    st.plotly_chart(fig,use_container_width=True)
                except Exception as exc: st.warning(f"SHAP unavailable: {exc}")
            st.markdown("### Held-out metrics")
            st.json({k:metrics[k] for k in ["accuracy","roc_auc","precision","recall","f1","majority_class_baseline_accuracy"] if k in metrics})
        else: st.error("Wisconsin model assets are missing. Run scripts/train_real_models.py first.")
    else:
        bundle_path=MODEL_DIR/"metabric_5y_xgb.joblib"; metrics=load_json(MODEL_DIR/"metabric_5y_metrics.json")
        if bundle_path.exists() and not metabric.empty:
            bundle=joblib.load(bundle_path); features=bundle["features"]
            st.caption("5-year endpoint: deceased by 60 months vs observed 5-year survivors; censored before 60 months excluded.")
            vals={}
            source_cols={"age_at_diagnosis":"Age at Diagnosis","tumor_size":"Tumor Size","tumor_stage":"Tumor Stage","neoplasm_histologic_grade":"Neoplasm Histologic Grade","lymph_nodes_examined_positive":"Lymph nodes examined positive","mutation_count":"Mutation Count","nottingham_prognostic_index":"Nottingham prognostic index"}
            grid=st.columns(3)
            for i,(f,col) in enumerate(source_cols.items()):
                s=pd.to_numeric(metabric[col],errors="coerce").dropna(); lo=float(s.min()); hi=float(s.max()); med=float(s.median())
                with grid[i%3]: vals[f]=st.number_input(col,min_value=lo,max_value=hi,value=med,key=f"m_{f}")
            with grid[0]: vals["er_positive"]=float(st.selectbox("ER Status",["Positive","Negative"])=="Positive")
            with grid[1]: vals["her2_positive"]=float(st.selectbox("HER2 Status",["Positive","Negative"])=="Positive")
            with grid[2]: vals["pr_positive"]=float(st.selectbox("PR Status",["Positive","Negative"])=="Positive")
            if st.button("Run METABRIC research prediction",type="primary"):
                X=pd.DataFrame([vals]); Xi=bundle["preprocess"].transform(X[features]); prob=float(bundle["model"].predict_proba(Xi)[0,1]); pred=int(prob>=0.5)
                st.success(f"Model output: {'5-year event class' if pred else 'No 5-year event class'} · probability={prob:.3f}")
                st.caption("This is a research endpoint derived from observed follow-up; it is not an individualized prognosis.")
                try:
                    from xgboost import DMatrix
                    contrib=bundle["model"].get_booster().predict(DMatrix(Xi),pred_contribs=True)[0][:-1]
                    shap_df=pd.DataFrame({"Feature":features,"SHAP contribution":contrib}).sort_values("SHAP contribution")
                    fig=px.bar(shap_df,x="SHAP contribution",y="Feature",orientation="h",title="Individual SHAP contributions",template="plotly_white")
                    st.plotly_chart(fig,use_container_width=True)
                except Exception as exc: st.warning(f"SHAP unavailable: {exc}")
            st.markdown("### Held-out metrics")
            st.json({k:metrics[k] for k in ["accuracy","roc_auc","precision","recall","f1"] if k in metrics})
        else: st.error("METABRIC model assets are missing. Run scripts/train_real_models.py first.")

with tabs[3]:
    st.markdown('<div class="kicker">Time-to-event analysis</div>', unsafe_allow_html=True)
    st.subheader("Observed METABRIC survival analysis")
    sm=load_json(RESULTS/"tables"/"metabric_survival_metrics.json")
    if sm:
        a,b,c,d=st.columns(4)
        with a: metric("Records analyzed",f"{sm['records_analyzed']:,}","p")
        with b: metric("Observed deaths",f"{sm['events']:,}","r")
        with c: metric("Median follow-up",f"{sm['median_followup_months']:.1f} mo","c")
        with d: metric("Held-out C-index",f"{sm['cox_concordance_index_test']:.3f}","g")
        c1,c2=st.columns(2)
        with c1:
            p=RESULTS/"figures"/"metabric_kaplan_meier.png"
            if p.exists(): st.image(str(p),caption="Kaplan–Meier: overall survival",use_container_width=True)
        with c2:
            p=RESULTS/"figures"/"metabric_kaplan_meier_er.png"
            if p.exists(): st.image(str(p),caption="Kaplan–Meier: survival by ER status",use_container_width=True)
        cox=RESULTS/"tables"/"metabric_cox_results.csv"
        if cox.exists(): st.dataframe(pd.read_csv(cox),use_container_width=True,hide_index=True)
        st.caption("The C-index is calculated on a held-out test partition. Cox coefficients are statistical associations; they do not establish causality or patient-specific prognosis.")
    else: st.error("Survival artifacts are missing. Run scripts/train_and_report.py.")
    st.markdown("### Interactive Kaplan–Meier")
    group=st.selectbox("Group by",["None","tumor_stage","neoplasm_histologic_grade","er_status","her2_status"])
    if st.button("Build curve"):
        try:
            result=kaplan_meier_from_metabric(str(METABRIC_CSV),None if group=="None" else group)
            rows=[{**p,"group":c["group"]} for c in result["curves"] for p in c["points"]]
            if rows: st.plotly_chart(px.line(pd.DataFrame(rows),x="time_months",y="survival",color="group",template="plotly_white"),use_container_width=True)
        except Exception as exc: st.error(str(exc))

with tabs[4]:
    st.markdown('<div class="kicker">Data engineering</div>', unsafe_allow_html=True)
    st.subheader("ETL, normalization and provenance")
    st.write("The real-data ETL layer remains available for reproducible ingestion of documented public or institutionally authorized datasets.")
    st.code("python scripts/download_real_data.py wisconsin\npython scripts/download_real_data.py metabric\npython scripts/train_real_models.py --wisconsin data/raw/wisconsin/breast_cancer_wisconsin_diagnostic.csv --metabric 'data/raw/metabric/Breast Cancer METABRIC.csv'")
    st.dataframe(pd.DataFrame({"Dataset":["Wisconsin Diagnostic","METABRIC"],"Rows":[len(wisconsin),len(metabric)],"Missing cells":[int(wisconsin.isna().sum().sum()),int(metabric.isna().sum().sum())]}),use_container_width=True,hide_index=True)
    st.info("Pan-cancer source access is deliberately separated from the bundled real cohorts. The application never treats an inaccessible CancerSEEK workbook as if it were present.")

with tabs[5]:
    st.markdown('<div class="kicker">Computer vision</div>', unsafe_allow_html=True)
    st.subheader("Medical imaging research extension")
    st.write("Image upload and quality inspection are implemented. A validated multi-cancer histopathology classifier is not claimed in this build.")
    image=st.file_uploader("Upload a research image for QC",type=["png","jpg","jpeg"])
    if image:
        from PIL import Image
        im=Image.open(image); st.image(im,use_container_width=True); st.json({"width":im.width,"height":im.height,"mode":im.mode,"format":im.format})

with tabs[6]:
    st.markdown('<div class="kicker">Research workspace</div>', unsafe_allow_html=True)
    st.subheader("Literature and trial discovery")
    q=st.text_input("Research topic")
    if q:
        c1,c2=st.columns(2)
        with c1:
            if st.button("Search PubMed"):
                try:
                    from oncoverse.integrations.public_sources import pubmed_search
                    st.dataframe(pd.DataFrame(pubmed_search(q,10)),use_container_width=True,hide_index=True)
                except Exception as exc: st.error(str(exc))
        with c2:
            if st.button("Search clinical trials"):
                try:
                    from oncoverse.integrations.public_sources import clinical_trials
                    st.dataframe(pd.DataFrame(clinical_trials(q,10).get("studies",[])),use_container_width=True,hide_index=True)
                except Exception as exc: st.error(str(exc))

with tabs[7]:
    st.markdown('<div class="kicker">Responsible research</div>', unsafe_allow_html=True)
    st.subheader("Governance and limitations")
    st.markdown("""
- **Multi-cancer evidence:** CancerSEEK cohort counts and published performance are source-derived summaries, not OncoVerse model metrics.
- **Patient-level ML:** only the bundled Wisconsin and METABRIC models produce patient-level research outputs in this offline build.
- **No fabricated survival:** survival curves use observed METABRIC follow-up; the old synthetic survival route is not used.
- **Held-out evaluation:** model and Cox metrics are reported on held-out data where applicable.
- **No diagnosis or treatment:** outputs are academic research results, not clinical decisions.
- **Data provenance:** source names and limitations are retained with the project; check licenses before redistribution.
    """)
