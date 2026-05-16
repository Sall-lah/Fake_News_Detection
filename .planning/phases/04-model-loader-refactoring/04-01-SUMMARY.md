---
phase: 04-model-loader-refactoring
plan: 01
subsystem: model-loading
tags: [refactoring, soft-load, backward-compatibility]
dependency_graph:
  requires: [START-04]
  provides: [load_model-soft-load, load_model_or_exit-delegation]
  affects: [app.py-startup (Phase 6)]
tech_stack:
  added: []
  patterns: [delegation-pattern, soft-load, global-state]
key_files:
  created: []
  modified: [model.py]
decisions:
  - "Kept print() for info messages per D-04 (no logging module)"
  - "Corruption exceptions bubble up per D-02 (not silently swallowed)"
  - "load_model_or_exit delegates to load_model per D-03 (single source of truth)"
metrics:
  duration: "< 5 min"
  completed_date: "2026-05-16"
  tasks_completed: 2
  tasks_total: 2
---

# Phase 04 Plan 01: Model Loader Refactoring Summary

**One-liner:** Added `load_model()` soft-load returning None on missing file; refactored `load_model_or_exit()` to delegate — enabling conditional startup training.

## Objective

Add `load_model()` soft-load function to model.py and refactor `load_model_or_exit()` to delegate to it, enabling Phase 6's conditional startup training while preserving backward compatibility.

## Tasks Completed

| # | Task | Type | Commit | Files |
|---|------|------|--------|-------|
| 1 | Add `load_model()` soft-load function | auto | `f7c5a4a` | model.py |
| 2 | Refactor `load_model_or_exit()` to delegate | auto | `cffd648` | model.py |

## Final State of model.py

```python
from __future__ import annotations

from pathlib import Path

import joblib

MODEL = None


def load_model(model_path: Path) -> object | None:
    """Soft-load: returns None if file missing, raises on corruption."""
    global MODEL
    if not model_path.exists():
        print(f"No model found at {model_path} — training will run on startup")
        return None
    MODEL = joblib.load(model_path)
    return MODEL


def load_model_or_exit(model_path: Path) -> object:
    model = load_model(model_path)
    if model is None:
        print("Failed to load model.")
        raise SystemExit(1)
    return model


def get_model() -> object | None:
    return MODEL
```

## Verification Results

| Check | Status |
|-------|--------|
| `load_model()` returns None for non-existent path | PASS |
| `load_model()` sets global MODEL on success | PASS (code review) |
| `load_model_or_exit()` exits with code 1 on missing model | PASS |
| `load_model_or_exit()` delegates to `load_model()` | PASS (grep confirms) |
| `get_model()` unchanged, returns global MODEL | PASS |
| Imports preserved (joblib, Path, annotations) | PASS |

## Deviations from Plan

None - plan executed exactly as written.

## Known Stubs

None.

## Threat Flags

| Flag | File | Description |
|------|------|-------------|
| (none) | | No new threat surface introduced beyond plan's threat model |

## Self-Check: PASSED
