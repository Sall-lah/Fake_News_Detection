# Phase 06: Startup Hook Integration - Discussion Log

> **Audit trail only.** Do not use as input to planning, research, or execution agents.
> Decisions are captured in CONTEXT.md — this log preserves the alternatives considered.

**Date:** 2026-05-16
**Phase:** 06-startup-hook-integration
**Areas discussed:** Training trigger method, Startup blocking behavior, Training status feedback, train.py refactoring

---

## Training Trigger Method

| Option | Description | Selected |
|--------|-------------|----------|
| Import train() function | Add train() to train.py, import in app.py. Clean, Pythonic. | ✓ |
| Subprocess call | subprocess.run(['python', 'train.py']). Isolated but harder to capture results. | |
| Inline in app.py | Inline training logic in app.py. Simple but bloats app.py. | |

**User's choice:** Import train() function (recommended)
**Notes:** Clean Python import pattern. app.py imports and calls train() when model.pkl is missing.

---

## Startup Blocking Behavior

| Option | Description | Selected |
|--------|-------------|----------|
| Block until done | Block Flask startup until training completes. Simple, model ready before requests. | ✓ |
| Background thread + 503 | Start Flask immediately, return 503 until training finishes. More complex. | |
| Loading page + polling | Start Flask with loading page, poll for readiness. Best UX but most complex. | |

**User's choice:** Block until done (recommended)
**Notes:** Simple approach for a local API. User sees training output in terminal, then API is ready.

---

## Training Status Feedback

| Option | Description | Selected |
|--------|-------------|----------|
| Terminal output only | Training output prints to terminal/console. User sees progress in same window. | ✓ |
| Status endpoint + terminal | Add /status endpoint that reports training progress. Overkill for local API. | |
| No feedback | No feedback at all. User just waits. Not great UX. | |

**User's choice:** Terminal output only (recommended)
**Notes:** Matches local API pattern — user runs `python app.py`, sees training output, then API is ready.

---

## train.py Refactoring

| Option | Description | Selected |
|--------|-------------|----------|
| Add train() + keep CLI | Wrap in train() function, keep if __name__ block. Both importable and runnable. | ✓ |
| Function only, remove CLI | Move all logic into function, remove if __name__ block. Loses standalone usage. | |
| No changes needed | Keep as-is (script only), use subprocess. No refactoring. | |

**User's choice:** Keep both function + CLI
**Notes:** Best of both worlds — train.py can be imported as a module AND run standalone.

---

## the agent's Discretion

- Exact function signature for `train()` — planner can decide return type (model path vs model object).
- How app.py structures the conditional: `if load_model() is None: train()` — exact flow left to planner.
- Whether to print a "Training complete, model loaded" message after training — flexible.
- Error handling if training fails — planner should decide (exit vs retry).

## Deferred Ideas

None — discussion stayed within phase scope.
