# Phase 105: Governance rule datafication and milestone freeze - Context

**Gathered:** 2026-03-28
**Status:** Ready for planning
**Source:** v1.29 continuation after Phase 104 complete

<domain>
## Phase Boundary

本 phase 只处理 `v1.29` 的终局治理数据化与里程碑冻结：

- 把 `tests/meta` 中 current-route / closeout / continuation follow-up guards 的重复 literal 收束到共享 helper / table-driven truth，避免 route freeze 再靠散落硬编码维持。
- 把 `scripts/check_file_matrix_registry_*.py` 中重复的 registry classifier / override 规则进一步 family 化、数据化，降低 file-matrix / governance freeze 的维护噪音。
- 把 planning / baseline / review / docs / focused guards / GSD fast-path 一次性前推到 `v1.29 active route / Phase 105 complete / latest archived baseline = v1.28`，并把默认下一步固定为 `$gsd-complete-milestone v1.29`。
- 不重开 production 架构 surgery，不回改 `Phase 103` / `104` 已关闭的 hotspot，也不提前把 `v1.29` 写成 archived-only baseline。

</domain>

<decisions>
## Implementation Decisions

### Locked Decisions
- 本 phase 对应 `ROADMAP.md` 中 `Phase 105`，只覆盖 `GOV-69` 与 `QLT-44`。
- `tests/meta/governance_current_truth.py` 继续作为 active route / latest archived pointer / focused-guard inventory 的共享 formal home；follow-up guards 只能 pull 它与新的 shared tables，不能复制第二套 live literals。
- `governance_followup_route_current_milestones.py`、`governance_followup_route_closeouts.py`、`governance_followup_route_continuation.py` 必须减少 `Current mapped/complete/pending`、requirement trace row、default-next command 等散落硬编码，改为 shared helper / spec-table 驱动。
- `scripts/check_file_matrix_registry_classifiers.py` 必须把 exact/prefix classifier truth 进一步 family 化，避免 recent governance / focused-guard / registry script rows 继续散落在裸 tuple 列表里；`scripts/check_file_matrix_registry_overrides.py` 保持 override-family 真源身份，不再与 classifier 侧重复 recent governance 口径。
- `Phase 104` focused guard 必须从 active-route guard 降级为 predecessor guard；`Phase 105` 新增 focused freeze guard，作为当前 active route 的唯一专属 closeout guard。
- closeout bundle 需要包含 `105-01/02/03-SUMMARY.md`、`105-SUMMARY.md`、`105-VERIFICATION.md`、`105-VALIDATION.md`，并通过 `.planning/reviews/PROMOTED_PHASE_ASSETS.md` allowlist 正式提升为长期治理证据。
- `v1.29` 在本 phase 完成后仍保持 active milestone 身份；只有 `$gsd-complete-milestone v1.29` 才能把 current route 切换成 archived-only baseline。

### The Agent's Discretion
- shared helper 可以落在新的 `tests/meta/governance_followup_route_specs.py`，也可以合并进现有 helper，只要不制造第三套 authority chain。
- registry datafication 可以通过 dataclass/builder families 或 helper constructors 落地；重点是把重复 metadata 从裸 tuple 中抽离为 machine-checkable family truth，而不是追求花哨抽象。
- verification bundle 可以按“targeted governance/datafication checks → repo-wide quality gates”组织，但必须同时证明 current route、promoted allowlist、file matrix 与 gsd fast-path 已同步到 `Phase 105 complete`。

</decisions>

<canonical_refs>
## Canonical References

**Downstream agents MUST read these before planning or implementing.**

### Active-route / archived-baseline truth
- `AGENTS.md`
- `docs/NORTH_STAR_TARGET_ARCHITECTURE.md`
- `docs/developer_architecture.md`
- `.planning/PROJECT.md`
- `.planning/ROADMAP.md`
- `.planning/REQUIREMENTS.md`
- `.planning/STATE.md`
- `.planning/MILESTONES.md`
- `tests/meta/governance_current_truth.py`
- `tests/meta/governance_contract_helpers.py`
- `tests/meta/test_governance_route_handoff_smoke.py`

### Follow-up guards to datafy
- `tests/meta/governance_followup_route_current_milestones.py`
- `tests/meta/governance_followup_route_closeouts.py`
- `tests/meta/governance_followup_route_continuation.py`
- `tests/meta/governance_promoted_assets.py`
- `tests/meta/test_governance_closeout_guards.py`
- `tests/meta/test_phase103_root_thinning_guards.py`
- `tests/meta/test_phase104_service_router_runtime_split_guards.py`

### Registry / file-matrix truth
- `scripts/check_file_matrix_registry_shared.py`
- `scripts/check_file_matrix_registry_classifiers.py`
- `scripts/check_file_matrix_registry_overrides.py`
- `scripts/check_file_matrix_registry.py`
- `scripts/check_file_matrix.py`
- `.planning/reviews/FILE_MATRIX.md`

### Freeze targets / evidence destinations
- `.planning/baseline/VERIFICATION_MATRIX.md`
- `.planning/codebase/TESTING.md`
- `.planning/reviews/PROMOTED_PHASE_ASSETS.md`
- `.planning/reviews/RESIDUAL_LEDGER.md`
- `.planning/reviews/KILL_LIST.md`
- `.planning/reviews/V1_28_EVIDENCE_INDEX.md`
- `.planning/phases/104-service-router-family-split-and-command-runtime-second-pass-decomposition/{104-01-SUMMARY.md,104-02-SUMMARY.md,104-03-SUMMARY.md,104-VERIFICATION.md,104-VALIDATION.md}`

</canonical_refs>

<code_context>
## Existing Code Insights

### Reusable Assets
- `tests/meta/governance_current_truth.py` 已持有 current milestone / latest archived pointer / focused-guard inventory / historical forbidden prose 等 shared constants。
- `tests/meta/governance_contract_helpers.py` 已提供 current-route / state continuation / testing inventory 的共用断言，可继续扩充而不必在 follow-up suites 中复制。
- `scripts/check_file_matrix_registry_shared.py` 已提供 `FileGovernanceRow` 与 `OverrideTruthFamily` dataclass，可作为 classifier family builders 的自然落点。
- `Phase 88` 的 governance freeze、`Phase 104` 的 route projection、`Phase 102` 的 archived-only portability freeze 都提供了 closeout bundle 与 focused guard 模板。

### Hotspots to Resolve
- `tests/meta/governance_followup_route_current_milestones.py` 仍以大量散落 literal 维护 `Current mapped/complete/pending`、default next command 与 route-specific prose。
- `tests/meta/governance_followup_route_closeouts.py` 与 `tests/meta/governance_followup_route_continuation.py` 仍重复 requirement row / coverage arithmetic / project/state continuation tokens。
- `scripts/check_file_matrix_registry_classifiers.py` 的 recent governance exact/prefix rules 仍是手写 tuple 家族，`Phase 103` / `104` / `105` focused guard 与 registry-helper ownership 不够 machine-shaped。
- `docs/developer_architecture.md`、`VERIFICATION_MATRIX.md`、`TESTING.md`、`RESIDUAL_LEDGER.md`、`KILL_LIST.md` 仍停留在 `Phase 104 complete` continuation 叙事。

</code_context>

<verification_outline>
## Verification Outline

- `uv run pytest -q tests/meta/governance_followup_route_current_milestones.py tests/meta/governance_followup_route_closeouts.py tests/meta/governance_followup_route_continuation.py tests/meta/test_governance_route_handoff_smoke.py tests/meta/test_governance_closeout_guards.py tests/meta/test_phase103_root_thinning_guards.py tests/meta/test_phase104_service_router_runtime_split_guards.py tests/meta/test_phase105_governance_freeze_guards.py`
- `uv run python scripts/check_file_matrix.py --write`
- `uv run python scripts/check_file_matrix.py --check`
- `node "$HOME/.codex/get-shit-done/bin/gsd-tools.cjs" init progress`
- `node "$HOME/.codex/get-shit-done/bin/gsd-tools.cjs" phase-plan-index 105`
- `uv run pytest -q tests/meta`
- `uv run ruff check .`
- `uv run mypy`
- `uv run python scripts/check_architecture_policy.py --check`
- `uv run python scripts/check_markdown_links.py`
- `uv run pytest -q`

</verification_outline>
