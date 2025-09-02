<<<<<<< HEAD

````markdown
# Satellite Fire vs Explosion Classifier

🚀 **Detect and classify fires vs explosions in satellite thermal data (VIIRS/MODIS)**

This project provides a machine learning pipeline to analyze geospatial thermal time-series data from satellites, distinguishing between fires and explosions. It includes preprocessing, ML-based classification, an API for predictions, and a dashboard for visualization — all in real-time.

---

## 🌟 Features
- Process VIIRS and MODIS satellite thermal imagery
- Geospatial tiling & time-series preprocessing
- Machine learning classification: fire vs explosion
- API for automated predictions
- Interactive dashboard for visualization
- Open-source and extensible for research & applications

---

## ⚡ Quick Start

### 1. Clone the repository
```bash
git clone https://github.com/your-username/satellite-fire-explosion-classifier.git
cd satellite-fire-explosion-classifier
````

### 2. Install dependencies

```bash
python -m venv venv
source venv/bin/activate  # Linux/Mac
venv\Scripts\activate     # Windows
pip install -r requirements.txt
```

### 3. Run the pipeline

* **Preprocess data:**

```bash
python src/preprocess.py
```

* **Train the model:**

```bash
python src/train_model.py
```

* **Run the API:**

```bash
python api/app.py
```

* **View dashboard:**
  Open `dashboard/index.html` in your browser

---

## 🛠️ Contributing

We welcome contributions!

1. Fork the repo
2. Create a branch: `git checkout -b feature/my-feature`
3. Commit changes: `git commit -m "Add feature"`
4. Push and open a Pull Request

See `CONTRIBUTING.md` for more details.

---

## 📂 Repository Structure

```
├── data/           # Sample or download scripts
├── notebooks/      # Jupyter notebooks for exploration
├── src/            # Core preprocessing & ML code
├── api/            # API scripts
├── dashboard/      # Visualization dashboard
├── requirements.txt
├── README.md
└── LICENSE
=======
# Gaza Satellite Time-Series Classifier: Fires vs Explosions (Open Source)

## Quick Start

1. Clone the repo:
   ```bash
   git clone https://github.com/your-org/gaza-fires-explosions.git
   cd gaza-fires-explosions
   ```
2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
3. Add your NASA FIRMS API key to a `.env` file:
   ```
   MAP_KEY=your_nasa_firms_api_key_here
   ```
4. Run the data fetcher:
   ```bash
   python fetch_hotspots.py
   ```
5. Start the web server:
   ```bash
   python app.py
   ```
6. Open [http://localhost:5000](http://localhost:5000) in your browser.

---

> **Note:** Do not commit your `.env` file or API keys to public repositories. `.env` is already in `.gitignore`.

---

## Cloud & Container Deployment
- You can deploy this app on cloud platforms (Heroku, DigitalOcean, AWS, etc.) or containerize it with Docker.
- For static frontend hosting, consider Netlify or Vercel. For full-stack, deploy Flask on a cloud server.

---

## Contributing

Contributions are welcome! Please see [CONTRIBUTING.md](CONTRIBUTING.md) for guidelines.

---

## Architecture Overview

<!-- Removed broken Mermaid diagram -->

---

## System Components

Recommended repository structure:

```
project-root/
  data/                 # optional sample data (placeholders)
  docs/                 # MODEL.md, ARCHITECTURE.md, etc.
  model/                # trained models, utils
  notebooks/            # EDA/training notebooks
  src/                  # future: library modules (pipeline/modeling)
  app.py                # API server
  fetch_hotspots.py     # data fetcher
  index.html            # demo map UI
  requirements.txt      # dependencies
  README.md             # this file
  LICENSE, CONTRIBUTING.md, CODE_OF_CONDUCT.md
```

### 1. **Data Pipeline** (`fetch_hotspots.py`)
- **Automated fetcher**: Downloads VIIRS and MODIS fire data every 15 minutes (cron or daemon)
- **Outputs**: `hotspots_viirs.csv`, `hotspots_modis.csv`, `fetch_status.json`, and `fetcher.log`
- **Logging**: All actions and errors are logged to `fetcher.log` (rotating file, also stdout)
- **Status**: Writes `fetch_status.json` with status, timestamp, and message after each run
- **Testing**: Modular, type-annotated, and ready for unit testing
 - **Geography**: Defaults to Gaza bbox; configurable via `.env`

### 2. **API Layer** (`app.py`)
- **Flask server**: Serves RESTful endpoints
    - `/hotspots?model=viirs|modis` (GeoJSON)
    - `/fetch_status` (JSON)
    - `/logs` (plain text, last 200 lines of both logs)
    - `/predict?model=viirs|modis&from=...&to=...&bbox=lon_min,lat_min,lon_max,lat_max&window_minutes=180` (GeoJSON incidents with `event_type` and `confidence`)
- **Logging**: All API actions and errors are logged to `api.log` (rotating file, also stdout)
- **CORS**: Enabled for public access
- **Error Handling**: Robust 404/500 handlers
- **Testing**: Modular, type-annotated, and ready for unit testing
 - **ML**: Uses an optional trained RandomForest model (if available) with heuristic fallback

### 3. **Web Interface** (`index.html`)
- **Modern, accessible UI**: Google/Material/Apple/Netflix-inspired, responsive, ARIA, keyboard nav
- **Map**: Leaflet.js with VIIRS/MODIS toggle, time slider, playback, provenance, etc.
- **Legend**: Fully interactive, Material-style legend with:
    - Clickable items to toggle map layers (current, recent, spread path, highest FRP, decreasing FRP, risk buffer)
    - Info icons (ℹ) for every legend item, opening detailed modals explaining each map symbol and its significance
    - Custom icons for each item, including a buffer+hotspot icon for risk buffer
- **Info Modals**: Each legend item has a dedicated, accessible modal with:
    - Clear definition, visual characteristics, data significance, and usage tips
    - Color-coded headers and sections
    - Emergency and operational guidance
    - Consistent, modern design
- **Risk Buffer**: 1km red translucent circle around each hotspot, with a new icon in the legend and a detailed info modal
- **Spread Path**: Directional arrows and color-coded lines show fire movement; toggled together from the legend
- **Decreasing FRP**: Green glow and down arrow for dying-out fires, with legend and info modal
- **Highest FRP**: Blue glow and star badge for the most intense fire, with legend and info modal
- **Live Log Popup**: Floating button opens a modal showing live logs from `/logs` (polls every 5s)
- **All times in local timezone display**
- **No unused code or overlays**

---

## Logging & Monitoring

- **Fetcher logs**: `fetcher.log` (rotating, in project root)
- **API logs**: `api.log` (rotating, in project root)
- **Live logs**: `/logs` endpoint streams last 200 lines of both logs
- **Frontend log popup**: Click the 📝 button (bottom right) to view live system logs in the browser
- **Status**: `/fetch_status` endpoint and sidebar card show last fetch status

---

## Data Freshness and Detection Logic

- **Last fetch**: This is the time your system last checked for new fire data from NASA FIRMS (shown as 'Data Pipeline Healthy' or 'Last fetch'). It indicates when the data pipeline was last run, not when a fire was last detected.
- **Recent Fire Detection Times**: These are the timestamps of the most recent fire detections in the downloaded data. They reflect when NASA satellites last observed a fire in the area, not when your system fetched the data.

**Important:**
- If there are no new fires detected by NASA, the 'Recent Fire Detection Times' will remain unchanged, even as the 'Last fetch' time updates with each successful data pipeline run.
- The app now hides all hotspots and displays a popup message ('No fires detected!') if there are no recent fire detections in the data. This ensures the map only shows active or very recent fires, and avoids displaying outdated hotspots.

---

## Getting Started

### 1. Prerequisites
- Python 3.8+
- NASA FIRMS API key (register at https://firms.modaps.eosdis.nasa.gov/api)
- Web browser with JavaScript enabled

### 2. Install Dependencies
```bash
pip install requests pandas flask flask-cors numpy scikit-learn python-dotenv joblib
```

### 3. Data Fetching
```bash
python fetch_hotspots.py
```
This will download the latest fire data and update logs/status.

### 4. Start the Web Server
```bash
python app.py
```
The web interface will be available at `http://localhost:5000`

### 5. Automation (Recommended)
Set up a cron job to run the fetcher every 15 minutes:
```
*/15 * * * * cd /path/to/project && /path/to/venv/bin/python fetch_hotspots.py >> fetch_cron.log 2>&1
>>>>>>> 0674c41 (Initial open-source release: Satellite fire vs explosion classifier (FIRMS VIIRS/MODIS))
```

---

<<<<<<< HEAD
## 📄 License

MIT License ©

---

## 🔗 Links

* [Satellite data sources: VIIRS & MODIS](https://nasa.gov)
* [Learn more about thermal anomaly detection](https://en.wikipedia.org/wiki/Fire_detection)


=======
## Key NASA FIRMS Resources & API Endpoints

- [NASA FIRMS Map (Global, 24hrs)](https://firms.modaps.eosdis.nasa.gov/map/)
- [NASA FIRMS Area API Documentation](https://firms.modaps.eosdis.nasa.gov/api/area/)
- [Sample Area API Call (VIIRS, World, 2025-07-11)](https://firms.modaps.eosdis.nasa.gov/api/area/html/3d47c7709150c515edb9beb54ac9832a/VIIRS_SNPP_NRT/world/1/2025-07-11)

---

## Running the System: Required Endpoints & Automation

To run the full wildfire mapping system, ensure the following are running and accessible:

- **Flask API Endpoints:**
    - [http://localhost:5000/hotspots?model=viirs](http://localhost:5000/hotspots?model=viirs)  
      (GeoJSON for VIIRS fire hotspots)
    - [http://localhost:5000/hotspots?model=modis](http://localhost:5000/hotspots?model=modis)  
      (GeoJSON for MODIS fire hotspots)
    - [http://localhost:5000/fetch_status](http://localhost:5000/fetch_status)  
      (JSON status of last data fetch)
    - [http://localhost:5000/logs](http://localhost:5000/logs)  
      (Live logs)
    - [http://localhost:5000/predict?model=viirs](http://localhost:5000/predict?model=viirs)  
      (Incident classification with baseline heuristic; supports `from`, `to`, `bbox`, `window_minutes`)
- **Frontend:**
    - Open `index.html` in your browser (or access via the Flask server if served statically)
- **Backend (optional):**
    - [http://[::]:8000/](http://[::]:8000/)  
      (If running an additional backend service, e.g., for advanced analytics)
- **Automation:**
    - Set up a **cron job** to run `fetch_hotspots.py` every 15 minutes to keep the data fresh and the map up to date. See the 'Getting Started' section above for a sample cron entry.

> **Note:** The Flask API and the data fetcher must be running for the map and endpoints to function correctly. The cron job ensures the latest NASA FIRMS data is always available for the frontend and API.

---

## Environment Configuration

Create a `.env` file in the project root:

```
MAP_KEY=your_nasa_firms_api_key
# Optional: override default Gaza bbox (lon_min,lat_min,lon_max,lat_max)
BBOX=34.2,31.2,34.65,31.6
# Optional: number of days of history to fetch
DAY_RANGE=10
```

The fetcher reads these values at startup. You can also pass a `bbox` to `/predict` for on-the-fly filtering.

---

## ML: Training and Model Usage

- A baseline heuristic classifier is built-in. For higher accuracy:
  - Use the Jupyter notebook in `notebooks/eda_train.ipynb` to engineer features and train a RandomForest.
  - Save the trained model to `model/model_rf.pkl` (default path) or set `MODEL_PATH` in `.env`.
  - The API will automatically use the trained model for `/predict` if present; otherwise it falls back to the heuristic.

### Features used (starter set)
- Max FRP, mean FRP, std FRP
- Peak sharpness (rise/decay), duration above threshold
- Count of observations in window

See `docs/MODEL.md` for notes on labeling, validation, and ethics.

---

## Usage

- **Map**: Open `
```
import webbrowser
import threading

def open_browser():
    webbrowser.open_new('http://localhost:5000/')

if __name__ == '__main__':
    threading.Timer(1.25, open_browser).start()
    app.run()
>>>>>>> 0674c41 (Initial open-source release: Satellite fire vs explosion classifier (FIRMS VIIRS/MODIS))
