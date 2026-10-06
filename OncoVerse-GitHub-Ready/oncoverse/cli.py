import argparse,json,os
from pathlib import Path

def main():
    parser=argparse.ArgumentParser(prog="oncoverse")
    sub=parser.add_subparsers(dest="command",required=True)
    sub.add_parser("pancancer-benchmark",help="print the published eight-cancer cohort summary")
    w=sub.add_parser("train-wisconsin",help="train the real Wisconsin XGBoost model"); w.add_argument("csv")
    m=sub.add_parser("train-metabric",help="train the real METABRIC 5-year XGBoost model"); m.add_argument("csv")
    s=sub.add_parser("survival",help="compute observed METABRIC Kaplan–Meier curves"); s.add_argument("--csv",default="data/raw/metabric/Breast Cancer METABRIC.csv"); s.add_argument("--group-by",choices=["all","tumor_stage","neoplasm_histologic_grade","er_status","her2_status"],default="all")
    sub.add_parser("summary",help="print local aggregate cohort counts")
    report=sub.add_parser("export-report",help="write the active aggregate research report"); report.add_argument("--output",default="reports/oncoverse_summary.html")
    trials=sub.add_parser("trials",help="search ClinicalTrials.gov"); trials.add_argument("query"); trials.add_argument("--limit",type=int,default=10)
    pubmed=sub.add_parser("pubmed",help="search PubMed"); pubmed.add_argument("query"); pubmed.add_argument("--limit",type=int,default=10)
    args=parser.parse_args()
    if args.command=="pancancer-benchmark":
        from .pancancer_benchmark import load_benchmark; result=load_benchmark()
    elif args.command=="train-wisconsin":
        from .real_model import train_wisconsin; result=train_wisconsin(args.csv)
    elif args.command=="train-metabric":
        from .real_model import train_metabric_5y; result=train_metabric_5y(args.csv)
    elif args.command=="survival":
        from .real_survival import kaplan_meier_from_metabric
        result=kaplan_meier_from_metabric(args.csv,None if args.group_by=="all" else args.group_by)
    elif args.command=="summary":
        from .analytics import summary; result=summary()
    elif args.command=="export-report":
        from .reports import export_report; result=export_report(args.output)
    elif args.command=="trials":
        from .integrations.public_sources import clinical_trials; result=clinical_trials(args.query,args.limit)
    elif args.command=="pubmed":
        from .integrations.public_sources import pubmed_search; result=pubmed_search(args.query,args.limit)
    else: raise SystemExit("Unsupported command")
    print(json.dumps(result,indent=2,default=str))

if __name__=="__main__": main()
