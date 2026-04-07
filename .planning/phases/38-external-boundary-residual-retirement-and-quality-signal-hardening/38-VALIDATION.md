---
phase: 38
slug: external-boundary-residual-retirement-and-quality-signal-hardening
status: passed
nyquist_compliant: true
wave_0_complete: true
created: 2026-03-18
updated: 2026-03-18
---

# Phase 38 — Validation Strategy

> Per-phase validation contract for external-boundary residual retirement and assurance-signal hardening.

---

## Test Infrastructure

| Property | Value |
|----------|-------|
| **Framework** | `pytest` |
| **Config file** | `pyproject.toml` |
| **Quick run command** | `uv run pytest -q tests/meta/test_external_boundary_authority.py tests/meta/test_external_boundary_fixtures.py tests/meta/test_toolchain_truth.py` |
| **Full suite command** | `uv run pytest -q tests/meta/test_external_boundary_authority.py tests/meta/test_external_boundary_fixtures.py tests/meta/test_firmware_support_manifest_repo_asset.py tests/meta/test_governance*.py tests/meta/test_toolchain_truth.py tests/meta/test_version_sync.py tests/meta/test_public_surface_guards.py` |
| **Static gates** | `uv run ruff check .` + `uv run mypy` |
| **Estimated runtime** | `~35s` |

## Per-Task Verification Map

| Task ID | Plan | Wave | Requirement | Test Type | Automated Command | Status |
|---------|------|------|-------------|-----------|-------------------|--------|
| 38-01-01 | 01 | 1 | RES-08 | external-boundary authority | `uv run pytest -q tests/meta/test_external_boundary_authority.py tests/meta/test_external_boundary_fixtures.py tests/meta/test_firmware_support_manifest_repo_asset.py tests/core/ota/test_firmware_manifest.py` | ✅ passed |
| 38-02-01 | 02 | 2 | QLT-10 | toolchain / CI truth | `uv run pytest -q tests/meta/test_toolchain_truth.py tests/meta/test_governance_release_contract.py tests/meta/test_version_sync.py` | ✅ passed |
| 38-03-01 | 03 | 2 | GOV-31 | governance closeout truth | `uv run pytest -q tests/meta/test_governance_closeout_guards.py tests/meta/test_governance_phase_history.py tests/meta/test_governance_phase_history_runtime.py tests/meta/test_governance_phase_history_topology.py tests/meta/test_toolchain_truth.py` | ✅ passed |
| 38-03-02 | 03 | 2 | RES-08, QLT-10, GOV-31 | end-to-end recheck | `uv run pytest -q tests/meta/test_external_boundary_authority.py tests/meta/test_external_boundary_fixtures.py tests/meta/test_firmware_support_manifest_repo_asset.py tests/meta/test_governance*.py tests/meta/test_toolchain_truth.py tests/meta/test_version_sync.py tests/meta/test_public_surface_guards.py` | ✅ passed |

## Validation Sign-Off

- [x] Every planned task has an automated verification path
- [x] Validation commands stay aligned with current CI / governance topology
- [x] No watch-mode or interactive commands
- [x] `nyquist_compliant: true` only after execution evidence lands

**Approval:** complete
