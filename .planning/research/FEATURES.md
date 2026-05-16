# Feature Landscape: Model Training Pipeline

**Domain:** Text classification model training pipeline for fake news detection
**Researched:** 2026-05-16

## Context

This milestone adds a **model training pipeline** to an existing Flask API (v1.0). The API already has `/predict`, `/info`, `/` endpoints, a `preprocess.py` text cleaner, and loads `model.pkl` at startup. The new pipeline builds `model.pkl` from raw CSV datasets (`dataset/Fake.csv`, `dataset/True.csv`) and auto-runs on startup when the model is missing.

## Table Stakes

Features the training pipeline must have. Missing = model won't train or will be unusable.

| Feature | Why Expected | Complexity | Notes |
|---------|--------------|------------|-------|
| **Dataset loading (pandas)** | Raw data comes in two separate CSVs (`Fake.csv`, `True.csv`) with identical schema (`title`, `text`, `subject`, `date`). Must load both and combine. | Low | `pd.read_csv()` for each, then `pd.concat()`. Handle encoding issues (CSVs contain non-ASCII characters). |
| **Label assignment** | Each CSV needs a binary label: 0 = fake, 1 = true. | Low | Add `label` column during load: `fake_df["label"] = 0`, `true_df["label"] = 1`. |
| **Feature engineering (pandas)** | The model trains on a single text column, not separate title/text. Raw columns (`subject`, `date`) are not used for prediction. | Low | Create `string = title + " " + text`, drop `title`, `text`, `subject`, `date`. Handle NAs with `fillna("")` before concatenation. |
| **Preprocessing at scale** | The existing `preprocess.py` `clean_text()` function must be applied to every row. | Medium | Apply row-by-row via `df["string"].apply()` or vectorized. The function takes `(title, text)` — may need a wrapper that operates on the merged `string` column, or call with original columns before dropping. **Decision:** apply `clean_text(title, text)` before merging/dropping to reuse existing function. |
| **Train/test split** | Standard ML practice — need held-out data for evaluation. | Low | `train_test_split(X, y, test_size=0.2, random_state=42, stratify=y)`. Stratify ensures class balance in both splits. |
| **TF-IDF + LightGBM pipeline** | Text must be vectorized before the classifier can use it. Pipeline ensures consistent transform at inference time. | Medium | `Pipeline([("tfidf", TfidfVectorizer()), ("classifier", LGBMClassifier())])`. The pipeline is saved as `model.pkl` — at inference, `model.predict([text])` runs both steps. |
| **RandomizedSearchCV hyperparameter tuning** | Default LightGBM params are suboptimal. Tuning improves accuracy. | Medium | Search over `n_estimators`, `num_leaves`, `learning_rate`, `max_depth`, `colsample_bytree`, `subsample`, `reg_alpha`, `reg_lambda`. Use `n_iter=20-50`, `cv=3-5`, `scoring="accuracy"`, `n_jobs=-1`. |
| **Model persistence (joblib)** | Trained model must be saved as `model.pkl` for the API to load. | Low | `joblib.dump(best_model, "model.pkl")`. The existing `model.py` already does `joblib.load()`. |
| **Auto-run on startup (conditional)** | Training should run automatically when `model.pkl` doesn't exist, skip when it does. | Low | `if not MODEL_PATH.exists(): run_training()` in `app.py` startup. Must not block server when model exists. |

## Differentiators

Features that set this pipeline apart. Not expected, but valued.

| Feature | Value Proposition | Complexity | Notes |
|---------|-------------------|------------|-------|
| **Training metrics logging** | Print best params, best CV score, and test accuracy so users can verify model quality. | Low | After `RandomizedSearchCV.fit()`, log `best_params_`, `best_score_`, and `score(X_test, y_test)`. |
| **Reproducible random state** | Same dataset + same params = same model. Critical for debugging. | Low | Set `random_state=42` on `train_test_split`, `LGBMClassifier`, and `RandomizedSearchCV`. |
| **Stratified split** | Ensures fake/true ratio is preserved in train and test sets. | Low | `stratify=y` in `train_test_split`. Fake news datasets are often imbalanced. |
| **Pipeline encapsulation** | TF-IDF vectorizer + classifier in one object means inference is a single `predict()` call. | Low | `Pipeline` from sklearn handles this natively. The existing API already calls `model.predict([cleaned])`. |

## Anti-Features

Features to explicitly NOT build.

| Anti-Feature | Why Avoid | What to Do Instead |
|--------------|-----------|-------------------|
| **GridSearchCV** | Exhaustive search is too slow for LightGBM's parameter space. RandomizedSearchCV gives comparable results in fraction of time. | Use `RandomizedSearchCV` with `n_iter=20-50`. |
| **Optuna / FLAML** | Adds unnecessary dependencies for a local API. Overkill for this scope. | Stick with sklearn's `RandomizedSearchCV` — already in the stack. |
| **GPU training** | LightGBM GPU support requires compilation and adds complexity. Not needed for dataset of this size (~45K rows). | Use CPU (`n_jobs=-1` for parallel trees). |
| **Model retraining endpoint** | Exposing training via API adds security risk and complexity. Training is a startup-time concern. | Auto-run on startup only. Manual retraining = delete `model.pkl` and restart. |
| **Incremental / online learning** | LightGBM doesn't support true incremental learning well. Adds complexity with minimal benefit for a static dataset. | Full retrain from scratch when dataset updates. |
| **Cross-validation with early stopping inside RandomizedSearchCV** | sklearn's RandomizedSearchCV doesn't pass `eval_set` to inner folds. Workarounds are fragile and leak validation data. | Use standard CV without early stopping during search. Early stopping is optional for final model refit. |
| **Separate vectorizer + classifier files** | Saving TF-IDF and classifier separately complicates inference and version mismatches. | Save the full `Pipeline` as a single `model.pkl`. |

## Feature Dependencies

```
Dataset loading → Label assignment → Feature engineering → Preprocessing → Train/test split
                                                                              ↓
Model persistence ← RandomizedSearchCV (on pipeline) ← TF-IDF + LightGBM pipeline
        ↓
Auto-run on startup (depends on model.pkl existence check)
```

## LightGBM Hyperparameter Search Space (Recommended)

Based on LightGBM tuning docs and scikit-learn API patterns:

| Parameter | Distribution | Rationale |
|-----------|-------------|-----------|
| `n_estimators` | `randint(100, 1000)` | Number of trees. More trees = better fit but slower. |
| `num_leaves` | `randint(20, 150)` | LightGBM is leaf-wise; must be < 2^max_depth. Controls complexity. |
| `max_depth` | `randint(3, 12)` | Limits tree depth to prevent overfitting. |
| `learning_rate` | `uniform(0.01, 0.2)` | Lower = more stable but needs more trees. |
| `colsample_bytree` | `uniform(0.5, 0.5)` | Feature subsampling (0.5-1.0). Reduces overfitting. |
| `subsample` | `uniform(0.5, 0.5)` | Row subsampling (0.5-1.0). Reduces overfitting. |
| `reg_alpha` | `uniform(0, 5)` | L1 regularization. |
| `reg_lambda` | `uniform(0, 5)` | L2 regularization. |
| `min_child_samples` | `randint(5, 50)` | Minimum data per leaf. Higher = smoother model. |

## Training Script Structure (Recommended)

```
train_model.py
├── load_datasets()          # Load Fake.csv + True.csv, assign labels
├── engineer_features(df)    # Merge title+text, drop unused columns, handle NAs
├── preprocess_all(df)       # Apply clean_text() to every row
├── build_pipeline()         # Create TF-IDF + LightGBM Pipeline
├── tune_hyperparameters()   # RandomizedSearchCV with param distributions
├── evaluate_model()         # Score on test set, print metrics
├── save_model()             # joblib.dump to model.pkl
└── main()                   # Orchestrate all steps
```

## Startup Integration Pattern

```python
# In app.py (modified)
MODEL_PATH = Path(__file__).parent / "model.pkl"

if not MODEL_PATH.exists():
    from train_model import train_and_save
    train_and_save(MODEL_PATH)

load_model_or_exit(MODEL_PATH)
```

## MVP Recommendation

**Prioritize (in order):**
1. Dataset loading + labeling (foundation — nothing else works without data)
2. Feature engineering + preprocessing (prepares data for the model)
3. TF-IDF + LightGBM pipeline (core model structure)
4. Train/test split + RandomizedSearchCV (model quality)
5. Model persistence (enables API inference)
6. Auto-run on startup (usability)

**Defer:**
- Training metrics logging — nice to have, not blocking
- Extensive hyperparameter search — start with `n_iter=20`, increase later if needed
- Class weight balancing — check dataset balance first; LightGBM handles mild imbalance

## Complexity Summary

| Area | Complexity | Why |
|------|-----------|-----|
| Dataset loading | Low | Straightforward pandas operations |
| Feature engineering | Low | Column merge + drop + fillna |
| Preprocessing at scale | Medium | Row-by-row apply of existing function; may be slow on 45K rows |
| Pipeline construction | Low | sklearn Pipeline is well-documented |
| Hyperparameter tuning | Medium | RandomizedSearchCV is straightforward but search space design matters |
| Model persistence | Low | Single joblib.dump call |
| Startup integration | Low | File existence check + conditional function call |

## Sources

- scikit-learn Pipeline docs: https://scikit-learn.org/stable/modules/compose.html#pipeline (Confidence: HIGH)
- scikit-learn RandomizedSearchCV docs: https://scikit-learn.org/stable/modules/generated/sklearn.model_selection.RandomizedSearchCV.html (Confidence: HIGH)
- scikit-learn TfidfVectorizer docs: https://scikit-learn.org/stable/modules/generated/sklearn.feature_extraction.text.TfidfVectorizer.html (Confidence: HIGH)
- scikit-learn model persistence: https://scikit-learn.org/stable/modules/model_persistence.html (Confidence: HIGH)
- LightGBM LGBMClassifier API: https://lightgbm.readthedocs.io/en/latest/pythonapi/lightgbm.LGBMClassifier.html (Confidence: HIGH)
- LightGBM parameter tuning guide: https://lightgbm.readthedocs.io/en/latest/Parameters-Tuning.html (Confidence: HIGH)
- LightGBM sklearn API GridSearch example: https://github.com/microsoft/LightGBM/issues/146 (Confidence: MEDIUM)
- Towards Data Science LightGBM tuning: https://towardsdatascience.com/how-to-tune-the-hyperparameters-for-better-performance-cfe223d398b3/ (Confidence: MEDIUM)
