# Phase 1: Core Local Inference API - Context

**Gathered:** 2026-05-15
**Status:** Ready for planning

## Phase Boundary

Deliver the core local `/predict` API with preprocessing, startup model load, and declared runtime dependencies.

## Implementation Decisions

### Response payload
- **D-01:** Success response returns `{status, label}` with `label` values `fake` or `true`
- **D-02:** Error response returns `{status:"error", message:"..."}`

### Model loading
- **D-03:** Load `model.pkl` at app startup (single load, reused)
- **D-04:** If model load fails, fail fast and exit on startup
- **D-05:** If a request is served without a loaded model, return error with HTTP 503
- **D-06:** Error messages should not include the model filename

### Preprocessing
- **D-07:** Combine input as `title + " " + text` (missing fields treated as empty strings)
- **D-08:** Lowercase before cleanup; replace non-alpha chars with spaces, then normalize
- **D-09:** Remove stopwords after cleanup using sklearn `ENGLISH_STOP_WORDS`
- **D-10:** Deduplicate words by preserving first occurrence order
- **D-11:** Normalize whitespace (collapse to single spaces, trim ends)
- **D-12:** If cleaned input is empty, return error with HTTP 400

### the agent's Discretion
- None

## Canonical References

**Downstream agents MUST read these before planning or implementing.**

### Project context
- `.planning/PROJECT.md` — scope, constraints, and baseline decisions
- `.planning/REQUIREMENTS.md` — v1 requirements and traceability
- `.planning/ROADMAP.md` — phase goal and success criteria

## Existing Code Insights

### Reusable Assets
- None yet (no codebase present)

### Established Patterns
- None yet (no codebase present)

### Integration Points
- None yet (no codebase present)

## Specific Ideas

No specific requirements — open to standard approaches.

## Deferred Ideas

None — discussion stayed within phase scope.

---

*Phase: 1-Core Local Inference API*
*Context gathered: 2026-05-15*
