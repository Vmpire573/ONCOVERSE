# OncoVerse — Presentation Demo Checklist

## What is implemented
- Bundled METABRIC dataset: 2,509 records
- Bundled Wisconsin Diagnostic dataset: 569 records
- Stored XGBoost research models for both cohorts
- Held-out model metrics and confusion/ROC/SHAP artifacts
- Kaplan–Meier survival analysis
- Cox proportional-hazards associations
- C-index calculation
- Patient-level prediction with source-data min/max validation
- Load Example Patient + one-click demo workflow
- Individual SHAP explanation automatically shown after prediction
- Medical Imaging image upload + quality inspection

## What is intentionally not claimed
- No diagnosis or treatment recommendation
- No clinical validation claim
- No external validation/calibration claim
- No trained histopathology classifier bundled in this presentation build

## Fast start on macOS
```bash
cd /path/to/OncoVerse-Real-Project
bash scripts/run_dashboard.sh
```

## Presentation flow
1. **Overview** — show 3,078 bundled public records across two source datasets.
2. **AI Prediction → Patient Demo + SHAP** — keep Demo mode on, click **Load Example Patient**, then run the research prediction.
3. Explain the actual held-out metrics shown on the Wisconsin and METABRIC tabs.
4. **Survival** — explicitly walk through **Kaplan–Meier**, **Cox PH**, and **C-index**.
5. **Medical Imaging** — show the implemented image-QC workflow and the clearly separated planned extension.
6. **Governance** — finish with the research-only boundary and limitations.
