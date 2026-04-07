# Phase 13 PRD — Explicit Domain Surface, Governance Guard Hardening & Hotspot Boundary Decomposition

**Date:** 2026-03-14
**Status:** Executed
**Owner:** v1.1 closeout stream

## Problem Statement

Phase 12 已把类型契约、显式 compat seams 与 contributor-facing governance 拉回绿色，但全仓复审仍显示三类高价值残留：

1. `core/device/device.py` / `state.py` 仍通过动态 `__getattr__` 维持设备域表面；
2. `core/coordinator/orchestrator.py` 与 `core/api/status_service.py` 仍是 runtime/status 热点；
3. README / support / CODEOWNERS / quality-scale / devcontainer 等公开治理资产虽然齐全，但自动守卫仍不够结构化。

## Goals

- 去掉 device/state 动态委托，让领域表面显式可裁决；
- 继续拆薄 runtime/status 主链热点，并收敛内部 `protocol` 术语；
- 让 README / SUPPORT / SECURITY / CODEOWNERS / quality-scale / devcontainer 与 meta guards 形成自动一致性约束。

## Non-Goals

- 不重新引入任何 compat shell、legacy constructor name 或测试专用生产冗余；
- 不重开 `LiproMqttClient` legacy naming 之外的里程碑级主题；
- 不改变对外用户功能语义。

## Acceptance Criteria

- `LiproDevice` / `DeviceState` 不再定义 `__getattr__`，并有 focused tests 锁定；
- `RuntimeOrchestrator` / `status_service` 的核心热点被拆成更小 helper；
- README / README_zh / CONTRIBUTING / SUPPORT / CODEOWNERS / quality-scale / devcontainer 被 meta guards 结构化校验；
- 相关治理真源与 phase 资产同步到 Phase 13 完成态。

## Already Fixed / Must Not Be Replanned

- `core.api.LiproClient`、`LiproProtocolFacade.get_device_list`、`LiproMqttFacade.raw_client`、`DeviceCapabilities` 已在 Phase 12 删除；
- `services/wiring.py` 已在 Phase 11 删除；
- 本 phase 不得为了测试恢复任何已删除 seam。
