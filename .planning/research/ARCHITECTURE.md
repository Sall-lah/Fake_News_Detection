# Architecture Research

**Domain:** Local ML inference API (Flask, sklearn pipeline)
**Researched:** 2026-05-15
**Confidence:** MEDIUM

## Standard Architecture

### System Overview

```
┌─────────────────────────────────────────────────────────────┐
│                        API Layer                             │
├─────────────────────────────────────────────────────────────┤
│  ┌────────────┐  ┌────────────┐  ┌────────────┐             │
│  │ / (docs)   │  │ /info      │  │ /predict   │             │
│  └─────┬──────┘  └─────┬──────┘  └─────┬──────┘             │
│        │               │               │                    │
├────────┴───────────────┴───────────────┴───────────────────┤
│                     Application Core                        │
├─────────────────────────────────────────────────────────────┤
│  ┌────────────────┐  ┌────────────────┐  ┌────────────────┐│
│  │ Input Validator│  │ Preprocessor    │  │ Inference Svc  ││
│  └───────┬────────┘  └───────┬────────┘  └───────┬────────┘│
│          │                   │                   │         │
├──────────┴───────────────────┴───────────────────┴─────────┤
│                     Runtime / Assets                        │
├─────────────────────────────────────────────────────────────┤
│  ┌───────────────┐  ┌───────────────┐  ┌──────────────────┐│
│  │ model.pkl     │  │ Config        │  │ Logging          ││
│  └───────────────┘  └───────────────┘  └──────────────────┘│
└─────────────────────────────────────────────────────────────┘
```

### Component Responsibilities

| Component | Responsibility | Typical Implementation |
|-----------|----------------|------------------------|
| API Routes | HTTP endpoints, response formatting, docs | Flask blueprints or simple route module |
| Input Validator | Enforce JSON schema (title/text), empty checks | Lightweight validation functions |
| Preprocessor | Normalize/clean text, combine title+text | Pure functions; shared with training pipeline if possible |
| Inference Service | Load model, run predictions, map labels | Lazy-loaded singleton / app startup load |
| Config | Environment-based settings | Env vars + config module |
| Logging | Request + error logging | Python logging |

## Recommended Project Structure

```
src/
├── app.py                 # Flask app factory / app init
├── routes/
│   ├── docs.py            # / and /info endpoints
│   └── predict.py         # /predict endpoint
├── core/
│   ├── validate.py        # request validation & error helpers
│   ├── preprocess.py      # text normalization & combination
│   └── inference.py       # model loading + predict
├── config/
│   └── settings.py        # environment configuration
├── assets/
│   └── model.pkl          # sklearn pipeline artifact
└── logging/
    └── setup.py           # logging configuration
```

### Structure Rationale

- **routes/** isolates HTTP concerns from ML logic for clear boundaries.
- **core/** keeps model, preprocessing, validation reusable and testable.
- **assets/** makes artifact location explicit for container packaging.

## Architectural Patterns

### Pattern 1: Application Factory + Singleton Model Loader

**What:** Build the Flask app in a factory, load the model once at startup or on first request, and reuse it.
**When to use:** Any local inference API where cold-start is acceptable and model is static.
**Trade-offs:** Simpler than per-request loading; must be careful with thread-safety and process workers.

**Example:**
```python
# app.py
from flask import Flask
from core.inference import load_model

def create_app():
    app = Flask(__name__)
    load_model()  # preload at startup
    return app
```

### Pattern 2: Thin Controller, Fat Service

**What:** Routes only parse inputs and call core services for validation, preprocessing, inference.
**When to use:** Keeps HTTP layer slim, improves testability of core logic.
**Trade-offs:** Slightly more modules, but avoids route bloat.

**Example:**
```python
# routes/predict.py
from core.validate import validate_payload
from core.preprocess import normalize
from core.inference import predict

def handle_predict(payload):
    validate_payload(payload)
    text = normalize(payload)
    return predict(text)
```

### Pattern 3: Explicit Error Envelope

**What:** Uniform response schema for errors (status + message).
**When to use:** Local API with human-readable errors.
**Trade-offs:** Slightly more code, but clearer diagnostics.

## Data Flow

### Request Flow

```
Client
  ↓
/predict route
  ↓
Input Validator → Preprocessor → Inference Service (model.pkl)
  ↓
Post-process label/score
  ↓
JSON response { status, label, ... }
```

### Key Data Flows

1. **Prediction:** JSON (title,text) → validation → combined normalized text → model.predict → label.
2. **Docs:** GET / and /info → static markdown/JSON describing usage.

## Scaling Considerations

| Scale | Architecture Adjustments |
|-------|--------------------------|
| 0-1k users | Single Flask process, model loaded once |
| 1k-100k users | Multiple workers (gunicorn), ensure model load per worker |
| 100k+ users | Consider async queue + model server (overkill for local scope) |

### Scaling Priorities

1. **First bottleneck:** model load time → preload on startup, avoid per-request load.
2. **Second bottleneck:** CPU-bound inference → increase workers or batch requests.

## Anti-Patterns

### Anti-Pattern 1: Loading model inside every request

**What people do:** Call joblib.load in /predict handler each request.
**Why it's wrong:** Massive latency and CPU overhead.
**Do this instead:** Load once at startup or on first access and reuse.

### Anti-Pattern 2: Mixing preprocessing in route handlers

**What people do:** Put all cleaning logic in Flask routes.
**Why it's wrong:** Hard to test and reuse, routes become fragile.
**Do this instead:** Move preprocessing to core module and unit test separately.

## Integration Points

### External Services

| Service | Integration Pattern | Notes |
|---------|---------------------|-------|
| Docker runtime | Container loads model at start | Ensures local repeatability |

### Internal Boundaries

| Boundary | Communication | Notes |
|----------|---------------|-------|
| routes ↔ core | direct function calls | Keep HTTP concerns isolated |
| core ↔ assets | file read | Only inference module touches model.pkl |

## Suggested Build Order (Dependencies)

1. **Model + preprocessing contract**
   - Define expected inputs, preprocessing pipeline, and label mapping.
2. **Inference service**
   - Implement model loading and predict interface.
3. **Validation & error envelope**
   - Ensure predictable responses for bad inputs.
4. **API routes**
   - Wire /predict, /, /info to core services.
5. **Containerization**
   - Dockerfile loads model at startup, pin dependencies.

## Sources

- Project context: .planning/PROJECT.md (local requirements)

---
*Architecture research for: local Flask ML inference API*
*Researched: 2026-05-15*
