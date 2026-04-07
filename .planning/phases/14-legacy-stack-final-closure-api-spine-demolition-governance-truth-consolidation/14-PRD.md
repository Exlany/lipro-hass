# Phase 14 PRD — Legacy Stack Final Closure, API Spine Demolition & Governance Truth Consolidation

**Date:** 2026-03-15
**Status:** Executed
**Owner:** v1.1 closeout stream

## Problem Statement

Phase 13 已把显式领域表面、热点边界收薄与治理守卫拉回绿色，但全仓终审仍看到四类旧架构残留：

1. `Coordinator` 内部仍以 `client` 术语承载 protocol-facing passthrough 群，runtime root 还没真正卸下 API spine；
2. `core/api` 仍保留 `ScheduleApiService` ↔ `ScheduleEndpoints` ↔ `LiproRestFacade` 的回环，以及 `_Client*Mixin` / `_EndpointAdapter.__getattr__` 一类旧 helper spine；
3. `status_service.py` 与 `control/service_router.py` 仍有可继续拆下的 fallback / glue 热点；
4. 文档与治理真源仍残留少量过期措辞，且尚未对 `_ClientBase` / `_Client*Mixin` / `LiproMqttClient` 的 residual 使用方式加上更强 guard。

## Goals

- 让 `Coordinator` 通过正式 `protocol` 术语与 `CoordinatorProtocolService` 拥有更薄、更清晰的 protocol-facing surface；
- 删除 `ScheduleApiService` 回环与 schedule 私有 passthrough seam，继续拆掉 API 旧 helper spine；
- 抽离 `status_service` fallback kernel 与 `service_router` 私有 glue helpers，降低热点温度；
- 回写 governance / phase assets / meta guards，使 residual owner、delete gate 与现行架构口径完全一致。

## Non-Goals

- 不重写 MQTT transport，不强行在本 phase 内物理更名 `LiproMqttClient`；
- 不改变 Home Assistant 对外服务注册名、实体行为或用户可见功能语义；
- 不为了测试保留新的生产 compat seam。

## Acceptance Criteria

- `Coordinator` 内部不再把正式协议真源写作 `client`；protocol-facing passthrough 群转入 `CoordinatorProtocolService`；
- `ScheduleApiService` 与 `LiproRestFacade` 尾部的 schedule 私有 helper passthrough 被删除，相关测试改走正式 collaborator / helper；
- `status_service` 的 binary-split kernel 与 `service_router` 的私有 developer glue 抽入聚焦模块，原 public 行为不变；
- `PUBLIC_SURFACES` / `ARCHITECTURE_POLICY` / `RESIDUAL_LEDGER` / `KILL_LIST` / `developer_architecture` / `STRUCTURE` / meta guards 与 Phase 14 完成态一致。

## Already Fixed / Must Not Be Replanned

- `core.api.LiproClient`、`LiproProtocolFacade.get_device_list`、`LiproMqttFacade.raw_client`、`DeviceCapabilities` 已在 Phase 12 删除；
- `services/wiring.py` 已在 Phase 11 删除；
- `LiproDevice` / `DeviceState` 动态 `__getattr__` 已在 Phase 13 删除；
- 本 phase 不得为了测试恢复任何已删除 compat seam。
