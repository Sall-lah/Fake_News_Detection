# Codebase Concerns

## Technical Debt

| Issue | Location | Severity | Notes |
|-------|----------|----------|-------|
| Inline HTML template | `app.py:62-106` | Low | 45-line HTML string in Python file; no template engine |
| Hardcoded paths | `app.py:13`, `train.py:21-22`, `train.py:115` | Low | `model.pkl`, `dataset/` paths relative to project root; no config |
| Shared `sys.path` hack in conftest | `tests/conftest.py:4` | Low | Standard pytest pattern but fragile with installed packages |
| No `__init__.py` in tests | `tests/` | Low | Works with pytest but not a proper package |
| No linter/formatter config | project root | Medium | No `ruff`, `black`, `flake8`, or `pylint` config |

## Performance Concerns

| Concern | Details |
|---------|---------|
| Cold start latency | Training takes 2-5 minutes on first startup; blocks API availability |
| Memory usage | ~116MB CSV loaded into RAM during training; pipeline object ~2MB serialized |
| Single-threaded inference | Flask dev server handles one request at a time; no concurrency |
| No caching | Every request runs through the full pipeline; no prediction cache |
| Training data size | 45K rows × combined string column may cause OOM on low-memory systems |

## Known Issues

| Issue | Status | Location |
|-------|--------|----------|
| LightGBM multiprocessing crashes on Windows | **Fixed** with `n_jobs=1` | `train.py:93` |
| LGBMClassifier feature name warning | **Fixed** with `warnings.filterwarnings` | `app.py:52-53` |

## Fragile Areas

| Area | Risk | Why |
|------|------|-----|
| Module-level model loading in `app.py` | Medium | `import app` triggers training if model.pkl missing; affects test imports |
| Pickle compatibility | High | `model.pkl` must be loaded with same scikit-learn/LightGBM versions; version mismatch causes cryptic errors |
| Shared MODEL singleton | Medium | `model.py:7` — `MODEL = None` is mutable module state; race-prone if Flask reloader enabled |
| Cold start blocking | Medium | API unavailable during training; no async or health check for "loading" state |
| `.dockerignore` excludes `*.md` | Low | Includes `README.md` exclusion — docs not shipped but also blocks `requirements.txt` (has explicit `!requirements.txt` exception) |

## Security Observations

| Observation | Severity | Notes |
|-------------|----------|-------|
| No auth on endpoints | None (informational) | Local API — by design |
| No rate limiting | None (informational) | Local API — by design |
| No input size validation | Low | No limit on `title`/`text` payload size; large payload could cause OOM |
| No secrets in codebase | None | No API keys, tokens, or credentials |
| Predict endpoint has no CORS | None (informational) | Local API — not exposed to browser clients |

## Missing Features

- **Health check endpoint** — no `/health` or `/_ping` for orchestration probes
- **Request logging** — no structured logging; only `print()` statements
- **Graceful shutdown** — no signal handlers for clean model unloading
- **Configuration** — no environment variables or config file for port, model path, etc.
- **Async support** — sync Flask; blocking I/O during training blocks the server

## Dependency Risks

| Dependency | Risk | Mitigation |
|------------|------|------------|
| `lightgbm==4.6.0` | Windows compilation issues, large wheel | Pinned in `requirements.txt` |
| `scikit-learn==1.7.1` | Pickle incompatibility across versions | Pinned to exact version |
| `pandas==3.0.3` | Larger install footprint | Required for CSV loading |
| All deps pinned | Security updates missed | Manual review needed |
