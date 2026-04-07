---
phase: 31
slug: runtime-service-typed-budget-and-exception-closure
status: passed
nyquist_compliant: true
wave_0_complete: true
created: 2026-03-17
---

# Phase 31 — Validation Strategy

## Test Infrastructure

| Property | Value |
|----------|-------|
| **Framework** | pytest runtime/services/platform/meta suites + governance budget guards + focused mypy proof |
| **Config file** | `pyproject.toml` |
| **Quick run command** | `uv run pytest -q tests/core/test_coordinator.py tests/core/coordinator/runtime/test_mqtt_runtime.py tests/core/coordinator/runtime/test_device_runtime.py && uv run mypy custom_components/lipro/core/coordinator` |
| **Phase gate command** | `uv run pytest -q tests/core/test_coordinator.py tests/core/coordinator/runtime/test_mqtt_runtime.py tests/core/test_coordinator_integration.py tests/core/coordinator/runtime/test_device_runtime.py tests/core/test_device_refresh.py tests/core/test_device.py tests/services/test_services_diagnostics.py tests/services/test_maintenance.py tests/platforms/test_update.py tests/platforms/test_select.py tests/platforms/test_sensor.py tests/core/test_diagnostics.py tests/core/test_system_health.py tests/meta/test_governance_guards.py tests/meta/test_governance_closeout_guards.py tests/meta/test_public_surface_guards.py tests/meta/test_toolchain_truth.py tests/meta/test_phase31_runtime_budget_guards.py && uv run mypy custom_components/lipro/core/coordinator custom_components/lipro/services custom_components/lipro/entities custom_components/lipro/select.py custom_components/lipro/sensor.py` |
| **Estimated runtime** | ~60-150 seconds |

## Wave Structure

- **Wave 1:** `31-01` —— runtime lifecycle / transport exception closure
- **Wave 2:** `31-02` —— runtime device/state typed narrowing
- **Wave 3:** `31-03` —— service/platform/entity targeted closure
- **Wave 4:** `31-04` —— budget truth / no-growth guards / closeout evidence

## Per-Task Verification Map

| Task ID | Plan | Wave | Requirement | Test Type | Automated Command | Status |
|---------|------|------|-------------|-----------|-------------------|--------|
| 31-01-01 | 01 | 1 | ERR-05 | focused | `uv run pytest -q tests/core/test_coordinator.py tests/core/coordinator/runtime/test_mqtt_runtime.py tests/core/test_coordinator_integration.py` | ✅ passed |
| 31-01-02 | 01 | 1 | ERR-05 | focused | `uv run pytest -q tests/core/test_coordinator.py tests/core/coordinator/runtime/test_mqtt_runtime.py tests/core/test_coordinator_integration.py -k "error or failure or reconnect or teardown"` | ✅ passed |
| 31-02-01 | 02 | 2 | TYP-07 | focused | `uv run pytest -q tests/core/coordinator/runtime/test_device_runtime.py tests/core/test_device_refresh.py tests/core/test_device.py` | ✅ passed |
| 31-02-02 | 02 | 2 | ERR-05 | focused | `uv run pytest -q tests/core/coordinator/runtime/test_device_runtime.py tests/core/test_device_refresh.py -k "failure or reject or degrade"` | ✅ passed |
| 31-03-01 | 03 | 3 | TYP-07 | focused | `uv run pytest -q tests/services/test_services_diagnostics.py tests/services/test_maintenance.py tests/platforms/test_update.py tests/platforms/test_select.py tests/platforms/test_sensor.py` | ✅ passed |
| 31-03-02 | 03 | 3 | ERR-05 | focused | `uv run pytest -q tests/core/test_diagnostics.py tests/core/test_system_health.py tests/services/test_services_diagnostics.py tests/services/test_maintenance.py tests/platforms/test_update.py` | ✅ passed |
| 31-04-01 | 04 | 4 | GOV-23, TYP-07, ERR-05 | focused + static | `uv run mypy custom_components/lipro/core/coordinator custom_components/lipro/services custom_components/lipro/entities custom_components/lipro/select.py custom_components/lipro/sensor.py && uv run pytest -q tests/meta/test_governance_guards.py tests/meta/test_governance_closeout_guards.py` | ✅ passed |
| 31-04-02 | 04 | 4 | GOV-23, TYP-07, ERR-05 | phase-gate + static | `uv run mypy custom_components/lipro/core/coordinator custom_components/lipro/services custom_components/lipro/entities custom_components/lipro/select.py custom_components/lipro/sensor.py && uv run pytest -q tests/meta/test_governance_guards.py tests/meta/test_governance_closeout_guards.py tests/meta/test_public_surface_guards.py tests/meta/test_toolchain_truth.py tests/meta/test_phase31_runtime_budget_guards.py` | ✅ passed |

## Manual-Only Verifications

- 确认 runtime broad-catch closure 使用的是明确语义分类，而不是换个名字继续吞错。
- 确认 typed budget truth 明确区分 `sanctioned_any`、`backlog_any` 与 touched-zone `type: ignore` no-growth，且测试噪声未混入生产预算。
- 确认 `Phase 31` closeout truth 诚实记录 remaining defer 边界，而不是制造 repo-wide zero-debt 幻象。

## Validation Sign-Off

- [x] All planned tasks have automated verification commands.
- [x] Commands use `uv run ...` consistently.
- [x] Wave order follows `lifecycle -> device/state -> service/platform -> guards/closeout`.
- [x] Typed/exception budget proof includes `uv run mypy ...` for touched production zones.
- [x] `nyquist_compliant: true` set in frontmatter.
- [x] Execution evidence recorded in `31-VERIFICATION.md`.
