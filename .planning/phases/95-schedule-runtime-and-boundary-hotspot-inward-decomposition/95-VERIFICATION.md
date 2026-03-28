---
phase: 95
slug: schedule-runtime-and-boundary-hotspot-inward-decomposition
status: passed
verified_on: 2026-03-28
requirements:
  - HOT-41
---

# Phase 95 Verification

## Goal

验证 `Phase 95` 是否真正把 schedule/runtime hotspot inward split 冻结为单一 current truth：`schedule_service.py` 不再把 batch query / mutation refresh / delete choreography 压成单体热点，`command_runtime.py`、`mqtt_runtime.py` 与 `auth_recovery.py` 继续保持 formal home 不变但内部 choreography 已被局部 helper 吸收，且 current route 已稳定前推到 `Phase 96 planning-ready`。

## Must-Have Score

- Verified: `3 / 3`
- Human-only items: `0`
- Gaps found: `0`

## Requirement Verdict

| Requirement | Verdict | Evidence |
|-------------|---------|----------|
| `HOT-41` | ✅ partial tranche passed | `custom_components/lipro/core/api/{schedule_service.py,endpoints/schedule.py,schedule_codec.py}`、`custom_components/lipro/core/coordinator/runtime/{command_runtime.py,mqtt_runtime.py}`、`custom_components/lipro/core/api/auth_recovery.py` 与 `tests/meta/test_phase95_hotspot_decomposition_guards.py` 共同证明 hotspot inward split 已发生且 formal home 未漂移；剩余 HOT-41 scope 已继续登记在 `Phase 96`。 |

## Automated Proof

- `uv run pytest -q tests/core/api/test_api_schedule_candidate_queries.py tests/core/api/test_api_schedule_candidate_mutations.py tests/core/api/test_api_schedule_service.py tests/core/api/test_api_schedule_endpoints.py tests/core/api/test_schedule_codec.py`
- `uv run pytest -q tests/core/coordinator/runtime/test_command_runtime.py tests/core/coordinator/runtime/test_command_runtime_orchestration.py tests/core/coordinator/runtime/test_mqtt_runtime.py tests/core/coordinator/runtime/test_mqtt_runtime_connection.py tests/core/coordinator/runtime/test_mqtt_runtime_notifications.py tests/core/api/test_auth_recovery_telemetry.py tests/core/api/test_api_transport_executor.py tests/core/anonymous_share/test_observability.py`
- `uv run pytest -q tests/meta/test_phase95_hotspot_decomposition_guards.py`
- `uv run pytest -q tests/meta`
- `uv run python scripts/check_file_matrix.py --check`
- `uv run ruff check .`
- `uv run mypy`
- `node "$HOME/.codex/get-shit-done/bin/gsd-tools.cjs" state json`
- `node "$HOME/.codex/get-shit-done/bin/gsd-tools.cjs" init progress`
- `node "$HOME/.codex/get-shit-done/bin/gsd-tools.cjs" phase-plan-index 95`

## Verified Outcomes

- `schedule_service.py` 把 candidate batch、mutation refresh 与 delete batch choreography inward split 为 local helpers，公开 verbs 继续稳定。
- `endpoints/schedule.py` 不再内嵌重复 `_typed_iot_request()` wrapper；endpoint/service 边界只剩 boundary orchestration。
- `command_runtime.py`、`mqtt_runtime.py` 与 `auth_recovery.py` 的主链函数已明显缩短，trace / connect / refresh choreography 被命名 helper 吸收，但 runtime/protocol 正式根没有变化。
- route truth 已从 `Phase 95` closeout 前推到 `v1.26 active route / Phase 96 planning-ready / latest archived baseline = v1.25`。

## Human Verification

- none

## Gaps

- none

## Verdict

`Phase 95` 达成目标，并已准备把下一步自动路由交给 `$gsd-plan-phase 96`。
