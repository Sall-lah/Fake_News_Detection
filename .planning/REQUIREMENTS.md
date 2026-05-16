# Requirements: Fake News Detection API

**Defined:** 2026-05-15
**Core Value:** Return a reliable fake/true classification for a given title+text payload through a simple local API.

## v1 Requirements

Requirements for initial release. Each maps to roadmap phases.

### API Endpoints

- [x] **API-01**: User can call `POST /predict` with JSON body containing `title` and `text`

### Preprocessing

- [x] **PRE-01**: Input is combined as `title + " " + text` before processing
- [x] **PRE-02**: Input is lowercased before further cleanup
- [x] **PRE-03**: Non-alphabetic characters are removed
- [x] **PRE-04**: English stopwords (sklearn ENGLISH_STOP_WORDS) are removed
- [x] **PRE-05**: Duplicate words are removed
- [x] **PRE-06**: Extra/empty whitespace is normalized
- [x] **PRE-07**: If cleaned input is empty, API returns error status

### Runtime

- [x] **RUN-01**: Model is loaded once on startup and reused for all requests
- [ ] **RUN-02**: `requirements.txt` defines runtime dependencies

## v2 Requirements

Deferred to future release. Tracked but not in current roadmap.

### API Endpoints

- **API-02**: `/` and `/info` return endpoint usage documentation
- **API-03**: Responses use a consistent envelope (`status` + `label`)

### Runtime

- **RUN-03**: Dockerfile builds and runs the API container

## Out of Scope

Explicitly excluded. Documented to prevent scope creep.

| Feature | Reason |
|---------|--------|
| Rate limiting | Local-only API |
| Advanced security/auth | Local-only API |
| Batch inference | Not required for v1 |
| Explainability output | Not required for v1 |

## Traceability

Which phases cover which requirements. Updated during roadmap creation.

| Requirement | Phase | Status |
|-------------|-------|--------|
| API-01 | Phase 1 | Complete |
| PRE-01 | Phase 1 | Complete |
| PRE-02 | Phase 1 | Complete |
| PRE-03 | Phase 1 | Complete |
| PRE-04 | Phase 1 | Complete |
| PRE-05 | Phase 1 | Complete |
| PRE-06 | Phase 1 | Complete |
| PRE-07 | Phase 1 | Complete |
| RUN-01 | Phase 1 | Complete |
| RUN-02 | Phase 1 | Pending |

**Coverage:**
- v1 requirements: 10 total
- Mapped to phases: 10
- Unmapped: 0

---
*Requirements defined: 2026-05-15*
*Last updated: 2026-05-15 after initial definition*
