# Pitfalls Research

**Domain:** Local ML inference API (Flask + scikit-learn pipeline)
**Researched:** 2026-05-15
**Confidence:** MEDIUM

## Critical Pitfalls

### Pitfall 1: Training/Serving Environment Drift (Pickle Incompatibility)

**What goes wrong:**
Model loads fail or behave inconsistently because the runtime library versions differ from training (scikit-learn, numpy, scipy), especially for pickle/joblib artifacts.

**Why it happens:**
Teams assume pickled models are forward-compatible and only pin top-level dependencies. scikit-learn explicitly warns that loading with different versions is unsupported.

**How to avoid:**
- Pin exact dependency versions (including transitive) and bake them into the container image.
- Record model metadata: training script, data snapshot reference, and library versions alongside the model artifact.
- Treat model retraining as the upgrade path when dependencies change.

**Warning signs:**
- `InconsistentVersionWarning` from scikit-learn.
- Model loads locally but fails in Docker.
- Prediction outputs differ between dev and container.

**Phase to address:**
Phase 1 (Model artifact + Dockerization)

---

### Pitfall 2: Unsafe Model Loading (Pickle Code Execution Risk)

**What goes wrong:**
Loading untrusted `model.pkl` can execute arbitrary code, creating a local security risk even in “local-only” APIs.

**Why it happens:**
Pickle/joblib are convenient and default to unsafe deserialization; teams overlook that model files are executable payloads.

**How to avoid:**
- Only load artifacts from trusted sources.
- Keep model artifacts under version control or controlled build pipeline.
- Consider safer formats (e.g., skops/ONNX) if artifact provenance is uncertain.

**Warning signs:**
- Model file shared via ad-hoc channels.
- Loading model from user-provided paths.
- No documented provenance for `model.pkl`.

**Phase to address:**
Phase 1 (Model artifact handling) and Phase 2 (API hardening)

---

### Pitfall 3: Preprocessing Mismatch Between Training and Inference

**What goes wrong:**
The API’s text cleaning diverges from training preprocessing (stopwords, casing, tokenization), leading to silent accuracy degradation and inconsistent predictions.

**Why it happens:**
Developers re-implement preprocessing in the API instead of using the same pipeline object.

**How to avoid:**
- Persist and load the full sklearn Pipeline (preprocessing + model).
- Avoid re-implementing cleaning logic in the API except validation/empty checks.
- Create a golden test payload set to verify predictions across environments.

**Warning signs:**
- Code duplicates text cleaning separate from the model pipeline.
- Small input tweaks cause large output swings.
- No parity tests between training notebook and API.

**Phase to address:**
Phase 1 (Model load + predict endpoint)

---

### Pitfall 4: Startup Latency from Cold Model Load

**What goes wrong:**
API appears “down” or times out during first request because the model loads lazily or too slowly at request time.

**Why it happens:**
Loading the model inside the request handler is easy during development but causes latency spikes.

**How to avoid:**
- Load the model at container startup and keep it in memory.
- Add a `/health` endpoint that verifies the model is loaded.
- Use a WSGI server with a pre-fork model if concurrency is needed.

**Warning signs:**
- First request significantly slower than subsequent ones.
- Logs show model loading inside `/predict` handler.

**Phase to address:**
Phase 1 (Dockerized startup) and Phase 2 (Performance hardening)

---

### Pitfall 5: Using Flask Dev Server in “Local Production”

**What goes wrong:**
Unstable performance, lack of concurrency, and fragile behavior when multiple requests are made.

**Why it happens:**
Teams conflate “local-only” with “development server is fine,” but Flask docs treat any non-dev use as production.

**How to avoid:**
- Use a WSGI server (e.g., Waitress/Gunicorn) even for local Docker.
- Explicitly document run commands and server choice.

**Warning signs:**
- Running via `flask run` in Docker.
- Single-threaded request handling and timeouts.

**Phase to address:**
Phase 2 (Deployment configuration)

---

### Pitfall 6: Silent Failure on Empty or Invalid Inputs

**What goes wrong:**
API returns a prediction for empty/near-empty inputs after preprocessing removes everything, producing misleading results.

**Why it happens:**
Input validation is bolted on late or assumed to be handled by the model.

**How to avoid:**
- Validate that cleaned input is non-empty before inference.
- Return a clear error response with guidance.
- Add validation tests for empty/whitespace-only payloads.

**Warning signs:**
- API returns a label for `{"title": "", "text": ""}`.
- No explicit validation in request handler.

**Phase to address:**
Phase 1 (API contract + validation)

---

### Pitfall 7: Ignoring Model Size/Memory Footprint in Docker

**What goes wrong:**
Container fails to start or crashes due to memory pressure when loading the model.

**Why it happens:**
Model size and dependencies are not validated within the container constraints.

**How to avoid:**
- Measure model size and container memory usage during build.
- Use slim base images but ensure required libs are present.
- Document expected resource requirements.

**Warning signs:**
- Container exits on startup with OOM.
- High memory usage before serving requests.

**Phase to address:**
Phase 1 (Dockerization) and Phase 2 (Runtime tuning)

---

### Pitfall 8: Lack of Reproducible Build for Model Artifact

**What goes wrong:**
Model cannot be rebuilt when dependencies change or bugs are found, blocking upgrades.

**Why it happens:**
Training code, data snapshot, and versions are not captured.

**How to avoid:**
- Store training script and metadata next to model artifact.
- Tag model versions and include a build manifest.

**Warning signs:**
- Only `model.pkl` exists with no training recipe.
- “We don’t know which notebook trained it.”

**Phase to address:**
Phase 0/1 (Initial artifact governance)

---

## Technical Debt Patterns

| Shortcut | Immediate Benefit | Long-term Cost | When Acceptable |
|----------|-------------------|----------------|-----------------|
| Hard-coding preprocessing in API | Faster to ship | Drift from training pipeline, accuracy loss | Only for early spike, replace before MVP |
| Using pickle without provenance docs | Simple load | Security risk, upgrade fragility | Never if artifact source is not controlled |
| Skipping WSGI server | Fewer moving parts | Concurrency/perf issues | Only for one-off local testing |

## Integration Gotchas

| Integration | Common Mistake | Correct Approach |
|-------------|----------------|------------------|
| Docker | Loading model on first request | Load at container start and fail fast if missing |
| Model artifact | Upgrading deps without retraining | Pin versions or retrain when upgrading |
| Flask server | Using dev server in Docker | Use a WSGI server for stability |

## Performance Traps

| Trap | Symptoms | Prevention | When It Breaks |
|------|----------|------------|----------------|
| Lazy model loading | First request >5s, timeouts | Eager load at startup | Even at single-user local use |
| Single-threaded dev server | Requests queue | Use WSGI server with workers | Multiple requests or concurrent clients |
| Excessive per-request preprocessing | High latency per call | Precompile pipeline, avoid heavy regex in handler | Low concurrency but noticeable at ~10+ req/min |

## Security Mistakes

| Mistake | Risk | Prevention |
|---------|------|------------|
| Loading untrusted pickle | Arbitrary code execution | Only load trusted artifacts; consider skops/ONNX |
| Exposing model path via API | Local file disclosure | Hardcode path; never accept file path input |
| Logging raw user text | Privacy leaks in logs | Redact or truncate input in logs |

## UX Pitfalls

| Pitfall | User Impact | Better Approach |
|---------|-------------|-----------------|
| Opaque error on empty input | Confusion, retries | Return clear validation error and example payload |
| Inconsistent labels (`0/1` vs `fake/true`) | Misuse by clients | Standardize response schema (`status`, `label`) |
| Missing `/info` usage docs | Extra friction | Provide request/response examples on root endpoints |

## "Looks Done But Isn't" Checklist

- [ ] **/predict endpoint:** Often missing empty-input validation — verify cleaned input is non-empty
- [ ] **Docker image:** Often missing pinned dependency versions — verify `pip freeze` matches training
- [ ] **Model artifact:** Often missing provenance — verify training script + versions saved
- [ ] **Server run mode:** Often using Flask dev server — verify WSGI server configured

## Recovery Strategies

| Pitfall | Recovery Cost | Recovery Steps |
|---------|---------------|----------------|
| Version drift | MEDIUM | Rebuild container with pinned deps; retrain model if needed |
| Preprocessing mismatch | MEDIUM | Re-export full pipeline; delete duplicated preprocessing code |
| Unsafe pickle source | HIGH | Quarantine artifact; rebuild from trusted training pipeline |

## Pitfall-to-Phase Mapping

| Pitfall | Prevention Phase | Verification |
|---------|------------------|--------------|
| Training/serving drift | Phase 1 | Container loads model without warnings; versions pinned |
| Unsafe model loading | Phase 1–2 | Artifact provenance documented; no user-provided paths |
| Preprocessing mismatch | Phase 1 | Golden test payloads match training outputs |
| Startup latency | Phase 1–2 | First request latency acceptable; model loaded at startup |
| Flask dev server | Phase 2 | WSGI server used in Docker run command |
| Invalid inputs | Phase 1 | Empty payload returns validation error |
| Memory footprint | Phase 2 | Container starts within memory budget |
| Reproducible build | Phase 0–1 | Training recipe + versions recorded with model |

## Sources

- https://scikit-learn.org/stable/model_persistence.html (model persistence risks, version compatibility, pickle security)
- https://flask.palletsprojects.com/en/3.0.x/deploying/ (production server guidance)

---
*Pitfalls research for: Local ML inference API (Flask + scikit-learn)*
*Researched: 2026-05-15*
