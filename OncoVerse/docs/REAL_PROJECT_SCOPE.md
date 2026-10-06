# OncoVerse Multi-Cancer Scope

The active presentation build is a **multi-cancer research platform** with two explicitly separated evidence layers.

| Requirement | Active implementation |
|---|---|
| Multi-cancer scope | Published CancerSEEK cohort summary covering 8 cancer types |
| Real patient-level data | Wisconsin Diagnostic + METABRIC bundled cohorts |
| ETL | `oncoverse/real_data/` + `oncoverse/real_db.py` |
| Prediction | Held-out XGBoost models for real bundled cohorts |
| Explainability | SHAP for trained XGBoost models |
| Survival | Observed METABRIC Kaplan–Meier + held-out Cox C-index |
| Dashboard | `dashboard/app.py` |
| API | `oncoverse/api.py` |
| Research discovery | PubMed + clinical-trial integrations |
| Imaging | Image upload / QC extension |
| Orchestration | Airflow/Kafka components retained as optional infrastructure |

## Pan-cancer evidence source

The pan-cancer layer is based on the published CancerSEEK study. It stores study-level cohort counts, stage distribution, demographics and published benchmark figures. It does **not** contain individual CancerSEEK observations.

This separation is intentional: inaccessible or unbundled patient-level data must never be replaced by synthetic rows and then presented as real research data.
