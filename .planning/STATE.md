---
gsd_state_version: 1.0
milestone: v1.1
milestone_name: protocol-fidelity-operability
status: active
last_updated: "2026-03-14T11:20:19Z"
progress:
  total_phases: 9
  completed_phases: 8
  total_plans: 31
  completed_plans: 26
---

# Project State

## Project Reference

See: `.planning/PROJECT.md`

**Current milestone:** `v1.1 Protocol Fidelity & Operability`
**Core value:** 在既有北极星单一主链基础上，把 fidelity / enforcement / telemetry / replay / AI-debug evidence 做成下一层正式能力。
**Current mode:** `Phase 11 replanning`；已完成 control-router formalization 子成果，现正把全仓复审暴露的 residual / runtime / entity / governance gaps 纳入 addendum plans。

## Current Position

- `v1.0` 已归档到 `.planning/MILESTONES.md` 与 `.planning/milestones/v1.0-*.md`
- `v1.1` 已完成里程碑初始化、研究收敛、requirements/roadmap 落表
- `Phase 7.1` 已完成：boundary inventory / decoder skeleton / representative REST+MQTT pipeline / replay-ready fixtures / governance handoff
- `Phase 7.2` 已完成：architecture policy baseline、shared policy helpers、architecture script、meta guards refactor、CI fail-fast ordering 与 verification evidence 已落地
- `Phase 7.3` 已完成：exporter formal home、真实运行信号、consumer convergence、black-box evidence 与治理回写均已落地
- `Phase 7.4` 已完成：authority-indexed replay manifests、deterministic driver、REST/MQTT replay assertions、replay run summary 与 meta guards 已形成 assurance 资产
- `Phase 7.5` 已完成：governance matrix sync、`V1_1_EVIDENCE_INDEX.md`、`07.5-SUMMARY.md`、residual/delete gate closeout arbitration 已落地
- `Phase 8` 已完成：AI debug evidence pack formal home、唯一 exporter entrypoint、integration/meta guards 与 governance handoff 已全部落地
- `Phase 9` 已完成：production residual closure + `09-04` / `09-05` legacy test convergence addendum 均已落地；API mega-test、runtime/platform/integration tests 与治理文档已对齐到正式架构
- `Phase 10` 已完成：`rest.device-list` / `rest.device-status` / `rest.mesh-group-status` boundary family 与 canonical contracts 已正式落地，`AuthSessionSnapshot` 成为 formal auth/session truth，`core/__init__.py` 已不再导出 `Coordinator`，governance / replay / meta guards 已同步收口
- `Phase 11` 第一波已完成：`control/service_router.py` 已成为真实 formal router，仓库 tests 已切到 formal seam，`services/wiring.py` 已降为显式 compat shell，治理与验证资产已同步回写；当前正基于全仓复审结果扩展 addendum plans

## Active Milestone Scope

- `Phase 7.1`：Protocol Boundary Schema/Decoder 收口
- `Phase 7.2`：Architecture Enforcement 加固
- `Phase 7.3`：Runtime Telemetry Exporter 正式化
- `Phase 7.4`：Protocol Replay / Simulator Harness 建立
- `Phase 7.5`：Integration / Governance / Verification 收尾
- `Phase 8`：AI Debug Evidence Pack
- `Phase 9`：Residual Surface Closure
- `Phase 10`：API Drift Isolation & Core Boundary Prep
- `Phase 11`：Control Router Formalization & Wiring Residual Demotion（expanded replanning）

## Carry-Forward Truths

- 正式协议根仍是 `LiproProtocolFacade`
- 正式 runtime root 仍是 `Coordinator`
- `Coordinator` 的正式 home 继续固定在 `custom_components/lipro/coordinator_entry.py`
- compat/residual 仍必须显式登记，不能重新合法化
- canonical normalization 仍必须在 protocol boundary 完成
- telemetry/replay/evidence 都只能 pull 正式真源，不得反向定义第二套事实
- 未来 CLI / 其他宿主若要复用，只能建立在 host-neutral boundary/auth/device contracts 之上，而不是把 HA runtime 抽成 second root

## Cross-Phase Arbitration (7.3-11)

1. `07.3` 只锁定 telemetry truth（fields / redaction / cardinality / timestamp / pseudo-id compatibility）
2. `07.4` 只锁定 replay truth（manifests / deterministic driver / replay assertions / run summary）
3. `07.5` 只锁定 governance closeout（matrices / evidence index / residual / delete gate）
4. `08` 只锁定 AI debug packaging（collector / schema / exporter entrypoint）
5. `09` 已完整完成：production residual surface closure 与 `09-04` / `09-05` test convergence addendum 已统一收敛到相同 formal surface / shared harness / explicit compat seam
6. `10` 已完整完成：boundary contract closure、host-neutral auth/result contracts、HA adapter 降耦与文档/治理同步均已落地；仍不把 physical shared core 抽离提升为正式里程碑目标
7. `11` 已完成第一波：control-plane formal router ownership、test-truth alignment、compat shell demotion 与 governance closeout 已统一收敛；当前已接受 full-repo audit expansion 并进入 addendum planning

## Accumulated Context

### Roadmap Evolution

- Phase 10 executed and completed: API Drift Isolation & Core Boundary Prep
- Phase 11 executed subset completed: Control Router Formalization & Wiring Residual Demotion
- Phase 11 reopened for audit-expansion planning

## Governance Truth Sources

1. `docs/NORTH_STAR_TARGET_ARCHITECTURE.md`
2. `.planning/MILESTONES.md`
3. `.planning/ROADMAP.md`
4. `.planning/REQUIREMENTS.md`
5. `.planning/STATE.md`
6. `.planning/baseline/*.md`
7. `.planning/reviews/*.md`
8. `docs/developer_architecture.md`
9. `AGENTS.md`
10. `CLAUDE.md`（若使用 Claude Code）

## Recommended Next Command

1. `$gsd-execute-phase 11` —— 执行新增 11-04 ~ 11-08 addendum plans
2. `$gsd-progress` —— 查看当前 expanded Phase 11 进度与阻塞
3. `uv run pytest -q` —— 若需要再确认当前基线稳定性，可重跑全量回归

## Session Continuity

If resuming, read in this order:
1. `docs/NORTH_STAR_TARGET_ARCHITECTURE.md`
2. `.planning/MILESTONES.md`
3. `.planning/milestones/v1.0-ROADMAP.md`
4. `.planning/milestones/v1.0-REQUIREMENTS.md`
5. `.planning/PROJECT.md`
6. `.planning/REQUIREMENTS.md`
7. `.planning/ROADMAP.md`
8. `.planning/STATE.md`
9. `.planning/baseline/*.md`
10. `.planning/reviews/*.md`
11. `AGENTS.md`
12. `CLAUDE.md`（若使用 Claude Code）
13. `docs/developer_architecture.md`
