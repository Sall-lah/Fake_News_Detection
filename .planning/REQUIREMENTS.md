# Requirements: Fake News Detection API

**Defined:** 2026-05-16
**Core Value:** Return a reliable fake/true classification for a given title+text payload through a simple local API.

## v1.1 Requirements

### Dataset Loading & Prep

- [ ] **DATA-01**: Load `dataset/fake.csv` with pandas
- [ ] **DATA-02**: Load `dataset/true.csv` with pandas
- [ ] **DATA-03**: Combine both datasets into a single DataFrame
- [ ] **DATA-04**: Create `label` column (0 for fake, 1 for true)

### Feature Engineering

- [ ] **FEAT-01**: Combine `title` and `text` into `string` column separated by space
- [ ] **FEAT-02**: Drop `title`, `text`, `subject`, and `date` columns
- [ ] **FEAT-03**: Apply `preprocess.py` cleaning on all `string` column values
- [ ] **FEAT-04**: Remove rows with NA values
- [ ] **FEAT-05**: Filter out empty strings after preprocessing

### Model Training

- [ ] **TRAIN-01**: Split dataset into train/test sets (stratified)
- [ ] **TRAIN-02**: Build sklearn Pipeline with TF-IDF vectorizer and LightGBM classifier
- [ ] **TRAIN-03**: Run RandomizedSearchCV for hyperparameter tuning
- [ ] **TRAIN-04**: Print training metrics (accuracy, classification report, best params)

### Model Persistence

- [ ] **SAVE-01**: Save trained model as `model.pkl` using joblib

### Startup Integration

- [ ] **START-01**: Auto-run training script on server startup when `model.pkl` is missing
- [ ] **START-02**: Skip training when `model.pkl` already exists
- [ ] **START-03**: Use lazy import pattern to avoid pandas overhead on warm starts
- [ ] **START-04**: Add soft `load_model()` function to `model.py` (returns None if missing)

### Dependencies

- [ ] **DEP-01**: Add `pandas==3.0.3` to `requirements.txt`
- [ ] **DEP-02**: Pin `lightgbm==4.6.0` in `requirements.txt`

### Docker

- [ ] **DOCKER-01**: Update Dockerfile to include dataset files and support conditional training at startup

## v2 Requirements

Deferred to future release. Tracked but not in current roadmap.

### Notifications

- **NOTF-01**: User receives in-app notifications
- **NOTF-02**: User receives email for new followers
- **NOTF-03**: User receives email for comments on own posts
- **NOTF-04**: User can configure notification preferences

### Moderation

- **MODR-01**: User can report content
- **MODR-02**: User can block other users
- **MODR-03**: Admin can view reported content
- **MODR-04**: Admin can remove content
- **MODR-05**: Admin can ban users

## Out of Scope

| Feature | Reason |
|---------|--------|
| Rate limiting or advanced security controls | Local API only |
| External services or hosted deployments | Local runtime only |
| UI or frontend | API-only deliverable |
| Training endpoint via API | Security risk, out of scope |
| Incremental/online learning | LightGBM doesn't support it well |
| Extensive hyperparameter search | Start with n_iter=20, increase later |
| Class weight balancing | Check dataset balance first |

## Traceability

Which phases cover which requirements. Updated during roadmap creation.

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
| DOCKER-01 | Phase 7 | Pending |

**Coverage:**
- v1.1 requirements: 21 total (20 original + 1 DOCKER-01 added during roadmap)
- Mapped to phases: 21
- Unmapped: 0 ✓

---
*Requirements defined: 2026-05-16*
*Last updated: 2026-05-16 after v1.1 roadmap creation*
