# Phase 1: Core Local Inference API — Research

**Date:** 2026-05-15
**Status:** Complete
**Scope:** Phase 1 (Core Local Inference API)

## Summary

Phase 1 delivers a local Flask `/predict` endpoint that preloads `model.pkl` on startup, applies deterministic preprocessing, and returns a `{status, label}` response for inference. The solution should follow the project’s Flask + Waitress stack, use `joblib` for model loading, and avoid advanced security (local-only API). Runtime dependencies must be declared in `requirements.txt` and pinned to avoid sklearn pickle incompatibility.

## Standard Stack (Use As-Designed)

- **Python**: 3.13.x
- **Flask**: 3.1.1
- **WSGI server**: Waitress 3.0.2 (local cross-platform)
- **Model loading**: joblib 1.5.3
- **ML runtime**: scikit-learn 1.7.1 + numpy 2.4.4 + scipy 1.17.1

## Architecture Patterns

### Runtime Model Load

- Load `model.pkl` **once** at process startup; reuse for all requests.
- If loading fails, **fail fast** (exit startup) — no degraded mode.
- If a request arrives without a loaded model, return **HTTP 503** with an error payload (no model filename in message).

### API Endpoint Shape

- `POST /predict` with JSON body: `{ "title": "...", "text": "..." }`.
- Success response: `{ "status": "ok", "label": "fake" | "true" }`.
- Error response: `{ "status": "error", "message": "..." }`.

### Preprocessing Pipeline (Deterministic)

Apply these steps in this exact order:
1. Combine inputs: `title + " " + text` (treat missing fields as empty strings).
2. Lowercase.
3. Replace non‑alphabetic characters with spaces.
4. Normalize whitespace (collapse to single spaces, trim ends).
5. Remove stopwords using `sklearn.feature_extraction.text.ENGLISH_STOP_WORDS`.
6. Deduplicate words while preserving first occurrence order.
7. Normalize whitespace again (collapse + trim).
8. If cleaned input is empty: return **HTTP 400** with error payload.

## File/Module Expectations

No existing codebase patterns. Suggested minimal structure:

- `app.py` (or `src/app.py`): Flask app, routes, startup load
- `preprocess.py` (or `src/preprocess.py`): preprocessing function
- `model.py` (or `src/model.py`): model loader + cached instance
- `requirements.txt`: runtime deps pinned

## Error Handling Guidance

- **400**: cleaned input empty
- **503**: model unavailable at request time
- **500**: unexpected inference errors (generic message, no internal details)

## Deployment Notes

- For Docker/local production, run via **Waitress**, not Flask dev server.
- Keep `model.pkl` in the container image so startup preload is fast.

## Validation Architecture

Testing infrastructure is not installed; do **not** run unit tests. Prefer lightweight automated checks that do not require extra dependencies.

- **Quick check:** `python -m compileall .` (ensures syntax validity)
- **Runtime smoke:** `python -c "import app"` (verifies import succeeds and model load path is reachable)
- **Endpoint smoke (manual/optional):** `curl -X POST http://localhost:PORT/predict -H "Content-Type: application/json" -d '{"title":"t","text":"x"}'`

If a testing framework is introduced later, update validation strategy accordingly.

## Common Pitfalls

- Unpinned sklearn/numpy/scipy causing model pickle incompatibility.
- Using Flask dev server in Docker (avoid; use Waitress).
- Returning model filename in error messages (privacy/ops concern).
- Skipping whitespace normalization after stopword removal and deduplication.

## Constraints to Enforce in Plans

- Flask backend only (no FastAPI).
- No rate limiter or advanced security features.
- Do not run tests (deps not installed).
- Respect response payload decisions and error status codes.
