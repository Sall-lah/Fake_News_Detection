# Phase 3: Dependencies & Foundation - Context

**Gathered:** 2026-05-16
**Status:** Ready for planning

<domain>
## Phase Boundary

Add pandas and pin lightgbm in requirements.txt. All required Python packages installed with pinned versions to prevent pickle incompatibility. This phase covers requirements DEP-01 and DEP-02 from the v1.1 roadmap.

</domain>

<decisions>
## Implementation Decisions

### Version Pinning Scope
- **D-01:** Pin only ML-critical dependencies (pandas, lightgbm, scikit-learn, numpy, scipy, joblib). Flask transitive dependencies (Werkzeug, Jinja2, etc.) remain unpinned — Flask manages their compatibility.

### Python Version Constraint
- **D-02:** Add a comment at the top of requirements.txt: `# Requires Python 3.13`. Simple, visible, no additional tooling files needed.

### Dependency Organization
- **D-03:** Keep all dependencies in a single requirements.txt file. No separate requirements-dev.txt — project is local-only and simplicity preferred over separation.

### Installation Verification
- **D-04:** After `pip install -r requirements.txt`, run an import smoke test: `python -c "import pandas; import lightgbm"` to verify imports succeed.

### LightGBM Pin Documentation
- **D-05:** Add an inline comment for `lightgbm==4.6.0`: `# Pinned to match model.pkl training provenance`. Documents why this specific version matters.

### Pandas Version Strategy
- **D-06:** Trust REQUIREMENTS.md specification for pandas 3.0.3. Since train.py (Phase 5) doesn't exist yet, no backward compatibility concerns. Breaking changes research deferred to Phase 5 planning if needed.

### the agent's Discretion
- Requirements.txt ordering: agent may organize by category or keep current installation order — no strong preference expressed.

</decisions>

<canonical_refs>
## Canonical References

**Downstream agents MUST read these before planning or implementing.**

### Requirements
- `.planning/REQUIREMENTS.md` — DEP-01 (pandas==3.0.3), DEP-02 (lightgbm==4.6.0)
- `.planning/ROADMAP.md` — Phase 3 goal, success criteria

### Project Context
- `PROJECT.md` — Key Decisions table, current tech stack (Flask 3.1.1, scikit-learn 1.7.1, etc.)

### Existing Code
- `requirements.txt` — Current dependency file to be modified
- `model.py` — Uses joblib for model loading (relevant for joblib pin)
- `model.pkl` — Trained model file (lightgbm version tied to this artifact)

</canonical_refs>

<code_context>
## Existing Code Insights

### Reusable Assets
- `requirements.txt`: Existing file with 5 pinned deps + 1 unpinned (lightgbm). Pattern: `package==version` format already established.
- `model.py`: Uses `joblib.load()` for model.pkl — confirms joblib is a runtime dependency.
- `preprocess.py`: Uses nltk (not yet in requirements.txt — Phase 5 may need to add it).

### Established Patterns
- Dependency format: `package==version` (e.g., Flask==3.1.1, scikit-learn==1.7.1)
- No comments currently in requirements.txt — D-05 and D-02 introduce first comments

### Integration Points
- `requirements.txt` is referenced by Dockerfile (`pip install -r requirements.txt`)
- `requirements.txt` is referenced by project documentation (PROJECT.md, AGENTS.md)

</code_context>

<specifics>
## Specific Ideas

No specific requirements — open to standard approaches for requirements.txt organization.

</specifics>

<deferred>
## Deferred Ideas

None — discussion stayed within phase scope.

</deferred>

---

*Phase: 3-Dependencies & Foundation*
*Context gathered: 2026-05-16*
