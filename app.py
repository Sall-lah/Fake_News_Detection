from __future__ import annotations

from pathlib import Path
import warnings

from flask import Flask, jsonify, render_template_string, request

from model import get_model, load_model
from preprocess import clean_text

app = Flask(__name__)

MODEL_PATH = Path(__file__).parent / "model.pkl"

# Try soft load first (warm start — model.pkl exists)
model = load_model(MODEL_PATH)

if model is None:
    # Cold start — model.pkl missing, run training (D-02: block startup)
    print("No pre-trained model found. Running training...")
    from train import train  # Lazy import — pandas not imported on warm start (D-05)
    model_path = train()
    print(f"Training complete. Loading model from {model_path}")
    model = load_model(MODEL_PATH)
    if model is None:
        print("Error: Training completed but model could not be loaded.")
        raise SystemExit(1)
    print("Model loaded successfully. API is ready.")
else:
    # Warm start — model.pkl already exists
    print("Model loaded from existing model.pkl. API is ready.")


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
        with warnings.catch_warnings():
            warnings.simplefilter("ignore", category=UserWarning)
            prediction = model.predict([cleaned])[0]
    except Exception:
        return jsonify({"status": "error", "message": "prediction failed"}), 500

    label = "true" if str(prediction).lower() in ("1", "true", "real") else "fake"
    return jsonify({"status": "ok", "label": label}), 200


HTML_DOC = """\
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Fake News Detection API</title>
    <style>
        body { font-family: monospace; max-width: 800px; margin: 2rem auto; padding: 0 1rem; }
        h1 { border-bottom: 1px solid #333; padding-bottom: 0.5rem; }
        h2 { margin-top: 1.5rem; }
        pre { background: #f4f4f4; padding: 1rem; overflow-x: auto; }
        code { font-family: monospace; }
    </style>
</head>
<body>
    <h1>Fake News Detection API</h1>
    <p>A local API that classifies news articles as fake or true.</p>

    <h2>Available Endpoints</h2>

    <h3>GET /</h3>
    <p>This page — API documentation.</p>

    <h3>GET /info</h3>
    <p>Machine-readable API metadata (JSON).</p>

    <h3>POST /predict</h3>
    <p>Classify a news article as fake or true.</p>
    <p><strong>Request body (JSON):</strong></p>
    <pre><code>{
  "title": "Breaking News",
  "text": "Article content here"
}</code></pre>
    <p><strong>Response:</strong></p>
    <pre><code>{"status": "ok", "label": "fake"}</code></pre>
    <p>Label is <code>"fake"</code> or <code>"true"</code>.</p>

    <h2>Example</h2>
    <pre><code>curl -X POST http://localhost:5000/predict \\
  -H "Content-Type: application/json" \\
  -d '{"title": "Breaking News", "text": "Article content here"}'</code></pre>
</body>
</html>
"""


@app.get("/")
def index():
    return render_template_string(HTML_DOC), 200


@app.get("/info")
def info():
    return jsonify({
        "status": "ok",
        "name": "Fake News Detection API",
        "version": "1.0.0",
        "endpoints": {
            "GET /": "API documentation (HTML)",
            "GET /info": "API metadata (this endpoint)",
            "POST /predict": "Classify news article (JSON)",
        },
        "predict_request": {
            "title": "string (optional) — news article title",
            "text": "string (required) — news article body text",
        },
        "predict_response": {
            "status": "ok | error",
            "label": "fake | true (only when status is ok)",
        },
    }), 200
