# Phase 1: Core Local Inference API - Discussion Log

> **Audit trail only.** Do not use as input to planning, research, or execution agents.
> Decisions are captured in CONTEXT.md — this log preserves the alternatives considered.

**Date:** 2026-05-15
**Phase:** 1-Core Local Inference API
**Areas discussed:** Response payload, Model loading, Preprocess

---

## Response payload

| Option | Description | Selected |
|--------|-------------|----------|
| status+label | {status, label} with label 'fake'/'true' | ✓ |
| status+result | {status, result} with result 0/1 | |
| status+both | {status, result, label} | |

**User's choice:** status+label
**Notes:** Error responses should be `{status:"error", message:"..."}`

---

## Model loading

| Option | Description | Selected |
|--------|-------------|----------|
| App startup | Load once when Flask app starts | ✓ |
| First request | Lazy load on first /predict call | |
| Per request | Reload every request (slow) | |

**User's choice:** App startup
**Notes:** On load failure, fail fast at startup. If a request arrives without a model loaded, return 503; do not include filename in the error message.

---

## Preprocess

| Option | Description | Selected |
|--------|-------------|----------|
| Preserve order | Keep first occurrence, drop later duplicates | ✓ |
| Sort unique | Unique + sort alphabetically | |
| Keep all | No deduplication | |

**User's choice:** Preserve order
**Notes:** Stopword removal occurs after cleanup. Replace non-alpha with spaces, normalize whitespace. Treat missing title/text as empty strings; if cleaned input is empty, return HTTP 400.

---

## the agent's Discretion

None

## Deferred Ideas

None
