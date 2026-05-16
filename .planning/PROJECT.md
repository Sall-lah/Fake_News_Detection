# Fake News Detection API

## What This Is

A local Flask API that serves predictions from a pre-trained `model.pkl` for fake-news classification. It exposes self-documenting endpoints (`/`, `/info`), and a `/predict` endpoint that accepts `title` and `text`, preprocesses them, and returns a fake/true label. Containerized via Dockerfile with Flask dev server.

## Core Value

Users can send a title + text and reliably receive a fake/true prediction from the model.

## Current Milestone: v1.1 Model Training Pipeline

**Goal:** Add a model training script that builds `model.pkl` from raw CSV datasets using pandas, and auto-runs on server startup (skipped if model already exists).

**Target features:**
- Dataset loader (pandas): combine `fake.csv` + `true.csv`, label them (0/1)
- Feature engineering (pandas): merge title+text, drop raw columns, clean NAs
- Apply `preprocess.py` on all 'string' column
- Train/test split
- LightGBM + TF-IDF pipeline with RandomizedSearchCV hyperparameter tuning
- Save trained model as `model.pkl`
- Auto-run training on server startup when `model.pkl` is missing
- Skip training when `model.pkl` already exists

## Requirements

### Validated

- ✓ Preprocess input by combining `title + " " + text`, lowercasing, removing non-letters, removing stopwords, removing duplicate words, and normalizing whitespace — v1.0
- ✓ Return error status when the processed string is empty — v1.0
- ✓ Load `model.pkl` on startup and perform inference per request — v1.0
- ✓ Return JSON with inference status and prediction value (0 = fake, 1 = true) — v1.0
- ✓ Provide `/predict` endpoint that accepts `title` and `text` inputs — v1.0
- ✓ Provide `/` and `/info` endpoints that describe API usage and examples — v1.0
- ✓ Provide `requirements.txt` for dependencies — v1.0
- ✓ Provide containerization (Dockerfile) that loads the model on startup — v1.0

### Active

(None — planning next milestone)

### Out of Scope

- Rate limiting or advanced security controls — local API only.
- External services or hosted deployments — local runtime only.
- UI or frontend — API-only deliverable.

## Context

Shipped v1.0 with ~200 LOC Python (app.py, model.py, preprocess.py) + tests (26 pytest tests across 3 files). Tech stack: Flask 3.1.1, scikit-learn 1.7.1, LightGBM 4.6.0, Python 3.13. Model loaded at startup via joblib. Server runs on Flask dev server (Waitress removed). All 26 tests pass.

## Constraints

- **Tech stack**: Flask (Python) — required backend framework.
- **Model loading**: `model.pkl` must be loaded at startup — minimize per-request load time.
- **Deployment**: Docker container required — must run locally.
- **Testing**: pytest tests exist in `tests/` directory — 26 tests across 3 files.

## Key Decisions

| Decision | Rationale | Outcome |
|----------|-----------|---------|
| Use `/predict` as canonical endpoint | Simpler, standard naming | ✓ Good |
| Store `model.pkl` at repo root | Matches current project layout | ✓ Good |
| Remove Waitress, use Flask dev server | User preference, no extra dependencies | ✓ Good |
| Split tests into separate files | Better organization: endpoints, preprocess, model | ✓ Good |
| Add `lightgbm` dependency | Model requires LightGBM classifier | ✓ Good |

## Evolution

This document evolves at phase transitions and milestone boundaries.

**After each phase transition** (via `/gsd-transition`):
1. Requirements invalidated? → Move to Out of Scope with reason
2. Requirements validated? → Move to Validated with phase reference
3. New requirements emerged? → Add to Active
4. Decisions to log? → Add to Key Decisions
5. "What This Is" still accurate? → Update if drifted

**After each milestone** (via `/gsd-complete-milestone`):
1. Full review of all sections
2. Core Value check — still the right priority?
3. Audit Out of Scope — reasons still valid?
4. Update Context with current state

---
*Last updated: 2026-05-16 after v1.0 milestone*
