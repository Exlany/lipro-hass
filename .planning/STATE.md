---
gsd_state_version: 1.0
milestone: v1.0
milestone_name: milestone
status: in_progress
last_updated: "2026-03-12T23:47:23Z"
progress:
  total_phases: 10
  completed_phases: 6
  total_plans: 21
  completed_plans: 19
---

# Project State

## Project Reference

See: `.planning/PROJECT.md` (rebuilt 2026-03-12)

**Core value:** 把 `lipro-hass` 重建为面向 Home Assistant 的北极星终态架构，而不是继续由历史兼容结构定义边界。
**Current mode:** `Phase 4 / 04-01 executed + governance sync`，用于把 capability truth 从 device helper 散点收敛到正式 domain root，并为 `04-02 / 04-03 / Phase 5+` 提供单一能力真源。

## Baseline Dashboard

- **Research pack**: `5/5` 已就绪
- **Baseline asset pack**: `5/5` 已在 `Phase 1.5` 正式落地并经 meta guards 验证
- **v1 requirements**: `40`
- **roadmap phases**: `10`（含 `1.5 / 2.5 / 2.6`）
- **Python files**: `406`
- **治理矩阵覆盖**: 当前仍以 cluster-level 为主，但 `Phase 2 / 2.5 / 2.6 / 3` 已补入关键 slice closeout
- **残留 burn-down**: 已形成 ledger / kill / owner 机制，`services/wiring.py`、私有 auth seam、remote advisory naming cleanup 已进入显式 residual
- **Phase 1 status**: `Completed + validated (2/2)`
- **Phase 1.5 status**: `Completed + validated (3/3)`
- **Phase 2 status**: `Completed + validated (4/4)`
- **Phase 2.5 status**: `Completed + validated (3/3)`
- **Phase 2.6 status**: `Completed + validated (3/3)`
- **Phase 3 status**: `Completed + validated (3/3)`
- **Phase 4 status**: `In progress (1/3 planned, 04-01 complete)`

## Current Position

- `.planning/ROADMAP.md`、治理台账与 `Phase 4` planning package 已同步建立，`04-01` 不再只是路线图占位。
- `Phase 1 / 1.5 / 2 / 2.5 / 2.6 / 3` 的 summary / validation / governance 口径继续保持统一，没有回退。
- `Phase 4 / 04-01` 已把 `CapabilityRegistry / CapabilitySnapshot` 落到 `custom_components/lipro/core/capability/`，并让 `core/device` 通过 compat bridge 接回正式 domain truth。
- `Capability duplication` residual 仍未关闭，但它已从“没有正式根”收敛为“消费者迁移与旧 helper 清退未完成”。
- 当前剩余的结构性工作重心已经前移到 `Phase 4 / 5 / 6 / 7`：capability projection migration、runtime invariants、assurance gates、全仓零残留清扫。

## Architectural Position

当前项目的北极星裁决已固定为：

- **终态协议根**：`LiproProtocolFacade`
- **Phase 2 正式 REST 子门面**：`LiproRestFacade`
- **MQTT 终态位置**：`LiproMqttFacade` 作为统一协议根下的 child façade
- **终态控制面 home**：`custom_components/lipro/control/`
- **控制面正式组件**：`EntryLifecycleController`、`ServiceRegistry`、`DiagnosticsSurface`、`SystemHealthSurface`、`RuntimeAccess`
- **终态领域能力真源**：`custom_components/lipro/core/capability/` 中的 `CapabilityRegistry / CapabilitySnapshot`
- **外部边界真源**：`.planning/baseline/AUTHORITY_MATRIX.md` + `.planning/phases/02.6-external-boundary-convergence/02.6-BOUNDARY-INVENTORY.md` + `tests/fixtures/external_boundaries/**`
- **`LiproClient` 定性**：不是终态正式设计，只允许作为显式 compat shell；最终删除属于 `Phase 7`
- **新架构标准**：不再承认 `mixin` 作为正式设计模式
- **终态 capability home**：`custom_components/lipro/core/capability/`
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

## Active Residuals

- `custom_components/lipro/core/device/capabilities.py`：仍保留 compat bridge 语义，删除进入 `04-03 / Phase 7`
- `custom_components/lipro/core/device/state_accessors.py` 中的 `supports_color_temp`：仍是 domain duplication 残留，待 `04-02 / 04-03` 收口
- `custom_components/lipro/services/wiring.py`：仍是 legacy implementation carrier，但不再是正式 service root；删除进入 `Phase 7`
- `custom_components/lipro/services/execution.py` 的 coordinator 私有 auth seam：仍待在 `Phase 5 / 7` 用正式 runtime/auth contract 取代
- firmware remote advisory naming cleanup：authority 已正确，但命名仍需在 `Phase 7` 清理为更诚实的术语
- `FILE_MATRIX` 仍需在 `Phase 7` 升级到真正 file-level `406/406`

## Governance Truth Sources

- `.planning/baseline/TARGET_TOPOLOGY.md`
- `.planning/baseline/DEPENDENCY_MATRIX.md`
- `.planning/baseline/PUBLIC_SURFACES.md`
- `.planning/baseline/VERIFICATION_MATRIX.md`
- `.planning/baseline/AUTHORITY_MATRIX.md`
- `.planning/reviews/FILE_MATRIX.md`
- `.planning/reviews/RESIDUAL_LEDGER.md`
- `.planning/reviews/KILL_LIST.md`

## Recommended Next Command

优先继续：

1. `$gsd-execute-phase 4` —— 继续 `04-02` 的 platform / entity projection migration
2. `$gsd-validate-phase 4` —— 在 `04-02 / 04-03` 完成后补齐 capability phase 验证
3. `$gsd-plan-phase 5` —— 规划 runtime invariants、runtime public surface 与 auth seam hardening
4. `$gsd-plan-phase 7` —— 准备 compat/legacy/shadow/docs 的最终 kill sweep

## Session Continuity

If resuming, read in this order:
1. `docs/NORTH_STAR_TARGET_ARCHITECTURE.md`
2. `docs/NORTH_STAR_EXECUTION_PLAN_2026-03-12.md`
3. `.planning/PROJECT.md`
4. `.planning/research/SUMMARY.md`
5. `.planning/baseline/TARGET_TOPOLOGY.md`
6. `.planning/baseline/DEPENDENCY_MATRIX.md`
7. `.planning/baseline/PUBLIC_SURFACES.md`
8. `.planning/baseline/VERIFICATION_MATRIX.md`
9. `.planning/baseline/AUTHORITY_MATRIX.md`
10. `.planning/REQUIREMENTS.md`
11. `.planning/ROADMAP.md`
12. `.planning/reviews/FILE_MATRIX.md`
13. `.planning/reviews/RESIDUAL_LEDGER.md`
14. `.planning/reviews/KILL_LIST.md`
15. `.planning/phases/01-protocol-contract-baseline/`
16. `.planning/phases/01.5-north-star-baseline-assets/`
17. `.planning/phases/02-api-client-de-mixin/`
18. `.planning/phases/02.5-protocol-root-unification/`
19. `.planning/phases/02.6-external-boundary-convergence/`
20. `.planning/phases/03-control-plane-convergence/`
21. `.planning/phases/04-capability-model-unification/`
