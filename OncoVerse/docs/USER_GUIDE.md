# OncoVerse User Guide

## 1. Install

```bash
python -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt
```

For tests:

```bash
python -m pip install -r requirements-dev.txt
```

## 2. Verify the presentation build

```bash
python scripts/verify_presentation_build.py
python -m pytest -q
```

## 3. Train the bundled real models

```bash
python scripts/train_real_models.py \
  --wisconsin data/raw/wisconsin/breast_cancer_wisconsin_diagnostic.csv \
  --metabric 'data/raw/metabric/Breast Cancer METABRIC.csv'
```

Then refresh survival artifacts:

```bash
python - <<'PY'
from oncoverse.real_survival import run_metabric_survival
print(run_metabric_survival('data/raw/metabric/Breast Cancer METABRIC.csv')['metrics'])
PY
```

## 4. Launch

```bash
python -m streamlit run dashboard/app.py
```

There is no Demo Mode. The patient prediction screens require manually entered feature values and do not display a hidden ground-truth label.

## 5. What the dashboard shows

- **Overview:** multi-cancer scope plus real bundled data assets.
- **Pan-Cancer Evidence:** published CancerSEEK cohort composition and study-level benchmarks.
- **AI Prediction:** real Wisconsin and METABRIC models with individual SHAP explanations.
- **Survival:** observed METABRIC Kaplan–Meier and held-out Cox C-index.
- **Data Engineering:** ETL/provenance workflow.
- **Medical Imaging:** image quality inspection only.
- **Research:** literature and trial discovery.
- **Governance:** explicit scientific limitations.

## 6. Scientific boundary

CancerSEEK published metrics are not OncoVerse metrics. The individual CancerSEEK workbook is not bundled. The platform does not fabricate patient-level multi-cancer rows to fill that gap.
