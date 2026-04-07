# Phase 76 Context

## Phase

- **Number:** `76`
- **Title:** `Governance bootstrap truth hardening, archive-seed determinism, and active-route activation`
- **Milestone:** `v1.21 Governance Bootstrap Truth Hardening & Planning Route Automation`
- **Starting baseline:** `v1.21 active / Phase 76 planning-ready / latest archived baseline = v1.20`
- **Archived reference:** `v1.20 archived / evidence-ready`

## Why This Phase Exists

`v1.20` 已完成 archive promotion，且 recent machine-readable bootstrap drift 已被局部修正；但当前 active-route 能否被稳定消费，仍取决于 `PROJECT / ROADMAP / REQUIREMENTS / STATE / MILESTONES / tests/meta` 是否共同讲同一条 deterministic bootstrap 故事。

本 phase 的目标不是重开生产架构迁移，而是把“如何从 archived baseline 稳定进入下一条正式路线”这件事本身正式化：

- current milestone / latest archived baseline / previous archived baseline 必须同时可供人读与机读消费
- 历史 milestone prose、archive narrative 与 legacy route 不能继续抢占 parser-visible current selector
- next-step bootstrap 必须能直接支撑 `$gsd-plan-phase 76`、后续 `$gsd-execute-phase 76` 与 `$gsd-next`，而不是依赖人工热修
- current-truth guards 需要继续收口，减少对同一故事线的重复 literal 依赖

## In Scope

- `.planning/PROJECT.md`
- `.planning/ROADMAP.md`
- `.planning/REQUIREMENTS.md`
- `.planning/STATE.md`
- `.planning/MILESTONES.md`
- `.planning/baseline/VERIFICATION_MATRIX.md`
- `.planning/reviews/FILE_MATRIX.md`
- `tests/meta/governance_current_truth.py`
- `tests/meta/test_governance_closeout_guards.py`
- `tests/meta/test_governance_milestone_archives.py`
- `tests/meta/governance_followup_route_current_milestones.py`
- `tests/meta/test_phase71_hotspot_route_guards.py`
- `tests/meta/test_phase72_runtime_bootstrap_route_guards.py`
- `tests/meta/test_phase75_governance_closeout_guards.py`
- `tests/meta/test_governance_release_contract.py`
- `tests/meta/test_version_sync.py`
- GSD bootstrap smoke: `node "$HOME/.codex/get-shit-done/bin/gsd-tools.cjs" init new-milestone`, `init plan-phase 76`, `init progress`

## Constraints

- 不修改外部 GSD 工具源码；本 phase 先把 repo-local planning/bootstrap truth 做成 deterministic contract
- 不恢复 `no active milestone route`，也不把历史 `v1.20 active / Phase 75 complete` 旧故事回写成当前正式真相
- 历史 milestone 资产继续保留审计 / archive 身份，但不能再以 parser-visible current selector 形式抢占 active route
- public docs 继续保持 docs-first / contributor-first 边界，不泄露 internal bootstrap folklore
- 所有 Python / test / script 命令统一使用 `uv run ...`
