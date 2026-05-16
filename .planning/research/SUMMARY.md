# Project Research Summary

**Project:** Fake News Detection API
**Domain:** Local Flask ML inference API (fake-news classification)
**Researched:** 2026-05-15
**Confidence:** MEDIUM

## Executive Summary

This project is a local-only Flask API that loads a scikit-learn pipeline (`model.pkl`) on startup and exposes a simple `/predict` endpoint for fake-news classification. Research converges on a lean, production-like local serving setup: Flask for routing, a WSGI server (Waitress for cross‑platform; Gunicorn only on Linux), and strict version pinning to avoid model pickle incompatibility. Experts build this type of service as a thin HTTP layer over a reusable core (validation, preprocessing, inference), with the model loaded once at startup to avoid cold-start latency.

The recommended approach is to deliver an MVP with predictable request/response contracts, preloaded model, and Dockerized local run. The architecture should isolate routes from core logic, reuse the model’s pipeline for preprocessing, and provide clear local docs on `/` and `/info`. The biggest risks are environment drift (pickle incompatibility), unsafe model loading, and preprocessing mismatch between training and inference—each mitigated by pinned dependencies, artifact provenance, and loading the full pipeline rather than re-implementing preprocessing.

## Key Findings

### Recommended Stack

The stack centers on Python 3.13 with Flask 3.1.1 and a production WSGI server (Waitress 3.0.2 for cross‑platform local use; Gunicorn 26.0.0 only for Linux containers). scikit-learn 1.7.1 plus pinned NumPy/SciPy/joblib ensures model compatibility and predictable inference.

**Core technologies:**
- **Python 3.13.x:** Runtime — current stable CPython with broad compatibility and long support window.
- **Flask 3.1.1:** HTTP API — lightweight, stable framework required by project constraints.
- **Waitress 3.0.2:** WSGI server — cross‑platform and Windows‑friendly for local production-like runs.
- **scikit-learn 1.7.1:** Inference pipeline — aligns with `model.pkl` usage and persistence guidance.

### Expected Features

The MVP should deliver a single `/predict` endpoint with preloaded model, input validation/preprocessing, and local docs. Differentiators like batch inference and logging can follow; explainability and benchmarking are future options if user demand appears.

**Must have (table stakes):**
- `/predict` JSON endpoint — core value delivery.
- Model preloading on startup — avoids cold-start latency.
- Input validation + preprocessing — ensures clean, non-empty inputs.
- `/` and `/info` docs — quick local usage guidance.
- Dockerized local run — reproducible setup.

**Should have (competitive):**
- Health/readiness indicator — model loaded status.
- Batch inference endpoint — faster local dataset checks.
- Request/response logging — optional, controlled via env.

**Defer (v2+):**
- Explainability snippets — only if users need trust signals.
- Benchmarking endpoint — add if performance comparisons matter.
- Configurable preprocessing — only if input diversity emerges.

### Architecture Approach

Architecture should separate HTTP routes from core inference logic using a thin-controller/fat-service approach. Load the model once at startup via an app factory or singleton loader. Keep preprocessing in the sklearn pipeline when possible, limiting API-side logic to validation and minimal normalization.

**Major components:**
1. **API routes** — Flask endpoints for `/`, `/info`, `/predict` and response formatting.
2. **Validation + preprocessing** — schema checks, empty-input checks, minimal normalization.
3. **Inference service** — model loading, prediction, label mapping.
4. **Config & logging** — environment settings and structured logging.

### Critical Pitfalls

1. **Training/serving drift (pickle incompatibility)** — pin exact dependency versions and record training metadata.
2. **Unsafe model loading** — only load trusted artifacts; document provenance; consider safer formats if provenance is weak.
3. **Preprocessing mismatch** — load the full sklearn Pipeline and avoid re-implementing training logic.
4. **Cold-start latency** — preload model at startup and expose a readiness check.
5. **Using Flask dev server in Docker** — always run via WSGI server for stability.

## Implications for Roadmap

Based on research, suggested phase structure:

### Phase 1: Core Inference MVP
**Rationale:** Dependencies flow from model contract → inference service → validation → `/predict`; this phase delivers the minimum user value and mitigates the most severe pitfalls early.
**Delivers:** `/predict` endpoint, model preload, validation/preprocessing, response schema, local docs (`/`, `/info`).
**Addresses:** MVP table stakes (predict, preload, validation, docs).
**Avoids:** Drift, preprocessing mismatch, empty-input errors, cold-start latency.

### Phase 2: Containerized Local Deployment
**Rationale:** Dockerization relies on stable runtime behavior and pinned deps; once core works, containerize and harden runtime.
**Delivers:** Docker image, pinned requirements, WSGI server configuration (Waitress), health/readiness endpoint.
**Uses:** Stack choices (Flask + Waitress, pinned sklearn/NumPy/SciPy/joblib).
**Implements:** Runtime/config/logging boundaries.

### Phase 3: Operational Enhancements
**Rationale:** Adds convenience and performance features after baseline stability is proven.
**Delivers:** Batch inference endpoint, optional request logging, basic benchmarking if needed.
**Addresses:** Differentiators without complicating MVP reliability.

### Phase 4: Trust & Flexibility (Optional)
**Rationale:** Only pursue if users need deeper insights or varied input handling.
**Delivers:** Explainability snippets, configurable preprocessing.

### Phase Ordering Rationale

- Model compatibility and pipeline correctness are prerequisites for any reliable API behavior.
- Dockerization and WSGI configuration build on stable core logic and version pins.
- Differentiators like batch inference and logging are additive and should not delay MVP stability.
- Explainability/configurable preprocessing are higher‑risk and user‑driven; defer until demand is clear.

### Research Flags

Phases likely needing deeper research during planning:
- **Phase 2:** Docker/WSGI configuration details for local Windows vs Linux targets; verify startup behavior with model size.
- **Phase 4:** Explainability approach depends on pipeline compatibility and user expectations.

Phases with standard patterns (skip research-phase):
- **Phase 1:** Standard Flask + sklearn inference pattern is well documented.
- **Phase 3:** Batch endpoint and logging are straightforward extensions.

## Confidence Assessment

| Area | Confidence | Notes |
|------|------------|-------|
| Stack | HIGH | Versions sourced from official docs and PyPI; Flask/Waitress guidance is clear. |
| Features | MEDIUM | Competitive analysis is directional; local user expectations inferred. |
| Architecture | MEDIUM | Patterns are standard but rely on project context, not external validation. |
| Pitfalls | HIGH | scikit-learn and Flask docs explicitly warn about version drift and dev server use. |

**Overall confidence:** MEDIUM

### Gaps to Address

- **Model provenance & training metadata:** Ensure training script/versions are captured alongside `model.pkl`.
- **Runtime constraints (memory/latency):** Validate model size and startup time in Docker on target machine.
- **Explainability feasibility:** Confirm pipeline supports feature attribution before committing to this feature.

## Sources

### Primary (HIGH confidence)
- /pallets/flask/3_1_1 — WSGI deployment guidance
- /scikit-learn/scikit-learn/1.7.1 — model persistence compatibility and warnings
- https://scikit-learn.org/stable/model_persistence.html — pickle risks and version drift
- https://flask.palletsprojects.com/en/3.0.x/deploying/ — production server guidance

### Secondary (MEDIUM confidence)
- https://pypi.org/project/waitress/ — current Waitress version
- https://pypi.org/project/gunicorn/ — Gunicorn version details
- https://pypi.org/project/numpy/ — NumPy version
- https://pypi.org/project/scipy/ — SciPy version
- https://pypi.org/project/joblib/ — joblib version
- https://www.python.org/downloads/ — Python release info
- https://docs.bentoml.com/en/latest/ — feature expectations and patterns
- https://pytorch.org/serve/ — model serving patterns for comparison
- https://docs.seldon.io/projects/seldon-core/en/latest/ — observability/serving concepts

---
*Research completed: 2026-05-15*
*Ready for roadmap: yes*
