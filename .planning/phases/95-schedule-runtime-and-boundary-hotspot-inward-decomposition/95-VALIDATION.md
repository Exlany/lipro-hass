---
phase: 95
slug: schedule-runtime-and-boundary-hotspot-inward-decomposition
nyquist_compliant: true
wave_0_complete: true
updated: 2026-03-28
---

# Phase 95 Validation Contract

## Wave Order

1. `95-01` schedule service / endpoint / codec inward split
2. `95-02` command-runtime / mqtt-runtime / auth-recovery hotspot inward split
3. `95-03` focused guard, closeout proof, and route handoff

## Focused Gates

- `95-01`
  - `uv run pytest -q tests/core/api/test_api_schedule_candidate_queries.py tests/core/api/test_api_schedule_candidate_mutations.py tests/core/api/test_api_schedule_service.py tests/core/api/test_api_schedule_endpoints.py tests/core/api/test_schedule_codec.py` → `passed`
  - `uv run ruff check custom_components/lipro/core/api/schedule_service.py custom_components/lipro/core/api/endpoints/schedule.py custom_components/lipro/core/api/schedule_endpoint.py custom_components/lipro/core/api/schedule_codec.py tests/core/api/test_api_schedule_candidate_queries.py tests/core/api/test_api_schedule_candidate_mutations.py tests/core/api/test_api_schedule_service.py tests/core/api/test_api_schedule_endpoints.py tests/core/api/test_schedule_codec.py` → `passed`
- `95-02`
  - `uv run pytest -q tests/core/coordinator/runtime/test_command_runtime.py tests/core/coordinator/runtime/test_command_runtime_orchestration.py tests/core/coordinator/runtime/test_mqtt_runtime.py tests/core/coordinator/runtime/test_mqtt_runtime_connection.py tests/core/coordinator/runtime/test_mqtt_runtime_notifications.py tests/core/api/test_auth_recovery_telemetry.py tests/core/api/test_api_transport_executor.py tests/core/anonymous_share/test_observability.py` → `passed`
  - `uv run ruff check custom_components/lipro/core/coordinator/runtime/command_runtime.py custom_components/lipro/core/coordinator/runtime/mqtt_runtime.py custom_components/lipro/core/api/auth_recovery.py tests/core/coordinator/runtime/test_command_runtime.py tests/core/coordinator/runtime/test_command_runtime_orchestration.py tests/core/coordinator/runtime/test_mqtt_runtime.py tests/core/coordinator/runtime/test_mqtt_runtime_connection.py tests/core/coordinator/runtime/test_mqtt_runtime_notifications.py tests/core/api/test_auth_recovery_telemetry.py tests/core/api/test_api_transport_executor.py tests/core/anonymous_share/test_observability.py` → `passed`
  - `uv run mypy custom_components/lipro/core/coordinator/runtime/command_runtime.py custom_components/lipro/core/coordinator/runtime/mqtt_runtime.py custom_components/lipro/core/api/auth_recovery.py` → `passed`
- `95-03`
  - `uv run pytest -q tests/meta/test_phase95_hotspot_decomposition_guards.py` → `passed`
  - `uv run pytest -q tests/meta` → `passed (527 passed)`
  - `uv run python scripts/check_file_matrix.py --check` → `passed`
  - `uv run ruff check .` → `passed`
  - `uv run mypy` → `passed`

## GSD Route Evidence

- `node "$HOME/.codex/get-shit-done/bin/gsd-tools.cjs" state json` → `milestone = v1.26`, `current_phase = 96`, `status = active`, `completed_phases = 2`, `completed_plans = 6`
- `node "$HOME/.codex/get-shit-done/bin/gsd-tools.cjs" init progress` → `Phase 95 summary_count = 3`, `current_phase = null`, `next_phase = 96`, `Phase 96 = planning-ready target`
- `node "$HOME/.codex/get-shit-done/bin/gsd-tools.cjs" phase-plan-index 95` → `incomplete = []`

## Sign-off Checklist

- [x] schedule batch / mutation / refresh choreography no longer挤在同一长函数里
- [x] command-runtime / mqtt-runtime / auth-recovery hotspots inward split to named helpers without changing formal home
- [x] focused guard、file/dependency truth 与 planning route 共同承认 `Phase 95` closeout
- [x] next step 已降到 `$gsd-plan-phase 96`
