# Technology Stack

## Languages & Runtimes

| Language | Version | Usage |
|----------|---------|-------|
| Python | 3.13 | Application runtime |

## Core Frameworks & Libraries

| Package | Version | Category | Purpose |
|---------|---------|----------|---------|
| `Flask` | 3.1.1 | Web framework | HTTP API server, routing, JSON serialization |
| `scikit-learn` | 1.7.1 | ML library | `TfidfVectorizer`, `Pipeline`, `RandomizedSearchCV`, `train_test_split` |
| `lightgbm` | 4.6.0 | ML classifier | `LGBMClassifier` — gradient boosting for text classification |
| `joblib` | 1.5.3 | Serialization | Save/load trained pipeline as `model.pkl` |
| `pandas` | 3.0.3 | Data processing | CSV loading, DataFrame manipulation, train/test split |
| `numpy` | 2.4.4 | Numerical | Array operations (scikit-learn dependency) |
| `scipy` | 1.17.1 | Scientific | scikit-learn dependency |

## Development Tools

| Tool | Purpose |
|------|---------|
| `pytest` | Test runner |

## Infrastructure

| Component | Technology | Notes |
|-----------|-----------|-------|
| Container | Docker `python:3.13-slim` | Model trained at runtime, not baked |
| WSGI | Flask dev server (`flask run`) | Used in CMD for both dev and container |

## Dependencies (`requirements.txt`)

```
Flask==3.1.1
scikit-learn==1.7.1
numpy==2.4.4
scipy==1.17.1
joblib==1.5.3
pandas==3.0.3
lightgbm==4.6.0
```

## Configuration

No `.env` or config files. Configuration is minimal:
- Port: `5000` (Flask default)
- Host: `0.0.0.0` (explicit in Dockerfile CMD)
- Model path: `model.pkl` (hardcoded in `app.py` and `train.py`)
- Dataset path: `dataset/` (relative to project root)

## Version Pinning Strategy

All dependencies are pinned to exact versions to ensure `model.pkl` pickle compatibility across environments. LightGBM is explicitly pinned to match training provenance (`requirements.txt` comment).

## Key Constraints

- **LightGBM multiprocessing disabled** (`n_jobs=1` in `train.py:93`) — crashes on Windows
- **Cold start training** requires 2GB+ RAM for large CSV files (~116MB combined)
