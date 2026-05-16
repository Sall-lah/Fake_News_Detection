# Phase 04: Model Loader Refactoring - Discussion Log

> **Audit trail only.** Do not use as input to planning, research, or execution agents.
> Decisions are captured in CONTEXT.md — this log preserves the alternatives considered.

**Date:** 2026-05-16
**Phase:** 04-model-loader-refactoring
**Areas discussed:** Soft load behavior, Backward compatibility, Startup messaging, Error handling scope

---

## Soft Load Behavior

| Option | Description | Selected |
|--------|-------------|----------|
| Return None | Return None when model.pkl doesn't exist. Clean, lets app.py decide. | ✓ |
| Return None + warning | Return None but also print/log a warning message. | |
| Return (None, False) tuple | Return a tuple so callers know if load succeeded. | |

**User's choice:** Return None (recommended)
**Notes:** Clean approach — caller (app.py) decides what to do next. Aligns with existing `get_model()` returning None pattern.

---

## Error Handling Scope

| Option | Description | Selected |
|--------|-------------|----------|
| FileExists only | Only check if file exists. Let other exceptions bubble up. | ✓ |
| Catch all exceptions | Catch all (corrupted pickle, version mismatch) and return None. | |
| FileExists + pickle errors | Catch FileNotFoundError and specific pickle/joblib errors. | |

**User's choice:** FileExists only
**Notes:** Catches real problems early rather than silently hiding them. If model.pkl exists but is corrupted, the exception should surface.

---

## Backward Compatibility

| Option | Description | Selected |
|--------|-------------|----------|
| Delegate to load_model | load_model_or_exit() calls load_model() internally. Single source of truth. | ✓ |
| Keep independent | Each function does its own joblib.load call independently. | |

**User's choice:** Delegate to load_model (recommended)
**Notes:** DRY principle — single source of truth for the loading logic. load_model_or_exit() becomes a thin wrapper.

---

## Startup Messaging

| Option | Description | Selected |
|--------|-------------|----------|
| Silent | No output when model is missing. Cleanest UX. | |
| Print info message | Print a simple message so user knows what's happening. | ✓ |
| Use logging module | Use Python logging module for structured output. | |

**User's choice:** Print info message
**Notes:** User wants visibility — a simple print statement like "No model found — training will run on startup". Not silent, not full logging module.

---

## the agent's Discretion

- Function naming: `load_model` is the natural name; planner can confirm no conflicts.
- Exact wording of the startup info message is left to the planner.
- Whether to use `logging` vs `print` for the info message — user said "print info message", exact mechanism is flexible.

## Deferred Ideas

None — discussion stayed within phase scope.
