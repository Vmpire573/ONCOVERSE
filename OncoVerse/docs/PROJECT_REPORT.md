# OncoVerse — Project Report Summary

## Abstract
OncoVerse is a research-oriented multi-cancer intelligence platform combining published pan-cancer evidence with real public cancer cohorts. The system provides ETL, provenance, XGBoost research models, SHAP explanations, observed survival analysis, a FastAPI service and a Streamlit dashboard.

The multi-cancer evidence layer is based on the published CancerSEEK cohort, which evaluated eight cancer types. Because the individual supplementary workbook is not bundled in this build, the application stores only source-derived study-level cohort information and published benchmark values. Patient-level predictions are generated only from the real Wisconsin Diagnostic and METABRIC datasets bundled with the repository.

## Objectives
- Integrate heterogeneous cancer research sources.
- Provide an eight-cancer research view.
- Train reproducible real-data XGBoost models.
- Provide explainable model outputs.
- Perform observed survival analysis without fabricated follow-up.
- Provide a presentation-ready research dashboard and API.

## Data
### Published pan-cancer evidence
CancerSEEK: 1,005 cancer patients and 812 healthy controls across breast, colorectal, esophageal, liver, lung, ovarian, pancreatic and stomach cancers. The source study reported 39 protein biomarkers and published detection/localization benchmarks.

### Real bundled cohorts
Wisconsin Diagnostic is used for benign/malignant classification. METABRIC is used for observed survival and a derived 5-year endpoint.

## Modelling
XGBoost models use a fixed random seed and a stratified holdout split. Preprocessing is fit on the training partition and applied to the test partition. Metrics are stored as JSON and plots/tables are generated reproducibly.

The METABRIC 5-year endpoint treats death by 60 months as an event and excludes observations censored before 60 months. Patients observed at or beyond 60 months without death are treated as 5-year survivors for this research endpoint.

## Survival analysis
Kaplan–Meier estimates use observed METABRIC follow-up. Cox regression is fit on a training partition and the C-index is evaluated on a held-out partition. Nottingham prognostic index is excluded from the Cox feature set because it is derived from related tumour characteristics, reducing direct redundancy.

## Presentation design
The active dashboard has no Demo Mode, no hidden example patient and no fabricated survival route. The distinction between published study evidence and OncoVerse-generated model metrics is visible in the UI.

## Limitations
- The CancerSEEK individual-level supplementary workbook is not bundled, so no new eight-class CancerSEEK patient-level model is claimed.
- Wisconsin and METABRIC are breast-focused datasets; they do not constitute external validation across all eight cancer types.
- Metrics are research results and not clinical validation.
- Imaging is limited to image QC in this build.
- Institutional deployment requires appropriate governance, de-identification, access control and security review.
