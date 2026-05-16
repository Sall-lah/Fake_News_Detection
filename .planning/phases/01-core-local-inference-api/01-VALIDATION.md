---
phase: 01
slug: core-local-inference-api
status: draft
nyquist_compliant: false
wave_0_complete: false
created: 2026-05-15
---

# Phase 01 — Validation Strategy

> Per-phase validation contract for feedback sampling during execution.

---

## Test Infrastructure

| Property | Value |
|----------|-------|
| **Framework** | none — no tests installed |
| **Config file** | none — Wave 0 not required |
| **Quick run command** | `python -m compileall .` |
| **Full suite command** | `python -m compileall .` |
| **Estimated runtime** | ~10 seconds |

---

## Sampling Rate

- **After every task commit:** Run `python -m compileall .`
- **After every plan wave:** Run `python -m compileall .`
- **Before `/gsd-verify-work`:** Full suite must be green
- **Max feedback latency:** 20 seconds

---

## Per-Task Verification Map

| Task ID | Plan | Wave | Requirement | Threat Ref | Secure Behavior | Test Type | Automated Command | File Exists | Status |
|---------|------|------|-------------|------------|-----------------|-----------|-------------------|-------------|--------|
| 01-01-01 | 01 | 1 | API-01 | T-01-01 | Validate JSON input before inference | lint/compile | `python -m compileall .` | ❌ W0 | ⬜ pending |
| 01-02-01 | 02 | 1 | PRE-01..07 | T-01-02 | Reject empty cleaned input | lint/compile | `python -m compileall .` | ❌ W0 | ⬜ pending |
| 01-03-01 | 03 | 2 | RUN-01..02 | T-01-03 | Fail fast on model load | lint/compile | `python -m compileall .` | ❌ W0 | ⬜ pending |

*Status: ⬜ pending · ✅ green · ❌ red · ⚠️ flaky*

---

## Wave 0 Requirements

- None — compile-only validation is sufficient for this phase.

---

## Manual-Only Verifications

| Behavior | Requirement | Why Manual | Test Instructions |
|----------|-------------|------------|-------------------|
| POST /predict responds with `{status,label}` | API-01 | No automated test framework installed | Run API locally and send a POST to `/predict` with title+text JSON; expect 200 and `label` of `fake` or `true`. |
| Empty cleaned input returns 400 | PRE-07 | No automated test framework installed | Send input that cleans to empty (e.g., only punctuation) and expect 400 with error payload. |

---

## Validation Sign-Off

- [ ] All tasks have `<automated>` verify or Wave 0 dependencies
- [ ] Sampling continuity: no 3 consecutive tasks without automated verify
- [ ] Wave 0 covers all MISSING references
- [ ] No watch-mode flags
- [ ] Feedback latency < 20s
- [ ] `nyquist_compliant: true` set in frontmatter

**Approval:** pending
