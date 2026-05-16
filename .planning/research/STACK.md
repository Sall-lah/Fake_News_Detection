# Stack Research

**Domain:** Local Flask ML inference API (scikit-learn pipeline)
**Researched:** 2026-05-15
**Confidence:** MEDIUM (versions verified; some compatibility assumptions)

## Recommended Stack

### Core Technologies

| Technology | Version | Purpose | Why Recommended |
|------------|---------|---------|-----------------|
| Python | 3.13.x (current bugfix) | Runtime | Current stable CPython with long support window and broad ecosystem compatibility. (Confidence: HIGH) |
| Flask | 3.1.1 | HTTP API framework | Lightweight, stable WSGI framework and explicit requirement. Flask 3.1.x docs show standard deployment patterns. (Confidence: HIGH) |
| Waitress | 3.0.2 | Production WSGI server (local, cross‑platform) | Pure‑Python, Windows-friendly WSGI server; Flask docs list it as a production option and it runs well for local APIs. (Confidence: HIGH) |
| scikit-learn | 1.7.1 | Model inference (Pipeline) | Current sklearn stable release with documented model persistence guidance; aligns with `model.pkl` pipeline usage. (Confidence: HIGH) |

### Supporting Libraries

| Library | Version | Purpose | When to Use |
|---------|---------|---------|-------------|
| numpy | 2.4.4 | Array/matrix ops for model inputs | Required by scikit-learn pipelines; use current NumPy to match supported wheels. (Confidence: HIGH) |
| scipy | 1.17.1 | Scientific computing dependencies | Many sklearn models depend on SciPy; include to avoid runtime import errors. (Confidence: HIGH) |
| joblib | 1.5.3 | Model loading and caching | Preferred serializer for sklearn (efficient with large arrays). Use for `model.pkl` load/store. (Confidence: HIGH) |
| gunicorn | 26.0.0 | WSGI server (Linux only) | Use only if deploying on Linux containers and want prefork workers. Not for Windows. (Confidence: HIGH) |
| python-dotenv | 1.0.1 | Local env config | Use if you need `.env` for ports/path config in local dev. (Confidence: MEDIUM) |

### Development Tools

| Tool | Purpose | Notes |
|------|---------|-------|
| ruff | Linting + formatting | Fast, single-tool lint + format for Python. (Confidence: MEDIUM) |
| black | Code formatting | Use if you prefer the classic formatter over ruff formatting. (Confidence: MEDIUM) |

## Installation

```bash
# Core
pip install Flask==3.1.1 waitress==3.0.2 scikit-learn==1.7.1

# Supporting
pip install numpy==2.4.4 scipy==1.17.1 joblib==1.5.3

# Optional (Linux-only WSGI)
pip install gunicorn==26.0.0

# Optional (local env)
pip install python-dotenv==1.0.1
```

## Alternatives Considered

| Recommended | Alternative | When to Use Alternative |
|-------------|-------------|-------------------------|
| Waitress | Gunicorn | Use Gunicorn on Linux containers when you want prefork workers and higher concurrency; not suitable for Windows. |
| Flask | FastAPI | Use FastAPI only if you can drop the Flask requirement and want async + auto‑docs. |
| joblib/pickle | skops.io | Use skops.io when you need safer model loading and can re-export the model; otherwise stick to joblib for sklearn defaults. |

## What NOT to Use

| Avoid | Why | Use Instead |
|-------|-----|-------------|
| Flask dev server in Docker | Not production-grade, single-threaded behavior; misleading performance. | Waitress (local cross-platform) or Gunicorn (Linux). |
| Unpinned scikit-learn/NumPy/SciPy versions | Model pickle compatibility breaks across versions. | Pin versions to match training environment (start with current stable set above). |
| Gunicorn on Windows | Not supported on Windows. | Waitress. |

## Stack Patterns by Variant

**If running purely local on Windows/macOS:**
- Use Flask + Waitress
- Because Waitress is pure‑Python and cross‑platform

**If running in Linux Docker only:**
- Use Flask + Gunicorn
- Because Gunicorn prefork workers can improve throughput for CPU‑bound inference

## Version Compatibility

| Package A | Compatible With | Notes |
|-----------|-----------------|-------|
| scikit-learn==1.7.1 | numpy==2.4.4, scipy==1.17.1 | Pin to avoid pickle mismatch warnings and runtime errors; ideally match training-time versions. (Confidence: MEDIUM) |

## Sources

- /pallets/flask/3_1_1 — WSGI deployment guidance (Flask docs)
- /scikit-learn/scikit-learn/1.7.1 — model persistence guidance
- https://pypi.org/project/waitress/ — current Waitress version
- https://pypi.org/project/gunicorn/ — current Gunicorn version
- https://pypi.org/project/numpy/ — current NumPy version
- https://pypi.org/project/scipy/ — current SciPy version
- https://pypi.org/project/joblib/ — current joblib version
- https://www.python.org/downloads/ — current Python release info

---
*Stack research for: Local Flask ML inference API*
*Researched: 2026-05-15*
