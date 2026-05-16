# Roadmap: Fake News Detection API

## Overview

Deliver a single, reliable local inference API that exposes a `/predict` endpoint, performs the required preprocessing, loads the model once at startup, and declares runtime dependencies for repeatable local use.

## Phases

**Phase Numbering:**
- Integer phases (1, 2, 3): Planned milestone work
- Decimal phases (2.1, 2.2): Urgent insertions (marked with INSERTED)

Decimal phases appear between their surrounding integers in numeric order.

- [ ] **Phase 1: Core Local Inference API** - Deliver the full v1 predict workflow with preprocessing, startup model load, and declared runtime deps.

## Phase Details

### Phase 1: Core Local Inference API
**Goal**: Users can submit a title+text payload and receive a reliable prediction from a preloaded model via the local API.
**Depends on**: Nothing (first phase)
**Requirements**: API-01, PRE-01, PRE-02, PRE-03, PRE-04, PRE-05, PRE-06, PRE-07, RUN-01, RUN-02
**Success Criteria** (what must be TRUE):
  1. User can call `POST /predict` with `title` and `text` JSON and receive a prediction response.
  2. User inputs are combined, cleaned, and normalized as specified before inference.
  3. User receives an error response when cleaned input is empty.
  4. Local API starts with the model already loaded and dependencies declared for runtime use.
**Plans**: TBD

## Progress

**Execution Order:**
Phases execute in numeric order: 1 → 1.1 → 1.2 → 2

| Phase | Plans Complete | Status | Completed |
|-------|----------------|--------|-----------|
| 1. Core Local Inference API | 1/3 | In Progress|  |
