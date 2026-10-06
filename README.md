# 🧬 OncoVerse — Multi-Cancer Intelligence Platform

> **A research-oriented cancer data engineering and AI platform for multi-cancer evidence exploration, patient-level machine learning, explainable AI, and survival analysis.**

[![Python](https://img.shields.io/badge/Python-3.x-blue?logo=python)](https://www.python.org/)
[![XGBoost](https://img.shields.io/badge/ML-XGBoost-orange)](https://xgboost.readthedocs.io/)
[![Streamlit](https://img.shields.io/badge/Dashboard-Streamlit-red?logo=streamlit)](https://streamlit.io/)
[![FastAPI](https://img.shields.io/badge/API-FastAPI-009688?logo=fastapi)](https://fastapi.tiangolo.com/)
[![SHAP](https://img.shields.io/badge/Explainability-SHAP-purple)](https://shap.readthedocs.io/)
[![Airflow](https://img.shields.io/badge/Orchestration-Airflow-017CEE?logo=apacheairflow)](https://airflow.apache.org/)

## 📌 Overview

**OncoVerse** is a research-focused multi-cancer intelligence platform that combines **data engineering, machine learning, explainable AI, survival analysis, research discovery, and interactive analytics** into a single system.

The platform is designed around two distinct evidence layers:

1. **Pan-cancer research evidence** derived from published CancerSEEK study results covering eight cancer types.
2. **Real patient-level public datasets** used to build and evaluate research-oriented machine learning and survival models.

The project deliberately separates published study-level evidence from independently trained model results to maintain clear data provenance and avoid presenting synthetic or unavailable patient-level data as real observations.

---

## 🚀 Key Features

### 🧬 Multi-Cancer Research Intelligence

OncoVerse provides study-level evidence exploration across eight cancer types:

- Breast
- Colorectum
- Esophagus
- Liver
- Lung
- Ovary
- Pancreas
- Stomach

The CancerSEEK evidence layer contains published cohort-level information rather than fabricated patient records.

### 🤖 Machine Learning

The platform includes research models trained on real public datasets:

- **Breast Cancer Wisconsin Diagnostic**
  - Benign vs malignant classification
  - XGBoost
  - Held-out evaluation

- **METABRIC**
  - Derived 5-year research endpoint
  - XGBoost classification
  - Held-out evaluation

### 🔍 Explainable AI

The project uses **SHAP (SHapley Additive exPlanations)** to provide feature-level explanations for trained XGBoost models.

This helps researchers understand:

- Which features influence predictions
- Feature importance
- Direction and magnitude of feature contributions
- Model decision behavior

### 📈 Survival Analysis

The METABRIC cohort is used for survival analysis including:

- Kaplan–Meier survival curves
- ER-stratified survival analysis
- Cox proportional-hazards analysis
- Held-out concordance index (C-index)

The Cox feature set deliberately excludes the Nottingham Prognostic Index because it is constructed from tumour characteristics represented by related predictors.

### 📊 Interactive Dashboard

A Streamlit dashboard provides an interactive interface for exploring:

- Pan-cancer evidence
- Cohort information
- Model predictions
- Model performance
- SHAP explanations
- Survival analysis
- Research results

### ⚡ Research API

OncoVerse includes a **FastAPI-based research API** for programmatic access to platform functionality.

### 🔬 Research Discovery

The platform also includes integrations for:

- PubMed research discovery
- Clinical-trial discovery
- Public cancer datasets
- FHIR-based healthcare data integration

### 🖼️ Imaging Extension

The project contains an imaging/QC extension designed to support image-based research workflows.

### 🔄 Data Engineering & ETL

The project includes:

- Data ingestion
- Data normalization
- ETL pipelines
- Database integration
- Dataset validation
- Research data processing

Optional orchestration infrastructure is provided using **Apache Airflow** and **Kafka** components.

---

## 🏗️ System Architecture

```text
                    ┌─────────────────────────┐
                    │ Published CancerSEEK   │
                    │ Multi-Cancer Evidence  │
                    └────────────┬────────────┘
                                 │
                                 ▼
                    ┌─────────────────────────┐
                    │ Pan-Cancer Evidence     │
                    │ Exploration              │
                    └─────────────────────────┘


      ┌─────────────────────┐       ┌─────────────────────┐
      │ Wisconsin Diagnostic │       │      METABRIC       │
      │ Public Dataset       │       │    Public Dataset   │
      └──────────┬──────────┘       └──────────┬──────────┘
                 │                             │
                 └──────────────┬──────────────┘
                                ▼
                    ┌─────────────────────────┐
                    │      ETL Pipeline       │
                    │ Validation & Processing │
                    └────────────┬────────────┘
                                 │
                ┌────────────────┴────────────────┐
                ▼                                 ▼
      ┌──────────────────┐             ┌──────────────────┐
      │ XGBoost Models   │             │ Survival Models  │
      │ Classification   │             │ KM + Cox         │
      └────────┬─────────┘             └────────┬─────────┘
               │                                │
               ▼                                ▼
      ┌──────────────────┐             ┌──────────────────┐
      │ SHAP Explainable │             │ Survival Analysis│
      │ AI               │             │ & C-index        │
      └────────┬─────────┘             └────────┬─────────┘
               │                                │
               └───────────────┬────────────────┘
                               ▼
                    ┌─────────────────────────┐
                    │    OncoVerse Platform   │
                    ├─────────────────────────┤
                    │ Streamlit Dashboard     │
                    │ FastAPI Research API    │
                    │ Research Discovery      │
                    │ Analytics               │
                    └─────────────────────────┘
```

---

## 🛠️ Technology Stack

| Area | Technologies |
|---|---|
| Programming | Python |
| Machine Learning | XGBoost |
| Explainable AI | SHAP |
| Data Processing | Pandas, NumPy |
| Visualization | Matplotlib / Streamlit |
| Dashboard | Streamlit |
| API | FastAPI |
| Survival Analysis | Kaplan–Meier, Cox Proportional Hazards |
| Database | SQLite / PostgreSQL support |
| Data Engineering | ETL pipelines, normalization |
| Orchestration | Apache Airflow |
| Streaming | Kafka components |
| Healthcare Integration | FHIR |
| Research Discovery | PubMed / Clinical Trials |
| Testing | Pytest |
| Deployment | Docker / Docker Compose |

---

## 📂 Project Structure

```text
OncoVerse/
│
├── oncoverse/
│   ├── integrations/
│   │   ├── fhir.py
│   │   ├── public_sources.py
│   │   └── datasets.py
│   │
│   ├── real_data/
│   │   ├── institutional.py
│   │   ├── kaggle.py
│   │   ├── multiomics.py
│   │   ├── normalization.py
│   │   └── pipeline.py
│   │
│   ├── api.py
│   ├── analytics.py
│   ├── discovery.py
│   ├── etl.py
│   ├── explain.py
│   ├── image_model.py
│   ├── imaging.py
│   ├── real_db.py
│   ├── real_model.py
│   ├── real_survival.py
│   ├── survival.py
│   ├── streaming.py
│   └── ...
│
├── dashboard/
│   └── app.py
│
├── models/
│   └── real/
│       ├── metabric_5y_xgb.joblib
│       ├── wisconsin_xgb.joblib
│       ├── metabric_5y_metrics.json
│       └── wisconsin_metrics.json
│
├── data/
│   ├── raw/
│   │   ├── metabric/
│   │   └── wisconsin/
│   └── processed/
│
├── results/
│   ├── figures/
│   ├── tables/
│   ├── RESULTS_SUMMARY.md
│   └── results_manifest.json
│
├── notebooks/
│   └── oncoverse_walkthrough.ipynb
│
├── tests/
│   ├── test_core.py
│   ├── test_km_fix.py
│   └── conftest.py
│
├── orchestration/
│   └── airflow/
│
├── scripts/
│   ├── train_real_models.py
│   ├── train_and_report.py
│   ├── download_real_data.py
│   └── run_dashboard.sh
│
├── docs/
│   ├── PROJECT_REPORT.md
│   ├── USER_GUIDE.md
│   ├── DATA_DICTIONARY.md
│   ├── ETHICS_AND_LIMITATIONS.md
│   └── ...
│
├── docker-compose.yml
├── requirements.txt
├── requirements-dev.txt
├── .gitignore
└── README.md
```

---

## 📊 Datasets

### Breast Cancer Wisconsin Diagnostic

Used for research-oriented binary classification:

```text
Benign vs Malignant
```

The model is trained and evaluated using held-out data.

### METABRIC

Used for:

- Survival analysis
- Kaplan–Meier estimation
- Cox proportional-hazards analysis
- Derived 5-year research endpoint
- XGBoost-based prediction

Patients censored before the five-year endpoint are excluded from the derived binary endpoint rather than being incorrectly assigned a class.

### CancerSEEK

The platform includes published study-level evidence from the CancerSEEK study covering:

- 1,005 cancer patients
- 812 healthy controls
- 8 cancer types
- 39 serum protein biomarkers

These published figures are treated as **source-study benchmarks**, not OncoVerse model results.

---

## 📈 Model Evaluation

The repository contains generated evaluation artifacts including:

- ROC curves
- Confusion matrices
- Classification reports
- SHAP feature importance
- Kaplan–Meier curves
- ER-stratified survival curves
- Cox survival analysis
- C-index results

All metrics are intended for **academic and research evaluation**, not clinical validation.


## 🔍 Example Results

Generated results are available under:

```text
results/
├── figures/
└── tables/


Example artifacts include:

```text
metabric_5y_xgboost_roc_curve.png
metabric_5y_xgboost_shap_importance.png
metabric_kaplan_meier.png
metabric_kaplan_meier_er.png
wisconsin_xgboost_confusion_matrix.png
wisconsin_xgboost_roc_curve.png
wisconsin_xgboost_shap_importance.png


## ⚙️ Installation

### 1. Clone the repository

```bash
git clone https://github.com/YOUR_USERNAME/OncoVerse.git
cd OncoVerse
```

### 2. Create a virtual environment

```bash
python -m venv .venv
```

### 3. Activate the environment

**macOS / Linux**

```bash
source .venv/bin/activate
```

**Windows**

```bash
.venv\Scripts\activate


### 4. Install dependencies

```bash
pip install -r requirements.txt


For development:

```bash
pip install -r requirements-dev.txt


## ▶️ Running the Project

### Train the research models

```bash
python scripts/train_real_models.py \
  --wisconsin data/raw/wisconsin/breast_cancer_wisconsin_diagnostic.csv \
  --metabric "data/raw/metabric/Breast Cancer METABRIC.csv"
```

### Run validation

```bash
python scripts/verify_presentation_build.py


### Run tests

bash
python -m pytest -q


### Launch the Streamlit dashboard

```bash
python -m streamlit run dashboard/app.py

The terminal will provide the local dashboard URL.

## 🧪 Testing

The project includes automated tests using **Pytest**.


python -m pytest -q


Tests cover core functionality and survival-analysis behavior.


## 🐳 Docker

Docker Compose configurations are included for local infrastructure and optional services.

bash
docker compose up


Additional configurations are available for:

- Airflow
- Kafka
- Supporting infrastructure

## 🔬 Research & Academic Scope

OncoVerse is intended to demonstrate how modern data engineering and AI techniques can be combined into a healthcare research platform.

The project focuses on:

- Cancer data integration
- Data preprocessing and normalization
- Machine learning
- Explainable AI
- Survival analysis
- Research data exploration
- Reproducible analytics
- Healthcare data interoperability


## ⚠️ Ethics & Limitations

**OncoVerse is academic/research software and is not a medical device.**

It does **not** provide:

- Medical diagnosis
- Treatment recommendations
- Individualized clinical-risk advice
- Clinical screening decisions

Model performance should not be interpreted as clinical validation.

Published CancerSEEK results are explicitly separated from metrics generated by the OncoVerse models.

The platform is designed to maintain clear data provenance and avoid presenting unavailable or synthetic patient-level data as real clinical observations.

For additional information, see:


docs/ETHICS_AND_LIMITATIONS.md

## 🗺️ Future Development

Potential future extensions include:

- Additional cancer datasets
- Multi-omics integration
- Larger-scale survival modeling
- Advanced imaging models
- Additional clinical-trial integrations
- Real-time research data pipelines
- Cloud deployment
- MLOps monitoring
- Model versioning
- Federated healthcare data workflows

## 👨‍💻 Project

**OncoVerse** was developed as a final-year academic project exploring the intersection of:

**Data Engineering + Artificial Intelligence + Healthcare Analytics**

### Core Areas

Data Engineering
        +
Machine Learning
        +
Explainable AI
        +
Survival Analysis
        +
Healthcare Data
        =
OncoVerse

> **Disclaimer:** OncoVerse is intended exclusively for academic and research purposes. It should not be used as a substitute for professional medical advice, diagnosis, or treatment.
