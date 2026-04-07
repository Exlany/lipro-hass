---
phase: 35
slug: protocol-hotspot-final-slimming
status: passed
nyquist_compliant: true
wave_0_complete: true
created: 2026-03-18
updated: 2026-03-18
---

# Phase 35 — Validation Strategy

> Per-phase validation contract for protocol hotspot slimming.

---

## Test Infrastructure

| Property | Value |
|----------|-------|
| **Framework** | `pytest` |
| **Config file** | `pyproject.toml` |
| **Quick run command** | `uv run pytest -q tests/core/api/test_auth_recovery_telemetry.py tests/core/api/test_api_command_surface.py tests/core/api/test_api_transport_and_schedule.py tests/core/api/test_protocol_contract_matrix.py` |
| **Full suite command** | `uv run pytest -q tests/core/api/test_api_command_surface.py tests/core/api/test_api_transport_and_schedule.py tests/core/api/test_auth_recovery_telemetry.py tests/core/api/test_protocol_contract_matrix.py tests/meta/test_public_surface_guards.py tests/meta/test_dependency_guards.py tests/meta/test_governance*.py tests/meta/test_version_sync.py` |
| **Static gate** | `uv run ruff check .` |
| **Estimated runtime** | `~20s` |

## Per-Task Verification Map

| Task ID | Plan | Wave | Requirement | Test Type | Automated Command | Status |
|---------|------|------|-------------|-----------|-------------------|--------|
| 35-01-01 | 01 | 1 | HOT-09 | protocol/api | `uv run pytest -q tests/core/api/test_auth_recovery_telemetry.py tests/core/api/test_api_transport_and_schedule.py` | ✅ passed |
| 35-01-02 | 01 | 1 | HOT-09, RES-07 | endpoint regression | `uv run pytest -q tests/core/api/test_api_command_surface.py tests/core/api/test_api_transport_and_schedule.py` | ✅ passed |
| 35-02-01 | 02 | 2 | HOT-09 | protocol-root | `uv run pytest -q tests/core/api/test_protocol_contract_matrix.py tests/meta/test_public_surface_guards.py` | ✅ passed |
| 35-02-02 | 02 | 2 | RES-07 | baseline/governance | `uv run pytest -q tests/meta/test_public_surface_guards.py tests/meta/test_dependency_guards.py` | ✅ passed |
| 35-03-01 | 03 | 2 | HOT-09, RES-07 | guardrails | `uv run pytest -q tests/core/api/test_protocol_contract_matrix.py tests/core/api/test_api_command_surface.py tests/core/api/test_api_transport_and_schedule.py tests/meta/test_public_surface_guards.py` | ✅ passed |
| 35-03-02 | 03 | 2 | HOT-09, RES-07 | governance | `uv run pytest -q tests/meta/test_governance*.py tests/meta/test_version_sync.py tests/meta/test_dependency_guards.py` | ✅ passed |

## Validation Sign-Off

- [x] All planned tasks have automated verify coverage
- [x] Wave 0 already exists
- [x] No watch-mode commands
- [x] `nyquist_compliant: true` set after execution evidence landed

**Approval:** complete
