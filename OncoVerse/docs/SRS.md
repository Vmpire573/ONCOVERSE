# Software Requirements Specification — OncoVerse Multi-Cancer

## Purpose
Provide a research dashboard that combines multi-cancer evidence with real public cohort analytics and explainable ML.

## Functional requirements
1. Display an eight-cancer research scope.
2. Display source-derived CancerSEEK cohort counts and published benchmark metrics.
3. Load real Wisconsin and METABRIC datasets.
4. Run held-out XGBoost research models.
5. Provide SHAP explanations for model outputs.
6. Provide observed Kaplan–Meier survival analysis.
7. Report a held-out Cox C-index.
8. Expose real-data analytics through FastAPI.
9. Provide ETL and provenance controls.
10. Keep synthetic legacy components outside the active presentation workflow.

## Non-functional requirements
- Reproducible local execution.
- Explicit source provenance.
- No hidden example patient.
- No fabricated survival endpoint.
- No clinical diagnosis or treatment claims.
