# Implementation Traceability

| Requirement | Implementation | Verification |
|---|---|---|
| Multi-cancer scope | `data/processed/pancancer_benchmark.json`, `oncoverse/pancancer_benchmark.py` | Dashboard Pan-Cancer Evidence tab |
| Real patient-level ML | `oncoverse/real_model.py` | `models/real/*metrics.json` |
| Explainability | XGBoost contribution/SHAP paths | Dashboard AI Prediction tab |
| Observed survival | `oncoverse/real_survival.py` | KM figures + survival metrics |
| Held-out survival discrimination | train/test Cox split | `cox_concordance_index_test` |
| API | `oncoverse/api.py` | `tests/test_core.py` |
| Presentation verification | `scripts/verify_presentation_build.py` | Required assets + dashboard assertions |
| Automated tests | `tests/test_core.py` | `python -m pytest -q` |

## Deliberate exclusions

The old synthetic model, fabricated survival generator and hidden example-patient workflow are not part of the active dashboard/API path.
