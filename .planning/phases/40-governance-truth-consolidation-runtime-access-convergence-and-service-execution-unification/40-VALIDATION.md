---
phase: 40
slug: governance-truth-consolidation-runtime-access-convergence-and-service-execution-unification
status: passed
nyquist_compliant: true
wave_0_complete: true
created: 2026-03-19
updated: 2026-03-19
---

# Phase 40 — Validation Strategy

> Per-phase validation contract for governance truth consolidation, runtime-access convergence, and service execution unification.

---

## Test Infrastructure

| Property | Value |
|----------|-------|
| **Framework** | `pytest` |
| **Config file** | `pyproject.toml` |
| **Quick run command** | `uv run pytest -q tests/meta/test_governance*.py tests/meta/test_public_surface_guards.py tests/meta/test_version_sync.py tests/meta/test_toolchain_truth.py` |
| **Full suite command** | `uv run pytest tests/ -v --ignore=tests/benchmarks --cov=custom_components/lipro --cov-fail-under=95 --cov-report=term-missing --cov-report=json --cov-report=xml` |
| **Static gates** | `uv run ruff check .` + `uv run mypy` |
| **Estimated runtime** | `~50s` |

## Per-Task Verification Map

| Task ID | Plan | Wave | Requirement | Test Type | Automated Command | Status |
|---------|------|------|-------------|-----------|-------------------|--------|
| 40-01-01 | 01 | 1 | GOV-33 | governance current-story truth | `uv run pytest -q tests/meta/test_governance_guards.py tests/meta/test_version_sync.py` | ✅ passed |
| 40-02-01 | 02 | 2 | GOV-33, QLT-11 | baseline / registry / guard sync | `uv run pytest -q tests/meta/test_governance_closeout_guards.py tests/meta/test_governance_guards.py tests/meta/test_toolchain_truth.py tests/meta/test_version_sync.py` | ✅ passed |
| 40-03-01 | 03 | 2 | QLT-11 | release / support / runbook truth | `uv run pytest -q tests/meta/test_governance_release_contract.py tests/meta/test_toolchain_truth.py tests/meta/test_version_sync.py` | ✅ passed |
| 40-04-01 | 04 | 3 | QLT-11 | contributor templates / drift guards | `uv run pytest -q tests/meta/test_governance_release_contract.py tests/meta/test_governance_guards.py tests/meta/test_version_sync.py` | ✅ passed |
| 40-05-01 | 05 | 4 | CTRL-09 | runtime-access control-plane convergence | `uv run pytest -q tests/core/test_control_plane.py tests/core/test_diagnostics.py tests/services/test_device_lookup.py tests/services/test_maintenance.py` | ✅ passed |
| 40-06-01 | 06 | 4 | ERR-10 | shared service execution contract | `uv run pytest -q tests/services/test_execution.py tests/services/test_services_schedule.py tests/services/test_service_resilience.py tests/core/api/test_api_transport_and_schedule.py` | ✅ passed |
| 40-07-01 | 07 | 5 | RES-10 | naming residue / review-guard sync | `uv run pytest -q tests/meta/test_public_surface_guards.py tests/meta/test_dependency_guards.py tests/meta/test_governance_guards.py` | ✅ passed |
| 40-07-02 | 07 | 5 | GOV-33, QLT-11, CTRL-09, ERR-10, RES-10 | end-to-end governance recheck | `uv run pytest -q tests/meta/test_dependency_guards.py tests/meta/test_public_surface_guards.py tests/meta/test_governance*.py tests/meta/test_toolchain_truth.py tests/meta/test_version_sync.py` | ✅ passed |

## Validation Sign-Off

- [x] Every planned task has an automated verification path
- [x] Validation commands stay aligned with current CI / governance topology
- [x] No watch-mode or interactive commands
- [x] `nyquist_compliant: true` only after execution evidence lands

**Approval:** complete
