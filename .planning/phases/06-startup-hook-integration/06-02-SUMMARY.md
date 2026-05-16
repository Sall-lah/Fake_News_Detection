---
phase: 06-startup-hook-integration
plan: 02
subsystem: startup
tags: [startup, conditional-training, lazy-import]
dependency_graph:
  requires: ["06-01 (train() function)"]
  provides: ["auto-train on cold start", "fast warm start without pandas"]
  affects: ["app.py startup flow"]
tech-stack:
  added: []
  patterns: ["soft-load pattern", "lazy import", "blocking startup training"]
key-files:
  created: []
  modified:
    - app.py
decisions:
  - "Replaced load_model_or_exit with load_model soft-load check"
  - "from train import train placed inside if model is None block for lazy import"
  - "Training blocks startup (D-02) — no background threads"
  - "SystemExit(1) if model still None after training completes"
metrics:
  duration: "< 1 min"
  completed_date: "2026-05-16T16:16:00Z"
---

# Phase 06 Plan 02: Conditional Startup Flow Summary

**One-liner:** Wired conditional training into app.py startup — soft-loads model, triggers full training on cold start (blocking), skips training on warm start with lazy pandas import.

## Tasks Completed

| Task | Name | Commit | Status |
|------|------|--------|--------|
| 1 | Replace load_model_or_exit with conditional startup flow | 87e3898 | Done |

## Verification

- `from model import get_model, load_model` (NOT `load_model_or_exit`)
- `from train import train` inside conditional block (line 20, not module-level)
- `if model is None:` check after `load_model(MODEL_PATH)` (line 17)
- `train()` called on cold start (line 21)
- `load_model(MODEL_PATH)` called again after training (line 23)
- "Model loaded from existing model.pkl" printed on warm start (line 30)
- `SystemExit(1)` raised if model still None after training (line 26)
- All route definitions preserved (`/predict`, `/`, `/info`)
- `HTML_DOC` string preserved unchanged
- `from preprocess import clean_text` import preserved

## Deviations from Plan

None - plan executed exactly as written.

## Self-Check: PASSED

- [x] app.py imports `load_model` from model (line 7)
- [x] `from train import train` inside conditional block (line 20)
- [x] `load_model_or_exit` no longer referenced
- [x] Commit 87e3898 exists
