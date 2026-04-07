---
phase: 36
slug: runtime-root-and-exception-burn-down
status: passed
updated: 2026-03-18
---

# Phase 36 Summary

## Outcome

- `36-01`: `CoordinatorPollingService` 已成为 polling/status/outlet/snapshot orchestration 的正式 helper home。
- `36-02`: runtime mainline broad catches 已继续 burn-down 为 typed arbitration / fail-closed semantics。
- `36-03`: runtime typed budget、verification guidance 与 planning/governance truth 已同步到新 reality。

## Validation

- `uv run pytest -q tests/core/test_coordinator.py tests/core/coordinator/services/test_polling_service.py tests/core/coordinator/services/test_command_service.py tests/core/coordinator/runtime/test_device_runtime.py tests/core/coordinator/runtime/test_mqtt_runtime.py tests/integration/test_mqtt_coordinator_integration.py tests/meta/test_phase31_runtime_budget_guards.py`
- `uv run pytest -q tests/meta/test_governance*.py tests/meta/test_public_surface_guards.py tests/meta/test_version_sync.py`
- `uv run ruff check .`
