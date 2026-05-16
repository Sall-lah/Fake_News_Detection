# Technology Stack — v1.1 Model Training Pipeline

**Project:** Fake News Detection API
**Researched:** 2026-05-16
**Confidence:** HIGH (versions verified via PyPI and Context7 docs)

## New Additions for v1.1

These are the **only new dependencies** needed for the training pipeline. Everything else from v1.0 carries forward unchanged.

### Data Loading & Manipulation

| Library | Version | Purpose | Why |
|---------|---------|---------|-----|
| pandas | 3.0.3 | CSV loading, combining, data manipulation | Latest stable release (May 2026). `pd.read_csv` + `pd.concat` is the standard pattern for combining `fake.csv` + `true.csv`. Requires Python >=3.11 (compatible with 3.13). (Confidence: HIGH) |

### Already In Stack (No New Deps Needed)

These capabilities are covered by existing v1.0 dependencies — **do not add anything**:

| Capability | Provided By | Why No New Dep |
|------------|-------------|----------------|
| Train/test split | `sklearn.model_selection.train_test_split` (scikit-learn 1.7.1) | Already in stack |
| TF-IDF vectorization | `sklearn.feature_extraction.text.TfidfVectorizer` (scikit-learn 1.7.1) | Already in stack |
| LightGBM classifier | `lightgbm.LGBMClassifier` (4.6.0) | Already in stack — **pin this version** |
| Hyperparameter search | `sklearn.model_selection.RandomizedSearchCV` (scikit-learn 1.7.1) | Already in stack |
| Model persistence | `joblib.dump` / `joblib.load` (1.5.3) | Already in stack |
| sklearn Pipeline | `sklearn.pipeline.Pipeline` (scikit-learn 1.7.1) | Already in stack |
| Stop words | `sklearn.feature_extraction.text.ENGLISH_STOP_WORDS` | Already imported in `preprocess.py` |

## Recommended Full Stack (v1.1)

### Core Technologies

| Technology | Version | Purpose | Why |
|------------|---------|---------|-----|
| Python | 3.13.x | Runtime | Current stable; pandas 3.0.x requires >=3.11. (Confidence: HIGH) |
| Flask | 3.1.1 | HTTP API framework | Explicit requirement; stable. (Confidence: HIGH) |
| scikit-learn | 1.7.1 | Pipeline, TF-IDF, train_test_split, RandomizedSearchCV | Current stable; model pickle compatibility. (Confidence: HIGH) |
| pandas | 3.0.3 | CSV loading, DataFrame manipulation, dataset combining | **NEW** — standard for tabular data loading. `read_csv` + `concat` pattern. (Confidence: HIGH) |

### ML Libraries

| Library | Version | Purpose | Why |
|---------|---------|---------|-----|
| lightgbm | 4.6.0 | LGBMClassifier for binary classification | Already in use; **must pin** (was unpinned in v1.0 requirements.txt). Full sklearn API compatibility. (Confidence: HIGH) |
| numpy | 2.4.4 | Array ops for sklearn pipelines | Required by scikit-learn. (Confidence: HIGH) |
| scipy | 1.17.1 | Scientific computing deps | Many sklearn models depend on it. (Confidence: HIGH) |
| joblib | 1.5.3 | Model serialization (`model.pkl`) | Preferred sklearn serializer; efficient with large arrays. (Confidence: HIGH) |

### Flask Startup Pattern (No New Dep)

| Pattern | How | Why |
|---------|-----|-----|
| Run training before `app.run()` | Call `train_and_save_model()` in `app.py` module-level code, before `load_model_or_exit()` | `@app.before_first_request` was **removed in Flask 2.3**. Flask 3.2 docs explicitly say: "Run setup code when creating the application." Running at module load time ensures model exists before any request handler tries to load it. (Confidence: HIGH) |
| Self-removing `before_request` (alternative) | Use `@app.before_request` with `app.before_request_funcs[None].remove(handler)` after first run | Works but unnecessary complexity for local API. Only use if training must be deferred past module import. (Confidence: HIGH) |

## Installation

```bash
# NEW: pandas for training pipeline
pip install pandas==3.0.3

# EXISTING: pin lightgbm (was unpinned in v1.0)
pip install lightgbm==4.6.0

# EXISTING: core stack (unchanged)
pip install Flask==3.1.1 scikit-learn==1.7.1 numpy==2.4.4 scipy==1.17.1 joblib==1.5.3
```

### Updated requirements.txt

```
Flask==3.1.1
scikit-learn==1.7.1
numpy==2.4.4
scipy==1.17.1
joblib==1.5.3
lightgbm==4.6.0
pandas==3.0.3
```

## What NOT to Add

| Avoid | Why | Use Instead |
|-------|-----|-------------|
| Dask / Polars | Overkill for combining 2 CSVs; adds complexity and Docker image bloat | pandas `read_csv` + `concat` is sufficient. (Confidence: HIGH) |
| MLflow / Weights & Biases | Experiment tracking not needed for local single-model pipeline | Print best params + accuracy to console. (Confidence: HIGH) |
| pytest fixtures for model training | Training is slow; existing 26 tests cover inference only | Add separate `test_train.py` that runs training script directly, not via Flask. (Confidence: MEDIUM) |
| `before_first_request` | **Removed in Flask 2.3** — will cause ImportError | Run training at module load time before `app.run()`. (Confidence: HIGH) |
| `flask.cli.with_appcontext` for training | Adds unnecessary Flask app context overhead for a script that doesn't need it | Plain Python function called from `app.py` module level. (Confidence: HIGH) |
| Unpinned `lightgbm` | Was unpinned in v1.0; pickle compatibility breaks across versions | Pin to 4.6.0 to match existing `model.pkl`. (Confidence: HIGH) |

## Version Compatibility

| Package A | Compatible With | Notes |
|-----------|-----------------|-------|
| pandas==3.0.3 | Python>=3.11 | Compatible with Python 3.13. (Confidence: HIGH) |
| lightgbm==4.6.0 | scikit-learn>=1.0, numpy>=1.17 | Full sklearn API compatibility; works with sklearn 1.7.1. (Confidence: HIGH) |
| scikit-learn==1.7.1 | numpy==2.4.4, scipy==1.17.1 | Pin to avoid pickle mismatch; ideally match training-time versions. (Confidence: MEDIUM) |
| pandas==3.0.3 | numpy>=2.0 | pandas 3.0.x supports NumPy 2.x. (Confidence: HIGH) |

## Startup Flow (Recommended)

```
app.py module load
  -> train.py: train_and_save_model(MODEL_PATH, DATA_DIR)
     -> if MODEL_PATH exists: skip
     -> else: load CSVs -> preprocess -> split -> search -> save model.pkl
  -> model.py: load_model_or_exit(MODEL_PATH)
  -> Flask app ready for requests
```

Key: Training runs **once** at module import time (before `app.run()`), not per-request. This ensures `model.pkl` exists before the inference loader runs.

## Sources

- https://pypi.org/project/pandas/ — pandas 3.0.3 (latest, May 2026)
- https://pypi.org/project/lightgbm/ — lightgbm 4.6.0 (latest stable, Feb 2025)
- /pandas-dev/pandas — CSV loading, `pd.concat` patterns (Context7 docs)
- /lightgbm-org/lightgbm — LGBMClassifier sklearn API, GridSearchCV integration (Context7 docs)
- https://flask.palletsprojects.com/en/latest/lifecycle/ — Flask 3.2 lifecycle docs (setup before first request)
- https://github.com/pallets/flask/issues/4876 — `before_first_request` deprecation discussion

---
*Stack research for: v1.1 Model Training Pipeline additions*
*Researched: 2026-05-16*
