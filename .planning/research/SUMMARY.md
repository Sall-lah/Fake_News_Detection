# Project Research Summary

**Project:** Fake News Detection API
**Domain:** ML model training pipeline for a Flask-based fake news classification API
**Researched:** 2026-05-16
**Confidence:** HIGH

## Executive Summary

This milestone (v1.1) adds a **model training pipeline** to an existing Flask API that already serves fake/true predictions via `model.pkl`. The pipeline loads two CSV datasets (`Fake.csv`, `True.csv`), applies shared text preprocessing, trains a TF-IDF + LightGBM classifier with hyperparameter tuning via `RandomizedSearchCV`, and persists the result as `model.pkl`. The model auto-trains on first startup when `model.pkl` is missing, then skips on subsequent boots. This is a well-understood pattern for local ML services — the research identified clear, standard approaches with no exotic dependencies.

The recommended approach keeps training in a **standalone `train.py`** script (not inside `app.py`), reuses the existing `preprocess.py` for training-serving parity, wraps TF-IDF + LightGBM in a single sklearn Pipeline, and uses a conditional startup hook in `app.py` that only imports training code when needed. The only new dependency is **pandas 3.0.3**; everything else (scikit-learn, LightGBM, joblib) already exists in the v1.0 stack but needs version pinning (especially `lightgbm==4.6.0`, which was previously unpinned).

The key risks are: (1) **data leakage** from preprocessing before train/test split — mitigated by sklearn Pipeline encapsulation; (2) **training blocking Flask startup** — mitigated by conditional skip when `model.pkl` exists and build-time training in Docker; (3) **pickle version mismatch** between training and inference — mitigated by exact version pins and training inside the same Docker image; (4) **CPU oversubscription** during hyperparameter search — mitigated by explicit thread budgeting (`n_jobs=1` for search, `n_jobs=-1` for LightGBM).

## Key Findings

### Recommended Stack

The v1.1 stack adds only **pandas 3.0.3** to v1.0. All other capabilities (TF-IDF, LightGBM, RandomizedSearchCV, joblib serialization, train/test split) are already covered by existing dependencies. The critical change is **pinning all versions** — `lightgbm` was unpinned in v1.0, which risks pickle incompatibility.

**Core technologies:**
- **Python 3.13.x** — runtime; pandas 3.0.x requires >=3.11
- **Flask 3.1.1** — HTTP API framework (explicit requirement)
- **scikit-learn 1.7.1** — Pipeline, TF-IDF, train_test_split, RandomizedSearchCV
- **pandas 3.0.3** — CSV loading, DataFrame manipulation, dataset combining (NEW)
- **lightgbm 4.6.0** — LGBMClassifier for binary classification (must pin)
- **numpy 2.4.4 / scipy 1.17.1 / joblib 1.5.3** — supporting ML dependencies

**What NOT to add:** Dask/Polars (overkill for 2 CSVs), MLflow/W&B (unnecessary for local API), `before_first_request` (removed in Flask 2.3), GridSearchCV (too slow), Optuna/FLAML (unnecessary complexity).

### Expected Features

**Must have (table stakes):**
- **Dataset loading** — `pd.read_csv()` + `pd.concat()` for Fake.csv + True.csv
- **Label assignment** — explicit 0=fake, 1=true integers
- **Feature engineering** — merge title+text into single `string` column, handle NAs
- **Preprocessing at scale** — apply `clean_text()` from existing `preprocess.py` to every row
- **Train/test split** — stratified split (preserve class balance)
- **TF-IDF + LightGBM pipeline** — sklearn Pipeline for consistent inference
- **RandomizedSearchCV** — hyperparameter tuning (n_iter=20, cv=3)
- **Model persistence** — `joblib.dump()` as single `model.pkl`
- **Auto-run on startup** — conditional: only train when `model.pkl` missing

**Should have (differentiators):**
- **Training metrics logging** — print best params, CV score, test accuracy
- **Reproducible random state** — `random_state=42` everywhere
- **Stratified split** — handles class imbalance
- **Pipeline encapsulation** — single `predict()` call at inference

**Defer (v2+):**
- Extensive hyperparameter search (start with n_iter=20, increase later)
- Class weight balancing (check dataset balance first)
- Training endpoint via API (security risk, out of scope)
- Incremental/online learning (LightGBM doesn't support it well)

### Architecture Approach

The architecture introduces one new file (`train.py`) and modifies three existing ones (`app.py`, `model.py`, `Dockerfile`). The design follows three key patterns: (1) **conditional startup training** — check artifact existence before expensive setup; (2) **shared preprocessing** — import `preprocess.py` in both training and inference to eliminate training-serving skew; (3) **pipeline-as-artifact** — serialize the full sklearn Pipeline as a single `model.pkl`.

**Major components:**
1. **`train.py`** (NEW) — standalone training script: loads CSVs, labels, preprocesses, splits, tunes, saves model
2. **`app.py`** (MODIFIED) — Flask app with conditional startup hook: trains if model missing, then loads
3. **`model.py`** (MODIFIED) — adds soft `load_model()` returning None, preserves hard `load_model_or_exit()`
4. **`preprocess.py`** (UNCHANGED) — shared text cleaning used by both training and inference
5. **`Dockerfile`** (MODIFIED) — copies dataset, adds pandas, supports conditional training at startup

**Build order:** requirements.txt → model.py → train.py → app.py → Dockerfile → tests

### Critical Pitfalls

1. **Data leakage (preprocessing before split)** — Never call `fit()` or `fit_transform()` on full data. Use sklearn Pipeline so `fit_transform` only sees training folds during CV. Split first, then process.
2. **Training blocking Flask startup** — Full RandomizedSearchCV can take minutes. Keep `model.pkl` committed so Docker copies it (warm start). Training at startup is a safety net, not the primary path.
3. **CPU oversubscription during search** — `n_jobs=-1` on both RandomizedSearchCV and LightGBM causes thread contention. Use `n_jobs=1` for search, `n_jobs=-1` for LightGBM.
4. **Pickle version mismatch** — scikit-learn doesn't support cross-version model loading. Pin all ML dependencies with `==` and train inside the same Docker image.
5. **Empty strings after preprocessing** — Rows reduced to empty after stopword removal will crash TF-IDF. Filter empty rows after preprocessing; log dropped count.

## Implications for Roadmap

Based on research, suggested phase structure:

### Phase 1: Dependencies & Foundation
**Rationale:** Everything depends on having the right packages installed with correct versions. This unblocks all subsequent work.
**Delivers:** Updated `requirements.txt` with pinned versions (adds pandas, pins lightgbm), dependency installation verification
**Addresses:** Pickle version mismatch prevention (Pitfall 4)
**Uses:** pandas 3.0.3, lightgbm 4.6.0, scikit-learn 1.7.1

### Phase 2: Model Loader Refactoring
**Rationale:** `model.py` must support soft loading (returns None) before `app.py` can implement the conditional startup hook. This is a prerequisite for Phase 3.
**Delivers:** Modified `model.py` with `load_model()` (soft) and `load_model_or_exit()` (hard) functions
**Addresses:** Training blocking startup (Pitfall 2) — enables conditional skip pattern
**Implements:** Architecture component: model.py modifications

### Phase 3: Training Script (`train.py`)
**Rationale:** The core of this milestone. Depends on Phase 1 (dependencies) and reuses `preprocess.py` (existing). Must implement split-first ordering to avoid data leakage.
**Delivers:** Standalone `train.py` with load_datasets → prepare_data → build_pipeline → RandomizedSearchCV → save_model
**Addresses:** Data leakage (Pitfall 1), CPU oversubscription (Pitfall 3), empty string handling (Pitfall 5), label encoding (Pitfall 6)
**Implements:** Architecture component: train.py (NEW)
**Features:** Dataset loading, label assignment, feature engineering, preprocessing at scale, train/test split, TF-IDF + LightGBM pipeline, RandomizedSearchCV, model persistence, training metrics logging

### Phase 4: Startup Hook Integration (`app.py`)
**Rationale:** Depends on Phase 2 (model loader) and Phase 3 (training script). Ties everything together into the Flask app.
**Delivers:** Modified `app.py` with conditional startup: check model → train if missing → load → serve
**Addresses:** Training blocking startup (Pitfall 2) — conditional skip, lazy import
**Implements:** Architecture component: app.py modifications, Pattern 1 (conditional startup training)
**Features:** Auto-run on startup (conditional)

### Phase 5: Docker & Deployment
**Rationale:** Depends on all previous phases. Updates container to support dataset copying and conditional training.
**Delivers:** Modified `Dockerfile` with dataset COPY, pandas in requirements, model.pkl safety net
**Addresses:** Docker build caching (Pitfall 9), pickle version mismatch (Pitfall 4) — train in same image
**Implements:** Architecture component: Dockerfile modifications

### Phase Ordering Rationale

- **Dependencies first** because nothing else installs without them
- **Model loader before app.py** because the startup hook needs the soft-load API
- **Training script before startup hook** because the hook imports and calls it
- **Docker last** because it packages everything built in previous phases
- This ordering avoids all critical pitfalls by establishing version pins, split-first training, and conditional startup before any integration point

### Research Flags

Phases likely needing deeper research during planning:
- **Phase 3 (Training Script):** Hyperparameter search space design — the recommended ranges are starting points; actual optimal ranges depend on dataset characteristics. May benefit from a quick spike to validate search space.

Phases with standard patterns (skip research-phase):
- **Phase 1 (Dependencies):** Well-documented, straightforward version pinning
- **Phase 2 (Model Loader):** Simple refactoring with clear API contract
- **Phase 4 (Startup Hook):** Standard conditional initialization pattern
- **Phase 5 (Docker):** Standard COPY + RUN pattern for ML services

## Confidence Assessment

| Area | Confidence | Notes |
|------|------------|-------|
| Stack | HIGH | All versions verified via PyPI and Context7 docs; pandas 3.0.3 compatibility with Python 3.13 confirmed |
| Features | HIGH | Table stakes derived from sklearn/LightGBM docs; feature dependencies clearly mapped |
| Architecture | HIGH | Component boundaries well-defined; patterns validated against Flask and sklearn best practices |
| Pitfalls | HIGH | All critical pitfalls sourced from official sklearn docs, Flask lifecycle docs, and documented Stack Overflow reports |

**Overall confidence:** HIGH

### Gaps to Address

- **Dataset characteristics unknown:** The exact size, class balance, and text quality of `Fake.csv` / `True.csv` are not confirmed. This affects RandomizedSearchCV configuration (n_iter, cv folds) and whether class weight balancing is needed. Validate during Phase 3 implementation.
- **Existing `model.pkl` training provenance:** The current model.pkl was trained with unknown versions and parameters. If retraining produces significantly different results, this may indicate the original model used different preprocessing or features. Compare metrics during Phase 3.
- **Docker dev server vs. production WSGI:** The current Dockerfile uses Flask dev server. STACK.md recommends Waitress for local production use, but this is deferred — the dev server is acceptable for local-only API. Consider upgrading in a future milestone.

## Sources

### Primary (HIGH confidence)
- `/scikit-learn/scikit-learn/1.7.1` — model persistence, Pipeline best practices, data leakage prevention
- `/pandas-dev/pandas` — CSV loading, pd.concat patterns
- `/lightgbm-org/lightgbm` — LGBMClassifier sklearn API, parameter tuning
- https://flask.palletsprojects.com/en/latest/lifecycle/ — Flask 3.2 lifecycle docs (setup before first request)
- https://scikit-learn.org/stable/modules/compose.html — Pipeline composition
- https://scikit-learn.org/stable/modules/model_persistence.html — pickle version compatibility warnings

### Secondary (MEDIUM confidence)
- https://pypi.org/project/pandas/ — pandas 3.0.3 release info
- https://pypi.org/project/lightgbm/ — lightgbm 4.6.0 release info
- LightGBM parameter tuning guide (readthedocs)
- Stack Overflow: LightGBM + RandomizedSearchCV CPU/memory oversubscription
- GitHub issues: scikit-learn pickle compatibility breaks across versions

### Tertiary (LOW confidence)
- Towards Data Science LightGBM tuning article — hyperparameter range recommendations
- Docker ML deployment best practices — build-time vs runtime training patterns

---
*Research completed: 2026-05-16*
*Ready for roadmap: yes*
