# v1.25 Evidence Index

**Purpose:** 为 `v1.25 Hotspot Inward Decomposition, Typed Boundary Hardening & Redaction Convergence` 提供机器友好的 `archived / evidence-ready` closeout 入口，集中索引 hotspot formal-home freeze、protocol/runtime typed-boundary hardening、shared redaction convergence、assurance topicization / quality freeze，以及 milestone closeout / archive handoff 的正式证据指针。
**Status:** Pull-only archived closeout index (`archived / evidence-ready`)
**Updated:** 2026-03-28

## Pull Contract

- 本文件只索引正式真源、promoted phase closeout bundle、milestone audit 与 archive snapshots；它不是新的 authority source。
- 后续任何新 milestone 都必须从这里 pull `v1.25` 已登记证据，不得重新扫描仓库拼装第二套 closeout / governance 故事。
- `.planning/v1.25-MILESTONE-AUDIT.md` 是 `v1.25` 的 verdict home；`.planning/milestones/v1.25-ROADMAP.md` 与 `.planning/milestones/v1.25-REQUIREMENTS.md` 只保留历史快照，不反向定义未来 active story。
- `Phase 90 -> 93` 的 closeout bundle 已通过 `.planning/reviews/PROMOTED_PHASE_ASSETS.md` 成为长期治理 / CI evidence；在 `v1.25` closeout 当时，archived-only route truth 固定为 `no active milestone route / latest archived baseline = v1.25`，后续下一条正式路线只能通过 `$gsd-new-milestone` 建立。

## Evidence Families

| Family | Upstream truth | Stable home | Core verify command | Phase owner | Closeout note |
|--------|----------------|-------------|---------------------|-------------|---------------|
| Hotspot formal-home freeze / protected thin-shell map | `.planning/phases/90-hotspot-routing-freeze-and-formal-home-decomposition-map/{90-01-SUMMARY.md,90-02-SUMMARY.md,90-03-SUMMARY.md,90-VERIFICATION.md,90-VALIDATION.md}`, `.planning/reviews/{FILE_MATRIX.md,RESIDUAL_LEDGER.md,KILL_LIST.md}` | `.planning/`, `tests/meta/`, `.planning/phases/90-hotspot-routing-freeze-and-formal-home-decomposition-map/` | `uv run pytest -q tests/meta/test_phase90_hotspot_map_guards.py tests/meta/test_governance_route_handoff_smoke.py tests/meta/governance_followup_route_current_milestones.py` | `90` | hotspot ownership / delete-gate / thin-shell truth 先被冻结，再允许后续 inward decomposition |
| Protocol/runtime canonicalization and typed-boundary hardening | `.planning/phases/91-protocol-runtime-decomposition-and-typed-boundary-hardening/{91-01-SUMMARY.md,91-02-SUMMARY.md,91-03-SUMMARY.md,91-VERIFICATION.md,91-VALIDATION.md}`, `custom_components/lipro/core/protocol/`, `custom_components/lipro/core/coordinator/`, `custom_components/lipro/runtime_types.py` | production homes, `tests/meta/`, `.planning/phases/91-protocol-runtime-decomposition-and-typed-boundary-hardening/` | `uv run pytest -q tests/meta/test_phase91_typed_boundary_guards.py tests/core/api/test_protocol_contract_facade_runtime.py tests/core/api/test_protocol_contract_boundary_decoders.py` | `91` | canonical protocol live path and runtime typed contracts now converge on one machine-checkable story |
| Shared redaction truth / diagnostics-report-export convergence | `.planning/phases/92-control-entity-thin-boundary-and-redaction-convergence/{92-01-SUMMARY.md,92-02-SUMMARY.md,92-03-SUMMARY.md,92-VERIFICATION.md,92-VALIDATION.md}`, `custom_components/lipro/core/utils/redaction.py`, `custom_components/lipro/control/redaction.py`, `custom_components/lipro/core/anonymous_share/{sanitize.py,report_builder.py}`, `custom_components/lipro/core/telemetry/{json_payloads.py,exporter.py}` | production homes, `tests/core/`, `tests/services/`, `tests/meta/`, `.planning/phases/92-control-entity-thin-boundary-and-redaction-convergence/` | `uv run pytest -q tests/core/anonymous_share/test_manager_submission.py tests/core/test_report_builder.py tests/core/test_diagnostics_config_entry.py tests/core/test_diagnostics_device.py tests/core/test_diagnostics_redaction.py tests/core/anonymous_share/test_sanitize.py` | `92` | diagnostics / anonymous-share / telemetry no longer maintain parallel sanitizer folklore |
| Assurance topicization / governance freeze / final quality proof | `.planning/phases/93-assurance-topicization-and-quality-freeze/{93-01-SUMMARY.md,93-02-SUMMARY.md,93-03-SUMMARY.md,93-VERIFICATION.md,93-VALIDATION.md}`, `.planning/baseline/VERIFICATION_MATRIX.md`, `.planning/codebase/TESTING.md`, `docs/developer_architecture.md` | `.planning/`, `docs/`, `tests/meta/`, `.planning/phases/93-assurance-topicization-and-quality-freeze/` | `uv run pytest -q tests/meta && uv run python scripts/check_file_matrix.py --check && uv run ruff check . && uv run mypy && uv run pytest -q` | `93` | the last full-suite regressions were closed and current-route drift fully frozen before archive promotion |
| Milestone closeout / latest archived handoff | `.planning/{PROJECT,ROADMAP,REQUIREMENTS,STATE,MILESTONES}.md`, `.planning/baseline/{AUTHORITY_MATRIX.md,PUBLIC_SURFACES.md,VERIFICATION_MATRIX.md}`, `docs/{developer_architecture.md,MAINTAINER_RELEASE_RUNBOOK.md}`, `.planning/v1.25-MILESTONE-AUDIT.md`, `.planning/reviews/V1_25_EVIDENCE_INDEX.md` | `.planning/`, `docs/`, `tests/meta/`, `.planning/milestones/` | `uv run pytest -q tests/meta && uv run python scripts/check_file_matrix.py --check` | `90-93 / milestone closeout` | current governance truth has flipped to `no active milestone route / latest archived baseline = v1.25` |

## Promoted Closeout Bundles

- `Phase 90` promoted bundle: `.planning/phases/90-hotspot-routing-freeze-and-formal-home-decomposition-map/{90-01-SUMMARY.md,90-02-SUMMARY.md,90-03-SUMMARY.md,90-VERIFICATION.md,90-VALIDATION.md}`
- `Phase 91` promoted bundle: `.planning/phases/91-protocol-runtime-decomposition-and-typed-boundary-hardening/{91-01-SUMMARY.md,91-02-SUMMARY.md,91-03-SUMMARY.md,91-VERIFICATION.md,91-VALIDATION.md}`
- `Phase 92` promoted bundle: `.planning/phases/92-control-entity-thin-boundary-and-redaction-convergence/{92-01-SUMMARY.md,92-02-SUMMARY.md,92-03-SUMMARY.md,92-VERIFICATION.md,92-VALIDATION.md}`
- `Phase 93` promoted bundle: `.planning/phases/93-assurance-topicization-and-quality-freeze/{93-01-SUMMARY.md,93-02-SUMMARY.md,93-03-SUMMARY.md,93-VERIFICATION.md,93-VALIDATION.md}`

## Archive Promotion Outputs

- Milestone audit: `.planning/v1.25-MILESTONE-AUDIT.md`
- Evidence index: `.planning/reviews/V1_25_EVIDENCE_INDEX.md`
- Archived roadmap snapshot: `.planning/milestones/v1.25-ROADMAP.md`
- Archived requirements snapshot: `.planning/milestones/v1.25-REQUIREMENTS.md`

## Cross-Surface Integration

- planning governance-route contract family 现共同承认 `active_milestone = null`、latest archived baseline = `v1.25`、previous archived baseline = `v1.24` 与 `default next = $gsd-new-milestone`。
- `docs/MAINTAINER_RELEASE_RUNBOOK.md` 现只指向 `.planning/reviews/V1_25_EVIDENCE_INDEX.md` 与 `.planning/v1.25-MILESTONE-AUDIT.md` 作为 latest archived pointer / verdict home。
- `docs/developer_architecture.md`、`PUBLIC_SURFACES.md`、`AUTHORITY_MATRIX.md` 与 `VERIFICATION_MATRIX.md` 已共同冻结 `v1.25` archive promotion 后的 archived-only route truth。
- `tests/meta/governance_current_truth.py`、`tests/meta/governance_followup_route_current_milestones.py`、`tests/meta/governance_milestone_archives_truth.py`、`tests/meta/governance_milestone_archives_assets.py`、`tests/meta/test_governance_bootstrap_smoke.py` 与 `tests/meta/test_governance_route_handoff_smoke.py` 共同守卫 latest archived pointer、promoted evidence 与 handoff route 不回退。
