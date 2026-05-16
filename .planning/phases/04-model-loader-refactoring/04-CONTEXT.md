# Phase 04: Model Loader Refactoring - Context

**Gathered:** 2026-05-16
**Status:** Ready for planning

<domain>
## Phase Boundary

Add a soft `load_model()` function to `model.py` that returns `None` when `model.pkl` does not exist (no crash). Keep `load_model_or_exit()` backward compatible. This enables Phase 6's conditional startup training without breaking the current hard-load behavior.

</domain>

<decisions>
## Implementation Decisions

### Soft Load Behavior
- **D-01:** `load_model()` returns `None` when `model.pkl` doesn't exist — no crash, no exception. The caller (app.py) decides what to do next.

### Error Handling Scope
- **D-02:** `load_model()` only checks if the file exists. If the file exists but is corrupted or has a version mismatch, let the exception bubble up. This catches real problems early rather than silently hiding them.

### Backward Compatibility
- **D-03:** `load_model_or_exit()` delegates to `load_model()` internally. If `load_model()` returns `None`, then `load_model_or_exit()` prints its error message and calls `SystemExit(1)`. Single source of truth for the loading logic.

### Startup Messaging
- **D-04:** When `model.pkl` is missing at startup, print an info message (e.g., "No model found — training will run on startup") so the user knows what's happening. Not silent, not full logging module — just a simple print statement.

### the agent's Discretion
- Function naming: `load_model` is the natural name; planner can confirm no conflicts.
- Exact wording of the startup info message is left to the planner.
- Whether to use `logging` vs `print` for the info message — user said "print info message", exact mechanism is flexible.

</decisions>

<canonical_refs>
## Canonical References

**Downstream agents MUST read these before planning or implementing.**

### Phase Requirements
- `.planning/ROADMAP.md` §Phase 4 — Goal, requirements (START-04), and success criteria
- `.planning/REQUIREMENTS.md` — START-04 requirement definition

### Source Files (modified by this phase)
- `model.py` — Add `load_model()`, refactor `load_model_or_exit()` to delegate
- `app.py` — No changes required in this phase (startup wiring is Phase 6), but planner should verify

### Existing Code Patterns
- `model.py:10-17` — Current `load_model_or_exit()` implementation (joblib.load + SystemExit pattern)
- `model.py:20-21` — Current `get_model()` returns global MODEL
- `app.py:13` — Current startup call: `load_model_or_exit(MODEL_PATH)`
- `app.py:29-31` — Predict endpoint already handles `get_model()` returning None (503 response)

No external specs — requirements fully captured in decisions above.

</canonical_refs>

<code_context>
## Existing Code Insights

### Reusable Assets
- `joblib` — Already imported and used for model loading. No new dependency needed.
- `pathlib.Path` — Already used for MODEL_PATH. Consistent path handling.
- Global `MODEL` variable + `get_model()` — Existing pattern for model access. `load_model()` should set this global on success.

### Established Patterns
- `from __future__ import annotations` — Present in both model.py and app.py.
- Type hints with `object | None` return types — Used in `get_model()`.
- `SystemExit(1)` for fatal errors — Current pattern in `load_model_or_exit()`.
- `MODEL_PATH = Path(__file__).parent / "model.pkl"` — Path resolution pattern in app.py.

### Integration Points
- `load_model()` must set the global `MODEL` variable (like `load_model_or_exit()` does) so `get_model()` continues to work.
- `load_model_or_exit()` currently called at module level in app.py:13 — this phase does NOT change app.py, only model.py.
- Phase 6 will change app.py to use `load_model()` instead of `load_model_or_exit()`.

</code_context>

<specifics>
## Specific Ideas

No specific requirements — open to standard approaches. User prefers simple print statements over logging module for startup messages.

</specifics>

<deferred>
## Deferred Ideas

None — discussion stayed within phase scope.

</deferred>

---

*Phase: 04-Model Loader Refactoring*
*Context gathered: 2026-05-16*
