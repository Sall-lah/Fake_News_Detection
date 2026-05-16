# Phase 05: Training Script - Context

**Gathered:** 2026-05-16
**Status:** Ready for planning

<domain>
## Phase Boundary

A standalone `train.py` that loads `dataset/Fake.csv` and `dataset/True.csv`, preprocesses text, trains a LightGBM+TF-IDF pipeline with RandomizedSearchCV hyperparameter tuning, and saves the trained model as `model.pkl` at the project root. Idempotent — overwrites existing `model.pkl` on re-run.

</domain>

<decisions>
## Implementation Decisions

### CLI Argument Design
- **D-01:** Hardcoded default paths: `dataset/Fake.csv` and `dataset/True.csv` relative to project root. No CLI arguments needed for basic usage.

### Preprocessing Reuse
- **D-02:** Import and reuse `clean_text()` from `preprocess.py` for training data. Guarantees identical text processing between training and inference. No separate training preprocessing logic.

### Training Pipeline Design
- **D-03:** 80/20 stratified train/test split. Standard ML practice with sufficient training data.
- **D-04:** Output after training: accuracy score, classification report (precision/recall/f1 per class), and best hyperparameters from RandomizedSearchCV.

### Hyperparameter Tuning
- **D-05:** RandomizedSearchCV with n_iter=5, cv=2, scoring='accuracy'. Fast training suitable for local development with ~44K rows.
- **D-06:** Optimize for accuracy — matches ROADMAP success criteria.

### the agent's Discretion
- Exact parameter distributions for RandomizedSearchCV (learning rate, num_leaves, etc.) left to planner/researcher.
- Random state for reproducibility — planner should set a fixed seed.
- Whether to print training time — flexible.
- Model pipeline structure (TF-IDF params, LightGBM params) — researcher should determine best ranges.

</decisions>

<canonical_refs>
## Canonical References

**Downstream agents MUST read these before planning or implementing.**

### Phase Requirements
- `.planning/ROADMAP.md` §Phase 5 — Goal, requirements (DATA-01 through DATA-04, FEAT-01 through FEAT-05, TRAIN-01 through TRAIN-04, SAVE-01), and 5 success criteria
- `.planning/REQUIREMENTS.md` — All DATA-*, FEAT-*, TRAIN-*, SAVE-* requirement definitions

### Source Files (used by this phase)
- `preprocess.py` — `clean_text(title, text)` function to reuse for training preprocessing
- `model.py` — `load_model()` and `get_model()` for post-training verification
- `requirements.txt` — All dependencies already pinned (pandas, lightgbm, scikit-learn, numpy, scipy, joblib)

### Dataset
- `dataset/Fake.csv` — 23,481 rows, columns: title, text, subject, date (label = 0)
- `dataset/True.csv` — 21,417 rows, columns: title, text, subject, date (label = 1)
- Total: ~44,898 rows

### Existing Code Patterns
- `preprocess.py:8-32` — `clean_text()` implementation: combines title+text, lowercases, removes non-letters, removes stopwords, deduplicates tokens, normalizes whitespace
- `model.py` — Global MODEL pattern, joblib serialization

No external specs — requirements fully captured in decisions above.

</canonical_refs>

<code_context>
## Existing Code Insights

### Reusable Assets
- `preprocess.clean_text(title, text)` — Exact same function used by the API's `/predict` endpoint. Must be reused for training to ensure consistency.
- `joblib` — Already used for model persistence in `model.py`. Use for saving `model.pkl`.
- `sklearn.feature_extraction.text.ENGLISH_STOP_WORDS` — Already imported in preprocess.py. Available for training too.
- `pathlib.Path` — Consistent path handling pattern across the project.

### Established Patterns
- `from __future__ import annotations` — Present in all Python files.
- Type hints with `str | None` and `object | None` — Used throughout.
- Global module-level constants (MODEL_PATH in app.py) — Pattern for configuration.
- `__all__` exports in preprocess.py — Clean module interface.

### Integration Points
- `train.py` must produce a `model.pkl` compatible with `model.py`'s `joblib.load()` — sklearn Pipeline object.
- The pipeline must accept the same preprocessed text format that `clean_text()` produces (single string).
- Phase 6 will call `train.py` programmatically from app.py startup — `train.py` should be importable as a module (not just a script).
- Phase 7 will run `train.py` inside Docker — paths must work relative to project root.

</code_context>

<specifics>
## Specific Ideas

No specific requirements — open to standard approaches. User prefers simplicity: hardcoded paths, reuse existing code, fast training (n_iter=5, cv=2).

</specifics>

<deferred>
## Deferred Ideas

None — discussion stayed within phase scope.

</deferred>

---

*Phase: 05-Training Script*
*Context gathered: 2026-05-16*
