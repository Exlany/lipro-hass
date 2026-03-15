# Phase 14: Legacy Stack Final Closure, API Spine Demolition & Governance Truth Consolidation - Context

**Gathered:** 2026-03-15
**Status:** Executed

<domain>
## Phase Boundary

本 phase 只处理四件高杠杆事情：
1. `Coordinator` protocol-facing API spine slimming；
2. `core/api` schedule residual / helper spine closeout；
3. `status_service` 与 `service_router` 热点私有 glue 再拆分；
4. governance 真源与 residual guards 同步回写。
</domain>

<decisions>
## Locked Decisions

- 不为了测试保留新的生产 compat 冗余；
- `Coordinator` 内部正式协议真源统一叫作 `protocol`；
- `ScheduleApiService` 不再作为 schedule 正式主链的一环，schedule 行为应直接归属 `ScheduleEndpoints` 与聚焦 helper；
- `status_service` 的 public API 保持不变，但内部 fallback kernel 可以迁移到独立模块；
- `service_router.py` 保留 public handler home，不移动导出 handler 身份，只下沉私有 glue；
- `LiproMqttClient` 本 phase 先做 residual ownership / guard hardening，不强推物理 rename。
</decisions>

<specifics>
## Specific Ideas

- 新增 `CoordinatorProtocolService`，承接 schedule / OTA / diagnostics / outlet power 的 protocol-facing 协作；
- 删除 `ScheduleApiService`，并让 `tests/core/api/test_api_schedule_service.py` 转为 focused helper / endpoint tests；
- 提取 `core/api/status_fallback.py` 一类内部模块，承载 binary-split context / accumulator / recursion helpers；
- 提取 `control/developer_router_support.py` 一类内部模块，承载 developer report collection、optional capability glue 与 sensor-history shared wrapper；
- 为 `_ClientBase` / `_Client*Mixin` / `LiproMqttClient` residual usage 增加更强 meta guards。
</specifics>

<deferred>
## Deferred Ideas

- `LiproMqttClient` 的物理 rename；
- `client_base.py` 的彻底文件级拆除；
- `service_router.py` 的进一步 handler family 物理拆文件。
</deferred>
