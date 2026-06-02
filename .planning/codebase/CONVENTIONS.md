# Coding Conventions

## Code Style

- **Snake case** for files, functions, and variables
- **`from __future__ import annotations`** at top of every file (enables PEP 604 union syntax)
- **No type hints in test files** (tests omit type annotations)
- **Production files** use modern type hints: `model_path: Path`, `-> object | None`
- **Docstrings** only on public functions (`clean_text` has `__all__`, `load_and_prepare_data` has docstring)
- **String quotes**: Double quotes consistently (`"text"`)
- **Line length**: Not explicitly enforced (no linter config), but stays reasonable

## Imports

Standard library → third-party → local, separated by blank lines:

```python
from __future__ import annotations

from pathlib import Path

import joblib
import pandas as pd
from lightgbm import LGBMClassifier
from sklearn.feature_extraction.text import TfidfVectorizer

from preprocess import clean_text
```

## Error Handling

| Pattern | Where | Example |
|---------|-------|---------|
| Guard clause for missing model | `app.py:18-28` | `if model is None: ... run training` |
| Soft-load returning None | `model.py:10-17` | Returns `None` if file missing (no exception) |
| JSON parse safety | `app.py:36` | `request.get_json(silent=True)` returns `None` without exception |
| Empty input guard | `app.py:44` | `if not cleaned: return 400` |
| Model not loaded guard | `app.py:48` | `if model is None: return 503` |
| Prediction error guard | `app.py:54-56` | `except Exception: return 500` |
| Shared validation | `preprocess.py:16-17` | Empty text check before processing |
| Warning suppression | `app.py:52-53` | `warnings.catch_warnings(ignore=UserWarning)` during prediction |

**No custom exception classes anywhere.** All error handling uses built-in exceptions and HTTP status codes.

## Module Conventions

| Module | Exports (via `__all__` or top-level) | Side Effects |
|--------|--------------------------------------|--------------|
| `app.py` | `app` (Flask instance) | Module-level model loading on import |
| `model.py` | `load_model`, `load_model_or_exit`, `get_model` | Module-level `MODEL = None` |
| `preprocess.py` | `clean_text` (via `__all__ = ["clean_text"]`) | None (pure function) |
| `train.py` | `train`, `load_and_prepare_data` | Writes `model.pkl` to disk |

## Test Conventions

- **Class-based**: `class TestXxx:` — groups related tests
- **Method naming**: `def test_xxx(self, client):` — prefix all test methods with `test_`
- **Flask test client** via fixture in `test_endpoints.py`
- **No test markers or parametrize** — simple method-per-scenario
- **Assert style**: `assert condition`, `assert value in container`, `assert result == expected`
- **No mocking framework** used — tests call the actual model

## Flask Conventions

| Convention | Usage |
|-----------|-------|
| `@app.get()` | GET routes (`/`, `/info`) |
| `@app.post()` | POST routes (`/predict`) |
| `jsonify()` | JSON responses |
| `render_template_string()` | Inline HTML template (no Jinja files) |
| `app.config["TESTING"] = True` | Set per-test in fixture |
| `app.test_client()` | Test client in context manager |

## Module-Loaded Pattern

All models/utilities are loaded at **module import time**, not inside request handlers:

```python
# app.py — at module level:
model = load_model(MODEL_PATH)

# Only if module-level load failed, run training:
if model is None:
    model_path = train()
    model = load_model(MODEL_PATH)
```

This means `import app` triggers training. The `get_model()` function returns the module-level reference with no lazy-loading.
