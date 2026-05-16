# Phase 07: Docker & Deployment - Context

**Gathered:** 2026-05-16
**Status:** Ready for planning

<domain>
## Phase Boundary

Update the Dockerfile to include the dataset directory and support runtime training at container startup. The container trains on first start (no model.pkl), then serves predictions. No pre-trained model baked into the image. Add .dockerignore to reduce build context size.

</domain>

<decisions>
## Implementation Decisions

### Build-time vs Runtime Training
- **D-01:** Train at runtime (container startup), NOT at build time. COPY dataset/ into the image, but training runs when the container starts. User sees training delay on first start, but model is always fresh.

### Pre-trained Model in Image
- **D-02:** Do NOT include model.pkl in the Docker image. Always train at container startup. No pre-trained model baked in.

### Container Command (CMD)
- **D-03:** Keep Flask dev server (`python -m flask run`). Matches current setup and v1.0 user preference. No Waitress, no gunicorn.

### Docker Optimization
- **D-04:** Create .dockerignore to exclude: .planning/, .git/, __pycache__/, *.pkl, venv/, .claude/, .opencode/, etc. Reduces build context size.

### the agent's Discretion
- Exact .dockerignore entries — planner should include all common exclusions.
- Whether to add HEALTHCHECK to Dockerfile — flexible.
- Whether to add labels/metadata to Dockerfile — flexible.
- Docker build args (e.g., PORT) — planner can decide.

</decisions>

<canonical_refs>
## Canonical References

**Downstream agents MUST read these before planning or implementing.**

### Phase Requirements
- `.planning/ROADMAP.md` §Phase 7 — Goal, requirements (DOCKER-01), and 3 success criteria
- `.planning/REQUIREMENTS.md` — DOCKER-01 requirement definition

### Source Files (modified by this phase)
- `Dockerfile` — Update to COPY dataset/, remove model.pkl COPY, keep Flask dev server CMD
- `.dockerignore` — New file to exclude unnecessary files from build context

### Source Files (read by this phase)
- `app.py` — Already has conditional startup training (cold/warm start). No changes needed.
- `train.py` — Already has `train()` function. No changes needed.
- `model.py` — Already has `load_model()` soft load. No changes needed.
- `requirements.txt` — All dependencies already pinned.
- `preprocess.py` — No changes needed.

### Prior Phase Context
- `.planning/phases/06-startup-hook-integration/06-CONTEXT.md` — D-01 through D-05 (startup training flow)
- `.planning/phases/05-training-script/05-CONTEXT.md` — Training script decisions

### Dataset
- `dataset/Fake.csv` — 23,481 rows (label = 0)
- `dataset/True.csv` — 21,417 rows (label = 1)
- Total: ~44,898 rows — will be COPY'd into Docker image

No external specs — requirements fully captured in decisions above.

</canonical_refs>

<code_context>
## Existing Code Insights

### Reusable Assets
- Current `Dockerfile` — Already has good structure: python:3.13-slim base, WORKDIR /app, requirements install layer caching, EXPOSE 5000.
- `app.py` — Already handles cold start (trains) and warm start (loads model.pkl). No changes needed for Docker.
- `train.py` — Already has `train()` function that can be called at startup.

### Established Patterns
- `python:3.13-slim` — Current base image. Keep for small image size.
- `pip install --no-cache-dir` — Current pattern for clean installs.
- Layer caching: COPY requirements.txt first, then code. Keep this pattern.
- Flask dev server: `python -m flask run --host=0.0.0.0 --port=5000` — Current CMD.

### Integration Points
- Dockerfile needs to COPY dataset/ directory into /app/dataset/
- Remove `COPY model.pkl .` line — model.pkl will be generated at runtime
- app.py's conditional startup flow (lines 14-30) works as-is in Docker
- train.py's `train()` function will be called by app.py at container startup
- Dataset files are ~tens of MB — will increase image size but acceptable for local use

</code_context>

<specifics>
## Specific Ideas

No specific requirements — open to standard approaches. User prefers simplicity: runtime training, no pre-trained model, Flask dev server, .dockerignore for cleanliness.

</specifics>

<deferred>
## Deferred Ideas

None — discussion stayed within phase scope.

</deferred>

---

*Phase: 07-Docker & Deployment*
*Context gathered: 2026-05-16*
