# Fake News Detection API

## What This Is

A local Flask API that serves predictions from a pre-trained `model.pkl` for fake-news classification. It exposes documentation-style responses on `/` and `/info`, and a `/predict` endpoint that accepts `title` and `text`, preprocesses them, and returns inference status plus a 0/1 prediction.

## Core Value

Users can send a title + text and reliably receive a fake/true prediction from the model.

## Requirements

### Validated

(None yet — ship to validate)

### Active

- [ ] Provide `/` and `/info` endpoints that describe API usage and examples.
- [ ] Provide `/predict` endpoint that accepts `title` and `text` inputs.
- [ ] Preprocess input by combining `title + " " + text`, lowercasing, removing non-letters, removing stopwords, removing duplicate words, and normalizing whitespace.
- [ ] Return error status when the processed string is empty.
- [ ] Load `model.pkl` on startup and perform inference per request.
- [ ] Return JSON with inference status and prediction value (0 = fake, 1 = true).
- [ ] Provide containerization (Dockerfile) that loads the model on startup.
- [ ] Provide `requirements.txt` for dependencies.

### Out of Scope

- Rate limiting or advanced security controls — local API only.
- External services or hosted deployments — local runtime only.
- UI or frontend — API-only deliverable.

## Context

The API is for a local fake-news detection workflow. The model file lives at the project root (`model.pkl`). Input is two fields (`title`, `text`), combined with a single space, then cleaned before inference. The service must be containerized and should not run tests since dependencies may not be installed locally.

## Constraints

- **Tech stack**: Flask (Python) — required backend framework.
- **Model loading**: `model.pkl` must be loaded at startup — minimize per-request load time.
- **Deployment**: Docker container required — must run locally.
- **Testing**: Do not run tests — dependencies not installed yet.

## Key Decisions

| Decision | Rationale | Outcome |
|----------|-----------|---------|
| Use `/predict` as canonical endpoint (alias `/prediction`) | Simpler, standard naming | — Pending |
| Store `model.pkl` at repo root | Matches current project layout | — Pending |

## Evolution

This document evolves at phase transitions and milestone boundaries.

**After each phase transition** (via `/gsd-transition`):
1. Requirements invalidated? → Move to Out of Scope with reason
2. Requirements validated? → Move to Validated with phase reference
3. New requirements emerged? → Add to Active
4. Decisions to log? → Add to Key Decisions
5. "What This Is" still accurate? → Update if drifted

**After each milestone** (via `/gsd-complete-milestone`):
1. Full review of all sections
2. Core Value check — still the right priority?
3. Audit Out of Scope — reasons still valid?
4. Update Context with current state

---
*Last updated: 2026-05-15 after initialization*
