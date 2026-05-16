# Phase 06: Startup Hook Integration - Context

**Gathered:** 2026-05-16
**Status:** Ready for planning

<domain>
## Phase Boundary

Flask app auto-trains on first startup when model.pkl is missing, skips training on warm starts (model.pkl exists). Blocks startup until training completes. Terminal output shows training progress. After training, the model is loaded and the API serves predictions normally.

</domain>

<decisions>
## Implementation Decisions

### Training Trigger Method
- **D-01:** Add a `train()` function to `train.py` that can be imported and called from `app.py`. Clean Python import pattern.

### Startup Blocking Behavior
- **D-02:** Block Flask startup until training completes. Simple, guarantees model is ready before any requests. User sees training output in terminal. No background threads, no loading pages.

### Training Status Feedback
- **D-03:** Training output prints to terminal/console only. No status endpoint, no loading page. User sees progress in the same window they started the app.

### train.py Refactoring
- **D-04:** Wrap training logic in a `train()` function that returns the model path. Keep `if __name__ == "__main__"` block that calls `train()` for standalone CLI usage. Both importable and runnable.

### Lazy Import Pattern
- **D-05:** On warm start (model.pkl exists), pandas should not be imported — lazy import pattern to avoid unnecessary overhead. Only import pandas when training is actually needed.

### the agent's Discretion
- Exact function signature for `train()` — planner can decide return type (model path vs model object).
- How app.py structures the conditional: `if load_model() is None: train()` — exact flow left to planner.
- Whether to print a "Training complete, model loaded" message after training — flexible.
- Error handling if training fails — planner should decide (exit vs retry).

</decisions>

<canonical_refs>
## Canonical References

**Downstream agents MUST read these before planning or implementing.**

### Phase Requirements
- `.planning/ROADMAP.md` §Phase 6 — Goal, requirements (START-01, START-02, START-03), and 4 success criteria
- `.planning/REQUIREMENTS.md` — START-01, START-02, START-03 requirement definitions

### Source Files (modified by this phase)
- `app.py` — Replace `load_model_or_exit()` with conditional training flow
- `train.py` — Wrap training logic in `train()` function, keep CLI block

### Source Files (read by this phase)
- `model.py` — `load_model()` (soft load, returns None when missing) — already exists from Phase 4
- `preprocess.py` — `clean_text()` — reused by train.py
- `requirements.txt` — All dependencies already pinned

### Prior Phase Context
- `.planning/phases/04-model-loader-refactoring/04-CONTEXT.md` — D-01 through D-04 (load_model behavior)
- `.planning/phases/05-training-script/05-CONTEXT.md` — D-01 through D-06 (training script decisions)

No external specs — requirements fully captured in decisions above.

</canonical_refs>

<code_context>
## Existing Code Insights

### Reusable Assets
- `model.load_model(model_path)` — Returns None if model.pkl missing, loads model if exists. Already prints info message.
- `model.get_model()` — Returns global MODEL variable.
- `train.py` — Has full training pipeline: load data, preprocess, train with RandomizedSearchCV, save model.pkl.
- `train.load_and_prepare_data()` — Already a separate function for data loading.

### Established Patterns
- `from __future__ import annotations` — Present in all Python files.
- `pathlib.Path(__file__).parent` — Consistent path resolution.
- `if __name__ == "__main__"` — Standard Python script pattern.
- Global MODEL variable + setter pattern in model.py.

### Integration Points
- `app.py:13` — Currently `load_model_or_exit(MODEL_PATH)`. This line needs to become a conditional: try soft load, if None then train, then load.
- `train.py:59-123` — All training logic in `if __name__` block. Needs to be extracted into a `train()` function.
- `model.py` — `load_model()` already sets global MODEL on success. After training, app.py needs to reload the model.
- Pandas import — Currently at top of train.py. For lazy import (D-05), pandas should only be imported when training runs.

</code_context>

<specifics>
## Specific Ideas

No specific requirements — open to standard approaches. User prefers simplicity: block startup, terminal output, import-based training trigger.

</specifics>

<deferred>
## Deferred Ideas

None — discussion stayed within phase scope.

</deferred>

---

*Phase: 06-Startup Hook Integration*
*Context gathered: 2026-05-16*
