---
phase: 36
slug: runtime-root-and-exception-burn-down
status: passed
nyquist_compliant: true
wave_0_complete: true
created: 2026-03-18
updated: 2026-03-18
---

# Phase 36 — Validation Strategy

> Per-phase validation contract for runtime root slimming and broad-exception burn-down.

---

## Test Infrastructure

| Property | Value |
|----------|-------|
| **Framework** | `pytest` |
| **Config file** | `pyproject.toml` |
| **Quick run command** | `uv run pytest -q tests/core/test_coordinator.py tests/core/coordinator/services/test_polling_service.py tests/core/coordinator/runtime/test_mqtt_runtime.py tests/integration/test_mqtt_coordinator_integration.py` |
| **Guard command** | `uv run pytest -q tests/meta/test_phase31_runtime_budget_guards.py tests/meta/test_public_surface_guards.py` |
| **Full suite command** | `uv run pytest -q tests/core/test_coordinator.py tests/core/coordinator/services/test_polling_service.py tests/core/coordinator/services/test_command_service.py tests/core/coordinator/runtime/test_device_runtime.py tests/core/coordinator/runtime/test_mqtt_runtime.py tests/integration/test_mqtt_coordinator_integration.py tests/meta/test_phase31_runtime_budget_guards.py tests/meta/test_public_surface_guards.py tests/meta/test_governance*.py tests/meta/test_version_sync.py` |
| **Static gate** | `uv run ruff check .` |
| **Estimated runtime** | `~25s` |

## Per-Task Verification Map

| Task ID | Plan | Wave | Requirement | Test Type | Automated Command | Status |
|---------|------|------|-------------|-----------|-------------------|--------|
| 36-01-01 | 01 | 1 | HOT-10, TYP-09 | runtime/integration | `uv run pytest -q tests/core/test_coordinator.py tests/core/coordinator/services/test_polling_service.py tests/integration/test_mqtt_coordinator_integration.py tests/meta/test_public_surface_guards.py` | ✅ passed |
| 36-02-01 | 02 | 2 | ERR-08, TYP-09 | runtime exception | `uv run pytest -q tests/core/test_coordinator.py tests/core/coordinator/services/test_command_service.py tests/core/coordinator/runtime/test_device_runtime.py tests/core/coordinator/runtime/test_mqtt_runtime.py tests/meta/test_phase31_runtime_budget_guards.py` | ✅ passed |
| 36-03-01 | 03 | 2 | HOT-10, ERR-08, TYP-09 | governance | `uv run pytest -q tests/meta/test_phase31_runtime_budget_guards.py tests/meta/test_governance*.py tests/meta/test_version_sync.py` | ✅ passed |

## Validation Sign-Off

- [x] All planned tasks have automated verify coverage
- [x] Existing guard suites cover no-growth semantics
- [x] No watch-mode commands
- [x] `nyquist_compliant: true` set after execution evidence landed

**Approval:** complete
