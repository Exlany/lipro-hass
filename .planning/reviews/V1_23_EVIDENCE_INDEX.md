# v1.23 Evidence Index

**Purpose:** 为 `v1.23 Repository-Wide Terminal Code Audit, Residual Eradication & Closeout Truth Freeze` 提供机器友好的 `archived / evidence-ready` closeout入口，集中索引 terminal repo audit、production residual eradication、assurance hotspot no-regrowth freeze，以及 governance sync / archive promotion 的正式证据指针。
**Status:** Pull-only archived closeout index (`archived / evidence-ready`)
**Updated:** 2026-03-27

## Pull Contract

- 本文件只索引正式真源、promoted phase closeout bundles、milestone audit 与 archive snapshots；它不是新的 authority source。
- 后续任何新 milestone 都必须从这里 pull `v1.23` 已登记证据，不得重新扫描仓库拼装第二套 closeout / governance 故事。
- `.planning/v1.23-MILESTONE-AUDIT.md` 是 `v1.23` 的 verdict home；`.planning/milestones/v1.23-ROADMAP.md` 与 `.planning/milestones/v1.23-REQUIREMENTS.md` 只保留历史快照，不反向定义未来 active story。
- `Phase 85 / 86 / 87 / 88` 的 closeout bundles 已通过 `.planning/reviews/PROMOTED_PHASE_ASSETS.md` 成为长期治理 / CI evidence；在 `v1.23` closeout 当时，archived-only route truth 固定为 `no active milestone route / latest archived baseline = v1.23`，后续下一条正式路线只能通过 `$gsd-new-milestone` 建立。

## Evidence Families

| Family | Upstream truth | Stable home | Core verify command | Phase owner | Closeout note |
|--------|----------------|-------------|---------------------|-------------|---------------|
| Terminal repo-wide audit / routed residual inventory | `.planning/reviews/V1_23_TERMINAL_AUDIT.md`, `.planning/reviews/RESIDUAL_LEDGER.md`, `.planning/reviews/KILL_LIST.md`, `.planning/phases/85-terminal-audit-refresh-and-residual-routing/` | `.planning/reviews/`, `.planning/phases/85-terminal-audit-refresh-and-residual-routing/` | `uv run pytest -q tests/meta/test_phase85_terminal_audit_route_guards.py tests/meta/test_governance_closeout_guards.py tests/meta/test_governance_promoted_phase_assets.py` | `85` | routed audit 继续保留 historical review artifact 身份，但 close-now / explicitly-keep 裁决已沉淀到 ledgers 与 promoted evidence |
| Production residual eradication / boundary re-tightening | `custom_components/lipro/**`, `.planning/reviews/FILE_MATRIX.md`, `.planning/phases/86-production-residual-eradication-and-boundary-re-tightening/` | production homes, `.planning/reviews/`, `.planning/phases/86-production-residual-eradication-and-boundary-re-tightening/` | `uv run pytest -q tests/core/api/test_api_diagnostics_service.py tests/core/api/test_api_diagnostics_service_*.py tests/core/coordinator/runtime/test_mqtt_runtime.py tests/core/coordinator/runtime/test_mqtt_runtime_*.py` | `86` | production-path residuals 已压回 formal/local collaborator homes，没有恢复第二条主链 |
| Assurance hotspot decomposition / no-regrowth guards | `tests/core/api/**`, `tests/core/coordinator/runtime/**`, `tests/meta/test_phase87_assurance_hotspot_guards.py`, `.planning/phases/87-assurance-hotspot-decomposition-and-no-regrowth-guards/` | assurance suites, `tests/meta/`, `.planning/phases/87-assurance-hotspot-decomposition-and-no-regrowth-guards/` | `uv run pytest -q tests/core/api/test_protocol_contract_matrix.py tests/core/api/test_protocol_contract_*.py tests/meta/test_phase87_assurance_hotspot_guards.py tests/meta/test_dependency_guards.py tests/meta/test_public_surface_guards.py` | `87` | giant truth-carrier shells 已被 topicization / thin-root 化；focused guards 冻结 no-regrowth |
| Governance sync / quality proof / archived-only route promotion | `.planning/{PROJECT,ROADMAP,REQUIREMENTS,STATE,MILESTONES}.md`, `.planning/baseline/{AUTHORITY_MATRIX.md,PUBLIC_SURFACES.md,VERIFICATION_MATRIX.md}`, `docs/MAINTAINER_RELEASE_RUNBOOK.md`, `.planning/v1.23-MILESTONE-AUDIT.md`, `.planning/reviews/V1_23_EVIDENCE_INDEX.md` | `.planning/`, `docs/`, `tests/meta/`, `.planning/phases/88-governance-sync-quality-proof-and-milestone-freeze/` | `uv run pytest -q tests/meta/test_governance_bootstrap_smoke.py tests/meta/test_governance_route_handoff_smoke.py tests/meta/test_governance_closeout_guards.py tests/meta/test_governance_milestone_archives.py tests/meta/governance_followup_route_current_milestones.py tests/meta/test_version_sync.py` | `88 / milestone closeout` | current governance truth 已翻转到 archived-only，latest archived pointer 已提升到 `.planning/reviews/V1_23_EVIDENCE_INDEX.md` |

## Promoted Closeout Bundles

- `Phase 85` promoted bundle: `.planning/phases/85-terminal-audit-refresh-and-residual-routing/{85-01-SUMMARY.md,85-02-SUMMARY.md,85-03-SUMMARY.md}`
- `Phase 86` promoted bundle: `.planning/phases/86-production-residual-eradication-and-boundary-re-tightening/{86-01-SUMMARY.md,86-02-SUMMARY.md,86-03-SUMMARY.md,86-04-SUMMARY.md,86-VALIDATION.md}`
- `Phase 87` promoted bundle: `.planning/phases/87-assurance-hotspot-decomposition-and-no-regrowth-guards/{87-01-SUMMARY.md,87-02-SUMMARY.md,87-03-SUMMARY.md,87-04-SUMMARY.md}`
- `Phase 88` promoted bundle: `.planning/phases/88-governance-sync-quality-proof-and-milestone-freeze/{88-01-SUMMARY.md,88-02-SUMMARY.md,88-03-SUMMARY.md,88-SUMMARY.md,88-VERIFICATION.md,88-VALIDATION.md}`

## Archive Promotion Outputs

- Milestone audit: `.planning/v1.23-MILESTONE-AUDIT.md`
- Evidence index: `.planning/reviews/V1_23_EVIDENCE_INDEX.md`
- Archived roadmap snapshot: `.planning/milestones/v1.23-ROADMAP.md`
- Archived requirements snapshot: `.planning/milestones/v1.23-REQUIREMENTS.md`

## Cross-Surface Integration

- planning governance-route contract family 现共同承认 `active_milestone = null`、latest archived baseline = `v1.23`、previous archived baseline = `v1.22` 与 `default next = $gsd-new-milestone`。
- `docs/MAINTAINER_RELEASE_RUNBOOK.md` 现只指向 `.planning/reviews/V1_23_EVIDENCE_INDEX.md` 与 `.planning/v1.23-MILESTONE-AUDIT.md` 作为 latest archived pointer / verdict home。
- `.planning/reviews/V1_23_TERMINAL_AUDIT.md` 保留历史 routed snapshot，`.planning/reviews/PROMOTED_PHASE_ASSETS.md` 则保留长期 evidence allowlist；两者分工明确，互不越权。
- future milestone closeout / audit / route arbitration 只能 pull 本索引登记的证据，不得回流 `Phase 85 -> 88` 的 execution trace 成新的 active truth。

## Next Step

- 当前无 active milestone route；下一条正式路线必须通过 `$gsd-new-milestone` 显式建立，而不是把 `Phase 88` closeout-ready truth 回写成新的 active story。
