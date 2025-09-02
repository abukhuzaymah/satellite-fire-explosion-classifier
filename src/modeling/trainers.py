from __future__ import annotations

from typing import Tuple, Dict, Any
import numpy as np
import pandas as pd
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
from sklearn.metrics import classification_report
import joblib


def train_random_forest(X: np.ndarray, y: np.ndarray, *, test_size: float = 0.25, seed: int = 42) -> Tuple[RandomForestClassifier, Dict[str, Any]]:
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=test_size, random_state=seed, stratify=y)
    clf = RandomForestClassifier(n_estimators=300, max_depth=None, random_state=seed, class_weight='balanced_subsample')
    clf.fit(X_train, y_train)
    report = classification_report(y_test, clf.predict(X_test), output_dict=True)
    return clf, report


def save_model(model: Any, path: str) -> None:
    joblib.dump(model, path)

