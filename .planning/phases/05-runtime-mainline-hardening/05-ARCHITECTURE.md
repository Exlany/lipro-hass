# Phase 05: Runtime 主链加固 - Architecture

**Status:** Execution-aligned
**Updated:** 2026-03-13

## Architectural Goal

让 runtime plane 从“单实例主链已出现，但仍有少量残余文档/治理偏差”的状态，升级为：

**`Coordinator` 唯一编排、`LiproProtocolFacade` 唯一协议根、runtime services 唯一正式 public surface、command/refresh/state/mqtt 全链条可验证。**

## Formal Components

### 1. `Coordinator`

**Owns**:
- canonical update loop；
- device snapshot refresh orchestration；
- MQTT setup / reconnect / shutdown orchestration；
- runtime service surface 组装；
- runtime public surface 的唯一对外入口。

**Must not own**:
- raw protocol payload normalization；
- runtime 内部子策略的重复实现；
- control plane 诊断拼装细节。

### 2. `MqttRuntime`

**Owns**:
- transport lifecycle；
- dedup / reconnect / message handling；
- 将 MQTT 消息转换为对 state/status/refresh 的显式端口调用。

**Must not own**:
- 设备快照重建；
- mesh topology refresh 本体；
- 私有 setter / coordinator backdoor。

### 3. `StatusRuntime`

**Owns**:
- REST status polling candidate selection；
- batch planning / execution；
- status query metrics；
- 向 `TuningRuntime` 暴露可调谐的查询信号。

**Must not own**:
- HA listener 更新；
- MQTT transport；
- protocol normalization；
- resurrect `connect-status` shadow chain。

### 4. `CoordinatorDeviceRefreshService`

**Owns**:
- device lookup；
- force refresh request；
- canonical full-refresh callback；
- group reconciliation 请求的正式调度入口。

### 5. `CoordinatorTelemetryService`

**Owns**:
- runtime telemetry snapshot；
- command / status / tuning / mqtt / signals 的统一暴露；
- Phase 6 governance / CI 可复用的观测面。

### 6. `CoordinatorSignalService`

**Owns**:
- runtime wiring 所需的 connect-state / group-reconciliation formal ports；
- 把 MQTT signal 统一路由到 telemetry service + refresh service；
- 避免把 coordinator 私有方法继续当作 wiring contract。

## Canonical Direction

```text
MQTT message
  -> MqttRuntime
  -> RuntimeContext(signal ports / state applier / listener notifier)
  -> CoordinatorTelemetryService / CoordinatorDeviceRefreshService
  -> Coordinator canonical refresh + state apply paths
  -> Control / Diagnostics / Assurance
```

任何 connect-state telemetry、group online topology reconcile、runtime metrics 输出，都必须沿这条主链完成。

## Phase 5 Execution Shape

### `05-01` — tighten runtime boundaries
- 把 signal ports 固化成正式 owner；
- 删除 no-op / shadow / backdoor 叙事；
- 收紧 runtime public surface 与 orchestration boundaries。

### `05-02` — invariant suite
- 建立 command / refresh / state / mqtt / telemetry 的正式 invariant tests；
- 把“单主链、不旁路、不吞异常、不双 owner、不 resurrect shadow chain”固化为测试契约。

### `05-03` — telemetry + governance handoff
- 扩展 runtime telemetry snapshot；
- 冻结 signals schema 与运行面 handoff；
- 回写 `ROADMAP / STATE / FILE_MATRIX / RESIDUAL_LEDGER / KILL_LIST`，为 Phase 6/7 提供单一真源。

## Handoff Rules

- **To Phase 6**：Phase 6 不再重新设计 runtime 结构，只负责把 Phase 5 已形成的 runtime truth 变成 guard / CI / assurance gate；
- **To Phase 7**：Phase 7 只处理 runtime residual 的最终治理与文档归一，不重新打开 runtime 主链设计争论。
