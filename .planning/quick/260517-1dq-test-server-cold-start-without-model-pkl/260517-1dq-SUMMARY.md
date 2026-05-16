---
status: complete
date: "2026-05-16"
---

# Quick Task 260517-1dq: Cold Start Test

## Summary

Tested server cold start behavior when `model.pkl` is absent from project root. The app correctly detected the missing model, triggered training via `train.py`, and served predictions after training completed.

## Results

| Check | Result |
|-------|--------|
| model.pkl removed before start | ✅ |
| Training triggered automatically | ✅ |
| Training completed (~8 min) | ✅ |
| Accuracy: 0.9987 | ✅ |
| Prediction endpoint works | ✅ `{"status":"ok","label":"fake"}` |
| model.pkl recreated in root | ✅ |

## Notes

- `dataset/model.pkl` was NOT used — app only looks in project root
- Training took ~8 minutes (RandomizedSearchCV, 5 candidates, 2-fold CV)
- Best hyperparameters: TF-IDF(20000 features, unigrams, min_df=1) + LGBM(200 estimators, lr=0.1, 15 leaves)
- Feature name warnings still appear during training (train.py verification step) — these are separate from the app.py prediction warnings fixed in quick task 260517-193
