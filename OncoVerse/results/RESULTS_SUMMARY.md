# OncoVerse Results Summary

## Pan-cancer published evidence
The dashboard summarizes the published CancerSEEK cohort:

- 1,005 cancer patients
- 812 healthy controls
- 8 cancer types
- 39 protein biomarkers
- Published median cancer detection sensitivity: 70%
- Published specificity: >99%
- Published median localization to two anatomic sites: 83%
- Published median localization to one anatomic site: 63%

These are **source-study benchmarks**, not OncoVerse model metrics.

## Wisconsin Diagnostic
The bundled model is a held-out benign-vs-malignant research classifier. The metrics file contains the test-set accuracy, ROC-AUC, precision, recall, F1 and majority-class baseline.

## METABRIC 5-year endpoint
The bundled model uses an observed-follow-up-derived endpoint: deceased by 60 months versus observed 5-year survivors, with patients censored before 60 months excluded.

## METABRIC survival
Kaplan–Meier curves use observed overall-survival follow-up. The Cox C-index is evaluated on a held-out test partition. The Cox feature set deliberately excludes Nottingham prognostic index because it is constructed from tumour characteristics represented by related predictors.

All metrics are research/academic results and are not clinical validation.
