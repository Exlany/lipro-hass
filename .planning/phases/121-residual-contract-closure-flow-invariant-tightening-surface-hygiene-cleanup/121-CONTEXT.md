# Phase 121: residual contract closure, flow invariant tightening & surface hygiene cleanup - Context

**Status:** planning-ready
**Milestone:** `v1.34 Terminal Audit Closure, Contract Hardening & Governance Truth Slimming`
**Current route:** `v1.34 active milestone route / starting from latest archived baseline = v1.33`
**Default next command:** `$gsd-execute-phase 121`

## Phase Boundary

**In scope**
- close the remaining raw-coordinator seam inside `custom_components/lipro/control/runtime_access*` and related control-plane consumers so runtime read-models stop re-exporting coordinator internals
- harden `custom_components/lipro/flow/login.py` so config-entry projection rejects malformed auth-session payloads instead of silently defaulting tokens and `user_id`
- deduplicate `custom_components/lipro/flow/submission.py` existing-entry validation while preserving `reauth` vs `reconfigure` outward error semantics
- remove default `scripts/lint` changed-surface routing from `Phase 113`-named guard ownership and move it to phase-agnostic assurance truth
- tighten any low-risk public-surface hygiene revealed by the above work, without inventing a new root or broad compat export

**Out of scope**
- adding product features, services, platforms, or any second runtime/control/protocol root
- changing `Coordinator` public home, archived milestone assets, or historical phase evidence semantics
- broad package API redesign outside the touched runtime-access / flow / toolchain slice

## Implementation Decisions

### Locked decisions
- `custom_components/lipro/control/runtime_access.py` remains the only formal control-plane runtime read home; helper clusters stay inward-only and must not regrow a raw coordinator bridge through read-model views.
- malformed auth/session payloads must fail closed as `invalid_response`; empty-string or zero-value projection is not acceptable as a config-entry truth.
- `reauth` and `reconfigure` may keep different outward error placement (`base` vs field errors), but the entry-bound validation path must reuse one internal invariant chain.
- changed-surface assurance in `scripts/lint` must point at a phase-agnostic guard home; historical `Phase 113` tests may remain archival evidence but cannot keep owning the live default route.

### the agent's Discretion
- choose the narrowest runtime-access view refactor that removes raw coordinator exposure without destabilizing legitimate raw-coordinator helpers (`get_entry_runtime_coordinator`, `iter_runtime_coordinators`, `iter_runtime_entry_coordinators`)
- choose whether flow projection strictness is enforced in `ConfigEntryLoginProjection`, `config_flow.py`, or both, as long as the outward error mapping stays single-source and explicit
- decide the smallest public-surface hygiene tweak worth landing with this phase (for example, trimming unnecessary aggregate exports) only if it is directly supported by current baseline truth and focused guards

## Canonical References

### North-star and governance truth
- `AGENTS.md`
- `docs/NORTH_STAR_TARGET_ARCHITECTURE.md`
- `.planning/PROJECT.md`
- `.planning/ROADMAP.md`
- `.planning/REQUIREMENTS.md`
- `.planning/STATE.md`
- `.planning/MILESTONES.md`
- `.planning/baseline/PUBLIC_SURFACES.md`

### Runtime / flow / tooling hotspots
- `custom_components/lipro/control/runtime_access.py`
- `custom_components/lipro/control/runtime_access_types.py`
- `custom_components/lipro/control/runtime_access_support_views.py`
- `custom_components/lipro/control/runtime_access_support_devices.py`
- `custom_components/lipro/control/developer_router_support.py`
- `custom_components/lipro/flow/login.py`
- `custom_components/lipro/config_flow.py`
- `custom_components/lipro/flow/submission.py`
- `custom_components/lipro/control/__init__.py`
- `scripts/lint`
- `tests/meta/test_phase113_hotspot_assurance_guards.py`

### Focused guards / tests
- `tests/core/test_runtime_access.py`
- `tests/meta/test_phase112_formal_home_governance_guards.py`
- `tests/meta/test_runtime_contract_truth.py`
- `tests/flows/test_flow_submission.py`
- `tests/flows/test_config_flow_user.py`
- `tests/flows/test_config_flow_reauth.py`
- `tests/flows/test_config_flow_reconfigure.py`
- `tests/meta/toolchain_truth_ci_contract.py`
- `tests/meta/test_phase89_tooling_decoupling_guards.py`

## Specific Ideas

- `121-01` should remove raw coordinator leakage from control read-models while preserving dedicated raw-coordinator access verbs for legitimate control/service consumers.
- `121-02` should make config-flow projection fail closed on malformed auth-session data and fold reauth/reconfigure validator duplication into one internal invariant path.
- `121-03` should move live changed-surface assurance to a neutral meta guard home and only keep `Phase 113` references where they are intentionally historical.

## Deferred Ideas

- wider package-level export slimming outside the touched control/runtime slice remains deferred unless a focused guard proves it is part of the same residual.
- repo-external continuity, delegate identity, and non-GitHub fallback governance remain external blockers and are not reopened here.

