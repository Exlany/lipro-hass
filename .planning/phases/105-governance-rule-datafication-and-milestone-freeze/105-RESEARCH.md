# Phase 105 Research: governance rule datafication and milestone freeze

**Date:** 2026-03-28
**Phase:** `105`
**Scope:** `GOV-69`, `QLT-44`

## Summary

`Phase 104` 已完成 production hotspot inward split；`v1.29` 剩余 live work 不再是生产代码大拆，而是治理真源的最后一轮降噪：

1. `tests/meta` 中 current-route / closeout / continuation suites 仍用大量重复 literal 维持 route truth。
2. `scripts/check_file_matrix_registry_classifiers.py` 仍用手写 tuple 家族维护 classifier metadata，而 override side 已经是 family-based dataclass truth。
3. planning / baseline / review / docs / focused guards 仍停留在 `Phase 104 complete` continuation wording，尚未冻结到 `Phase 105 complete -> $gsd-complete-milestone v1.29`。

因此本 phase 的最小彻底方案是：**先把 follow-up guards 与 registry classifiers 继续数据化，再统一推进 live route / promoted evidence / focused freeze 到 Phase 105 完成态。**

## Findings

### 1. `tests/meta` follow-up route suites still duplicate traceability arithmetic and route prose

高价值重复点：

- `governance_followup_route_current_milestones.py`
  - 重复的 `Current mapped/complete/pending` 字面量
  - 重复的 `- [x] **REQ**` 与 `| REQ | Phase N | Complete |` traceability rows
  - 重复的 default next command / promoted closeout package / project pointer断言
- `governance_followup_route_closeouts.py`
  - 多个 milestone closeout 继续手写 coverage arithmetic 与 project/state archived pointer checks
- `governance_followup_route_continuation.py`
  - predecessor phases 继续手写 requirement rows 与 route-continuation prose

结论：这些 suite 不缺 guard 覆盖，缺的是 **shared spec / helper truth**。把 strings 抽成 shared dataclass / table builder 可显著降低后续 milestone freeze 修改面。

### 2. `governance_current_truth.py` is already the right live truth home, but still contains manual inventory noise

当前优点：
- route contract、active/current/latest archived truth、historical forbidden prose 已集中
- testing inventory snapshot 与 focused guards 已作为 shared constants 暴露

仍可改进点：
- `TESTS_PYTHON_FILE_COUNT` / `TESTS_RUNNABLE_FILE_COUNT` / `TESTS_META_SUITE_COUNT` 为手写数字，每次新增 guard 都要同步修改
- `CURRENT_ROUTE_FOCUSED_GUARDS` 需要跟随 active-route handoff 从 `Phase 104` 扩展到 `Phase 105`
- current milestone status/default next command 仍停留在 `Phase 104 complete`

结论：Phase 105 应把 inventory counts 计算化，并把 active-route truth 前推到 `Phase 105 complete / $gsd-complete-milestone v1.29`。

### 3. `scripts/check_file_matrix_registry_classifiers.py` lags behind the family-based style already present in overrides

现状：
- `_COMPONENT_EXACT_RULES` / `_TEST_EXACT_RULES` / `_SCRIPT_EXACT_RULES` 与 prefix rules 仍为裸 tuple 列表
- recent governance files（如 `governance_followup_route_current_milestones.py`、`test_phase103_root_thinning_guards.py`、`test_phase104_service_router_runtime_split_guards.py`）仍逐条手写 metadata
- override side 已通过 `OverrideTruthFamily` 聚合同类规则，但 classifier side 没有对应 builder / family abstraction

结论：Phase 105 最值得做的是在 `scripts/check_file_matrix_registry_shared.py` 增加 classifier family builders，让 classifier rule truth 也变成 machine-shaped families，而不是继续堆 tuple。

### 4. The milestone-freeze surface spans more than planning docs

必须同步的冻结面：
- `.planning/{PROJECT,ROADMAP,REQUIREMENTS,STATE,MILESTONES}.md`
- `.planning/baseline/VERIFICATION_MATRIX.md`
- `.planning/codebase/TESTING.md`
- `.planning/reviews/{PROMOTED_PHASE_ASSETS,RESIDUAL_LEDGER,KILL_LIST,FILE_MATRIX}.md`
- `docs/developer_architecture.md`
- `tests/meta/{governance_current_truth.py,test_governance_route_handoff_smoke.py,test_governance_closeout_guards.py,test_phase103_root_thinning_guards.py,test_phase104_service_router_runtime_split_guards.py}`
- 新增 `tests/meta/test_phase105_governance_freeze_guards.py`

结论：若只改 planning docs 而不改 baseline/review/docs/guards，`QLT-44` 仍不成立。

## Chosen Approach

### Slice 105-01 — datafy governance follow-up suites
- 新增 shared route-spec helper（建议 `tests/meta/governance_followup_route_specs.py`）
- 用 dataclass / builders 生成 requirement rows 与 coverage arithmetic needles
- 顺带把 `governance_current_truth.py` testing inventory counts 改为 derivation，减少 guard 新增时的人工噪音

### Slice 105-02 — datafy classifier rule families
- 在 `scripts/check_file_matrix_registry_shared.py` 增加 classifier family dataclass / builder
- 把 classifier exact/prefix rules 重写为 family-driven data tables
- 把新增 `Phase 105` helper/guard 纳入明确的 Assurance ownership

### Slice 105-03 — freeze v1.29 current route and evidence story
- 把 route truth 前推到 `Phase 105 complete`
- 默认下一步改为 `$gsd-complete-milestone v1.29`
- `Phase 104` guard 降级为 predecessor visibility guard
- 新增 `Phase 105` focused freeze guard
- promoted assets allowlist / verification matrix / testing / ledgers / developer architecture 同步收口

## Alternatives Considered

### Alternative A: only edit current route strings
- **Pros:** 改动最少
- **Cons:** `GOV-69` 仍未完成，后续 route freeze 继续高噪音
- **Decision:** reject

### Alternative B: rewrite all historical follow-up route suites into one giant mega-table
- **Pros:** 表面上最统一
- **Cons:** 单文件过大，diff 难审阅，容易把已有稳定 guard 重新集中成新 mega-hotspot
- **Decision:** reject

### Alternative C: targeted helper extraction + current milestone freeze
- **Pros:** 命中本 phase 真正 residual；改动可验证、边界清晰、不会重开 production surgery
- **Cons:** 仍保留历史 suite 分文件布局
- **Decision:** accept

## Risks and Mitigations

- **Risk:** 把 current-route freeze 写成 archived-only truth。
  - **Mitigation:** current route 只前推到 `Phase 105 complete`；historical closeout marker 仍保持 `no active milestone route / latest archived baseline = v1.28`。
- **Risk:** data helpers 变成新的 mega-hotspot。
  - **Mitigation:** 只抽 shared builders / compact specs；保留 suite 按 current/closeout/continuation 分文件。
- **Risk:** file-matrix registry datafication 改坏 existing classifications。
  - **Mitigation:** `scripts/check_file_matrix.py --write && --check` + `tests/meta` + repo-wide quality gates 一起验证。

## Expected End State

- `init progress` 显示 `103 / 104 / 105` 全部 complete，`next_phase = null`，`has_work_in_progress = false`
- live docs / baseline / review / focused guards 一致承认：`v1.29 active route / Phase 105 complete / latest archived baseline = v1.28`
- default next command 统一为 `$gsd-complete-milestone v1.29`
- `tests/meta` 与 `scripts/check_*` 的 recent governance truth 明显更表驱动，后续 freeze 修改面下降
