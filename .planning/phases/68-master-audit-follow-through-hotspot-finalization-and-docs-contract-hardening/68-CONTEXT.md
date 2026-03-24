# Phase 68: Repository-wide review follow-through, hotspot finalization, and docs contract hardening - Context

**Gathered:** 2026-03-24
**Status:** Ready for planning
**Source:** refreshed repo-wide architecture/code/docs/governance audit + Phase 46 / 58 historical audit evidence

<domain>
## Phase Boundary

Phase 68 turns the latest full-repository review into one formal execution route:
- a handful of production hotspots are still architecturally correct but denser than ideal, especially telemetry/message-processing/share-flow/OTA-query/runtime-infra families
- a few localized residual stories still make the repo feel “not fully finished”, such as small compat wrappers, import cycles, stale aliases, or duplicated troubleshooting/release guidance
- public docs / metadata / release examples no longer fully tell one machine-checkable story across `README*`, `manifest.json`, `pyproject.toml`, `CHANGELOG.md`, `docs/README.md`, issue templates, and related guards
- the user explicitly asked for a full-spectrum review that must flow through GSD planning, cross-AI review, and execution rather than remain a conversational audit

Out of scope for this phase:
- inventing or promising a new maintainer delegate / backup owner that does not exist in reality
- broad historical cleanup of archived `.planning/phases/**` assets
- reopening already-closed `v1.14` / `v1.15` architecture routes except where needed for truthful maintainability follow-through
</domain>

<decisions>
## Implementation Decisions

### Locked Decisions
- Keep the single north-star story intact: no new public roots, compat shells, helper-owned second stories, or reintroduced dynamic probing folklore.
- Treat the refreshed audit as authoritative input, but only ship fixes that are grounded in code/tests/docs truth and can be verified locally.
- Run the phase through `$gsd-plan-phase`, then `$gsd-review`, then `$gsd-plan-phase --reviews`, then `$gsd-execute-phase`; cross-AI review must become durable planning input, not transient chat feedback.
- Public docs / metadata must converge on one first-hop, one version signal, and one release-example story.
- Organizational constraints (single-maintainer continuity risk, no documented delegate) may be documented honestly, but must not be “fixed” by made-up guarantees.

### the agent's Discretion
- Exact inward split boundaries for hotspot modules, as long as formal-home clarity improves and no second story appears.
- Whether docs/version drift is best frozen by focused tests, scripts, or existing meta guards, as long as no new dependency is introduced.
- Final wave decomposition across code hotspots, docs contract hardening, and verification/governance sync.
</decisions>

<canonical_refs>
## Canonical References

**Downstream agents MUST read these before planning or implementing.**

### Current-story governance
- `.planning/PROJECT.md` — active `v1.16` milestone intent and archived baseline posture
- `.planning/ROADMAP.md` — `Phase 68` route, success criteria, and milestone framing
- `.planning/REQUIREMENTS.md` — `GOV-52`, `ARC-15`, `HOT-24`, `HOT-25`, `OSS-08`, `TST-18`, `QLT-26`
- `.planning/STATE.md` — current execution position and continuity posture
- `.planning/v1.15-MILESTONE-AUDIT.md` — latest archived closeout audit baseline
- `.planning/reviews/V1_15_EVIDENCE_INDEX.md` — latest archived evidence pointer
- `.planning/phases/58-repository-audit-refresh-and-next-wave-routing/58-REMEDIATION-ROADMAP.md` — prior repo-wide audit follow-through seed

### Production hotspots
- `custom_components/lipro/core/telemetry/models.py`
- `custom_components/lipro/core/telemetry/sinks.py`
- `custom_components/lipro/core/mqtt/message_processor.py`
- `custom_components/lipro/core/anonymous_share/share_client_flows.py`
- `custom_components/lipro/core/anonymous_share/share_client.py`
- `custom_components/lipro/core/api/diagnostics_api_ota.py`
- `custom_components/lipro/core/api/request_policy_support.py`
- `custom_components/lipro/runtime_infra.py`
- `custom_components/lipro/control/runtime_access_support.py`

### Docs / metadata / release truth
- `README.md`
- `README_zh.md`
- `custom_components/lipro/manifest.json`
- `pyproject.toml`
- `CHANGELOG.md`
- `docs/README.md`
- `SUPPORT.md`
- `SECURITY.md`
- `.github/CODEOWNERS`
- `.github/ISSUE_TEMPLATE/*`
- `.github/pull_request_template.md`
- `.github/workflows/ci.yml`
- `.github/workflows/release.yml`

### Governance / verification truth
- `.planning/baseline/PUBLIC_SURFACES.md`
- `.planning/baseline/DEPENDENCY_MATRIX.md`
- `.planning/baseline/VERIFICATION_MATRIX.md`
- `.planning/reviews/FILE_MATRIX.md`
- `.planning/reviews/RESIDUAL_LEDGER.md`
- `.planning/reviews/KILL_LIST.md`
- `tests/meta/test_dependency_guards.py`
- `tests/meta/test_public_surface_guards.py`
- `tests/meta/test_governance_release_contract.py`
- `tests/meta/test_version_sync.py`
</canonical_refs>

<specifics>
## Specific Ideas

- Split telemetry contract density by separating failure/outcome/shared JSON/value helpers from snapshot/view-centric structures, but keep one clear outward telemetry contract family.
- Break `MqttMessageProcessor.process_message()` into explicit stages (topic validation, payload decode, property parse, callback dispatch, outcome mapping) so errors and tests localize better.
- Reduce share/OTA/runtime-infra orchestration density by extracting localized attempt/result/build helpers instead of broad rewrites.
- Collapse README troubleshooting duplication into a shorter public summary that points at canonical docs, and freeze stale tag/version examples with focused guards.
- Add machine-checkable coverage for docs-entry/version-signal drift so the same problem cannot silently return.
</specifics>

<deferred>
## Deferred Ideas

- Removing historical `.planning/phases/**` archives from version control
- Solving single-maintainer bus factor through documentation fiction rather than real human ownership changes
- Broad data-driven redesign of all tooling/governance truth registries beyond the subset touched by this phase
</deferred>

---

*Phase: 68-master-audit-follow-through-hotspot-finalization-and-docs-contract-hardening*
*Context gathered: 2026-03-24 via refreshed repo-wide audit evidence*
