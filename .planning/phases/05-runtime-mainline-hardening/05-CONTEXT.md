# Phase 05: Runtime 主链加固 - Context

**Gathered:** 2026-03-13
**Status:** Execution-aligned
**Decision mode:** North-star arbitration by default
**Source:** `.planning/PROJECT.md`, `.planning/REQUIREMENTS.md`, `.planning/ROADMAP.md`, `.planning/STATE.md`, `.planning/baseline/PUBLIC_SURFACES.md`, `.planning/baseline/DEPENDENCY_MATRIX.md`, `.planning/reviews/RESIDUAL_LEDGER.md`, `docs/NORTH_STAR_TARGET_ARCHITECTURE.md`, current coordinator/runtime slice inspection

## Phase Boundary

本阶段唯一目标：

**把 runtime plane 收紧为一条单一正式主链，让 `Coordinator` 作为唯一正式编排根、`LiproProtocolFacade` 作为唯一正式协议根，所有命令 / 刷新 / 状态应用 / MQTT 生命周期都通过显式协作端口闭环。**

本阶段必须完成：
- 维持单一 `MqttRuntime` 实例与单一 protocol-owned MQTT transport；
- 清除 runtime plane 中剩余的 no-op wiring、隐式 setter seam、双根语义与影子模块合法叙事；
- 为 command / refresh / state / mqtt 四条主链建立可执行 invariant suite；
- 把 runtime telemetry 提升为正式服务面，为 Phase 6 Assurance Plane 提供稳定输入。

本阶段明确**不做**：
- CI / pre-commit / meta guards 的体系化正式化（属于 Phase 6）；
- 全仓 file-level 治理矩阵、compat 最终删除、历史文档总收口（属于 Phase 7）。

## Current Structural Tension

当前 runtime plane 的主链裁决已经收口，但还需要把文档与验证基线完全追上真实代码：
- `connect_state_tracker` / `group_reconciler` 已接入正式 owner，不再是 no-op；
- runtime 侧不再接受 resurrect `connect-status` shadow chain，把 `query_connect_status` 重新抬成 runtime 主链；
- `CoordinatorTelemetryService` 已拥有 `signals` 快照，但 Assurance Plane 仍需补齐更完整的运行信号口径；
- `services/execution.py` 的 formal auth surface 已落地，但 residual delete gate 仍需在治理台账中收口。

## Locked Decisions

- `Coordinator` 是唯一正式 runtime orchestration root。
- `LiproProtocolFacade` 是唯一正式 protocol-plane root；MQTT transport 只能由 protocol root 持有并绑定到既有 runtime。
- 不允许恢复或新增 `mixin`、双 runtime、双 transport owner、两阶段 setter 注入、私有 backdoor。
- `StatusRuntime` 的正式职责是 status polling candidate selection / batching / execution；**connect-state 只是 runtime signal，不单独晋升为 shadow 主链。**
- group online / mesh topology reconciliation 必须通过正式 refresh surface 触发，不允许继续使用 no-op 占位。
- runtime telemetry 只能通过 `CoordinatorTelemetryService` 暴露给 control plane / diagnostics / assurance。

## Upstream Inputs

进入本 phase 前，上游已满足：
- `Phase 2 / 2.5`：`LiproProtocolFacade` 已成为唯一正式协议根；
- `Phase 3`：control plane 已收敛到 `control/`，并通过 `RuntimeAccess` 访问 runtime 状态；
- `Phase 4`：capability truth 已稳定，不再阻塞 runtime plane 的正式化。

## Downstream Handoff

- **To Phase 6**：交付稳定的 runtime telemetry surface、runtime invariants tests、可被 meta/CI 直接消费的治理信号；
- **To Phase 7**：交付已收缩的 residual 面、明确的 delete gate、以及 file-level 审计可引用的正式 runtime public surface。
