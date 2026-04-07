# v1.29 Evidence Index

**Purpose:** 为 `v1.29 Root Adapter Thinning, Test Topology Second Pass & Terminology Contract Normalization` 提供机器友好的 `archived / evidence-ready` closeout 入口，集中索引 root adapter thinning、test topology second pass、terminology contract normalization、service-router/runtime second-pass split，以及 governance rule datafication / milestone closeout handoff 的正式证据指针。
**Status:** Pull-only archived closeout index (`archived / evidence-ready`)
**Updated:** 2026-03-30

## Pull Contract

- 本文件只索引正式真源、promoted phase closeout bundle、milestone audit 与 archive snapshots；它不是新的 authority source。
- 后续任何新 milestone 都必须从这里 pull `v1.29` 已登记证据，不得重新扫描仓库拼装第二套 closeout / governance 故事。
- `.planning/v1.29-MILESTONE-AUDIT.md` 是 `v1.29` 的 verdict home；`.planning/milestones/v1.29-ROADMAP.md` 与 `.planning/milestones/v1.29-REQUIREMENTS.md` 只保留历史快照，不反向定义未来 active story。
- `Phase 103 -> 105` 的 closeout bundle 已通过 `.planning/reviews/PROMOTED_PHASE_ASSETS.md` 成为长期治理 / CI evidence；`v1.29` closeout 后，archived-only route truth 固定为 `no active milestone route / latest archived baseline = v1.29`，后续下一条正式路线只能通过 `$gsd-new-milestone` 建立。

## Evidence Families

| Family | Upstream truth | Stable home | Core verify command | Phase owner | Closeout note |
|--------|----------------|-------------|---------------------|-------------|---------------|
| Root adapter thinning / test topology second pass / terminology contract | `.planning/phases/103-root-adapter-thinning-test-topology-second-pass-and-terminology-contract-normalization/{103-01-SUMMARY.md,103-02-SUMMARY.md,103-03-SUMMARY.md,103-VERIFICATION.md,103-VALIDATION.md}`, `custom_components/lipro/control/entry_root_support.py`, `tests/{topicized_collection.py,coordinator_double.py}`, `docs/adr/0005-entry-surface-terminology-contract.md` | `.planning/phases/103-*`, `custom_components/lipro/control/`, `tests/`, `docs/adr/` | `uv run pytest -q tests/meta/test_phase103_root_thinning_guards.py tests/core/test_init.py tests/core/test_init_service_handlers.py` | `103` | root adapter、fixture topology 与 terminology contract 已冻结为 predecessor-visible archived evidence |
| Service-router family split / command-runtime outcome support | `.planning/phases/104-service-router-family-split-and-command-runtime-second-pass-decomposition/{104-01-SUMMARY.md,104-02-SUMMARY.md,104-03-SUMMARY.md,104-VERIFICATION.md,104-VALIDATION.md}`, `custom_components/lipro/control/service_router_{command,schedule,share,diagnostics,maintenance}_handlers.py`, `custom_components/lipro/core/coordinator/runtime/command_runtime_outcome_support.py` | `.planning/phases/104-*`, `custom_components/lipro/control/`, `custom_components/lipro/core/coordinator/runtime/` | `uv run pytest -q tests/meta/test_phase104_service_router_runtime_split_guards.py tests/services/test_services_registry.py tests/services/test_service_resilience.py` | `104` | service-router/runtime second-pass split 已冻结为 focused predecessor bundle，不再承担 current selector 职责 |
| Governance rule datafication / latest archived closeout handoff | `.planning/phases/105-governance-rule-datafication-and-milestone-freeze/{105-01-SUMMARY.md,105-02-SUMMARY.md,105-03-SUMMARY.md,105-SUMMARY.md,105-VERIFICATION.md,105-VALIDATION.md}`, `.planning/{PROJECT,ROADMAP,REQUIREMENTS,STATE,MILESTONES}.md`, `.planning/v1.29-MILESTONE-AUDIT.md`, `.planning/reviews/V1_29_EVIDENCE_INDEX.md`, `.planning/milestones/{v1.29-ROADMAP.md,v1.29-REQUIREMENTS.md}` | `.planning/`, `.planning/reviews/`, `.planning/milestones/`, `docs/`, `tests/meta/` | `uv run pytest -q tests/meta && uv run python scripts/check_file_matrix.py --check` | `105 / milestone closeout` | governance route truth 已翻转为 archived-only baseline `v1.29`，下一步只能经 `$gsd-new-milestone` 建立新 current route |

## Promoted Closeout Bundles

- `Phase 103` promoted bundle: `.planning/phases/103-root-adapter-thinning-test-topology-second-pass-and-terminology-contract-normalization/{103-01-SUMMARY.md,103-02-SUMMARY.md,103-03-SUMMARY.md,103-VERIFICATION.md,103-VALIDATION.md}`
- `Phase 104` promoted bundle: `.planning/phases/104-service-router-family-split-and-command-runtime-second-pass-decomposition/{104-01-SUMMARY.md,104-02-SUMMARY.md,104-03-SUMMARY.md,104-VERIFICATION.md,104-VALIDATION.md}`
- `Phase 105` promoted bundle: `.planning/phases/105-governance-rule-datafication-and-milestone-freeze/{105-01-SUMMARY.md,105-02-SUMMARY.md,105-03-SUMMARY.md,105-SUMMARY.md,105-VERIFICATION.md,105-VALIDATION.md}`

## Milestone Closeout Bundle

- Milestone audit: `.planning/v1.29-MILESTONE-AUDIT.md`
- Evidence index: `.planning/reviews/V1_29_EVIDENCE_INDEX.md`
- Archived roadmap snapshot: `.planning/milestones/v1.29-ROADMAP.md`
- Archived requirements snapshot: `.planning/milestones/v1.29-REQUIREMENTS.md`
- Promoted allowlist home: `.planning/reviews/PROMOTED_PHASE_ASSETS.md`
- Archived closeout route truth: `no active milestone route / latest archived baseline = v1.29`

## Carry-Forward Notes

- `maintainer / delegate continuity` 仍是组织治理层风险；它已诚实登记为 next-milestone carry-forward，而不是 `v1.29` blocker。
- `v1.28` 及更早 milestone 的 archived evidence 继续只承担 pull-only predecessor / historical baseline 身份；`v1.29` closeout 不反向改写它们的 verdict home。
