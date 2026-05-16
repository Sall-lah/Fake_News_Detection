---
status: complete
phase: 05-training-script
source: 05-01-SUMMARY.md, 05-02-SUMMARY.md
started: 2026-05-16T23:57:00Z
updated: 2026-05-16T23:57:00Z
---

## Current Test

[testing complete]

## Tests

### 1. train.py loads both CSVs and combines them
expected: Running `train.py` loads `dataset/Fake.csv` and `dataset/True.csv`, combines with labels (0=fake, 1=true), produces ~44,898 rows.
result: pass

### 2. train.py applies preprocessing via clean_text()
expected: Text preprocessing uses shared `clean_text()` from `preprocess.py`. Empty/NA rows filtered without crashing.
result: pass

### 3. train.py trains TF-IDF + LightGBM pipeline
expected: Training runs with RandomizedSearchCV (n_iter=5, cv=2, scoring='accuracy'). 80/20 stratified split.
result: pass

### 4. train.py prints accuracy, classification report, best params
expected: Output includes accuracy score, classification report (precision/recall/f1), and best hyperparameters.
result: pass

### 5. train.py saves model.pkl at project root
expected: `model.pkl` saved at project root. Can be loaded and produces predictions. Idempotent (overwrites on re-run).
result: pass

## Summary

total: 5
passed: 5
issues: 0
pending: 0
skipped: 0
blocked: 0

## Gaps

[none yet]
