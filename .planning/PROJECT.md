# Fake News Detection API

## What This Is

A local Flask API that auto-trains a LightGBM + TF-IDF model from raw CSV datasets on first startup (cold start), then serves fake/true predictions via `/predict`. Subsequent startups skip training and load the pre-trained `model.pkl` directly (warm start). Containerized via Dockerfile with dataset included for runtime training.

## Core Value

Users can send a title + text and reliably receive a fake/true prediction — with zero manual model setup. The server trains itself on first run.

## Current State

**Shipped:** v1.1 Model Training Pipeline (2026-05-16)

All 7 phases complete (5 v1.1 phases + 2 v1.0 phases). The application:
- Trains automatically on cold start when `model.pkl` is missing (~8 minutes)
- Skips training on warm start with lazy pandas import
- Achieves 99.87% accuracy with optimized hyperparameters
- Serves predictions via Flask API (`/`, `/info`, `/predict`)
- Includes dataset in Docker image for container runtime training

<details>
<summary>v1.1 Milestone Goals (completed)</summary>

**Original Goal:** Add a model training script that builds `model.pkl` from raw CSV datasets using pandas, and auto-runs on server startup (skipped if model already exists).

**Target features (all delivered):**
- Dataset loader (pandas): combine `fake.csv` + `true.csv`, label them (0/1)
- Feature engineering (pandas): merge title+text, drop raw columns, clean NAs
- Apply `preprocess.py` on all 'string' column
- Train/test split
- LightGBM + TF-IDF pipeline with RandomizedSearchCV hyperparameter tuning
- Save trained model as `model.pkl`
- Auto-run training on server startup when `model.pkl` is missing
- Skip training when `model.pkl` already exists

</details>

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
- ✓ Install pinned ML dependencies (pandas, lightgbm, scikit-learn, numpy, scipy, joblib) — v1.1
- ✓ Soft-load model without crash when `model.pkl` is missing — v1.1
- ✓ Train model from raw CSVs and save `model.pkl` at project root — v1.1
- ✓ Auto-train on cold start, skip on warm start — v1.1
- ✓ Docker image includes dataset for runtime training — v1.1

### Active

(None — planning next milestone)

### Out of Scope

- Rate limiting or advanced security controls — local API only.
- External services or hosted deployments — local runtime only.
- UI or frontend — API-only deliverable.

## Context

Shipped v1.1 with ~400 LOC Python (app.py, model.py, preprocess.py, train.py) + tests (26 pytest tests across 3 files). Tech stack: Flask 3.1.1, scikit-learn 1.7.1, LightGBM 4.6.0, pandas 3.0.3, Python 3.13. Model trained via RandomizedSearchCV with 99.87% accuracy. Server runs on Flask dev server with conditional startup training. All 26 tests pass.

## Constraints

- **Tech stack**: Flask (Python) — required backend framework.
- **Model loading**: `model.pkl` must be loaded at startup — minimize per-request load time.
- **Deployment**: Docker container required — must run locally.
- **Testing**: pytest tests exist in `tests/` directory — 26 tests across 3 files.
- **Training**: `n_jobs=1` required for RandomizedSearchCV to prevent LightGBM errors on Windows.

## Key Decisions

| Decision | Rationale | Outcome |
|----------|-----------|---------|
| Use `/predict` as canonical endpoint | Simpler, standard naming | ✓ Good |
| Store `model.pkl` at repo root | Matches current project layout | ✓ Good |
| Remove Waitress, use Flask dev server | User preference, no extra dependencies | ✓ Good |
| Split tests into separate files | Better organization: endpoints, preprocess, model | ✓ Good |
| Add `lightgbm` dependency | Model requires LightGBM classifier | ✓ Good |
| Use `n_jobs=1` for RandomizedSearchCV | Prevents LightGBM access violation on Windows | ✓ Good |
| Suppress LGBMClassifier feature name warning | Noisy but harmless during prediction | ✓ Good |
| Train at runtime (container startup), NOT at build time | Keeps Docker image smaller, trains on target hardware | ✓ Good |
| Do NOT include model.pkl in Docker image | Dataset is source of truth; model trains from it | ✓ Good |

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
*Last updated: 2026-05-17 after v1.1 milestone*
