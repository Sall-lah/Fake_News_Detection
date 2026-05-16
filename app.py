from __future__ import annotations

from pathlib import Path

from flask import Flask, jsonify, request

from model import get_model, load_model_or_exit
from preprocess import clean_text

app = Flask(__name__)

MODEL_PATH = Path(__file__).with_name("model.pkl")
load_model_or_exit(MODEL_PATH)


@app.post("/predict")
def predict():
    payload = request.get_json(silent=True)
    if not isinstance(payload, dict):
        payload = {}

    title = payload.get("title") or ""
    text = payload.get("text") or ""
    cleaned = clean_text(title, text)

    if not cleaned:
        return jsonify({"status": "error", "message": "cleaned input is empty"}), 400

    model = get_model()
    if model is None:
        return jsonify({"status": "error", "message": "model not loaded"}), 503

    try:
        prediction = model.predict([cleaned])[0]
    except Exception:
        return jsonify({"status": "error", "message": "prediction failed"}), 500

    label = "true" if str(prediction).lower() in ("1", "true", "real") else "fake"
    return jsonify({"status": "ok", "label": label}), 200
