# Roadmap: Fake News Detection API

## Milestones

- ✅ **v1.0 MVP** — Phases 1-2 (shipped 2026-05-16)
- ✅ **v1.1 Model Training Pipeline** — Phases 3-7 (complete)

## Phases

<details>
<summary>✅ v1.0 MVP (Phases 1-2) — SHIPPED 2026-05-16</summary>

- [x] Phase 1: Core Local Inference API (3/3 plans) — completed 2026-05-16
- [x] Phase 2: API Documentation & Docker Deployment (2/2 plans) — completed 2026-05-16

</details>

<details open>
<summary>🔄 v1.1 Model Training Pipeline (Phases 3-7)</summary>

- [ ] **Phase 3: Dependencies & Foundation** — Add pandas and pin lightgbm in requirements.txt
- [ ] **Phase 4: Model Loader Refactoring** — Add soft load_model() to model.py
- [ ] **Phase 5: Training Script** — Build train.py: load CSVs, preprocess, train LightGBM pipeline, save model.pkl
- [ ] **Phase 6: Startup Hook Integration** — Wire conditional training into app.py startup
- [ ] **Phase 7: Docker & Deployment** — Update Dockerfile for dataset + build-time training

</details>

## Phase Details

### Phase 3: Dependencies & Foundation
**Goal**: All required Python packages installed with pinned versions to prevent pickle incompatibility
**Depends on**: Nothing (first phase of v1.1)
**Requirements**: DEP-01, DEP-02
**Success Criteria** (what must be TRUE):
  1. `pip install -r requirements.txt` completes without errors, installing pandas 3.0.3 and lightgbm 4.6.0
  2. `import pandas` and `import lightgbm` succeed in the project's Python environment
  3. `requirements.txt` contains pinned versions (`==`) for all ML dependencies (pandas, lightgbm, scikit-learn, numpy, scipy, joblib)
**Plans**: 1 plan
Plans:
- [x] 03-01-PLAN.md — Update requirements.txt with pinned deps and verify installation

### Phase 4: Model Loader Refactoring
**Goal**: model.py supports soft loading (returns None if missing) to enable conditional startup training
**Depends on**: Phase 3
**Requirements**: START-04
**Success Criteria** (what must be TRUE):
  1. `load_model()` returns None when `model.pkl` does not exist (no crash)
  2. `load_model()` returns the loaded pipeline when `model.pkl` exists
  3. `load_model_or_exit()` still exits with error when model is missing (backward compatible)
  4. Existing `/predict` endpoint continues to work unchanged with the existing model.pkl
**Plans**: 1 plan
Plans:
- [x] 04-01-PLAN.md — Add load_model() soft-load and refactor load_model_or_exit() to delegate

### Phase 5: Training Script
**Goal**: A standalone `train.py` builds a trained `model.pkl` from raw CSV datasets
**Depends on**: Phase 3
**Requirements**: DATA-01, DATA-02, DATA-03, DATA-04, FEAT-01, FEAT-02, FEAT-03, FEAT-04, FEAT-05, TRAIN-01, TRAIN-02, TRAIN-03, TRAIN-04, SAVE-01
**Success Criteria** (what must be TRUE):
  1. Running `python train.py` with `dataset/fake.csv` and `dataset/true.csv` produces a `model.pkl` file at the project root
  2. Training output prints accuracy, classification report, and best hyperparameters
  3. The saved `model.pkl` can be loaded and produces predictions when given title+text input
  4. Running `train.py` when `model.pkl` already exists overwrites it (idempotent retraining)
  5. Rows that become empty after preprocessing are filtered out without crashing TF-IDF
**Plans**: 2 plans
Plans:
- [x] 05-01-PLAN.md — Data loading, combination, and feature engineering (DATA-01 to FEAT-05)
- [x] 05-02-PLAN.md — Training pipeline, hyperparameter tuning, metrics, model persistence (TRAIN-01 to SAVE-01)

### Phase 6: Startup Hook Integration
**Goal**: Flask app auto-trains on first startup when model.pkl is missing, skips on warm starts
**Depends on**: Phase 4, Phase 5
**Requirements**: START-01, START-02, START-03
**Success Criteria** (what must be TRUE):
  1. Starting the Flask app without `model.pkl` triggers training, then serves predictions after training completes
  2. Starting the Flask app with `model.pkl` present skips training and loads the model immediately (fast startup)
  3. On warm start (model.pkl exists), pandas is not imported (lazy import pattern — no unnecessary overhead)
  4. The `/predict` endpoint works correctly after both cold start (with training) and warm start (without training)
**Plans**: 2 plans
Plans:

Wave 1 *(parallel — no dependencies)*:
- [x] 06-01-PLAN.md — Extract train() function from train.py for importable training (START-01)

Wave 2 *(blocked on Wave 1 completion)*:
- [x] 06-02-PLAN.md — Wire conditional startup flow in app.py (START-01, START-02, START-03)

Cross-cutting constraints:
- Training blocks startup until complete (D-02)
- Lazy import of train module on cold start only (D-05, START-03)

### Phase 7: Docker & Deployment
**Goal**: Docker image includes dataset and produces a working container with pre-trained model
**Depends on**: Phase 3, Phase 4, Phase 5, Phase 6
**Requirements**: DOCKER-01
**Success Criteria** (what must be TRUE):
  1. `docker build` succeeds and produces an image that includes the dataset files
  2. Running the container without a pre-existing model.pkl triggers training at startup, then serves predictions
  3. The `/predict` endpoint returns correct fake/true classifications from within the container
**Plans**: 1 plan
Plans:
- [x] 07-01-PLAN.md — Update Dockerfile (dataset COPY, no model.pkl) and .dockerignore

## Progress

| Phase | Plans Complete | Status | Completed |
|-------|----------------|--------|-----------|
| 1. Core Local Inference API | 3/3 | Complete | 2026-05-16 |
| 2. API Documentation & Docker Deployment | 2/2 | Complete | 2026-05-16 |
| 3. Dependencies & Foundation | 1/1 | Complete   | 2026-05-16 |
| 4. Model Loader Refactoring | 1/1 | Complete   | 2026-05-16 |
| 5. Training Script | 2/2 | Complete   | 2026-05-16 |
| 6. Startup Hook Integration | 2/2 | Complete   | 2026-05-16 |
| 7. Docker & Deployment | 1/1 | Complete   | 2026-05-16 |

## Coverage

| Requirement | Phase | Status |
|-------------|-------|--------|
| DEP-01 | Phase 3 | Pending |
| DEP-02 | Phase 3 | Pending |
| START-04 | Phase 4 | Pending |
| DATA-01 | Phase 5 | Pending |
| DATA-02 | Phase 5 | Pending |
| DATA-03 | Phase 5 | Pending |
| DATA-04 | Phase 5 | Pending |
| FEAT-01 | Phase 5 | Pending |
| FEAT-02 | Phase 5 | Pending |
| FEAT-03 | Phase 5 | Pending |
| FEAT-04 | Phase 5 | Pending |
| FEAT-05 | Phase 5 | Pending |
| TRAIN-01 | Phase 5 | Pending |
| TRAIN-02 | Phase 5 | Pending |
| TRAIN-03 | Phase 5 | Pending |
| TRAIN-04 | Phase 5 | Pending |
| SAVE-01 | Phase 5 | Pending |
| START-01 | Phase 6 | Pending |
| START-02 | Phase 6 | Pending |
| START-03 | Phase 6 | Pending |
| DOCKER-01 | Phase 7 | Complete |

**Coverage:**
- v1.1 requirements: 21 total (20 original + 1 added for Docker)
- Mapped to phases: 21
- Unmapped: 0 ✓
