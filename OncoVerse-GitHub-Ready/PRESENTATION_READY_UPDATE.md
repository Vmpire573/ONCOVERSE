# OncoVerse — Presentation Polish Update

This build includes a presentation-focused dashboard pass.

## Added
- Patient input validation bounded to observed source-dataset ranges for every numeric field.
- No demo-mode toggle or hidden example-patient workflow is included in the active dashboard.
- Predictions require user-entered values bounded to observed source-dataset ranges.
- Individual tree-SHAP explanation automatically shown after a prediction and retained in session state.
- Survival section explicitly organized as:
  1. Kaplan–Meier survival
  2. Cox proportional-hazards associations
  3. Concordance index (C-index)
- Clear research-only wording around predictions, SHAP and survival statistics.
- Presentation-oriented visual theme with gradients, glass cards, metric cards, hover effects and improved spacing.

## Run
```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
streamlit run dashboard/app.py
```

For the Mac XGBoost runtime, install OpenMP if needed:
```bash
brew install libomp
```

## Suggested demo sequence
1. Open **Overview**.
2. Go to **AI Prediction** and enter values from the displayed observed ranges.
3. Click the research prediction button and explain the score and individual SHAP chart.
4. Open **Survival** and walk through Kaplan–Meier, Cox PH and C-index.
5. Open **Medical Imaging** to distinguish implemented image-QC from planned LC25000 training.
6. Finish with **Governance** and the research-only limitations.

## Additional reliability fixes
- Raw METABRIC uploads now recognize the bundled column names such as `Overall Survival (Months)` and `Overall Survival Status`.
- ETL upload detection is case/format tolerant for canonical column names.
- Medical Imaging copy no longer implies a GPU dependency; image-model training remains an explicit planned extension.
- Added `scripts/verify_presentation_build.py` to check that all bundled datasets, trained models and survival artifacts are present before a demo.
