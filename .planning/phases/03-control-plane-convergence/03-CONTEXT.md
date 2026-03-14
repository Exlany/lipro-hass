# Phase 03: Control Plane 收敛 - Context

**Gathered:** 2026-03-12
**Status:** Completed / validated (historical planning context retained for audit)
**Decision mode:** North-star arbitration by default
**Source:** `.planning/PROJECT.md`, `.planning/REQUIREMENTS.md`, `.planning/ROADMAP.md`, `.planning/STATE.md`, `.planning/codebase/ARCHITECTURE.md`, `.planning/codebase/CONCERNS.md`, `.planning/codebase/STRUCTURE.md`, `docs/NORTH_STAR_TARGET_ARCHITECTURE.md`, `.planning/phases/01-protocol-contract-baseline/01-RESEARCH.md`, `.planning/phases/02-api-client-de-mixin/02-ARCHITECTURE.md`, `.planning/phases/02.6-external-boundary-convergence/02.6-CONTEXT.md`, `.planning/phases/02.6-external-boundary-convergence/02.6-ARCHITECTURE.md`, current control-plane slice inspection

<domain>
## Phase Boundary

本阶段的边界同样必须先锁死，再允许执行：

**把 `lipro-hass` 的 lifecycle、flow、services、diagnostics、system health 收敛为单一正式 control plane，并且把它与 runtime plane 的交互从散落 backdoor 改造成稳定 public surface。**

本阶段必须完成：
- 从全仓治理视角，按 control-plane lens 审视 `.planning/REQUIREMENTS.md` 记录的 `378` 个 Python 文件，并把与 control plane 有关的文件纳入 `保留 / 重构 / 迁移适配 / 删除` 台账
- 明确交付 `EntryLifecycleController / ServiceRegistry / DiagnosticsSurface / SystemHealthSurface`
- 让 `__init__.py`、`config_flow.py`、`flow/**`、`services/**`、`diagnostics.py`、`system_health.py` 不再各自讲一套故事，而是围绕同一 control-plane 目标拓扑协作
- 把 control → runtime 的接缝收口为稳定 public surface / typed access contract，不再散落读取 `entry.runtime_data`、`coordinator.devices`、`mqtt_service.connected` 等内部结构
- 让测试围绕正式 control public surfaces、redaction、lifecycle guards，而不是围绕私有 helper 与私有 handler 导入

本阶段明确**不做**：
- protocol plane 的统一协议根落地（Phase 2 / 2.5 已定义）
- domain capability model 收敛（属于 Phase 4）
- runtime invariant 与 coordinator 正式 public surface 最终化（属于 Phase 5）
- assurance plane 的完整 guard rail / CI 体系化落地（属于 Phase 6）
- compat / 影子模块 / 历史残留的全仓清零（属于 Phase 7）

换言之，Phase 3 可以**全仓审视**，但只能**收敛 control plane 本身**；其余问题必须回写台账并 defer，不能把本 phase 膨胀成“全仓一次性重构”。
</domain>

<upstream_inputs>
## Required Upstream Inputs

以下上游输入曾是 Phase 3 进入执行态前的阻塞条件；截至 2026-03-12，均已满足并形成正式 handoff：

- `.planning/phases/02.6-external-boundary-convergence/02.6-CONTEXT.md`
- `.planning/phases/02.6-external-boundary-convergence/02.6-RESEARCH.md`
- `.planning/phases/02.6-external-boundary-convergence/02.6-ARCHITECTURE.md`
- `.planning/phases/02.6-external-boundary-convergence/02.6-BOUNDARY-INVENTORY.md`
- `.planning/phases/02.6-external-boundary-convergence/02.6-VALIDATION.md`
- `02.6-01/02/03-SUMMARY.md` 与执行后沉淀的 external-boundary outputs
- `Phase 1` 与 `Phase 1.5` 的基准资产收尾结果，确保 control plane 依赖的 baseline truth 已落表

上述输入现均已满足；本文件保留的是 pre-execution context，当前正式完成态以 `03-VALIDATION.md` 与 `03-01/02/03-SUMMARY.md` 为准。
</upstream_inputs>

<decisions>
## Implementation Decisions

### Locked Decisions
- `EntryLifecycleController / ServiceRegistry / DiagnosticsSurface / SystemHealthSurface` 是本阶段不可裁撤的正式交付物
- `__init__.py`、`diagnostics.py`、`system_health.py` 必须退化为 Home Assistant 入口适配薄层；正式控制逻辑必须下沉到明确 control-plane 组件
- `config_flow.py` 与 `flow/**` 属于 control plane 的用户入口面，不能再通过散落 helper 暗中塑造第二套 lifecycle 规则
- `custom_components/lipro/services/wiring.py` 不能继续作为终态控制面根；它只能被拆分、降级或删除，不能被“整理后继续主导正式边界”
- `diagnostics.py` 与 `system_health.py` 不得继续直接摸 runtime 内脏；它们必须通过稳定 runtime access contracts / read models 获取数据
- Phase 3 必须消费 Phase 2.6 已 formalize 的 `share / firmware / support payload / external boundary` 结果，不能在控制面重新定义这些边界
- control-plane read models 不能演化成第二套 capability truth；能力语义仍由 Phase 4 的 capability model 统一裁决
- control-owned runtime access contracts 只是在控制面侧建立稳定接缝，不能演化成与 Phase 5 `runtime public surface` 竞争的第二套运行时根
- service registration、developer/debug gating、service routing、listener lifecycle 必须只有一处正式 owner
- tests 必须面向 control public surfaces；`_async_handle_*` 一类私有 handler 不能继续被当作稳定外部接口
- 本阶段必须同步更新 `FILE_MATRIX.md`、`RESIDUAL_LEDGER.md`、`KILL_LIST.md`、`PUBLIC_SURFACES.md`、`DEPENDENCY_MATRIX.md`、`VERIFICATION_MATRIX.md`
- 新架构不承认 `mixin` 作为正式模式；control plane 也必须遵循显式组合与单一主链

### Claude's Discretion
- control-plane 内部正式模块的确切命名（例如 `control/` 子包下的 `runtime_access.py`、`service_router.py`）可按实现可读性裁决
- control → runtime 的适配层是落成一组 ports、facade adapters 还是 read-model providers，只要 public surface 单一、可测、可审计即可
- `services/**` 中哪些 handler 继续保留原路径、哪些迁入新的 control package，可由执行期结合 direct consumers 决定
</decisions>

<specifics>
## Specific Ideas

- 以 `custom_components/lipro/control/` 作为 control plane 的正式内部落点：HA 规定的根模块继续存在，但只保留 adapter 职责
- 把 `entry_auth.py`、`entry_options.py`、`runtime_infra.py`、`domain_data.py`、`coordinator_entry.py` 围绕 `EntryLifecycleController` 重组，而不是继续由 `__init__.py` 横向吸纳细节
- 把 `services/contracts.py`、`registry.py`、`registrations.py` 变成 `ServiceRegistry` 的正式真源；把 `wiring.py` 拆成命名化 collaborators，而不是保留 496 行热点
- 把 diagnostics / system health 统一成 support surface，复用同一 redaction policy 与 runtime read model，而不是各自读取 coordinator 细节
- 把 `tests/flows`、`tests/services`、`tests/core/test_diagnostics.py`、`tests/core/test_system_health.py`、`tests/core/test_init.py` 等整理成 control-plane 正式验收面
</specifics>

<code_context>
## Existing Code Insights

### Reusable Assets
- `custom_components/lipro/entry_auth.py`、`entry_options.py`、`runtime_infra.py`、`domain_data.py`、`coordinator_entry.py`：已经具备 lifecycle 分工雏形，可重组为 controller collaborators
- `custom_components/lipro/services/contracts.py`、`registry.py`、`registrations.py`：具备成为正式 `ServiceRegistry` 真源的基础
- `custom_components/lipro/services/execution.py`、`device_lookup.py`、`errors.py`：适合作为 service surface 的明确协作对象，而不是继续被 mega wiring 吞没
- `tests/flows/*.py`、`tests/services/*.py`、`tests/core/test_diagnostics.py`、`tests/core/test_system_health.py`：具备成为 Phase 3 最小验收面的基础

### Established Problems
- `custom_components/lipro/services/wiring.py` 目前约 `496` 行，集中了 runtime lookup、service registration、debug gating、error wrapping、handler routing，属于控制面热点与拆分优先级第一名
- `custom_components/lipro/diagnostics.py` 与 `custom_components/lipro/system_health.py` 仍直接读取 `entry.runtime_data`、`coordinator.devices`、`mqtt_service.connected`
- `custom_components/lipro/__init__.py` 仍承担过多 setup/unload/service sync 细节，未退化为薄 adapter
- 部分 tests 仍围绕私有 handler 与内部结构打补丁，说明正式 public surface 尚未形成

### Integration Points
- 本阶段直接承接 Phase 2 / 2.5 的 protocol-plane 正式化成果，但不回头重做协议根
- 本阶段输出的 control contracts 会成为 Phase 4 domain plane 与 Phase 5 runtime plane 的稳定上游消费者约束
- 本阶段的 residual / kill / verification 回写将决定 Phase 6 guard rails 与 Phase 7 清零成本
</code_context>

<deferred>
## Deferred Ideas

- `LiproProtocolFacade` 下的 REST / MQTT 统一对外终态
- runtime plane 正式 public surface 的最终命名与全面一体化
- capability registry / capability snapshot 终态建模
- architecture enforcement / CI guard rails 的全量落地
- compat shell、影子模块与历史文档的最终删除清零

这些都需要在台账中被看见，但不能被本阶段吞并。
</deferred>

---
*Phase: 03-control-plane-convergence*
*Context gathered: 2026-03-12 via north-star arbitration refresh*
