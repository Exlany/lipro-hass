# Phase 67: Typed contract convergence, telemetry/toolchain hardening, and mypy closure - Context

**Gathered:** 2026-03-23
**Status:** Ready for planning
**Source:** Fresh repository audit + full `uv run mypy` evidence (`339 errors in 53 files`)

<domain>
## Phase Boundary

Phase 67 closes the remaining objective hard gap after `v1.14` archive promotion:
- telemetry models / sinks / exporter views still leak broad JSON/object contracts into formal typed seams
- control-plane telemetry bridges still return overly broad mappings instead of `TelemetryJsonValue` dictionaries
- REST/auth/endpoint ports and anonymous-share submit manager contracts still conflict with their declared Protocol surfaces
- service-handler tests, exporter tests, YAML/meta/toolchain guards, and a handful of platform tests still rely on `object`, untyped YAML imports, union indexing, or method reassignment patterns that mypy rejects
- current-story planning docs must acknowledge `v1.15 / Phase 67` as the active route and treat `mypy` as a release-quality gate rather than advisory noise

Out of scope for this phase:
- introducing a new schema framework or external runtime validation library
- reopening archived `v1.14` release-trust / adapter-root stories except where required for type contract honesty
- broad contributor-governance policy changes such as multi-maintainer org design
</domain>

<decisions>
## Implementation Decisions

### Locked Decisions
- `uv run mypy` must end this phase with zero errors for the currently tracked repository scope; ignore-based silencing is not an acceptable closeout story.
- Telemetry contracts must converge around existing formal types (`FailureSummary`, `TelemetryJsonValue`, exporter snapshots/views, telemetry ports) rather than widening callers to `dict[str, object]`.
- `LiproRestFacade` and anonymous-share collaborators must satisfy their declared Protocols through honest signatures / typed helpers, not `cast`-heavy indirection.
- Service-handler and telemetry tests should be healed by shared typed fixture protocols / narrowing helpers, not by turning formal ports back into `Any`.
- YAML-driven meta tests must stop importing untyped `yaml` directly in checked modules; typed loader helpers or localized wrappers should be introduced in the existing test/toolchain surface.
- Governance docs for the active route must acknowledge `v1.15 / Phase 67` while keeping `v1.14` as the latest archived baseline.

### Claude's Discretion
- Exact plan granularity and wave split across telemetry, REST/anonymous-share, and toolchain/test helper work.
- Whether typed test helpers land in existing helper modules or new localized helper files, so long as discoverability improves and no new second-truth root appears.
- Whether a few very small follow-up doc/baseline updates belong in the same plan as toolchain hardening or in a separate governance-freeze plan.
</decisions>

<canonical_refs>
## Canonical References

**Downstream agents MUST read these before planning or implementing.**

### Current-story governance
- `.planning/PROJECT.md` — active milestone intent and north-star fit
- `.planning/ROADMAP.md` — `v1.15 / Phase 67` route and success criteria
- `.planning/REQUIREMENTS.md` — Phase 67 requirement IDs
- `.planning/STATE.md` — current active position / validation posture
- `.planning/v1.14-MILESTONE-AUDIT.md` — archived baseline being carried forward
- `.planning/reviews/V1_14_EVIDENCE_INDEX.md` — latest archived closeout pointer

### Telemetry typed seams
- `custom_components/lipro/core/telemetry/models.py`
- `custom_components/lipro/core/telemetry/sinks.py`
- `custom_components/lipro/core/telemetry/exporter.py`
- `custom_components/lipro/core/telemetry/ports.py`
- `custom_components/lipro/control/runtime_access_support.py`
- `custom_components/lipro/control/telemetry_surface.py`
- `tests/core/telemetry/test_models.py`
- `tests/core/telemetry/test_sinks.py`
- `tests/core/telemetry/test_exporter.py`

### REST / anonymous-share / service handler typed seams
- `custom_components/lipro/core/api/rest_facade.py`
- `custom_components/lipro/core/api/auth_service.py`
- `custom_components/lipro/core/api/endpoints/*.py`
- `custom_components/lipro/core/anonymous_share/manager.py`
- `custom_components/lipro/core/anonymous_share/manager_submission.py`
- `custom_components/lipro/core/anonymous_share/share_client_flows.py`
- `tests/core/api/test_api_transport_executor.py`
- `tests/core/api/test_api_status_service.py`
- `tests/core/test_init_service_handlers*.py`
- `tests/services/test_services_schedule.py`

### Toolchain / meta typing / governance
- `tests/meta/toolchain_truth_ci_contract.py`
- `tests/meta/toolchain_truth_release_contract.py`
- `tests/meta/toolchain_truth_python_stack.py`
- `tests/meta/toolchain_truth_docs_fast_path.py`
- `tests/meta/test_version_sync.py`
- `tests/meta/test_blueprints.py`
- `pyproject.toml`

</canonical_refs>

<specifics>
## Specific Ideas

- Introduce small typed coercion helpers for telemetry sink/exporter snapshots instead of repeated direct indexing into `TelemetryJsonValue`.
- Normalize REST façade request return types so endpoint/auth collaborators see the exact `JsonValue` / `JsonObject` shapes their ports declare.
- Replace direct `yaml` imports in typed test modules with one localized typed loader helper that returns concrete mappings/lists.
- Use lightweight Protocols or typed builder helpers in service-handler tests so `object` fixtures stop leaking across dozens of assertions.
- Keep plan execution focused on root-cause convergence; if a hotspot is only large but already honest, do not split it gratuitously.
</specifics>

<deferred>
## Deferred Ideas

- Bringing `scripts/**` under `mypy.files` once the currently tracked scope is green and the script/tooling helper boundary is separately planned
- Governance projection automation for archive pointer / continuity metadata
- Multi-maintainer / documented delegate organizational policy changes
</deferred>

---

*Phase: 67-typed-contract-convergence-toolchain-hardening-and-mypy-closure*
*Context gathered: 2026-03-23 via fresh repository audit and full mypy evidence*
