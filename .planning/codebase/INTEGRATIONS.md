# External Integrations

## No External Dependencies

This is a **fully local** API with zero external service integrations.

| Integration Type | Status | Details |
|-----------------|--------|---------|
| Database | None | No database; data loaded from local CSV files |
| Auth provider | None | No authentication (local-only API) |
| External API | None | Self-contained inference, no upstream calls |
| Webhook/Event | None | No webhook or event system |
| Cache | None | No Redis, Memcached, or similar |
| Queue | None | No message queue |

## Data Sources

| Source | Format | Location | Usage |
|--------|--------|----------|-------|
| Training data | CSV (`Fake.csv`, `True.csv`) | `dataset/` | Loaded by `train.py` during cold start |
| Model artifact | Pickle (`model.pkl`) | project root | serialized by `joblib`, loaded by `model.py` |

## Integration Points (For Future)

- **Monitoring/metrics**: No Prometheus, OpenTelemetry, or logging service
- **CI/CD**: No CI configuration (no `.github/`, `.gitlab-ci.yml`, etc.)
- **Secrets management**: No secrets needed (local API)
