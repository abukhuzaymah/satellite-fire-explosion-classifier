# ML Model Notes

## Objective
Classify satellite thermal anomaly time-series over Gaza into fire vs explosion events with explainability.

## Data & Features
- Source: NASA FIRMS (VIIRS/MODIS)
- Aggregation: ~1km grid, 3-hour windows (configurable)
- Features (starter): max/mean/std FRP, spike rise/decay, duration above threshold, count

## Labels
- Start with heuristic/weak labels.
- Improve using external reports/imagery when available.

## Models
- Baseline: heuristic (in API)
- Supervised: RandomForest (tabular); later LSTM/1D-CNN if enough data

## Evaluation
- Stratified temporal split
- Metrics: precision/recall/F1 for explosion class, AUROC/PR
- Explainability: SHAP values for feature importances

## Ethics & Risks
- Communicate uncertainty; provide confidence scores
- Avoid overclaiming; explosions are difficult to confirm from thermal alone
- Document limitations and potential biases

## Usage
- Train using `notebooks/eda_train.ipynb` and save to `model/model_rf.pkl`
- API loads model if available; otherwise uses heuristic