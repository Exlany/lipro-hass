# Phase 88: Governance sync, quality proof, and milestone freeze - Context

**Gathered:** 2026-03-27
**Status:** Ready for planning
**Source:** v1.23 continuation after Phase 87 complete

<domain>
## Phase Boundary

本 phase 只处理 `v1.23` 的终局治理同步、质量证明与里程碑冻结：

- 把 `PROJECT / ROADMAP / REQUIREMENTS / STATE / MILESTONES / baselines / reviews / docs / focused guards` 收口成同一条 post-eradication current truth。
- 为 `GOV-63` / `QLT-35` 提供 machine-checkable closeout-ready 证明：touched scope 质量门通过、active residual 与 active kill target 不留 orphan story。
- 若仍有 carry-forward，必须在 ledgers / verification truth 中显式写出 owner、exit condition 与 evidence pointer；不得只留在 summary prose 或会话记忆里。
- 不重开 production 架构 surgery，不把已在 `Phase 85`~`87` 关闭的 residual / hotspot 重新讲成 active debt，也不提前执行 milestone archive promotion。

</domain>

<decisions>
## Implementation Decisions

### Locked Decisions
- 本 phase 对应 `ROADMAP.md` 中 `Phase 88`，只覆盖 `GOV-63` 与 `QLT-35`。
- live route / current milestone truth 的唯一 formal machine truth 继续是 `.planning/{PROJECT,ROADMAP,REQUIREMENTS,STATE,MILESTONES}.md` 的 shared governance-route contract 与 `tests/meta/governance_current_truth.py`；review docs、historical audit 与 archived evidence 只能 pull 当前真源，不能复制第二套 active literal。
- `FILE_MATRIX.md`、`RESIDUAL_LEDGER.md`、`KILL_LIST.md`、`PUBLIC_SURFACES.md` 与 `docs/developer_architecture.md` 必须共同承认同一条 post-eradication topology、ownership 与 delete-gate truth；若口径冲突，以 north-star → project/roadmap/requirements/state → baseline/review 的权威顺序裁决。
- `Residual Ledger` 必须保持 truthful：active residual family 为空时要明确写成空，不得用模糊 prose 暗示 future debt；若仍有 carry-forward，必须直接给出 owner、exit condition、evidence。
- `KILL_LIST.md` 必须保持 truthful：`Phase 85` routed delete gates 继续为空表；历史 closed / explicitly-keep 条目可以保留，但不得借壳变回 active delete campaign。
- 质量证明必须采用 layered closeout bundle：至少包含 `ruff`、policy scripts、focused governance/meta guards、touched topical suites，以及足以证明 milestone freeze 的 broader proof；不得只跑局部 smoke 就宣称 repo-wide closeout 完成。
- 因为 `Phase 88` 是 `v1.23` 最后一个 active phase，完成后 live route 必须前推到 `v1.23 active route / Phase 88 complete / latest archived baseline = v1.22`，默认下一步固定为 `$gsd-complete-milestone v1.23`。

### The Agent's Discretion
- focused guard 可以新增独立 `Phase 88` suite，也可以局部复用现有 governance suites；但失败必须直接指向 governance sync / orphan-proof / milestone-freeze concern，而不是再做一个更大的 meta bucket。
- quality proof 可以按“touched scope + governance/tooling closeout bundle + broad confirmation”组织，只要命令集诚实、可复现、能直接服务 closeout-ready 断言。
- 若 `PUBLIC_SURFACES.md`、`docs/developer_architecture.md` 或 `TESTING.md` 仅需 freshness / guidance 同步，可做最小必要更新；不为了“看起来更整齐”重写无漂移 prose。

</decisions>

<canonical_refs>
## Canonical References

**Downstream agents MUST read these before planning or implementing.**

### North-star / active route truth
- `AGENTS.md`
- `docs/NORTH_STAR_TARGET_ARCHITECTURE.md`
- `docs/developer_architecture.md`
- `.planning/PROJECT.md`
- `.planning/ROADMAP.md`
- `.planning/REQUIREMENTS.md`
- `.planning/STATE.md`
- `.planning/MILESTONES.md`
- `tests/meta/governance_current_truth.py`
- `tests/meta/governance_followup_route_current_milestones.py`
- `tests/meta/test_governance_route_handoff_smoke.py`

### Baseline / review truth to freeze
- `.planning/baseline/PUBLIC_SURFACES.md`
- `.planning/baseline/DEPENDENCY_MATRIX.md`
- `.planning/baseline/AUTHORITY_MATRIX.md`
- `.planning/baseline/VERIFICATION_MATRIX.md`
- `.planning/baseline/GOVERNANCE_REGISTRY.json`
- `.planning/reviews/FILE_MATRIX.md`
- `.planning/reviews/RESIDUAL_LEDGER.md`
- `.planning/reviews/KILL_LIST.md`
- `.planning/reviews/PROMOTED_PHASE_ASSETS.md`
- `.planning/reviews/V1_23_TERMINAL_AUDIT.md`
- `.planning/reviews/V1_22_EVIDENCE_INDEX.md`

### Prior-phase evidence this phase must consume
- `.planning/phases/85-terminal-audit-refresh-and-residual-routing/85-CONTEXT.md`
- `.planning/phases/85-terminal-audit-refresh-and-residual-routing/85-RESEARCH.md`
- `.planning/phases/85-terminal-audit-refresh-and-residual-routing/{85-01-SUMMARY.md,85-02-SUMMARY.md,85-03-SUMMARY.md}`
- `.planning/phases/86-production-residual-eradication-and-boundary-re-tightening/{86-CONTEXT.md,86-RESEARCH.md,86-01-SUMMARY.md,86-02-SUMMARY.md,86-03-SUMMARY.md,86-04-SUMMARY.md}`
- `.planning/phases/87-assurance-hotspot-decomposition-and-no-regrowth-guards/{87-CONTEXT.md,87-RESEARCH.md,87-01-SUMMARY.md,87-02-SUMMARY.md,87-03-SUMMARY.md,87-04-SUMMARY.md}`

### Existing machine guards / proof tooling
- `tests/meta/test_phase85_terminal_audit_route_guards.py`
- `tests/meta/test_phase70_governance_hotspot_guards.py`
- `tests/meta/test_phase87_assurance_hotspot_guards.py`
- `tests/meta/test_governance_bootstrap_smoke.py`
- `tests/meta/test_governance_closeout_guards.py`
- `tests/meta/test_public_surface_guards.py`
- `tests/meta/test_dependency_guards.py`
- `tests/meta/test_toolchain_truth.py`
- `scripts/check_file_matrix.py`
- `scripts/check_architecture_policy.py`
- `.planning/codebase/TESTING.md`

</canonical_refs>

<code_context>
## Existing Code Insights

### Reusable Assets
- `tests/meta/governance_current_truth.py`：当前 route / default-next / archived pointer 的唯一 shared literal home，适合继续作为 `Phase 88` completion truth 的单点常量源。
- `tests/meta/governance_followup_route_current_milestones.py` 与 `tests/meta/test_governance_route_handoff_smoke.py`：已经把 current-route contract 做成机器守卫，可直接承接 `Phase 88 complete -> $gsd-complete-milestone v1.23` 的切换。
- `tests/meta/test_phase85_terminal_audit_route_guards.py`、`tests/meta/test_phase87_assurance_hotspot_guards.py`：提供“历史审计 artifact 保持 pull-only，而 current closeout truth 迁入 live ledgers / focused guards”的成熟模式。
- `scripts/check_file_matrix.py` 与 `scripts/check_architecture_policy.py`：现有 governance/tooling closeout proof 的固定脚本入口，适合直接纳入最终 verification bundle。

### Established Patterns
- live current truth 必须写回 `.planning/{PROJECT,ROADMAP,REQUIREMENTS,STATE,MILESTONES}.md` 与 focused tests；phase summary / terminal audit 只保留 evidence / audit 身份。
- review ledgers 必须 truthful：没有 active residual / kill target 时显式写“无新增 / none currently registered”，不能依赖空白语义。
- milestone freeze 的 closeout proof 采用“docs sync + machine guards + runnable verification bundle”三件套，而不是只靠 prose 声明完成。

### Integration Points
- 若新增 `Phase 88` guard，需要同步 `FILE_MATRIX.md`、`VERIFICATION_MATRIX.md` 与 `.planning/codebase/TESTING.md`，避免 derived truth 漂移。
- 若 live route 前推到 `Phase 88 complete`，需要同步 `PROJECT.md`、`ROADMAP.md`、`REQUIREMENTS.md`、`STATE.md`、`MILESTONES.md`、`tests/meta/governance_current_truth.py` 与 follow-up route guards。
- 若 residual / kill-list posture 在本 phase 明确“清零且无 orphan”，必须让 `RESIDUAL_LEDGER.md`、`KILL_LIST.md`、`PUBLIC_SURFACES.md`、`docs/developer_architecture.md` 与新 focused guard 共同承认，而不是只改一处说明。

</code_context>

<specifics>
## Specific Ideas

- 用一个 dedicated `Phase 88` focused guard 明确冻结三件事：current-route completion truth、zero-active residual / delete-gate posture、`PUBLIC_SURFACES / developer_architecture / ledgers / verification bundle` 的同步完成态。
- 让 `VERIFICATION_MATRIX.md` 直接列出 `Phase 88` 的 closeout-ready proof bundle，而不是继续让维护者翻 Phase 85/87 summary 猜测最终该跑哪些命令。
- 若 `developer_architecture.md` 仍停留在 `Phase 85` 对齐标记，就把它升级到 `Phase 88`，并同步最小充分测试/验证 guidance，避免文档 freshness 自身成为新的治理漂移。

</specifics>

<deferred>
## Deferred Ideas

- `v1.23` 的 milestone archive promotion、evidence-index promotion 与 `v1.23-MILESTONE-AUDIT.md` 归档属于 `$gsd-complete-milestone v1.23`，不是本 phase 的 active scope。
- 不再重开 `Phase 85`~`87` 已关闭的 production residual、assurance hotspot topicization 或 delete-gate 争议；本 phase 只消费它们的 closeout evidence。
- 若 broader full-suite proof 已有足够 current evidence，不为了“形式上更全”重做与本 phase 无关的大规模 refactor 或 fixture rewrite。

</deferred>
