# Phase 30 Verification

status: passed

## Goal

- 核验 `Phase 30: protocol/control typed contract tightening` 是否完成 `TYP-06` / `ERR-04`：在不创建第二 root 的前提下，把 REST result spine、protocol boundary/root contracts 与 control lifecycle exception arbitration 收回到正式 typed truth。
- 终审结论：**`TYP-06` 与 `ERR-04` 已完成；Phase 30 现已把 protocol/control 高杠杆热点中的 typed / broad-catch debt 收口成 machine-checked contracts。**

## Reviewed Assets

- Phase 资产：`30-CONTEXT.md`、`30-RESEARCH.md`、`30-VALIDATION.md`
- 已生成 summaries：`30-01-SUMMARY.md`、`30-02-SUMMARY.md`、`30-03-SUMMARY.md`
- synced truth：`custom_components/lipro/core/api/{client.py,client_auth_recovery.py,client_transport.py,endpoints/misc.py,endpoints/payloads.py,request_codec.py}`、`custom_components/lipro/core/protocol/{contracts.py,facade.py,boundary/rest_decoder.py,boundary/mqtt_decoder.py}`、`custom_components/lipro/control/{entry_lifecycle_controller.py,system_health_surface.py}`、`tests/core/api/{test_auth_recovery_telemetry.py,test_protocol_contract_matrix.py,test_api_status_service.py,test_api_schedule_service.py,test_api_diagnostics_service.py,test_protocol_replay_rest.py}`、`tests/core/mqtt/test_protocol_replay_mqtt.py`、`tests/integration/test_protocol_replay_harness.py`、`tests/core/{test_init.py,test_init_edge_cases.py,test_control_plane.py,test_system_health.py}`、`tests/meta/{test_governance_guards.py,test_public_surface_guards.py,test_governance_closeout_guards.py}`

## Must-Haves

- **1. REST response/result spine is visibly narrower — PASS**
  - `client.py` 保持 `LiproRestFacade` 作为唯一正式 REST child façade。
  - auth-recovery telemetry、result unwrapping 与 request/response codec 已下沉回 focused collaborators，没有把 typed ownership 再堆回 façade 顶层。

- **2. Protocol boundary/root contracts stay canonical without a new root — PASS**
  - `contracts.py`、`rest_decoder.py` 与 `mqtt_decoder.py` 已围绕 canonical contracts 收口，并通过 `TYPE_CHECKING` + 前向引用切断循环导入。
  - replay harness / entity protocol regressions 现在锁定的是 canonical shape，而不是宽口 `dict[str, Any]` 偶然通过。

- **3. Control lifecycle failure semantics are frozen as named truth — PASS**
  - `setup_auth_failed/setup_not_ready/setup_failed`、`unload_shutdown_degraded`、`reload_auth_failed/reload_not_ready/reload_failed` 已冻结为 control lifecycle truth。
  - `system_health_surface.py` 仍只同步 shared `failure_summary` 最小载荷，未扩成 diagnostics payload cleanup。

## Evidence

- `uv run pytest -q tests/core/api/test_protocol_replay_rest.py tests/core/mqtt/test_protocol_replay_mqtt.py tests/integration/test_protocol_replay_harness.py tests/core/coordinator/test_entity_protocol.py` → `18 passed`
- `uv run pytest -q tests/core/api/test_protocol_replay_rest.py tests/core/mqtt/test_protocol_replay_mqtt.py tests/integration/test_protocol_replay_harness.py tests/core/coordinator/test_entity_protocol.py tests/core/test_init.py tests/core/test_init_edge_cases.py tests/core/test_control_plane.py tests/core/test_system_health.py tests/meta/test_governance_guards.py tests/meta/test_public_surface_guards.py tests/meta/test_governance_closeout_guards.py` → `215 passed`
- `uv run pytest -q tests/core/api/test_auth_recovery_telemetry.py tests/core/api/test_protocol_contract_matrix.py tests/core/api/test_api_status_service.py tests/core/api/test_api_schedule_service.py tests/core/api/test_api_diagnostics_service.py tests/core/api/test_protocol_replay_rest.py tests/core/mqtt/test_protocol_replay_mqtt.py tests/integration/test_protocol_replay_harness.py tests/core/coordinator/test_entity_protocol.py tests/core/test_init.py tests/core/test_init_edge_cases.py tests/core/test_control_plane.py tests/core/test_system_health.py tests/meta/test_governance_guards.py tests/meta/test_public_surface_guards.py tests/meta/test_governance_closeout_guards.py && uv run ruff check custom_components/lipro/core/api custom_components/lipro/core/protocol custom_components/lipro/control tests/meta` → `293 passed`
- `uv run mypy custom_components/lipro/__init__.py custom_components/lipro/core/protocol/boundary/mqtt_decoder.py custom_components/lipro/core/protocol/boundary/rest_decoder.py custom_components/lipro/core/protocol/contracts.py custom_components/lipro/control/entry_lifecycle_controller.py custom_components/lipro/helpers/platform.py custom_components/lipro/select.py custom_components/lipro/sensor.py` → `Success: no issues found in 8 source files`
- `uv run ruff check custom_components/lipro/core/api custom_components/lipro/core/protocol custom_components/lipro/control tests/meta` → passed

## Risks / Notes

- `Phase 30` 有意只收口 protocol/control 高杠杆热点；runtime/service/platform 的 typed budget 与 no-growth guard 继续由 `Phase 31` 正式承接。
- `30-03` 现在不再是 partial/blocked truth；之前被 import/order drift 阻塞的静态 gate 已在本轮合并收平。