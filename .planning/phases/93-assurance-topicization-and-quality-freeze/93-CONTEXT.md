# Phase 93: Assurance topicization and quality freeze - Context

**Gathered:** 2026-03-28
**Status:** Ready for planning

<domain>
## Phase Boundary

`Phase 92` 已把 shared redaction truth 与 touched thin-shell topology 收敛到正式 home，但本轮最终治理检查仍暴露出 assurance / quality freeze 层的最后一批漂移：`FILE_MATRIX` 头部统计未刷新、`TESTING.md` 的 repo counts 与 Phase 55 test-topology 说明滞后、`VERIFICATION_MATRIX.md` 顶部 current-route 仍停在 `Phase 91`、current-route smoke / machine-readable route tests 仍残留 `Phase 91` / `Phase 92 -> 93` 的硬编码，以及 topicized diagnostics sibling suites 带来了无语义收益的 `Any` 预算回涨。

本 phase 只做 assurance / governance / typing / quality gate 冻结：一边把上述漂移全部清零，一边把 `Phase 92` 的 verification/validation 资产正式盖棺，并把当前里程碑前推到 `Phase 93 complete` / milestone closeout-ready，而不是继续留下“代码已收敛、治理未收敛”的尾巴。

</domain>

<decisions>
## Implementation Decisions

### Governance and route truth
- **D-01:** current-route truth 必须从 `Phase 92 complete / next = $gsd-discuss-phase 93` 收口到 `Phase 93 complete / next = $gsd-complete-milestone v1.25`；`PROJECT / ROADMAP / REQUIREMENTS / STATE / MILESTONES` 与 `tests/meta/governance_current_truth.py` 必须完全一致。
- **D-02:** `VERIFICATION_MATRIX.md` 顶部 mutable-story、default next command、focused guards 与 `Phase 92` / `Phase 93` sections 必须同时更新；不能只修 section、不修 header。
- **D-03:** `FILE_MATRIX.md`、`TESTING.md`、`PUBLIC_SURFACES.md`、`DEPENDENCY_MATRIX.md`、`RESIDUAL_LEDGER.md`、`KILL_LIST.md` 与 `docs/developer_architecture.md` 必须同步承认 assurance freeze 的最终真相；任何 phase note / delta / status update 不得缺位。

### Typing and no-growth
- **D-04:** repo-wide `tests_any_non_meta` budget 不得因为 topicization 复制 import 而隐性膨胀；应优先收紧类型或移除无必要 `Any`，而不是直接把 accidental drift 合法化。
- **D-05:** touched diagnostics sibling suites 只允许保留有语义价值的 `Any`；无语义收益的 cast / import duplication 必须 burn down。

### Quality freeze and closeout
- **D-06:** `Phase 92` 的 `92-VERIFICATION.md` / `92-VALIDATION.md` 必须从 `pending-final-validation` 收口到 passed/finalized 文案，并记录本 session 的最终命令结果。
- **D-07:** `Phase 93` 必须补齐 `93-CONTEXT.md`、`93-RESEARCH.md`、`93-01/02/03-PLAN.md`、对应 `SUMMARY.md`、`93-VERIFICATION.md`、`93-VALIDATION.md`，让 gsd-tools 可以把 phase 识别为完整完成态。
- **D-08:** quality freeze 的最小证明链必须覆盖：`scripts/check_file_matrix.py --check`、`tests/meta`、`ruff check .`、`mypy`，以及与本轮 touched scope 对应的 focused pytest suites。

### the agent's Discretion
- 自主决定是通过 tightening types 还是调整 helper usage 消除新增 `Any`，只要不放大测试复杂度。
- 自主决定是否在 meta guards 中追加 Phase 93 notes/route smoke，只要不新增第二条治理故事线。
- 自主决定 `Phase 93` 三份 plan 的颗粒度，但必须保证执行后能直接支撑 milestone closeout。

</decisions>

<specifics>
## Specific Ideas

- 优先修复当前已观测的 9 个 meta 失败，再把 route / docs 一次性前推到 `Phase 93 complete`，避免重复改动同一批治理资产。
- `ROADMAP.md` 当前 `Phase 93` section 被误写成 `Complete` + 指向 `Phase 92` closeout assets；这是明显的 governance drift，必须被真实 closeout 取代，而不是保留占位。
- `FILE_MATRIX` 正文已全覆盖，问题仅在头部总数；`TESTING.md` 问题则是 counts 和 Phase 55 prose 滞后。

</specifics>

<canonical_refs>
## Canonical References

**Downstream agents MUST read these before planning or implementing.**

### Governance / north-star truth
- `AGENTS.md`
- `docs/NORTH_STAR_TARGET_ARCHITECTURE.md`
- `.planning/PROJECT.md`
- `.planning/ROADMAP.md`
- `.planning/REQUIREMENTS.md`
- `.planning/STATE.md`
- `.planning/MILESTONES.md`

### Phase 92 closeout inputs
- `.planning/phases/92-control-entity-thin-boundary-and-redaction-convergence/92-03-SUMMARY.md`
- `.planning/phases/92-control-entity-thin-boundary-and-redaction-convergence/92-VERIFICATION.md`
- `.planning/phases/92-control-entity-thin-boundary-and-redaction-convergence/92-VALIDATION.md`
- `tests/meta/test_phase92_redaction_convergence_guards.py`

### Assurance / governance hotspots
- `.planning/baseline/VERIFICATION_MATRIX.md`
- `.planning/reviews/FILE_MATRIX.md`
- `.planning/codebase/TESTING.md`
- `.planning/baseline/PUBLIC_SURFACES.md`
- `.planning/baseline/DEPENDENCY_MATRIX.md`
- `.planning/reviews/RESIDUAL_LEDGER.md`
- `.planning/reviews/KILL_LIST.md`
- `docs/developer_architecture.md`

### Route / guard homes
- `tests/meta/governance_current_truth.py`
- `tests/meta/governance_followup_route_current_milestones.py`
- `tests/meta/test_governance_bootstrap_smoke.py`
- `tests/meta/test_governance_route_handoff_smoke.py`
- `tests/meta/public_surface_phase_notes.py`
- `tests/meta/dependency_guards_review_ledgers.py`
- `tests/meta/test_phase31_runtime_budget_guards.py`
- `tests/meta/test_phase90_hotspot_map_guards.py`

### Touched tests
- `tests/services/test_services_diagnostics_capabilities.py`
- `tests/services/test_services_diagnostics_feedback.py`
- `tests/services/test_services_diagnostics_support.py`

</canonical_refs>
