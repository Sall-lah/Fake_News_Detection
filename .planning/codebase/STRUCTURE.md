# Directory Structure

```
Fake_News_Detection/
├── app.py               # Flask API — routes, startup logic, HTML docs
├── train.py             # Training pipeline — data loading, CV, model persistence
├── model.py             # Model loading utilities — load_model(), get_model()
├── preprocess.py        # Shared text preprocessing — clean_text()
├── requirements.txt     # Pinned Python dependencies
├── Dockerfile           # Container build instructions
├── .dockerignore        # Docker build exclusions
├── .gitignore           # Git exclusion rules
├── README.md            # Project documentation
├── AGENTS.md            # AI assistant configuration
├── model.pkl            # Pre-trained pipeline artifact (auto-generated)
│
├── dataset/
│   ├── Fake.csv         # 23,537 labeled fake news articles (63 MB)
│   └── True.csv         # 21,417 labeled true news articles (54 MB)
│
├── tests/
│   ├── conftest.py      # Pytest config — adds project root to sys.path
│   ├── test_endpoints.py  # 9 tests — API routes, predict, edge cases
│   ├── test_model.py    # 2 tests — model load and predict
│   └── test_preprocess.py # 4 tests — text cleaning edge cases
│
├── .planning/           # GSD planning artifacts (not shipped)
│   ├── codebase/        # Created by map-codebase workflow
│   ├── phases/          # Phase plans, discussions, UATs
│   ├── milestones/      # Milestone requirements and roadmaps
│   ├── research/        # Technology research docs
│   └── ...              # Various GSD state files
│
└── docs/                # User-facing documentation
    └── arsitektur-api.md  # API architecture docs (Indonesian)
```

## Key File Locations

| Concern | File | Lines | Notes |
|---------|------|-------|-------|
| API routes | `app.py:34-59` | 26 | POST /predict, input validation, error handling |
| HTML docs | `app.py:62-106` | 45 | Inline HTML template string |
| Info endpoint | `app.py:114-133` | 20 | JSON metadata endpoint |
| Model loading | `model.py:10-17` | 8 | Soft-load with None return for cold start |
| Clean text | `preprocess.py:8-32` | 25 | Shared preprocessing logic |
| Training pipeline | `train.py:59-126` | 68 | Full train function |
| Data preparation | `train.py:16-56` | 41 | CSV loading + cleaning |
| Docker build | `Dockerfile` | 18 | python:3.13-slim, flask run CMD |

## Naming Conventions

- **Files**: Snake case (snake_case) — `app.py`, `train.py`, `model.py`, `preprocess.py`
- **Functions**: Snake case — `clean_text()`, `load_model()`, `get_model()`, `load_and_prepare_data()`
- **Classes**: PascalCase — `TestPreprocess`, `TestModel`, `TestIndexEndpoint`, etc.
- **Tests**: Class-based with `Test` prefix, methods prefixed with `test_`
- **Constants**: UPPER_CASE — `MODEL`, `MODEL_PATH`
- **Module-level singletons**: UPPER_CASE — `MODEL = None` in `model.py`

## Python Version

Python 3.13 required (uses `from __future__ import annotations` and modern type hints like `object | None`).
