# Phase 14 Research

**Date:** 2026-03-15
**Status:** Final
**Plans / Waves:** 4 plans / 3 waves

## What The Review Confirmed

- `Coordinator` 仍把 protocol-facing schedule / diagnostics / OTA / outlet power 调用挂在 `self.client.*` 上，内部术语与职责边界仍可继续收口；
- `core/api` 仍残留 `ScheduleApiService` 回环、`_Client*Mixin` 旧 helper spine 与 `_EndpointAdapter.__getattr__` 隐式协作者表面；
- `status_service.py` 与 `control/service_router.py` 仍有可稳定拆出的 fallback / glue 内核；
- 文档与治理真源主裁决面总体干净，但 subordinate snapshots 与 residual guards 还有若干过期措辞与执法缺口；
- 用户明确偏好：不要为了测试保留生产 compat 冗余，而要把代码与测试一起重构到新的正式面。

## Risk Notes

- `Coordinator.client` 名称在测试中传播很广，直接删除会扩大回归面，因此必须同步测试与夹具；
- `service_router` 不能移动 public handler module identity，只能抽私有 helper；
- `status_service` 与 schedule residual 的拆分要避免破坏 focused tests 与协议行为；
- governance guards 必须锁结构与 policy，而不是重新把 subordinate docs 升格为第一真源。

## Chosen Strategy

1. 先让 `Coordinator` 内部切到 `protocol` 真源，并新增 `CoordinatorProtocolService` 吃掉 passthrough 群；
2. 删除 `ScheduleApiService`，把 schedule 正式行为收回 `ScheduleEndpoints` + focused helpers，同时清掉 `client.py` 尾部 schedule 私有代理；
3. 抽出 `status_service` fallback kernel 与 `service_router` 私有 developer glue，使热点文件只保留 public orchestration；
4. 同步治理文档、residual ledger、kill list、architecture policy 与 meta guards，把 Phase 14 的 residual ownership / delete gate 写成当前真相。

## Validation Focus

- `uv run pytest -q tests/core/api/test_api.py tests/core/api/test_api_schedule_endpoints.py tests/core/api/test_api_status_service.py tests/core/api/test_api_status_service_regressions.py tests/core/test_coordinator.py tests/services/test_services_registry.py`
- `uv run pytest -q tests/platforms/test_update.py tests/platforms/test_firmware_update_entity_edges.py tests/services/test_services_diagnostics.py tests/integration/test_mqtt_coordinator_integration.py`
- `uv run pytest -q tests/meta/test_governance_guards.py tests/meta/test_public_surface_guards.py tests/meta/test_dependency_guards.py tests/meta/test_version_sync.py`
- `uv run ruff check .`
- `uv run mypy`
- `uv run pytest -q`
