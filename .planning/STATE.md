---
gsd_state_version: 1.0
milestone: v1.0
milestone_name: milestone
status: complete
last_updated: "2026-03-13T03:04:07Z"
progress:
  total_phases: 10
  completed_phases: 10
  total_plans: 32
  completed_plans: 32
---

# Project State

## Project Reference

See: `.planning/PROJECT.md` (rebuilt 2026-03-12)

**Core value:** 把 `lipro-hass` 重建为面向 Home Assistant 的北极星终态架构，而不是继续由历史兼容结构定义边界。
**Current mode:** `Phase 1-7 complete`，正式主链、assurance plane 与 repo governance 已全部收口，后续进入 steady-state governance / next-milestone mode。

## Baseline Dashboard

- **Research pack**: `5/5` 已就绪
- **Baseline asset pack**: `5/5` 已在 `Phase 1.5` 正式落地并经 meta guards 验证
- **v1 requirements**: `40/40 complete`
- **roadmap phases**: `10/10 complete`（含 `1.5 / 2.5 / 2.6`）
- **roadmap plans**: `32/32 complete`
- **Python files**: `404`
- **治理矩阵覆盖**: `FILE_MATRIX` 已是 file-level `404/404` 权威视图
- **残留 burn-down**: 已形成 ledger / kill / owner 机制；所有活跃 residual 均为显式 compat / carrier / naming 项，不再存在未登记 shadow debt
- **Phase 1 status**: `Completed + validated (2/2)`
- **Phase 1.5 status**: `Completed + validated (3/3)`
- **Phase 2 status**: `Completed + validated (4/4)`
- **Phase 2.5 status**: `Completed + validated (3/3)`
- **Phase 2.6 status**: `Completed + validated (3/3)`
- **Phase 3 status**: `Completed + validated (3/3)`
- **Phase 4 status**: `Completed + validated (3/3)`
- **Phase 5 status**: `Completed + validated (3/3)`
- **Phase 6 status**: `Completed + validated (4/4)`
- **Phase 7 status**: `Completed + validated (4/4)`

## Current Position

- `Phase 5 / 6 / 7` planning packages 已全部补齐 `SUMMARY / VALIDATION` 与治理回写。
- runtime 主链现在以 `Coordinator` + formal service surfaces + `CoordinatorSignalService` 作为唯一正式运行面叙事。
- Assurance Plane 已通过 taxonomy / checker / meta guards / CI gates 固化为正式第五平面。
- repository closeout 已完成：`FILE_MATRIX`、`RESIDUAL_LEDGER`、`KILL_LIST`、活跃文档 authority、`AGENTS.md` / `agent.md`、终态报告已统一口径。

## Architectural Position

当前项目的北极星裁决已固定为：

- **终态协议根**：`LiproProtocolFacade`
- **Phase 2 正式 REST 子门面**：`LiproRestFacade`
- **MQTT 终态位置**：`LiproMqttFacade` 作为统一协议根下的 child façade
- **终态控制面 home**：`custom_components/lipro/control/`
- **控制面正式组件**：`EntryLifecycleController`、`ServiceRegistry`、`ServiceRouter`、`DiagnosticsSurface`、`SystemHealthSurface`、`RuntimeAccess`
- **终态领域能力真源**：`custom_components/lipro/core/capability/` 中的 `CapabilityRegistry / CapabilitySnapshot`
- **终态运行面约束**：`Coordinator` 是唯一 orchestration root，`MqttRuntime` / `StatusRuntime` / `CommandRuntime` / `TuningRuntime` 只通过 formal service ports 协作
- **外部边界真源**：`.planning/baseline/AUTHORITY_MATRIX.md` + `.planning/phases/02.6-external-boundary-convergence/02.6-BOUNDARY-INVENTORY.md` + `tests/fixtures/external_boundaries/**`
- **`LiproClient` / `LiproMqttClient` 定性**：不是终态正式设计，只允许作为显式 compat shell / export seam
- **新架构标准**：不再承认 `mixin` 作为正式设计模式
- **协议边界责任**：canonical normalization 必须在 protocol plane 或 registered external-boundary family 完成；上层不消费 raw vendor shape

## Completed Workstreams

1. **Phase 1：协议契约基线**
   - golden fixtures / contract matrix / canonical snapshots 已落地
   - immutable constraints ledger 与 downstream handoff 已完成

2. **Phase 1.5：北极星基准资产化**
   - baseline asset pack、seed guards、verification matrix 已成为正式 acceptance truth
   - downstream phases 只能引用、实例化或扩展这些基线，不能平行改写

3. **Phase 2 / 2.5：协议平面重建与统一**
   - `LiproRestFacade` 已确立为正式 REST 子门面
   - `LiproProtocolFacade` 已确立为唯一正式协议根
   - `LiproClient` / `LiproMqttClient` 已降级为显式 compat shells

4. **Phase 2.6：外部边界收口**
   - external-boundary inventory / authority / fixtures / meta drift audits 已正式落地
   - firmware 的 `local trust root` 与 `remote advisory` 已明确分责

5. **Phase 3：Control Plane 收敛**
   - `custom_components/lipro/control/` 已成为正式控制面载体
   - `__init__.py`、`diagnostics.py`、`system_health.py` 只保留 HA adapter 职责
   - control → runtime 访问已集中到 `control/runtime_access.py`

6. **Phase 4：Capability Model 统一**
   - `custom_components/lipro/core/capability/` 已成为正式 capability home
   - platform/entity/device/state 全部围绕 canonical capability truth 收口
   - `DeviceCapabilities` 已降级为显式 compat alias，并登记 delete gate

7. **Phase 5：Runtime 主链加固**
   - signal ports 已 formalize，runtime wiring 不再依赖 coordinator 私有信号回调
   - dead/shadow runtime chain 已清退，不再给 `connect-status` shadow story 留合法入口
   - runtime invariants、telemetry snapshot、signal schema 已形成正式 handoff

8. **Phase 6：Assurance Plane 正式化**
   - assurance taxonomy、governance checker、meta guards、CI/pre-commit gates 已全部落地
   - runtime evidence 已通过 snapshot / integration / targeted regression 证明
   - 结构退化现在先于功能回归被发现

9. **Phase 7：全仓治理与零残留收尾**
   - `FILE_MATRIX`、`RESIDUAL_LEDGER`、`KILL_LIST`、state/roadmap/requirements 已统一
   - codebase map 与历史执行文档已明确降级为 snapshot / archive
   - `AGENTS.md` / `agent.md` / final closeout report 已给出单一执行入口与单一 authority 顺序

## Intentional Residuals

以下 residual 仍然存在，但都已显式登记、可计数、不可反向定义正式架构：

- `custom_components/lipro/core/api/client.py` 与 `custom_components/lipro/core/mqtt/__init__.py`：compat shell / export seam，仅用于历史 public-name 兼容
- `custom_components/lipro/core/device/capabilities.py`：`DeviceCapabilities` compat alias
- `custom_components/lipro/services/wiring.py`：legacy implementation carrier / patch seam
- firmware remote advisory naming：authority 已正确，术语仍可在后续演进中继续诚实化

## Governance Truth Sources

- `docs/NORTH_STAR_TARGET_ARCHITECTURE.md`
- `.planning/ROADMAP.md`
- `.planning/REQUIREMENTS.md`
- `.planning/STATE.md`
- `.planning/baseline/TARGET_TOPOLOGY.md`
- `.planning/baseline/DEPENDENCY_MATRIX.md`
- `.planning/baseline/PUBLIC_SURFACES.md`
- `.planning/baseline/VERIFICATION_MATRIX.md`
- `.planning/baseline/AUTHORITY_MATRIX.md`
- `.planning/reviews/FILE_MATRIX.md`
- `.planning/reviews/RESIDUAL_LEDGER.md`
- `.planning/reviews/KILL_LIST.md`
- `docs/developer_architecture.md`
- `AGENTS.md`
- `agent.md`

## Recommended Next Command

优先继续：

1. `$gsd-new-milestone` —— 基于当前终态基线开启下一个演进里程碑
2. `$gsd-plan-phase <X.Y>` —— 以小数 phase 方式推进新增演进项（schema / stronger enforcement / telemetry exporter / simulator）
3. `$gsd-verify-work` —— 对当前终态做一次交互式 UAT 复核

## Session Continuity

If resuming, read in this order:
1. `docs/NORTH_STAR_TARGET_ARCHITECTURE.md`
2. `docs/FINAL_CLOSEOUT_REPORT_2026-03-13.md`
3. `.planning/PROJECT.md`
4. `.planning/ROADMAP.md`
5. `.planning/REQUIREMENTS.md`
6. `.planning/STATE.md`
7. `.planning/baseline/TARGET_TOPOLOGY.md`
8. `.planning/baseline/DEPENDENCY_MATRIX.md`
9. `.planning/baseline/PUBLIC_SURFACES.md`
10. `.planning/baseline/VERIFICATION_MATRIX.md`
11. `.planning/baseline/AUTHORITY_MATRIX.md`
12. `.planning/reviews/FILE_MATRIX.md`
13. `.planning/reviews/RESIDUAL_LEDGER.md`
14. `.planning/reviews/KILL_LIST.md`
15. `.planning/phases/05-runtime-mainline-hardening/`
16. `.planning/phases/06-assurance-plane-formalization/`
17. `.planning/phases/07-repo-governance-zero-residual-closeout/`
18. `docs/developer_architecture.md`
19. `AGENTS.md`
20. `agent.md`
