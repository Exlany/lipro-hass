---
phase: 09
slug: residual-surface-closure
status: draft
nyquist_compliant: true
wave_0_complete: true
created: 2026-03-14
updated: 2026-03-14
---

# Phase 09 — Validation Strategy

> Per-phase validation contract for residual surface closure.

---

## Test Infrastructure

| Property | Value |
|----------|-------|
| **Framework** | `pytest` + `ruff` |
| **Config file** | `pyproject.toml` |
| **Quick run command** | `uv run pytest -q tests/core/mqtt/test_mqtt.py tests/core/test_coordinator.py tests/core/test_outlet_power.py tests/platforms/test_sensor.py tests/test_coordinator_public.py tests/meta/test_public_surface_guards.py` |
| **Full suite command** | `uv run pytest -q` |
| **Estimated runtime** | ~45 seconds |

---

## Sampling Rate

- **After every task commit:** Run `Quick run command`
- **After every plan wave:** Run `Full suite command`
- **Before `$gsd-verify-work`:** Full suite must be green
- **Max feedback latency:** 60 seconds

---

## Per-Task Verification Map

| Task ID | Plan | Wave | Requirement | Test Type | Automated Command | File Exists | Status |
|---------|------|------|-------------|-----------|-------------------|-------------|--------|
| `09-01-01` | `09-01` | 1 | `RSC-01`, `RSC-02` | protocol surface regression | `uv run pytest -q tests/core/mqtt/test_mqtt.py tests/meta/test_public_surface_guards.py` | ✅ | ⬜ pending |
| `09-01-02` | `09-01` | 1 | `RSC-01`, `RSC-02` | compat export / integration | `uv run pytest -q tests/integration/test_mqtt_coordinator_integration.py tests/meta/test_governance_guards.py` | ✅ | ⬜ pending |
| `09-01-03` | `09-01` | 1 | `RSC-01`, `RSC-02` | package/public-surface proof | `uv run pytest -q tests/meta/test_public_surface_guards.py tests/meta/test_dependency_guards.py` | ✅ | ⬜ pending |
| `09-02-01` | `09-02` | 1 | `RSC-03` | runtime read-only access | `uv run pytest -q tests/core/test_coordinator.py tests/test_coordinator_public.py` | ✅ | ⬜ pending |
| `09-02-02` | `09-02` | 1 | `RSC-04` | outlet power primitive | `uv run pytest -q tests/core/test_outlet_power.py tests/platforms/test_sensor.py` | ✅ | ⬜ pending |
| `09-02-03` | `09-02` | 1 | `RSC-03`, `RSC-04` | diagnostics / helper convergence | `uv run pytest -q tests/core/test_diagnostics.py tests/core/test_coordinator.py tests/platforms/test_sensor.py` | ✅ | ⬜ pending |
| `09-03-01` | `09-03` | 2 | `RSC-01`, `RSC-02` | governance sync | `uv run pytest -q tests/meta/test_governance_guards.py tests/meta/test_public_surface_guards.py` | ✅ | ⬜ pending |
| `09-03-02` | `09-03` | 2 | `RSC-03`, `RSC-04` | authority / file ownership | `uv run pytest -q tests/meta/test_governance_guards.py tests/meta/test_dependency_guards.py` | ✅ | ⬜ pending |
| `09-03-03` | `09-03` | 2 | `RSC-01`, `RSC-02`, `RSC-03`, `RSC-04` | full regression | `uv run pytest -q` | ✅ | ⬜ pending |

*Status: ⬜ pending · ✅ green · ❌ red · ⚠️ flaky*

---

## Wave 0 Requirements

- [x] Existing infrastructure covers all phase requirements.

---

## Manual-Only Verifications

All phase behaviors have automated verification.

---

## Validation Sign-Off

- [x] All tasks have automated verify or Wave 0 dependencies
- [x] Sampling continuity: no 3 consecutive tasks without automated verify
- [x] Wave 0 covers all MISSING references
- [x] No watch-mode flags
- [x] Feedback latency < 60s
- [x] `nyquist_compliant: true` set in frontmatter

**Approval:** pending
