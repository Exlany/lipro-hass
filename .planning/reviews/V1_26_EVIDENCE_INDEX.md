# v1.26 Evidence Index

**Purpose:** 为 `v1.26 Terminal Architecture Audit Follow-through, Typed Mapping Retirement & Hotspot Decomposition` 提供机器友好的 `archived / evidence-ready` closeout 入口，集中索引 typed-boundary contraction、schedule/runtime inward decomposition、shared sanitizer burn-down、governance freeze，以及 milestone closeout / archive handoff 的正式证据指针。
**Status:** Pull-only archived closeout index (`archived / evidence-ready`)
**Updated:** 2026-03-28

## Pull Contract

- 本文件只索引正式真源、promoted phase closeout bundle、milestone audit 与 archive snapshots；它不是新的 authority source。
- 后续任何新 milestone 都必须从这里 pull `v1.26` 已登记证据，不得重新扫描仓库拼装第二套 closeout / governance 故事。
- `.planning/v1.26-MILESTONE-AUDIT.md` 是 `v1.26` 的 verdict home；`.planning/milestones/v1.26-ROADMAP.md` 与 `.planning/milestones/v1.26-REQUIREMENTS.md` 只保留历史快照，不反向定义未来 active story。
- `Phase 94 -> 97` 的 closeout bundle 已通过 `.planning/reviews/PROMOTED_PHASE_ASSETS.md` 成为长期治理 / CI evidence；`v1.26` closeout 后，archived-only route truth 固定为 `no active milestone route / latest archived baseline = v1.26`，后续下一条正式路线只能通过 `$gsd-new-milestone` 建立。

## Evidence Families

| Family | Upstream truth | Stable home | Core verify command | Phase owner | Closeout note |
|--------|----------------|-------------|---------------------|-------------|---------------|
| Typed payload contraction / domain-bag narrowing | `.planning/phases/94-typed-payload-contraction-and-domain-bag-narrowing/{94-01-SUMMARY.md,94-02-SUMMARY.md,94-03-SUMMARY.md,94-VERIFICATION.md,94-VALIDATION.md}`, `custom_components/lipro/{domain_data.py,diagnostics.py,entities/base.py}`, `custom_components/lipro/control/diagnostics_surface.py`, `custom_components/lipro/core/api/{command_api_service.py,status_fallback.py,transport_core.py}`, `custom_components/lipro/core/utils/property_normalization.py` | production homes, `tests/meta/`, `.planning/phases/94-typed-payload-contraction-and-domain-bag-narrowing/` | `uv run pytest -q tests/meta/test_phase94_typed_boundary_guards.py tests/meta/test_governance_route_handoff_smoke.py` | `94` | broad mapping / `Any` seam 已退回 formal typed contract，并由 focused guards 冻结 |
| Schedule/runtime and boundary hotspot inward decomposition | `.planning/phases/95-schedule-runtime-and-boundary-hotspot-inward-decomposition/{95-01-SUMMARY.md,95-02-SUMMARY.md,95-03-SUMMARY.md,95-VERIFICATION.md,95-VALIDATION.md}`, `custom_components/lipro/core/api/schedule_service.py`, `custom_components/lipro/core/protocol/boundary/rest_decoder_support.py`, runtime helper homes | production homes, `tests/meta/`, `.planning/phases/95-schedule-runtime-and-boundary-hotspot-inward-decomposition/` | `uv run pytest -q tests/meta/test_phase95_hotspot_decomposition_guards.py tests/meta/test_governance_route_handoff_smoke.py` | `95` | hotspot inward split 继续沿 formal-home map 发生，没有 helper 回升为新 root |
| Shared redaction / telemetry / anonymous-share sanitizer convergence | `.planning/phases/96-redaction-telemetry-and-anonymous-share-sanitizer-burndown/{96-01-SUMMARY.md,96-02-SUMMARY.md,96-03-SUMMARY.md,96-VERIFICATION.md,96-VALIDATION.md}`, `custom_components/lipro/control/redaction.py`, `custom_components/lipro/core/telemetry/exporter.py`, `custom_components/lipro/core/anonymous_share/{manager.py,sanitize.py}`, `custom_components/lipro/core/utils/redaction.py` | production homes, `tests/core/`, `tests/meta/`, `.planning/phases/96-redaction-telemetry-and-anonymous-share-sanitizer-burndown/` | `uv run pytest -q tests/meta/test_phase96_sanitizer_burndown_guards.py tests/core/anonymous_share/test_sanitize.py tests/core/telemetry/test_exporter.py` | `96` | shared redaction truth 未被 helper 分叉，unknown secret-like key 继续 fail-closed |
| Governance / open-source contract sync / assurance freeze | `.planning/phases/97-governance-open-source-contract-sync-and-assurance-freeze/{97-01-SUMMARY.md,97-02-SUMMARY.md,97-03-SUMMARY.md,97-VERIFICATION.md,97-VALIDATION.md}`, `.planning/{PROJECT.md,ROADMAP.md,REQUIREMENTS.md,STATE.md,MILESTONES.md}`, `.planning/baseline/{AUTHORITY_MATRIX.md,PUBLIC_SURFACES.md,VERIFICATION_MATRIX.md}`, `docs/{developer_architecture.md,MAINTAINER_RELEASE_RUNBOOK.md}`, `tests/meta/` | `.planning/`, `docs/`, `tests/meta/`, `.planning/phases/97-governance-open-source-contract-sync-and-assurance-freeze/` | `uv run pytest -q tests/meta && uv run python scripts/check_file_matrix.py --check && uv run ruff check . && uv run mypy` | `97` | route contract、developer guidance、archive pointer 与 quality proof 已冻结为单一 archived-only closeout story |
| Milestone closeout / latest archived handoff | `.planning/{PROJECT,ROADMAP,REQUIREMENTS,STATE,MILESTONES}.md`, `.planning/v1.26-MILESTONE-AUDIT.md`, `.planning/reviews/V1_26_EVIDENCE_INDEX.md`, `.planning/milestones/{v1.26-ROADMAP.md,v1.26-REQUIREMENTS.md}` | `.planning/`, `docs/`, `tests/meta/`, `.planning/milestones/` | `uv run pytest -q tests/meta && uv run python scripts/check_file_matrix.py --check` | `94-97 / milestone closeout` | current governance truth 已翻转为 `no active milestone route / latest archived baseline = v1.26` |

## Promoted Closeout Bundles

- `Phase 94` promoted bundle: `.planning/phases/94-typed-payload-contraction-and-domain-bag-narrowing/{94-01-SUMMARY.md,94-02-SUMMARY.md,94-03-SUMMARY.md,94-VERIFICATION.md,94-VALIDATION.md}`
- `Phase 95` promoted bundle: `.planning/phases/95-schedule-runtime-and-boundary-hotspot-inward-decomposition/{95-01-SUMMARY.md,95-02-SUMMARY.md,95-03-SUMMARY.md,95-VERIFICATION.md,95-VALIDATION.md}`
- `Phase 96` promoted bundle: `.planning/phases/96-redaction-telemetry-and-anonymous-share-sanitizer-burndown/{96-01-SUMMARY.md,96-02-SUMMARY.md,96-03-SUMMARY.md,96-VERIFICATION.md,96-VALIDATION.md}`
- `Phase 97` promoted bundle: `.planning/phases/97-governance-open-source-contract-sync-and-assurance-freeze/{97-01-SUMMARY.md,97-02-SUMMARY.md,97-03-SUMMARY.md,97-VERIFICATION.md,97-VALIDATION.md}`

## Milestone Closeout Bundle

- Milestone audit: `.planning/v1.26-MILESTONE-AUDIT.md`
- Evidence index: `.planning/reviews/V1_26_EVIDENCE_INDEX.md`
- Archived roadmap snapshot: `.planning/milestones/v1.26-ROADMAP.md`
- Archived requirements snapshot: `.planning/milestones/v1.26-REQUIREMENTS.md`
- Promoted allowlist home: `.planning/reviews/PROMOTED_PHASE_ASSETS.md`
- Archived closeout route truth: `no active milestone route / latest archived baseline = v1.26`

## Carry-Forward Notes

- `outlet_power` legacy side-car fallback 的最终物理删除仍依赖零命中 / 零写回证据；它已诚实登记为 next-milestone carry-forward，而不是 `v1.26` blocker。
- 组织层 continuity / delegate 风险继续只做诚实登记，不伪装成已被本轮代码彻底消灭。
