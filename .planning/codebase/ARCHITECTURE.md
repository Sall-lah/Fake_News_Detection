# Architecture

## System Pattern

**Single-process monolith**: A Flask application that loads a pre-trained scikit-learn pipeline into memory and exposes REST endpoints. No background workers, queues, or separate services.

## Layers

```
┌────────────────────────────────────────────┐
│              HTTP Layer (Flask)             │
│  app.py  ──  /, /info, /predict            │
├────────────────────────────────────────────┤
│            Model Layer (model.py)           │
│  load_model()  ──  get_model()             │
│  Singleton pattern (module-level MODEL)     │
├────────────────────────────────────────────┤
│          Preprocessing (preprocess.py)      │
│  clean_text() — shared by app + train      │
├────────────────────────────────────────────┤
│           Training (train.py)               │
│  Cold-start: load CSV → clean → train →    │
│  save model.pkl                            │
├────────────────────────────────────────────┤
│              Data (dataset/)                │
│  Fake.csv (23,537 rows)                    │
│  True.csv (21,417 rows)                    │
└────────────────────────────────────────────┘
```

## Entry Points

| Entry Point | File | When Called |
|-------------|------|-------------|
| `app.py` module-level | `app.py:16-31` | On `flask run` or `python app.py` — warm/cold start model loading |
| `train()` | `train.py:59-126` | On cold start from `app.py:21` |
| `python train.py` | `train.py:130` | Manual training (standalone) |

## Request Flow (POST /predict)

```
Client HTTP POST /predict
        │
        ▼
Flask route @app.post("/predict")  [app.py:34]
        │
        ├─ request.get_json()  →  payload dict
        ├─ extract title + text
        │
        ▼
preprocess.clean_text(title, text)  [preprocess.py:8]
        │  lowercase → strip non-alpha → stop words → dedupe
        │
        ▼
get_model()  →  Pipeline (in-memory singleton)  [model.py:28]
        │
        ├─ pipeline.predict([cleaned_text])  →  [0] or [1]
        │
        ▼
Map prediction → label string ("fake" / "true")
        │
        ▼
jsonify({"status": "ok", "label": "..."})  →  HTTP 200
```

## Warm/Cold Start Flow (Startup)

```
                    app.py startup
                         │
                         ▼
            model.load_model(MODEL_PATH)
                    │            │
               file found     file missing
                    │            │
                    ▼            ▼
              Warm Start     Cold Start
              MODEL ready    train.train()
                                  │
                            joblib.dump()
                                  │
                            MODEL loaded
                                  │
                            API ready
```

## Data Flow (Training)

```
Fake.csv ─┐
          ├─▶ pd.concat() → clean_text() → dropna → train_test_split
True.csv ─┘                                          │
                                                     ▼
                  ┌──────────────────────────────────────┐
                  │  Pipeline([                           │
                  │    ("tfidf", TfidfVectorizer),        │
                  │    ("classifier", LGBMClassifier)     │
                  │  ])                                   │
                  │  → RandomizedSearchCV(n_iter=5, cv=2) │
                  └──────────────────────────────────────┘
                                                     │
                                                     ▼
                                           joblib.dump(model.pkl)
```

## Key Design Decisions

| Decision | Rationale |
|----------|-----------|
| Module-level MODEL singleton | Avoid reloading model per request; loaded once at startup |
| Cold start auto-training | Eliminates manual training step; container works immediately |
| Shared `clean_text()` | Single source of truth for preprocessing (training + inference) |
| `n_jobs=1` in CV | LightGBM multiprocessing crashes on Windows |
| Hardcoded paths | Simple project, no config file needed |

## Abstractions

- **`model.py`** wraps model lifecycle: `load_model()` (soft-load), `get_model()` (singleton access)
- **`preprocess.py`** abstracts text cleaning logic shared by training and inference
- **`train.py`** encapsulates the full training pipeline as a single `train()` function
- **`app.py`** handles HTTP concerns only
