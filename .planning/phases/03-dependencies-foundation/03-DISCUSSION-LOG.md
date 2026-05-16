# Phase 3: Dependencies & Foundation - Discussion Log

**Date:** 2026-05-16
**Mode:** Interactive (default)

## Discussion Areas

### 1. Version Pinning Scope
**Question:** Pin only ML-critical deps or all transitive deps too?
**Options:**
- ML deps only (Recommended) — Pin pandas, lightgbm, scikit-learn, numpy, scipy, joblib. Leave Flask transitive deps unpinned.
- All transitive deps too — Pin everything including Werkzeug, Jinja2, MarkupSafe, click, etc.
- You decide
**Selected:** ML deps only (Recommended)
**Rationale:** Flask manages compatibility for its transitive dependencies; pinning only ML-critical deps reduces maintenance burden.

### 2. Python Version Constraint
**Question:** How should we enforce the Python 3.13 requirement?
**Options:**
- Comment in requirements.txt (Recommended) — Add `# Requires Python 3.13` at top of file.
- pyproject.toml constraint — Create setup.cfg or pyproject.toml with python_requires.
- Dockerfile only — Rely on Docker base image pin.
**Selected:** Comment in requirements.txt (Recommended)
**Rationale:** Simple, visible, no additional files needed.

### 3. Dev vs Prod Dependencies
**Question:** Separate requirements-dev.txt or keep in one file?
**Options:**
- Separate requirements-dev.txt (Recommended) — Clean separation of runtime and test deps.
- Single file — Simpler for local-only project.
**Selected:** Single file
**Rationale:** Project is local-only; simplicity preferred over separation.

### 4. Installation Verification
**Question:** Trust pip install or add import smoke test?
**Options:**
- Trust pip install — Just run `pip install -r requirements.txt`.
- Import smoke test (Recommended) — Also run `python -c "import pandas; import lightgbm"`.
**Selected:** Import smoke test (Recommended)
**Rationale:** Quick sanity check that imports actually work, not just install.

### 5. LightGBM Pin Documentation
**Question:** Add explanatory comment for lightgbm==4.6.0 or pin silently?
**Options:**
- Add explanatory comment (Recommended) — `# Pinned to match model.pkl training provenance`.
- No comment needed — Version documented in REQUIREMENTS.md and ROADMAP.md.
**Selected:** Add explanatory comment (Recommended)
**Rationale:** Helps future developers understand why this specific version matters.

### 6. Pandas 3.x Compatibility
**Question:** Trust the spec or research pandas 3.0 breaking changes?
**Options:**
- Trust the spec — train.py doesn't exist yet, no backward compatibility concerns.
- Research breaking changes — Web search before Phase 5 planning.
**Selected:** Trust the spec
**Rationale:** Since train.py (Phase 5) doesn't exist yet, no existing code to break.

## Deferred Ideas
None.

## Summary
6 decisions captured across 6 discussion areas. All decisions favor simplicity and trust in existing specifications. Phase is ready for planning.
