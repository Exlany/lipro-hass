---
gsd_state_version: 1.0
milestone: v1.1
milestone_name: protocol-fidelity-operability
status: active
last_updated: "2026-03-14T04:55:00Z"
progress:
  total_phases: 8
  completed_phases: 7
  total_plans: 23
  completed_plans: 19
---

# Project State

## Project Reference

See: `.planning/PROJECT.md`

**Current milestone:** `v1.1 Protocol Fidelity & Operability`
**Core value:** 在既有北极星单一主链基础上，把 fidelity / enforcement / telemetry / replay / AI-debug evidence 做成下一层正式能力。
**Current mode:** `Phase 10 planned`；计划、研究、验证策略与执行波次已落盘，等待执行。

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
- `Phase 10` 已完成计划：研究、架构裁决、Nyquist validation 与 4 份执行计划均已生成；目标是继续把逆向 API 漂移隔离在 protocol boundary 内，并在不抽离 shared SDK 的前提下收窄 HA adapter 对 concrete protocol/runtime shape 的依赖

## Active Milestone Scope

- `Phase 7.1`：Protocol Boundary Schema/Decoder 收口
- `Phase 7.2`：Architecture Enforcement 加固
- `Phase 7.3`：Runtime Telemetry Exporter 正式化
- `Phase 7.4`：Protocol Replay / Simulator Harness 建立
- `Phase 7.5`：Integration / Governance / Verification 收尾
- `Phase 8`：AI Debug Evidence Pack
- `Phase 9`：Residual Surface Closure
- `Phase 10`：API Drift Isolation & Core Boundary Prep

## Carry-Forward Truths

- 正式协议根仍是 `LiproProtocolFacade`
- 正式 runtime root 仍是 `Coordinator`
- control / domain / assurance 平面裁决不变
- compat/residual 仍必须显式登记，不能重新合法化
- canonical normalization 仍必须在 protocol boundary 完成
- telemetry/replay/evidence 都只能 pull 正式真源，不得反向定义第二套事实

## Cross-Phase Arbitration (7.3-10)

1. `07.3` 只锁定 telemetry truth（fields / redaction / cardinality / timestamp / pseudo-id compatibility）
2. `07.4` 只锁定 replay truth（manifests / deterministic driver / replay assertions / run summary）
3. `07.5` 只锁定 governance closeout（matrices / evidence index / residual / delete gate）
4. `08` 只锁定 AI debug packaging（collector / schema / exporter entrypoint）
5. `09` 已完整完成：production residual surface closure 与 `09-04` / `09-05` test convergence addendum 已统一收敛到相同 formal surface / shared harness / explicit compat seam
6. `10` 只锁定 API drift isolation / core-boundary prep：boundary contract closure、host-neutral auth/result contracts、HA adapter 降耦与文档/治理同步；不把 physical shared core 抽离提升为正式里程碑目标

## Accumulated Context

### Roadmap Evolution

- Phase 10 added: API Drift Isolation & Core Boundary Prep

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
10. `agent.md`

## Recommended Next Command

1. `$gsd-execute-phase 10` —— 按 4 个波次执行 API drift isolation / core-boundary prep 计划
2. `$gsd-verify-work 9` —— 若仍需先复核 Phase 9 最终 UAT 与 evidence handoff
3. `uv run pytest -q` —— 在后续任何文档改动后复跑全量回归确认无漂移

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
9. `.planning/research/SUMMARY.md`
10. `.planning/phases/07.5-integration-governance-verification-closeout/`
11. `.planning/phases/08-ai-debug-evidence-pack/`
12. `.planning/phases/09-residual-surface-closure/`
13. `.planning/phases/10-api-drift-isolation-core-boundary-prep/`
