# Architecture Overview

- Data fetcher (`fetch_hotspots.py`): pulls VIIRS/MODIS FIRMS for Gaza (configurable via `.env`).
- API (`app.py`): serves `/hotspots`, `/fetch_status`, `/logs`, and `/predict` (classification).
- Frontend (`index.html`): Leaflet map with Classified Incidents overlay.
- Modeling (`model/utils.py`): feature extraction; API loads optional RF model (`model/model_rf.pkl`).
- Notebooks (`notebooks/eda_train.ipynb`): EDA, training, save model.

Optional package structure for future installs:
- `src/pipeline/`: preprocessing/windowing helpers
- `src/modeling/`: training/inference modules

Config via `.env`:
- `MAP_KEY`, `BBOX`, `DAY_RANGE`, `INTERVAL_MINUTES`, `RUN_ONCE`, `MODEL_PATH`