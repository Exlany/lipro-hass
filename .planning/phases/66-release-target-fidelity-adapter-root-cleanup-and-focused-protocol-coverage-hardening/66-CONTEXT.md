# Phase 66: Release target fidelity, adapter-root cleanup, and focused protocol coverage hardening - Context

**Gathered:** 2026-03-23
**Status:** Ready for planning
**Source:** Fresh repository audit + post-Phase-65 residual review

<domain>
## Phase Boundary

Phase 66 closes the highest-leverage residuals surfaced after Phase 65:
- release workflow must validate the same ref it later builds/publishes
- baseline / review / README current-story drift must be removed
- HA root adapters must keep one thin explicit story without duplicated stub folklore
- protocol transport / service / root seams need focused regression coverage instead of relying on mega matrix tests

Out of scope for this phase:
- branch-coverage enablement repo-wide
- anonymous-share developer-feedback outcome reshaping
- outlet-power primitive sidecar retirement
- runtime-plane HA issue-registry decoupling
</domain>

<decisions>
## Implementation Decisions

### Locked Decisions
- Release validation and release build must operate on the same `refs/tags/${RELEASE_TAG}` truth for tagged and manual release paths.
- Baseline/review/docs current-story drift is a governance bug, not optional prose cleanup.
- `custom_components/lipro/__init__.py`, `custom_components/lipro/sensor.py`, and `custom_components/lipro/select.py` must remain thin adapters; duplicated Protocol blocks and runtime-only dynamic import folklore should be removed where explicit imports are safe.
- Focused tests should be added for `RestTransportExecutor`, `CoordinatorProtocolService`, `LiproProtocolFacade`, and `LiproMqttFacade`; do not grow meta guards to compensate for missing production-facing regressions.
- Public release/install examples should stop encoding one stale literal release tag as the canonical doc story.

### Claude's Discretion
- Exact plan granularity and wave assignment.
- Whether protocol focused tests land as one or multiple files, so long as failure localization improves.
- Whether adapter cleanup uses direct imports or another equally explicit formal import path that preserves test patching behavior.
</decisions>

<canonical_refs>
## Canonical References

**Downstream agents MUST read these before planning or implementing.**

### Current-story governance
- `.planning/PROJECT.md` — active milestone intent and north-star fit
- `.planning/ROADMAP.md` — phase routing and success criteria
- `.planning/REQUIREMENTS.md` — Phase 66 requirement IDs
- `.planning/STATE.md` — current milestone status / next focus
- `.planning/baseline/PUBLIC_SURFACES.md` — canonical public-surface truth
- `.planning/baseline/AUTHORITY_MATRIX.md` — authority/freshness truth
- `.planning/baseline/VERIFICATION_MATRIX.md` — verification contract and promoted evidence rules
- `.planning/reviews/README.md` — reviews workspace description

### Release/docs/governance targets
- `.github/workflows/ci.yml` — reusable CI gate contract
- `.github/workflows/release.yml` — tagged/manual release path to harden
- `README.md` — public release/install guidance
- `README_zh.md` — mirrored public release/install guidance
- `docs/README.md` — docs index active-route pointer
- `tests/meta/test_governance_release_contract.py` — release/docs/meta guard expectations

### Adapter-root cleanup
- `custom_components/lipro/__init__.py` — HA root adapter
- `custom_components/lipro/sensor.py` — sensor platform adapter
- `custom_components/lipro/select.py` — select platform adapter
- `custom_components/lipro/entities/base.py` — explicit entity base import home
- `tests/core/test_init.py` and `tests/core/test_init_runtime_setup_entry.py` — top-level adapter regression coverage

### Focused protocol coverage
- `custom_components/lipro/core/api/transport_executor.py` — lowest coverage protocol transport hotspot
- `custom_components/lipro/core/coordinator/services/protocol_service.py` — thin runtime protocol service seam
- `custom_components/lipro/core/protocol/facade.py` — unified protocol root
- `custom_components/lipro/core/protocol/mqtt_facade.py` — MQTT child façade
- `tests/core/api/test_api_transport_executor.py` — existing focused transport tests
- `tests/core/api/test_protocol_contract_matrix.py` — current mega matrix to complement, not expand
</canonical_refs>

<specifics>
## Specific Ideas

- Add a reusable release-ref input to `ci.yml` and have `release.yml` validate the exact tag/ref instead of branch HEAD.
- Replace README literal `v1.0.0` examples with a freshness-safe placeholder contract plus tests that validate structure instead of one hard-coded version.
- Remove duplicated Protocol blocks from `custom_components/lipro/__init__.py`.
- Prefer explicit runtime imports in `sensor.py` / `select.py` if they do not reintroduce import cycles.
- Add dedicated tests for protocol root/service/transport seams and keep the mega matrix as a higher-level contract layer.
</specifics>

<deferred>
## Deferred Ideas

- Branch coverage enablement and branch-aware CI gates
- Runtime-plane issue-registry decoupling
- Outlet power legacy sidecar retirement
- Developer-feedback outcome-native outward payload reshape
</deferred>

---

*Phase: 66-release-target-fidelity-adapter-root-cleanup-and-focused-protocol-coverage-hardening*
*Context gathered: 2026-03-23 via fresh repository audit*
