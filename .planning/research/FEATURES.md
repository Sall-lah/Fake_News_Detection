# Feature Research

**Domain:** Local ML inference API (fake-news classification)
**Researched:** 2026-05-15
**Confidence:** MEDIUM

## Feature Landscape

### Table Stakes (Users Expect These)

Features users assume exist. Missing these = product feels incomplete.

| Feature | Why Expected | Complexity | Notes |
|---------|--------------|------------|-------|
| Single `/predict` HTTP endpoint | Standard way to invoke inference locally | LOW | JSON input with `title` + `text`; consistent response schema. |
| Model preloading on startup | Avoids cold-start latency per request | LOW | Load `model.pkl` once; fail fast if missing. |
| Input validation + preprocessing | Prevents garbage-in/garbage-out and runtime errors | MEDIUM | Combine title+text, normalize whitespace, reject empty cleaned input. |
| Clear API docs/usage page | Local users need quick curl/examples | LOW | `/` and `/info` document request/response. |
| Health check / readiness indicator | Users need to know model is loaded | LOW | Simple `/health` or reuse `/info` with status. |
| Deterministic response payload | Consistent integration by callers | LOW | `status`, `label`, optional `confidence` if available. |
| Dockerized local run | Expected for reproducible local use | MEDIUM | Image builds with model included and loads on start. |

### Differentiators (Competitive Advantage)

Features that set the product apart. Not required, but valuable.

| Feature | Value Proposition | Complexity | Notes |
|---------|-------------------|------------|-------|
| Explainability snippets | Builds trust in predictions | MEDIUM | Return top tokens or features (if pipeline supports). |
| Batch inference endpoint | Faster throughput for local dataset checks | MEDIUM | Accept array of items; reuse preprocessing. |
| Local model benchmarking | Lets users validate latency/accuracy on sample set | MEDIUM | Provide `/benchmark` with canned dataset. |
| Configurable preprocessing pipeline | Flexibility for different inputs | MEDIUM | Simple flags for stopwords, min length, etc. |
| Request/response logging to file | Debugging and auditing locally | LOW | Toggle via env var; avoid PII by default. |

### Anti-Features (Commonly Requested, Often Problematic)

Features that seem good but create problems.

| Feature | Why Requested | Why Problematic | Alternative |
|---------|---------------|-----------------|-------------|
| Advanced auth (OAuth/JWT) | “Secure the API” | Overkill for local-only; adds dependencies and setup friction | Rely on localhost binding + explicit warning in docs. |
| Rate limiting | “Prevent abuse” | Local API doesn’t need it; adds complexity and false failures | Document intended local usage and expected load. |
| Online model training/tuning | “Improve accuracy on the fly” | Blurs inference-only scope; risks instability | Separate offline training pipeline. |
| Hot model reloading | “Update model without restart” | Adds state/versioning complexity for little local benefit | Restart container when model changes. |

## Feature Dependencies

```
Input validation + preprocessing
    └──requires──> `/predict` endpoint
                       └──requires──> Model preloading

Batch inference ──enhances──> `/predict` endpoint

Explainability ──requires──> Preprocessing + Model supports feature attribution
```

### Dependency Notes

- **Input validation + preprocessing requires `/predict` endpoint:** validation is part of request handling.
- **`/predict` requires model preloading:** avoid per-request disk loads; ensures readiness.
- **Batch inference enhances `/predict`:** reuse the same validation/preprocessing logic for arrays.
- **Explainability requires preprocessing + model support:** only feasible if the pipeline exposes feature weights or compatible explainers.

## MVP Definition

### Launch With (v1)

Minimum viable product — what's needed to validate the concept.

- [ ] `/predict` JSON endpoint — core value delivery.
- [ ] Model preloading on startup — avoids cold-start latency.
- [ ] Input validation + preprocessing — consistent inference behavior.
- [ ] `/` + `/info` docs — local users can call it quickly.
- [ ] Dockerized local run — reproducible setup.

### Add After Validation (v1.x)

- [ ] Health/readiness endpoint — operational convenience.
- [ ] Batch inference endpoint — speed for local datasets.
- [ ] Request/response logging — debugging and audit trail.

### Future Consideration (v2+)

- [ ] Explainability snippets — only if users need trust signals.
- [ ] Benchmarking endpoint — add if performance comparisons matter.
- [ ] Configurable preprocessing — add if input diversity emerges.

## Feature Prioritization Matrix

| Feature | User Value | Implementation Cost | Priority |
|---------|------------|---------------------|----------|
| `/predict` endpoint | HIGH | LOW | P1 |
| Model preloading | HIGH | LOW | P1 |
| Input validation + preprocessing | HIGH | MEDIUM | P1 |
| Docs (`/` and `/info`) | HIGH | LOW | P1 |
| Dockerized local run | HIGH | MEDIUM | P1 |
| Health/readiness endpoint | MEDIUM | LOW | P2 |
| Batch inference | MEDIUM | MEDIUM | P2 |
| Request logging | MEDIUM | LOW | P2 |
| Explainability snippets | MEDIUM | MEDIUM | P3 |
| Benchmarking endpoint | LOW | MEDIUM | P3 |

**Priority key:**
- P1: Must have for launch
- P2: Should have, add when possible
- P3: Nice to have, future consideration

## Competitor Feature Analysis

| Feature | Competitor A (BentoML) | Competitor B (TorchServe) | Our Approach |
|---------|-------------------------|---------------------------|--------------|
| HTTP service endpoints | “Create online API Services” | Model serving server | Simple Flask `/predict` |
| Model loading/management | Model loading and management docs | Model archive / server lifecycle | Load `model.pkl` at startup |
| Observability/logging | Observability (logging/metrics/tracing) | Metrics + performance guides | Minimal local logging only |
| Batch/adaptive batching | Adaptive batching | Performance tuning / batching | Optional batch endpoint |

## Sources

- BentoML documentation (service endpoints, model management, observability, batching): https://docs.bentoml.com/en/latest/
- TorchServe docs (model serving patterns; note limited maintenance): https://pytorch.org/serve/
- Seldon Core 2 overview (observability, scaling, standardization concepts): https://docs.seldon.io/projects/seldon-core/en/latest/

---
*Feature research for: local ML inference API*
*Researched: 2026-05-15*
