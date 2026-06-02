# Testing

## Framework

- **pytest** — test runner (no plugins like pytest-cov, pytest-mock)
- **No config file** — no `pytest.ini`, `pyproject.toml`, `setup.cfg` with pytest settings
- **Run**: `python -m pytest tests/ -v`

## Test Structure

```
tests/
├── conftest.py           # sys.path manipulation (project root)
├── test_endpoints.py     # API endpoint tests (9 tests)
├── test_model.py         # Model loading/prediction tests (2 tests)
└── test_preprocess.py    # Text cleaning tests (4 tests)
```

**Total: 15 tests** (as of current state)

## Test Categories

| File | Tests | Scope |
|------|-------|-------|
| `test_endpoints.py` | 9 | `GET /` (6), `GET /info` (8), `POST /predict` (6) |
| `test_model.py` | 2 | Model loaded, model.predict returns result |
| `test_preprocess.py` | 4 | Text cleaning, punctuation removal, lowercase, empty input |

## Patterns

### conftest.py

```python
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))
```

Ensures project root is on `sys.path` so `app`, `model`, `preprocess` can be imported from tests.

### Flask Test Client Fixture

```python
@pytest.fixture
def client():
    app.config["TESTING"] = True
    with app.test_client() as client:
        yield client
```

Used only in `test_endpoints.py`.

### Class Organization

Tests grouped by endpoint/component:

```python
class TestIndexEndpoint:
    def test_status_code(self, client): ...
    def test_content_type(self, client): ...
    def test_title_present(self, client): ...

class TestInfoEndpoint:
    def test_status_code(self, client): ...
    def test_content_type(self, client): ...
    def test_status_ok(self, client): ...
```

## What's NOT Tested

- **Cold start** (training from scratch during startup)
- **Model accuracy / performance degradation** (no CI benchmark)
- **Docker build** (no container integration test)
- **Error response schemas** (e.g., exact shape of error responses)
- **Training script** (`train.py` has no tests)
- **Performance / load testing**

## Test Setup Requirements

- `model.pkl` must exist (tests call `get_model()` which returns module-level MODEL)
- Dependencies must be installed (`pip install -r requirements.txt`)
- No mocking — tests run against the real model and real preprocessing

## Running Tests

```bash
# Install deps first
pip install -r requirements.txt

# Run all tests
python -m pytest tests/ -v

# Run specific test file
python -m pytest tests/test_endpoints.py -v

# Run specific test class
python -m pytest tests/ -k "TestPredictEndpoint" -v
```

## Warning Suppression in Tests

During prediction tests, `UserWarning` from LightGBM is suppressed:

```python
with warnings.catch_warnings():
    warnings.simplefilter("ignore", UserWarning)
    result = model.predict(["test article content"])
```

This matches the suppression pattern in `app.py`.
