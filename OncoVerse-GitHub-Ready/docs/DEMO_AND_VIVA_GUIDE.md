# Presentation and Viva Guide

## Recommended flow

1. Open **Overview** and explain the eight-cancer scope.
2. Open **Pan-Cancer Evidence** and distinguish published CancerSEEK results from OncoVerse results.
3. Open **AI Prediction → Wisconsin** and enter a real-data-range feature vector manually.
4. Show the model probability and individual SHAP explanation.
5. Open **METABRIC 5-year endpoint** and explain the observed-follow-up endpoint definition.
6. Open **Survival** and explain Kaplan–Meier plus the held-out Cox C-index.
7. Show **Data Engineering** and the provenance/ETL layer.
8. Finish with **Governance** and explain why the application does not claim clinical validation.

## Key viva distinction

The eight-cancer layer is a source-derived research benchmark. The bundled patient-level models are trained on Wisconsin and METABRIC. Do not state that OncoVerse trained a new CancerSEEK eight-class model unless the individual CancerSEEK workbook has actually been obtained and the training run has been completed.
