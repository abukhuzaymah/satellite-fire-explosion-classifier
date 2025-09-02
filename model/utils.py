from __future__ import annotations

from typing import List, Dict, Tuple
import numpy as np


def extract_features_from_sequence(frp_values: List[float]) -> Dict[str, float]:
    """Compute basic features from a sequence of FRP values.

    Returns a dict suitable for ML models. Non-finite values are treated as 0.
    """
    if frp_values is None:
        frp_values = []
    arr = np.array(frp_values, dtype=float)
    arr[~np.isfinite(arr)] = 0.0
    if arr.size == 0:
        return {
            "max_frp": 0.0,
            "mean_frp": 0.0,
            "std_frp": 0.0,
            "rise": 0.0,
            "decay": 0.0,
            "duration_high": 0.0,
            "count_obs": 0.0,
        }

    max_frp = float(arr.max())
    mean_frp = float(arr.mean())
    std_frp = float(arr.std())
    if arr.size >= 3:
        peak_idx = int(arr.argmax())
        left = arr[peak_idx] - arr[max(0, peak_idx - 1)]
        right_drop = arr[peak_idx] - arr[min(arr.size - 1, peak_idx + 1)]
    else:
        left = 0.0
        right_drop = 0.0
    duration_high = float((arr > 0.25 * max_frp).mean()) if max_frp > 0 else 0.0
    count_obs = float(arr.size)

    return {
        "max_frp": max_frp,
        "mean_frp": mean_frp,
        "std_frp": std_frp,
        "rise": float(left),
        "decay": float(right_drop),
        "duration_high": duration_high,
        "count_obs": count_obs,
    }


def vectorize_features(feature_dicts: List[Dict[str, float]]) -> Tuple[np.ndarray, List[str]]:
    """Convert a list of feature dicts into a 2D numpy array and return feature order."""
    if not feature_dicts:
        return np.zeros((0, 7), dtype=float), [
            "max_frp",
            "mean_frp",
            "std_frp",
            "rise",
            "decay",
            "duration_high",
            "count_obs",
        ]
    keys = [
        "max_frp",
        "mean_frp",
        "std_frp",
        "rise",
        "decay",
        "duration_high",
        "count_obs",
    ]
    X = np.array([[fd.get(k, 0.0) for k in keys] for fd in feature_dicts], dtype=float)
    return X, keys

