from flask import Flask, jsonify, request, Response, send_from_directory
import pandas as pd
from flask_cors import CORS
import json
import os
import logging
from logging.handlers import RotatingFileHandler
from typing import Dict, Any, List
import webbrowser
import threading
from datetime import datetime

# Simple heuristic classifier utilities (baseline)
import numpy as np
import joblib

app = Flask(__name__)
CORS(app)

API_LOG_FILE = "api.log"
FETCHER_LOG_FILE = "fetcher.log"
LOG_LINES = 200

MODEL_FILES = {
    "viirs": "hotspots_viirs.csv",
    "modis": "hotspots_modis.csv"
}

def setup_logger() -> logging.Logger:
    """Set up a rotating logger for API events."""
    logger = logging.getLogger("api")
    logger.setLevel(logging.INFO)
    handler = RotatingFileHandler(API_LOG_FILE, maxBytes=500_000, backupCount=3)
    formatter = logging.Formatter('%(asctime)s %(levelname)s %(message)s')
    handler.setFormatter(formatter)
    if not logger.handlers:
        logger.addHandler(handler)
    # Also log to stdout
    stream_handler = logging.StreamHandler()
    stream_handler.setFormatter(formatter)
    if not any(isinstance(h, logging.StreamHandler) for h in logger.handlers):
        logger.addHandler(stream_handler)
    return logger

logger = setup_logger()
MODEL_OBJ = None
MODEL_PATH = os.getenv("MODEL_PATH", os.path.join("model", "model_rf.pkl"))
if os.path.exists(MODEL_PATH):
    try:
        MODEL_OBJ = joblib.load(MODEL_PATH)
        logger.info(f"Loaded ML model from {MODEL_PATH}")
    except Exception as e:
        logger.error(f"Failed to load ML model at {MODEL_PATH}: {e}")

@app.route("/hotspots")
def hotspots():
    """Serve fire hotspots as GeoJSON for the requested model."""
    model = request.args.get("model", "viirs").lower()
    csv_file = MODEL_FILES.get(model, MODEL_FILES["viirs"])
    try:
        df = pd.read_csv(csv_file, comment="#")
    except Exception as e:
        logger.error(f"Failed to read {csv_file}: {e}")
        return jsonify({"error": f"Could not read data for model {model}"}), 500
    features = []
    for _, row in df.iterrows():
        # Use correct brightness column for each model
        if model == "viirs":
            brightness = getattr(row, "bright_ti4", None)
        else:  # modis
            brightness = getattr(row, "brightness", None)
        features.append({
            "type": "Feature",
            "geometry": {
                "type": "Point",
                "coordinates": [row.longitude, row.latitude]
            },
            "properties": {
                "acq_date": row.acq_date,
                "acq_time": row.acq_time,
                "brightness": brightness,
                "frp": getattr(row, "frp", None),
                "confidence": getattr(row, "confidence", None),
                "daynight": getattr(row, "daynight", None),
                "wind_direction": getattr(row, "wind_direction", None)
            }
        })
    logger.info(f"Served {len(features)} features for model {model}")
    return jsonify({"type": "FeatureCollection", "features": features})

def parse_timestamp(acq_date: str, acq_time: str) -> datetime:
    try:
        return datetime.strptime(f"{acq_date} {str(acq_time).zfill(4)}", "%Y-%m-%d %H%M")
    except Exception:
        return None

def classify_sequence(frps: List[float], times: List[datetime]) -> Dict[str, float]:
    # If a trained model is present, use features to predict
    if MODEL_OBJ is not None and frps:
        frps_arr = np.array(frps, dtype=float)
        frps_arr[~np.isfinite(frps_arr)] = 0.0
        max_frp = float(frps_arr.max()) if frps_arr.size else 0.0
        mean_frp = float(frps_arr.mean()) if frps_arr.size else 0.0
        std_frp = float(frps_arr.std()) if frps_arr.size else 0.0
        if frps_arr.size >= 3:
            peak_idx = int(frps_arr.argmax())
            left = frps_arr[peak_idx] - frps_arr[max(0, peak_idx-1)]
            right_drop = frps_arr[peak_idx] - frps_arr[min(len(frps_arr)-1, peak_idx+1)]
        else:
            left = 0.0
            right_drop = 0.0
        duration_high = float((frps_arr > 0.25 * max_frp).mean()) if max_frp > 0 else 0.0
        count_obs = float(len(frps_arr))
        X = np.array([[max_frp, mean_frp, std_frp, left, right_drop, duration_high, count_obs]])
        try:
            proba = MODEL_OBJ.predict_proba(X)[0]
            # Assume label order ['explosion','fire'] if available else argmax
            if hasattr(MODEL_OBJ, 'classes_') and 'explosion' in MODEL_OBJ.classes_:
                idx = list(MODEL_OBJ.classes_).index('explosion')
                conf_explosion = float(proba[idx])
                if conf_explosion >= 0.5:
                    return {"event_type": "explosion", "confidence": round(conf_explosion, 2)}
                else:
                    conf_fire = float(max(proba))
                    return {"event_type": "fire", "confidence": round(conf_fire, 2)}
            # Fallback if classes unknown
            label_idx = int(np.argmax(proba))
            label = str(MODEL_OBJ.classes_[label_idx]) if hasattr(MODEL_OBJ, 'classes_') else ('explosion' if label_idx == 0 else 'fire')
            return {"event_type": label, "confidence": round(float(max(proba)), 2)}
        except Exception:
            pass

    # Baseline heuristic: explosions are sharp spikes with quick decay within ~1-3 timesteps
    if not frps:
        return {"event_type": "unknown", "confidence": 0.0}
    frps_arr = np.array(frps, dtype=float)
    if np.all(~np.isfinite(frps_arr)):
        return {"event_type": "unknown", "confidence": 0.0}
    frps_arr[~np.isfinite(frps_arr)] = 0.0
    max_frp = float(frps_arr.max())
    if len(frps_arr) >= 3:
        peak_idx = int(frps_arr.argmax())
        left = frps_arr[peak_idx] - frps_arr[max(0, peak_idx-1)]
        right_drop = frps_arr[peak_idx] - frps_arr[min(len(frps_arr)-1, peak_idx+1)]
        sharp_rise = left > 0.6 * max_frp
        sharp_decay = right_drop > 0.6 * max_frp
        if sharp_rise and sharp_decay:
            conf = min(0.99, 0.5 + (max_frp / (max_frp + 25.0)))
            return {"event_type": "explosion", "confidence": round(conf, 2)}
    # Otherwise treat as fire if persistent signal
    persistence = float(np.mean(frps_arr > 0.25 * max_frp))
    if persistence > 0.5:
        conf = min(0.95, 0.4 + 0.5 * persistence)
        return {"event_type": "fire", "confidence": round(conf, 2)}
    return {"event_type": "unknown", "confidence": 0.3}

@app.route("/predict")
def predict():
    """Return classified incidents aggregated by approximate 1km grid and time window.
    Query params:
      - model: viirs|modis (default viirs)
      - from, to: ISO timestamps (optional)
      - bbox: lon_min,lat_min,lon_max,lat_max (optional, filters points)
      - window_minutes: aggregation window (default 180)
    """
    model = request.args.get("model", "viirs").lower()
    csv_file = MODEL_FILES.get(model, MODEL_FILES["viirs"])
    try:
        df = pd.read_csv(csv_file, comment="#")
    except Exception as e:
        logger.error(f"Failed to read {csv_file}: {e}")
        return jsonify({"error": f"Could not read data for model {model}"}), 500

    if df.empty:
        return jsonify({"type": "FeatureCollection", "features": []})

    # Parse timestamps
    df["timestamp"] = df.apply(lambda r: parse_timestamp(str(r.get("acq_date")), str(r.get("acq_time"))), axis=1)
    df = df[df["timestamp"].notna()].copy()

    # Time filter
    from_iso = request.args.get("from")
    to_iso = request.args.get("to")
    if from_iso:
        try:
            df = df[df["timestamp"] >= datetime.fromisoformat(from_iso.replace("Z", "+00:00"))]
        except Exception:
            pass
    if to_iso:
        try:
            df = df[df["timestamp"] <= datetime.fromisoformat(to_iso.replace("Z", "+00:00"))]
        except Exception:
            pass

    # BBOX filter if provided
    bbox = request.args.get("bbox")
    if bbox:
        try:
            lon_min, lat_min, lon_max, lat_max = [float(x) for x in bbox.split(",")]
            df = df[(df["longitude"].between(lon_min, lon_max)) & (df["latitude"].between(lat_min, lat_max))]
        except Exception:
            pass

    if df.empty:
        return jsonify({"type": "FeatureCollection", "features": []})

    # Choose brightness column
    brightness_col = "bright_ti4" if model == "viirs" else "brightness"
    frp_col = "frp" if "frp" in df.columns else None

    # Approx 1km grid index using rounding of lat/lon
    def grid_key(row):
        return (round(float(row["latitude"]) * 100) / 100.0, round(float(row["longitude"]) * 100) / 100.0)

    df["grid_latlon"] = df.apply(grid_key, axis=1)

    # Windowing by time (group into buckets)
    window_minutes = int(request.args.get("window_minutes", "180"))
    df["time_bucket"] = df["timestamp"].dt.floor(f"{window_minutes}T")

    features = []
    for (cell, t_bucket), g in df.groupby(["grid_latlon", "time_bucket" ]):
        g_sorted = g.sort_values("timestamp")
        times = list(g_sorted["timestamp"]) 
        frps = list(g_sorted[frp_col]) if frp_col else [0.0] * len(times)
        result = classify_sequence(frps, times)
        lat, lon = cell
        max_frp = float(g_sorted[frp_col].max()) if frp_col and not g_sorted[frp_col].isna().all() else None
        brightness_max = float(g_sorted[brightness_col].max()) if brightness_col in g_sorted else None
        props = {
            "acq_start": min(times).isoformat() + "Z",
            "acq_end": max(times).isoformat() + "Z",
            "event_type": result["event_type"],
            "confidence": result["confidence"],
            "model": model,
            "max_frp": max_frp,
            "max_brightness": brightness_max,
            "count": int(len(g_sorted))
        }
        features.append({
            "type": "Feature",
            "geometry": {"type": "Point", "coordinates": [lon, lat]},
            "properties": props
        })

    logger.info(f"/predict served {len(features)} incidents for model {model}")
    return jsonify({"type": "FeatureCollection", "features": features})

@app.route("/fetch_status")
def fetch_status():
    """Serve the latest fetch status as JSON."""
    if os.path.exists("fetch_status.json"):
        with open("fetch_status.json") as f:
            logger.info("Served fetch_status.json")
            return jsonify(json.load(f))
    else:
        logger.warning("fetch_status.json not found")
        return jsonify({"status": "unknown", "timestamp": None, "message": "No status file found."}), 404

@app.route("/logs")
def logs() -> Response:
    """Stream the last N lines of both fetcher and API logs as plain text."""
    def tail(filename: str, n: int) -> str:
        try:
            with open(filename, "r") as f:
                return ''.join(f.readlines()[-n:])
        except Exception:
            return f"(No log file: {filename})\n"
    api_log = tail(API_LOG_FILE, LOG_LINES)
    fetcher_log = tail(FETCHER_LOG_FILE, LOG_LINES)
    combined = f"--- API LOG ---\n{api_log}\n--- FETCHER LOG ---\n{fetcher_log}"
    return Response(combined, mimetype="text/plain")

# Serve index.html at the root URL
@app.route('/')
def serve_frontend():
    return send_from_directory('.', 'index.html')

# Serve other static files (e.g., JS, CSS) from the project root
@app.route('/<path:path>')
def static_proxy(path):
    return send_from_directory('.', path)

@app.errorhandler(404)
def not_found(e):
    logger.warning(f"404 Not Found: {request.path}")
    return jsonify({"error": "Not found"}), 404

@app.errorhandler(500)
def internal_error(e):
    logger.error(f"500 Internal Server Error: {e}")
    return jsonify({"error": "Internal server error"}), 500

def open_browser():
    webbrowser.open_new('http://localhost:5000/')

if __name__ == '__main__':
    threading.Timer(1.25, open_browser).start()
    app.run() 