---
phase: 37
slug: test-topology-and-derived-truth-convergence
status: passed
nyquist_compliant: true
wave_0_complete: true
created: 2026-03-18
updated: 2026-03-18
---

# Phase 37 — Validation Strategy

> Per-phase validation contract for third-wave test topicization and derived-truth convergence.

---

## Test Infrastructure

| Property | Value |
|----------|-------|
| **Framework** | `pytest` |
| **Config file** | `pyproject.toml` |
| **Quick run command** | `uv run pytest -q tests/core/test_init*.py tests/meta/test_governance_phase_history*.py tests/meta/test_toolchain_truth.py` |
| **Full suite command** | `uv run pytest -q tests/core/test_init*.py tests/meta/test_governance*.py tests/meta/test_toolchain_truth.py tests/meta/test_version_sync.py tests/meta/test_public_surface_guards.py` |
| **Static gate** | `uv run ruff check .` |
| **Estimated runtime** | `~25s` |

## Per-Task Verification Map

| Task ID | Plan | Wave | Requirement | Test Type | Automated Command | Status |
|---------|------|------|-------------|-----------|-------------------|--------|
| 37-01-01 | 01 | 1 | TST-06 | topical test split | `uv run pytest -q tests/core/test_init*.py tests/meta/test_governance_phase_history*.py` | ✅ passed |
| 37-02-01 | 02 | 2 | GOV-30, QLT-09 | derived truth | `uv run pytest -q tests/meta/test_toolchain_truth.py tests/meta/test_governance_closeout_guards.py tests/meta/test_version_sync.py` | ✅ passed |
| 37-03-01 | 03 | 2 | TST-06, GOV-30, QLT-09 | drift guards | `uv run pytest -q tests/meta/test_toolchain_truth.py tests/meta/test_governance_closeout_guards.py tests/meta/test_governance_phase_history*.py tests/meta/test_version_sync.py` | ✅ passed |
| 37-03-02 | 03 | 2 | GOV-30, QLT-09 | governance closeout | `uv run pytest -q tests/meta/test_governance*.py tests/meta/test_toolchain_truth.py tests/meta/test_version_sync.py` | ✅ passed |

## Validation Sign-Off

- [x] All planned tasks have automated verify coverage
- [x] Guard suites already exist and only need targeted tightening
- [x] No watch-mode commands
- [x] `nyquist_compliant: true` set after execution evidence landed

**Approval:** complete
