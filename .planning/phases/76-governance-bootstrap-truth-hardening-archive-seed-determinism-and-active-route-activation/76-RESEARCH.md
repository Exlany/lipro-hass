# Phase 76 Research

## Inputs

- `.planning/PROJECT.md`
- `.planning/ROADMAP.md`
- `.planning/REQUIREMENTS.md`
- `.planning/STATE.md`
- `.planning/MILESTONES.md`
- `.planning/v1.20-MILESTONE-AUDIT.md`
- `.planning/reviews/V1_20_EVIDENCE_INDEX.md`
- `tests/meta/governance_current_truth.py`
- `tests/meta/test_governance_milestone_archives.py`
- `tests/meta/test_governance_closeout_guards.py`
- `tests/meta/governance_followup_route_current_milestones.py`
- `tests/meta/test_phase71_hotspot_route_guards.py`
- `tests/meta/test_phase72_runtime_bootstrap_route_guards.py`
- `tests/meta/test_phase75_governance_closeout_guards.py`
- GSD smoke outputs: `init new-milestone`, `init plan-phase 76`, `init progress`

## Findings That Directly Drive Implementation

### 1. Current-route truth must be an explicit contract, not a side effect of document order

上一轮修复已经证明：只要 current milestone、latest archived baseline、previous archived baseline 没有被明确拆成 machine-readable contract，任何旧 heading、legacy route prose 或 archive narrative 都可能重新劫持 bootstrap 入口。`Phase 76` 不该只“修一个 parser-visible 点”，而应让 `PROJECT / ROADMAP / REQUIREMENTS / STATE / MILESTONES` 同时暴露同一条 current-route truth。

### 2. Active-route truth 与 latest-archived truth 需要在共享 helper 中分层表达

`tests/meta/governance_current_truth.py` 已从 archived-only 切到 `v1.21 active route`，但当前仍存在一类风险：active-route 断言、latest-archive 断言、historical closeout 断言混在同一 helper 中，容易让后续 phase 再次通过“改常量”碰运气。Phase 76 的计划应优先把 current route 与 latest archived baseline 的 helper/guard 消费面拆清楚。

### 3. `MILESTONES.md` 与 `ROADMAP.md` 需要同时兼顾 human-readable 与 bootstrap-readable 入口

上一轮已经把 `v1.20` 提升到 `MILESTONES.md` 顶部，并去掉 `ROADMAP.md` 中会抢占 current selector 的旧 heading；但这仍只是“当前版本正确”。Phase 76 应把这件事提升为长期合同：历史 milestone 仍可完整保留，但 parser-visible current selector 必须只来自显式 active milestone / latest archived baseline 入口。

### 4. GSD smoke 需要纳入 phase acceptance，而不是作为临时手工检查

`node "$HOME/.codex/get-shit-done/bin/gsd-tools.cjs" init new-milestone`、`init plan-phase 76`、`init progress` 现在都已回到正确结果；这类命令应成为 Phase 76 的 focused proof，而非一次性“修完顺手看一下”。否则后续 phase 很容易再次把 routing truth 改坏。

### 5. 本 phase 最佳策略是 repo-local determinism，而不是立刻改外部 GSD 工具

当前约束明确要求先保证仓库内部 planning/bootstrap truth 是 deterministic contract。直接去改外部 GSD tool 虽然长期可能有价值，但会把本 phase 从“收口 repo 真相”扩大成“维护上游工具”，风险和范围都过大。

## Validation Architecture

### Focused GSD Smoke

- `node "$HOME/.codex/get-shit-done/bin/gsd-tools.cjs" init new-milestone`
- `node "$HOME/.codex/get-shit-done/bin/gsd-tools.cjs" init plan-phase 76`
- `node "$HOME/.codex/get-shit-done/bin/gsd-tools.cjs" init progress`

这些命令应共同证明：`current_milestone = v1.21`、`latest_completed_milestone = v1.20`、`next_phase = 76`。

### Focused Governance Gates

- `uv run pytest -q tests/meta/test_governance_milestone_archives.py tests/meta/test_governance_closeout_guards.py tests/meta/governance_followup_route_current_milestones.py tests/meta/test_phase71_hotspot_route_guards.py tests/meta/test_phase72_runtime_bootstrap_route_guards.py tests/meta/test_phase75_governance_closeout_guards.py tests/meta/test_governance_release_contract.py tests/meta/test_version_sync.py`

这组测试应覆盖：
- active route / latest archive / previous archive 的 current truth
- machine-readable roadmap/milestones selector
- historical route demotion
- public docs 不泄露 internal bootstrap story

### Contract / Policy Gates

- `uv run python scripts/check_architecture_policy.py --check`
- `uv run python scripts/check_file_matrix.py --check`

这组门禁负责确认 planning/review/baseline story 没有因 current-route activation 漂移。

### Full Gate

- `uv run ruff check .`
- `uv run mypy --follow-imports=silent .`
- `uv run pytest -q`

Full gate 应作为 Phase 76 closeout-ready proof，而 focused gate 则用于每个 plan 的局部收口验证。

## Rejected Alternatives

- **直接修改外部 GSD 解析器**：长期也许值得，但超出本 phase 的 repo-local truth 收口边界；当前先保证仓库自己不制造 parser ambiguity。
- **重新退回 `no active milestone route`**：这会让 `v1.21` 再次变成 conversation-only milestone，与当前 active route 真相冲突。
- **删除历史 milestone 大段正文**：会损伤 audit / archive 可读性；更优解是保留历史 narrative，但把 parser-visible current selector 明确隔离。
- **继续在多份 meta tests 中散写完整 current-story literal**：短期省事，长期维护成本高；本 phase 应优先降低 literal drift 面积。
