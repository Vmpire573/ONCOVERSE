"""Export a research aggregate report from the active real-data assets."""
import html,json
from pathlib import Path
from .pancancer_benchmark import load_benchmark
from .real_survival import kaplan_meier_from_metabric

ROOT=Path(__file__).resolve().parents[1]
METABRIC=ROOT/"data/raw/metabric/Breast Cancer METABRIC.csv"

def export_report(destination="reports/oncoverse_summary.html"):
    benchmark=load_benchmark(); km=kaplan_meier_from_metabric(str(METABRIC))
    path=Path(destination); path.parent.mkdir(parents=True,exist_ok=True)
    rows="".join(f"<tr><td>{html.escape(str(x['cancer_type']))}</td><td>{x['patients']}</td></tr>" for x in benchmark['cancer_cohort'])
    content=f"""<!doctype html><meta charset='utf-8'><title>OncoVerse Multi-Cancer Research Report</title><style>body{{font:16px system-ui;max-width:1000px;margin:3rem auto;color:#263247}}table{{border-collapse:collapse;width:100%}}td,th{{border:1px solid #ccd2dc;padding:.6rem;text-align:left}}.notice{{background:#eef2ff;padding:1rem}}</style><h1>OncoVerse Multi-Cancer Research Report</h1><p class='notice'><b>Research use only.</b> Published CancerSEEK values are study-level evidence; METABRIC survival is observed cohort analysis.</p><h2>Published pan-cancer cohort</h2><p>{benchmark['cohort_totals']['cancer_patients']} cancer patients + {benchmark['cohort_totals']['healthy_controls']} healthy controls across {benchmark['cohort_totals']['cancer_types']} cancer types.</p><table><tr><th>Cancer type</th><th>Patients</th></tr>{rows}</table><h2>METABRIC survival</h2><pre>{html.escape(json.dumps({k:v for k,v in km.items() if k!='curves'},indent=2))}</pre></html>"""
    path.write_text(content,encoding="utf-8")
    return {"report":str(path.resolve()),"row_level_data_included":False,"warning":"Research aggregate report only."}
