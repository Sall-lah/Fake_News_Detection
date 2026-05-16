# Phase 07: Docker & Deployment - Discussion Log

> **Audit trail only.** Do not use as input to planning, research, or execution agents.
> Decisions are captured in CONTEXT.md — this log preserves the alternatives considered.

**Date:** 2026-05-16
**Phase:** 07-docker-deployment
**Areas discussed:** Build-time vs runtime training, Pre-trained model in image, Container command (CMD), Docker optimization

---

## Build-time vs Runtime Training

| Option | Description | Selected |
|--------|-------------|----------|
| Build-time training | COPY dataset/, RUN python train.py during docker build. Image ships with model.pkl. Fast startup. | |
| Runtime training only | COPY dataset/, train when container starts. Slower startup but model always fresh. | ✓ |
| Build-time with runtime override | Train at build time by default, allow env var override for runtime training. | |

**User's choice:** Runtime training only
**Notes:** User wants training to happen at container startup, not during build. Model is always fresh.

---

## Pre-trained Model in Image

| Option | Description | Selected |
|--------|-------------|----------|
| No model.pkl in image | Don't include model.pkl. Always train at startup. Model fresh every time. | ✓ |
| Include model.pkl as fallback | Include pre-trained model, train only if user wants to retrain. More complex. | |
| Include + retrain | Include model.pkl but retrain anyway. Wasteful. | |

**User's choice:** No model.pkl in image (recommended)
**Notes:** Consistent with runtime training decision. No pre-trained model baked in.

---

## Container Command (CMD)

| Option | Description | Selected |
|--------|-------------|----------|
| Flask dev server | python -m flask run. Matches current setup and v1.0 user preference. | ✓ |
| Waitress | Production server. User removed Waitress in v1.0. | |
| Gunicorn | Linux-only. Not suitable for Windows local dev. | |

**User's choice:** Flask dev server (recommended)
**Notes:** Consistent with v1.0 decisions. Local dev only, no production server needed.

---

## Docker Optimization

| Option | Description | Selected |
|--------|-------------|----------|
| Yes, create .dockerignore | Exclude .planning/, .git/, __pycache__, *.pkl, venv/, etc. Reduces build context. | ✓ |
| Not needed yet | Skip .dockerignore. Small project. | |

**User's choice:** Yes, create .dockerignore (recommended)
**Notes:** Good practice even for small projects. Reduces build context size and speeds up builds.

---

## the agent's Discretion

- Exact .dockerignore entries — planner should include all common exclusions.
- Whether to add HEALTHCHECK to Dockerfile — flexible.
- Whether to add labels/metadata to Dockerfile — flexible.
- Docker build args (e.g., PORT) — planner can decide.

## Deferred Ideas

None — discussion stayed within phase scope.
