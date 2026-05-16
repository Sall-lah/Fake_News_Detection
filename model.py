from __future__ import annotations

from pathlib import Path

import joblib

MODEL = None


def load_model(model_path: Path) -> object | None:
    """Soft-load: returns None if file missing, raises on corruption."""
    global MODEL
    if not model_path.exists():
        print(f"No model found at {model_path} — training will run on startup")
        return None
    MODEL = joblib.load(model_path)
    return MODEL


def load_model_or_exit(model_path: Path) -> object:
    global MODEL
    try:
        MODEL = joblib.load(model_path)
    except Exception:
        print("Failed to load model.")
        raise SystemExit(1)
    return MODEL


def get_model() -> object | None:
    return MODEL
