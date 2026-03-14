# Phase 05: Runtime 主链加固 - Research

**Updated:** 2026-03-13
**Status:** Execution-aligned

## What Already Landed

- MQTT 主链已从“双 runtime / 双构造来源”收敛为**单一 `MqttRuntime` + protocol-owned transport binding**；
- `CoordinatorTelemetryService`、`CoordinatorAuthService`、`CoordinatorDeviceRefreshService`、`CoordinatorMqttService` 已形成 service-oriented runtime surface；
- `connect_state_tracker` / `group_reconciler` 已不再是 no-op，正式接到 telemetry + canonical refresh path；
- dead shadow chain 已删除：`status_strategy.py`、`state_batch_runtime.py`、`group_lookup_runtime.py`、`room_sync_runtime.py`、`device_registry_sync.py` 不再保留生产合法叙事；
- `TuningRuntime` 已收缩为主链在用的批次/确认调优面，不再挂着一套未接线的影子分支。

## What Is Still Missing

### 1. Phase 文档仍在讲旧设计
- Phase 05 planning package 里仍有 `connect-status` 回接主链、no-op hooks、shadow chain 合法化等旧叙事；
- 若不修正，Phase 6/7 会继续被错误前提污染。

### 2. runtime invariants 还需要作为正式验收包收口
- 关键 runtime tests 已存在并通过核心子集验证；
- 但还需要完整 summary / validation / governance handoff，才能把 Phase 5 从“代码已落地”升级为“正式完成”。

### 3. Assurance Plane 仍需补齐更完整的运行信号口径
- 当前 `signals` 已覆盖 connect-state / group-reconciliation；
- Phase 6 仍需把 auth recovery、MQTT reconnect、command confirmation、refresh latency 一并纳入 assurance taxonomy。

## Arbitration

### A. 不要 resurrect `connect-status` shadow chain
- `query_connect_status` 继续留在 protocol/API slice，作为 vendor endpoint 能力存在；
- runtime 主链不重新引入 `status_strategy` / `connect-status fallback` 的影子故事线；
- Phase 5 的裁决是**删除 dead branch**，而不是把 dead branch 合法化。

### B. `group_reconciler` 的正式 owner 就是 refresh surface
- 最优做法不是在 MQTT runtime 内直接刷新设备列表，而是：
- 通过 `CoordinatorDeviceRefreshService.request_group_reconciliation()` 请求 canonical refresh；
- 再由 `Coordinator` 统一完成设备快照重建与订阅同步。

### C. runtime telemetry 必须停留在正式 service plane
- `CoordinatorTelemetryService` 是唯一正式 runtime observability surface；
- `CoordinatorSignalService` 只是 runtime wiring 端口，不额外创造第二套 consumer-facing truth。

## Recommended Execution Shape

- `05-01`：固化 formal signal ports、收紧 runtime wiring / boundaries；
- `05-02`：补齐 invariant suite，阻断 shadow chain 回流；
- `05-03`：冻结 telemetry snapshot schema，并把治理/validation handoff 落表。
