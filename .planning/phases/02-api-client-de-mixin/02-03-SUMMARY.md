---
phase: 02-api-client-de-mixin
plan: "03"
subsystem: api
tags: [refactor, endpoints, collaborators, normalizers, compat]
requires:
  - phase: 02-02
    provides: explicit rest facade chain, transport/auth/policy collaborators, transitional compat shell
provides:
  - endpoint surface 由显式 collaborator family 暴露，而不再由 `_ClientEndpointsMixin` 聚合定义
  - `LiproRestFacade` 改为组合根，按 family 管理 auth/device/status/command/misc/schedule collaborators
  - payload normalizer helpers 收口为显式 compat surface，不再要求 façade 继承 payload mixin 才可见
  - `ScheduleApiService` 与 endpoint/service helpers 继续在新 façade 结构上闭环，并保留必要 legacy patch seam
affects: [02-04, 02.5]
completed: 2026-03-12
---

# Phase 02 Plan 02-03 执行总结

## 本次完成

- 在 `custom_components/lipro/core/api/endpoints/` 下建立显式协作者族：`AuthEndpoints`、`DeviceEndpoints`、`StatusEndpoints`、`CommandEndpoints`、`MiscEndpoints`、`ScheduleEndpoints`。
- 将 `custom_components/lipro/core/api/client.py` 中的 `LiproRestFacade` 从 `_ClientEndpointsMixin` 继承根改为 `_ClientBase` 组合根，通过 `_endpoint_exports` + `__getattr__` 暴露 endpoint/public helper surface。
- 在 `custom_components/lipro/core/api/endpoints/payloads.py` 中把 `_EndpointAdapter` 提升为正式委托层，显式代理 transport/auth/helper seam，避免 `_ClientBase` 占位桩抢先命中。
- 把 `_extract_data_list`、`_extract_timings_list`、`_sanitize_iot_device_ids`、`_normalize_power_target_id`、`_coerce_int_list`、`_parse_mesh_schedule_json`、`_normalize_mesh_timing_rows` 等 helper surface 以受控 compat 形式挂回 façade class，确保 service/tests 不因 demixin 中断。
- 保留 `_ClientEndpointsMixin` 与各 family mixin，但其角色已降级为 narrow compat / focused helper tests，不再承担正式 REST root 叙事。
- 在 `tests/core/api/test_protocol_contract_matrix.py` 新增护栏，明确 `LiproRestFacade` 的 MRO 不得再回到 `_ClientEndpointsMixin` 聚合根。

## 关键裁决

- **正式根裁决**：Phase 2 的 endpoint public truth 已切换为 `LiproRestFacade + explicit collaborators`，不是聚合 mixin。
- **compat 裁决**：helper/mixin 仍保留，但只服务于测试、过渡接缝与局部 helper 复用，不再是架构入口。
- **委托裁决**：`_EndpointAdapter` 必须显式代理 `_smart_home_request` / `_iot_request` / `_request_iot_mapping*` / `_to_device_type_hex` 等 seam，不能只依赖 `__getattr__`，否则会被 `_ClientBase` 桩实现截获。
- **service 连通性裁决**：`ScheduleApiService` 等 helper 继续以 façade 为 owner，但其 helper 调用已由 collaborator graph 提供，Phase 2.5 可在此基础上继续上收为 unified protocol root。

## 验证结果

- `uv run pytest tests/core/api/test_api.py tests/core/api/test_api_command_service.py tests/core/api/test_api_diagnostics_service.py tests/core/api/test_api_schedule_endpoints.py tests/core/api/test_api_schedule_service.py tests/core/api/test_api_status_service.py tests/core/api/test_protocol_contract_matrix.py -q`
  - 结果：`283 passed`

## 修改文件

- `custom_components/lipro/core/api/client.py`
- `custom_components/lipro/core/api/endpoints/__init__.py`
- `custom_components/lipro/core/api/endpoints/auth.py`
- `custom_components/lipro/core/api/endpoints/commands.py`
- `custom_components/lipro/core/api/endpoints/devices.py`
- `custom_components/lipro/core/api/endpoints/misc.py`
- `custom_components/lipro/core/api/endpoints/payloads.py`
- `custom_components/lipro/core/api/endpoints/schedule.py`
- `custom_components/lipro/core/api/endpoints/status.py`
- `tests/core/api/test_protocol_contract_matrix.py`
- `.planning/phases/02-api-client-de-mixin/02-03-SUMMARY.md`

## 边界确认

- 本计划未删除 `LiproClient` compat shell，也未收口 governance 文档；这些属于 `02-04`。
- 本计划未开始 protocol-plane unified root；这些属于 `02.5`。
- 本计划已确保：endpoint/service 行为在真实 façade 结构上闭环，且原有 helper/test seam 继续可用。

## 主代理下一步

- 进入 `02-04`：集中收口 `LiproClient` compat shell、legacy public names 与 Phase 2 handoff 治理文档。
