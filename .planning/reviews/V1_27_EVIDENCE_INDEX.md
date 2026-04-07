# v1.27 Evidence Index

**Purpose:** 为 `v1.27 Final Carry-Forward Eradication & Route Reactivation` 提供机器友好的 `archived / evidence-ready` closeout 入口，集中索引 carry-forward eradication、runtime/schedule predecessor freeze、anonymous-share / REST-boundary hotspot decomposition、governance route handoff 与 milestone closeout / archive handoff 的正式证据指针。
**Status:** Pull-only archived closeout index (`archived / evidence-ready`)
**Updated:** 2026-03-28

## Pull Contract

- 本文件只索引正式真源、promoted phase closeout bundle、milestone audit 与 archive snapshots；它不是新的 authority source。
- 后续任何新 milestone 都必须从这里 pull `v1.27` 已登记证据，不得重新扫描仓库拼装第二套 closeout / governance 故事。
- `.planning/v1.27-MILESTONE-AUDIT.md` 是 `v1.27` 的 verdict home；`.planning/milestones/v1.27-ROADMAP.md` 与 `.planning/milestones/v1.27-REQUIREMENTS.md` 只保留历史快照，不反向定义未来 active story。
- `Phase 98 -> 101` 的 closeout bundle 已通过 `.planning/reviews/PROMOTED_PHASE_ASSETS.md` 成为长期治理 / CI evidence；`v1.27` closeout 后，archived-only route truth 固定为 `no active milestone route / latest archived baseline = v1.27`，后续下一条正式路线只能通过 `$gsd-new-milestone` 建立。

## Evidence Families

| Family | Upstream truth | Stable home | Core verify command | Phase owner | Closeout note |
|--------|----------------|-------------|---------------------|-------------|---------------|
| Carry-forward eradication / route reactivation | `.planning/phases/98-carry-forward-eradication-route-reactivation-and-closeout-proof/{98-01-SUMMARY.md,98-02-SUMMARY.md,98-03-SUMMARY.md,98-VERIFICATION.md,98-VALIDATION.md}`, `custom_components/lipro/core/device/device.py`, `tests/meta/test_phase98_route_reactivation_guards.py` | production homes, `.planning/phases/98-*`, `tests/meta/` | `uv run pytest -q tests/meta/test_phase98_route_reactivation_guards.py tests/meta/test_governance_route_handoff_smoke.py` | `98` | carry-forward eradication、route reactivation 与 next-step routing 已冻结为 predecessor closeout proof |
| Runtime hotspot support extraction | `.planning/phases/99-runtime-hotspot-support-extraction-and-terminal-audit-freeze/{99-01-SUMMARY.md,99-02-SUMMARY.md,99-03-SUMMARY.md,99-VERIFICATION.md,99-VALIDATION.md}`, `custom_components/lipro/core/api/{status_fallback.py,status_fallback_support.py}`, `custom_components/lipro/core/coordinator/runtime/{command_runtime.py,command_runtime_support.py}` | production homes, `.planning/phases/99-*`, `tests/core/`, `tests/meta/` | `uv run pytest -q tests/meta/test_phase99_runtime_hotspot_support_guards.py tests/core/api/test_api_status_service_fallback.py tests/core/coordinator/runtime/test_command_runtime_support.py` | `99` | outward formal homes 仍稳定，support mechanics inward split 后没有长出第二 runtime/protocol story |
| MQTT/schedule support extraction | `.planning/phases/100-mqtt-runtime-and-schedule-service-support-extraction-freeze/{100-01-SUMMARY.md,100-02-SUMMARY.md,100-03-SUMMARY.md,100-VERIFICATION.md,100-VALIDATION.md}`, `custom_components/lipro/core/coordinator/runtime/{mqtt_runtime.py,mqtt_runtime_support.py}`, `custom_components/lipro/core/api/{schedule_service.py,schedule_service_support.py}` | production homes, `.planning/phases/100-*`, `tests/core/`, `tests/meta/` | `uv run pytest -q tests/meta/test_phase100_runtime_schedule_support_guards.py tests/core/api/test_api_schedule_service.py tests/core/coordinator/runtime/test_mqtt_runtime_support.py` | `100` | runtime/API support seams 继续 inward split，同时作为 `Phase 101` 的 predecessor evidence 保持 pull-only 可审计 |
| Anonymous-share manager / REST-boundary hotspot decomposition | `.planning/phases/101-anonymous-share-manager-and-rest-decoder-hotspot-decomposition-freeze/{101-01-SUMMARY.md,101-02-SUMMARY.md,101-03-SUMMARY.md,101-VERIFICATION.md,101-VALIDATION.md}`, `custom_components/lipro/core/anonymous_share/{manager.py,manager_submission.py,manager_support.py}`, `custom_components/lipro/core/protocol/boundary/{rest_decoder.py,rest_decoder_support.py}`, `custom_components/lipro/core/api/{mqtt_api_service.py,rest_facade_endpoint_methods.py}` | production homes, `.planning/phases/101-*`, `tests/core/`, `tests/meta/` | `uv run pytest -q tests/meta/test_phase101_anonymous_share_rest_boundary_guards.py tests/core/anonymous_share/test_manager_submission.py tests/core/api/test_protocol_contract_boundary_decoders.py` | `101` | formal-home / boundary-truth cleanup 已收口为 `v1.27` 最终 current-route freeze，并在 closeout 后成为 latest archived hotspot bundle |
| Milestone closeout / latest archived handoff | `.planning/{PROJECT,ROADMAP,REQUIREMENTS,STATE,MILESTONES}.md`, `.planning/v1.27-MILESTONE-AUDIT.md`, `.planning/reviews/V1_27_EVIDENCE_INDEX.md`, `.planning/milestones/{v1.27-ROADMAP.md,v1.27-REQUIREMENTS.md}` | `.planning/`, `docs/`, `tests/meta/`, `.planning/milestones/` | `uv run pytest -q tests/meta && uv run python scripts/check_file_matrix.py --check` | `98-101 / milestone closeout` | governance route truth 已翻转为 archived-only baseline `v1.27`，下一步只能经 `$gsd-new-milestone` 建立新 current route |

## Promoted Closeout Bundles

- `Phase 98` promoted bundle: `.planning/phases/98-carry-forward-eradication-route-reactivation-and-closeout-proof/{98-01-SUMMARY.md,98-02-SUMMARY.md,98-03-SUMMARY.md,98-VERIFICATION.md,98-VALIDATION.md}`
- `Phase 99` promoted bundle: `.planning/phases/99-runtime-hotspot-support-extraction-and-terminal-audit-freeze/{99-01-SUMMARY.md,99-02-SUMMARY.md,99-03-SUMMARY.md,99-VERIFICATION.md,99-VALIDATION.md}`
- `Phase 100` promoted bundle: `.planning/phases/100-mqtt-runtime-and-schedule-service-support-extraction-freeze/{100-01-SUMMARY.md,100-02-SUMMARY.md,100-03-SUMMARY.md,100-VERIFICATION.md,100-VALIDATION.md}`
- `Phase 101` promoted bundle: `.planning/phases/101-anonymous-share-manager-and-rest-decoder-hotspot-decomposition-freeze/{101-01-SUMMARY.md,101-02-SUMMARY.md,101-03-SUMMARY.md,101-VERIFICATION.md,101-VALIDATION.md}`

## Milestone Closeout Bundle

- Milestone audit: `.planning/v1.27-MILESTONE-AUDIT.md`
- Evidence index: `.planning/reviews/V1_27_EVIDENCE_INDEX.md`
- Archived roadmap snapshot: `.planning/milestones/v1.27-ROADMAP.md`
- Archived requirements snapshot: `.planning/milestones/v1.27-REQUIREMENTS.md`
- Promoted allowlist home: `.planning/reviews/PROMOTED_PHASE_ASSETS.md`
- Archived closeout route truth: `no active milestone route / latest archived baseline = v1.27`

## Carry-Forward Notes

- `maintainer / delegate continuity` 仍是组织治理层风险；它已诚实登记为 next-milestone carry-forward，而不是 `v1.27` blocker。
- `v1.26` 及更早 milestone 的 archived evidence 继续只承担 pull-only baseline 身份；`v1.27` closeout 不反向改写它们的 verdict home。
