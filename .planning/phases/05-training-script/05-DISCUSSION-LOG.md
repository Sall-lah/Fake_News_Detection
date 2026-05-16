# Phase 05: Training Script - Discussion Log

> **Audit trail only.** Do not use as input to planning, research, or execution agents.
> Decisions are captured in CONTEXT.md — this log preserves the alternatives considered.

**Date:** 2026-05-16
**Phase:** 05-training-script
**Areas discussed:** CLI argument design, Preprocessing reuse, Training pipeline design, Hyperparameter tuning

---

## CLI Argument Design

| Option | Description | Selected |
|--------|-------------|----------|
| --fake and --true flags | python train.py --fake dataset/Fake.csv --true dataset/True.csv. Explicit, flexible. | |
| Positional arguments | python train.py dataset/Fake.csv dataset/True.csv. Simple but less clear. | |
| Hardcoded defaults | Hardcoded paths in train.py. Simplest, less flexible. | ✓ |

**User's choice:** Hardcoded defaults
**Notes:** Paths: `dataset/Fake.csv` and `dataset/True.csv` relative to project root. Matches current file layout.

---

## Preprocessing Reuse

| Option | Description | Selected |
|--------|-------------|----------|
| Reuse clean_text | Import clean_text from preprocess.py. Guarantees identical training/inference processing. | ✓ |
| Separate training preprocess | Copy logic into train.py. More control but risks drift. | |
| Reuse + training wrapper | Import clean_text with a training-specific wrapper for NA handling. | |

**User's choice:** Reuse clean_text (recommended)
**Notes:** Critical for consistency — training and inference must process text identically.

---

## Training Pipeline Design

| Option | Description | Selected |
|--------|-------------|----------|
| 80/20 stratified | Standard ML practice, good balance of training data and evaluation. | ✓ |
| 70/30 stratified | More test data, less training data. | |
| Train/val/test split | 70/15/15. Better for hyperparameter tuning but more complex. | |

**User's choice:** 80/20 stratified (recommended)
**Notes:** Standard approach, sufficient data for both sets.

---

## Training Output

| Option | Description | Selected |
|--------|-------------|----------|
| Accuracy + report + best params | Print accuracy, classification report, best hyperparameters. | ✓ |
| Add confusion matrix + AUC | Also include confusion matrix, ROC-AUC, training time. More verbose. | |
| Minimal output | Just accuracy and best params. | |

**User's choice:** Accuracy + report + best params (recommended)
**Notes:** Matches ROADMAP success criteria — "prints accuracy, classification report, and best hyperparameters".

---

## Hyperparameter Tuning

| Option | Description | Selected |
|--------|-------------|----------|
| n_iter=20, cv=3 | Reasonable speed for local training (~44K rows). | |
| n_iter=50, cv=5 | More thorough but significantly slower. | |
| n_iter=10, cv=2 | Fastest, may miss good hyperparameters. | |
| n_iter=5, cv=2 | Between fast and recommended. Quick training. | ✓ |

**User's choice:** n_iter=5, cv=2
**Notes:** User wants fast training. With ~44K rows, even n_iter=5 with cv=2 will take some time but is acceptable for local use.

---

## Scoring Metric

| Option | Description | Selected |
|--------|-------------|----------|
| accuracy | Optimize for overall accuracy. Matches ROADMAP criteria. | ✓ |
| f1_macro | Better for class imbalance. | |
| f1_weighted | Accounts for class imbalance with support weighting. | |

**User's choice:** accuracy (recommended)
**Notes:** Dataset is relatively balanced (23K fake vs 21K true), so accuracy is a reasonable metric.

---

## the agent's Discretion

- Exact parameter distributions for RandomizedSearchCV (learning rate, num_leaves, etc.) left to planner/researcher.
- Random state for reproducibility — planner should set a fixed seed.
- Whether to print training time — flexible.
- Model pipeline structure (TF-IDF params, LightGBM params) — researcher should determine best ranges.

## Deferred Ideas

None — discussion stayed within phase scope.
