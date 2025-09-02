from __future__ import annotations

from dataclasses import dataclass
from typing import List, Tuple, Optional, Dict
import numpy as np
import pandas as pd
from sklearn.cluster import DBSCAN


def _to_km_coords(lat: np.ndarray, lon: np.ndarray) -> Tuple[np.ndarray, np.ndarray]:
    # Approximate conversion to kilometers (local equirectangular)
    lat = np.asarray(lat, dtype=float)
    lon = np.asarray(lon, dtype=float)
    lat_km = lat * 111.32
    # Use latitude-dependent km/deg for longitude
    lon_km = lon * (111.32 * np.cos(np.deg2rad(np.clip(lat, -89.9, 89.9))))
    return lat_km, lon_km


def cluster_events(
    df: pd.DataFrame,
    spatial_eps_km: float = 1.5,
    temporal_eps_minutes: int = 240,
    min_samples: int = 2,
    timestamp_col: str = "timestamp",
    lat_col: str = "latitude",
    lon_col: str = "longitude",
) -> pd.Series:
    """Cluster hotspots into spatiotemporal events using DBSCAN on a fused feature space.

    Returns a pandas Series of integer cluster labels aligned with df.index (-1 for noise).
    """
    if df.empty:
        return pd.Series([], dtype=int)
    if timestamp_col not in df.columns:
        raise ValueError(f"Missing required column: {timestamp_col}")
    if lat_col not in df.columns or lon_col not in df.columns:
        raise ValueError("Missing latitude/longitude columns")

    df_local = df[[lat_col, lon_col, timestamp_col]].copy()
    lat_km, lon_km = _to_km_coords(df_local[lat_col].values, df_local[lon_col].values)
    times = pd.to_datetime(df_local[timestamp_col]).astype("int64") // 10**9  # seconds

    # Normalize features so that eps in Euclidean corresponds to (spatial_eps_km, temporal_eps_minutes)
    space_scale = spatial_eps_km
    time_scale = (temporal_eps_minutes * 60.0) / 60.0  # seconds -> minutes; we will keep units in minutes
    # Build feature matrix: [lat_km/space_scale, lon_km/space_scale, time_minutes/time_scale]
    time_minutes = (times - times.min()) / 60.0
    X = np.vstack([
        lat_km / space_scale,
        lon_km / space_scale,
        time_minutes / time_scale,
    ]).T

    db = DBSCAN(eps=1.0, min_samples=min_samples, metric="euclidean")
    labels = db.fit_predict(X)
    return pd.Series(labels, index=df.index, name="event_id")


def aggregate_event_features(
    df: pd.DataFrame,
    labels: pd.Series,
    frp_col: Optional[str] = "frp",
    timestamp_col: str = "timestamp",
) -> pd.DataFrame:
    """Aggregate per-event features (max/mean/std FRP, duration, count)."""
    if df.empty:
        return pd.DataFrame()
    g = pd.concat([df, labels], axis=1)
    g = g[g[labels.name] != -1]
    if g.empty:
        return pd.DataFrame()
    g["timestamp"] = pd.to_datetime(g[timestamp_col])
    agg = g.groupby(labels.name).agg(
        start_time=(timestamp_col, "min"),
        end_time=(timestamp_col, "max"),
        count=(timestamp_col, "count"),
        lat_mean=("latitude", "mean"),
        lon_mean=("longitude", "mean"),
        max_frp=(frp_col, "max") if frp_col in g.columns else (timestamp_col, "count"),
        mean_frp=(frp_col, "mean") if frp_col in g.columns else (timestamp_col, "count"),
        std_frp=(frp_col, "std") if frp_col in g.columns else (timestamp_col, "count"),
    ).reset_index().rename(columns={labels.name: "event_id"})
    agg["duration_hours"] = (agg["end_time"] - agg["start_time"]).dt.total_seconds() / 3600.0
    return agg

