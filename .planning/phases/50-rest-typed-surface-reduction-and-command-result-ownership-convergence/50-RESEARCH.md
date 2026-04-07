# Phase 50 — Research Notes

**Date:** 2026-03-21
**Status:** Complete
**Sources:** roadmap/requirements/state + targeted code reread + planner/checker subagent findings

## Key Findings

### 1. REST typed debt is concentrated, not repo-wide diffuse
- `custom_components/lipro/core/api/endpoint_surface.py` is the largest endpoint-facing hotspot: `_RestEndpointSurfacePort` still types every collaborator field as `Any`, and many methods simply `cast(...)` endpoint results into `dict[str, Any]` / `list[dict[str, Any]]`.
- `custom_components/lipro/core/api/request_gateway.py`, `custom_components/lipro/core/api/rest_facade.py`, and `custom_components/lipro/core/api/rest_facade_request_methods.py` mirror the same wide seams: raw mapping senders, mapping finalizers, `_smart_home_request`, `_iot_request`, `unwrap_iot_success_payload`, and `require_mapping_response` still expose `Any` well above the boundary edge.
- `custom_components/lipro/core/api/rest_facade_endpoint_methods.py` is mostly a thin wrapper already; its remaining `dict[str, Any]` / `list[dict[str, Any]]` signatures are better treated as “typed-surface lag” than a need for new business logic.

### 2. Existing typed truth already exists but is underused
- `custom_components/lipro/core/api/types.py` already contains reusable typed assets such as `JsonValue`, `MqttConfigResponse`, `CommandResultApiResponse`, and `DiagnosticsApiResponse`.
- Several current wide return types in `endpoint_surface.py` and wrapper methods appear to be backlog debt rather than inherently dynamic payloads.
- `tests/core/api/test_api_status_service.py` exposes the concrete `on_batch_metric(size, duration, depth)` callback shape, suggesting a typed callback alias/protocol can replace `Any` there.

### 3. Command-result ownership is split between implementation and export homes
- `custom_components/lipro/core/command/result_policy.py` already positions itself as the policy home and contains polling / retry / delayed-refresh logic.
- `custom_components/lipro/core/command/result.py` still duplicates major parts of that same logic while also acting as the stable import/export surface for downstream consumers.
- Current consumers mostly import from `core.command.result`, not directly from `result_policy.py`; therefore the likely target state is “implementation centralized in `result_policy.py`, stable export preserved in `result.py`”.

### 4. Diagnostics auth-error handling still has one duplicated branch
- `custom_components/lipro/services/execution.py` already provides the formal shared coordinator-authenticated execution chain via `async_execute_coordinator_call()`.
- `custom_components/lipro/services/diagnostics/handlers.py` already uses that shared execution path in command-result diagnostics.
- `custom_components/lipro/services/diagnostics/helpers.py` still contains a hand-rolled authenticated multi-coordinator capability loop that duplicates `async_ensure_authenticated()` / `async_trigger_reauth()` semantics.
- This duplication is conceptually small but architecturally important: if left in place, diagnostics keeps a parallel auth-error story.

### 5. Governance/guard truth has a visible gap for Phase 50 touched zone
- `tests/meta/test_phase31_runtime_budget_guards.py` and `tests/meta/test_phase45_hotspot_budget_guards.py` guard earlier touched zones, but neither currently covers the REST façade family targeted by Phase 50.
- `Phase 50` therefore needs a machine-checkable typed-budget guard strategy: either extend an existing phase guard or add a dedicated touched-zone guard for REST/command/diagnostics convergence.
- The guard should explicitly separate `sanctioned_any` from `backlog_any`, and should also keep `type: ignore` / broad-catch budgets at no-growth or zero.

## Hotspot Inventory

| Area | Primary files | Problem shape | Recommended formal home |
|------|---------------|---------------|-------------------------|
| REST endpoint typed surface | `core/api/endpoint_surface.py`, `core/api/rest_facade_endpoint_methods.py` | protocol fields typed as `Any`; wrapper returns over-widened | `core/api/types.py` + narrow endpoint-facing protocol aliases |
| REST request/mapping helpers | `core/api/request_gateway.py`, `core/api/rest_facade.py`, `core/api/rest_facade_request_methods.py` | raw mapping senders/finalizers leak `Any` too high | `core/api/request_gateway.py` for raw boundary alias, `core/api/types.py` for stable payload types |
| Command-result policy | `core/command/result.py`, `core/command/result_policy.py` | duplicated polling/retry/delayed-refresh logic | `core/command/result_policy.py` implementation; `core/command/result.py` stable export shell |
| Diagnostics auth-error chain | `services/execution.py`, `services/diagnostics/helpers.py`, `services/diagnostics/handlers.py` | duplicate auth-error behavior in helper loop | `services/execution.py` |
| Typed-budget truth | `tests/meta/test_phase31_runtime_budget_guards.py`, `tests/meta/test_phase45_hotspot_budget_guards.py` | no Phase 50 touched-zone guard | dedicated Phase 50 guard or extended hotspot guard |

## Sanctioned vs Backlog Guidance

### Likely sanctioned `Any` / raw-object seams
- raw mapping payload immediately at HTTP boundary before mapping validation/finalization
- narrowly scoped “opaque JSON value” positions that truly must remain polymorphic until normalized
- transport/request context placeholders that cannot be expressed more specifically without fighting `aiohttp` APIs

### Likely backlog `Any` seams
- endpoint collaborator fields inside `_RestEndpointSurfacePort`
- wrapper return types that can reuse existing `types.py` aliases
- `on_batch_metric` callback parameter
- `unwrap_iot_success_payload` / `require_mapping_response` signatures once boundary alias is narrowed
- mirrored `Any` signatures duplicated across `rest_facade.py`, `request_gateway.py`, and `rest_facade_request_methods.py`

## Recommended Plan Packaging

### Plan 50-01 — Endpoint typed-surface reduction
Focus on `endpoint_surface.py`, `rest_facade_endpoint_methods.py`, and `types.py`.

Target outcomes:
- narrow collaborator protocol fields where possible
- replace obvious `dict[str, Any]` / `list[dict[str, Any]]` surfaces with existing or newly localized API typed aliases
- formalize callback / response aliases already implied by tests

### Plan 50-02 — Request/mapping helper honesty tightening
Focus on `request_gateway.py`, `rest_facade.py`, `rest_facade_request_methods.py`, and `types.py`.

Target outcomes:
- define a formal raw-boundary alias close to `request_gateway.py`
- reduce mirrored `Any` helper signatures across gateway/facade/wrapper files
- keep `LiproRestFacade` as the only stable REST child façade

### Plan 50-03 — Command-result ownership convergence
Focus on `core/command/result.py`, `core/command/result_policy.py`, and adjacent command consumers/tests.

Target outcomes:
- centralize polling/retry/delayed-refresh implementation in one home
- preserve stable downstream imports
- make policy-vs-export roles explicit in code and docs/ledgers if wording changes

### Plan 50-04 — Diagnostics auth-error convergence + typed-budget guards
Focus on `services/execution.py`, `services/diagnostics/helpers.py`, `services/diagnostics/handlers.py`, and Phase 50 touched-zone meta guards/docs.

Target outcomes:
- remove duplicated diagnostics auth-error behavior as an independent logic family
- add machine-checkable typed-budget guard coverage for REST/command/diagnostics touched zone
- sync baseline/review wording only if formal-home wording genuinely changes; otherwise explicitly record unchanged truth in closeout

## Verification Implications

- `tests/core/api/test_api_command_surface.py` and `tests/core/api/test_api_status_service.py` remain the main behavior guards for REST child façade changes.
- `tests/core/test_command_result.py` is the main behavior guard for command-result policy convergence.
- `tests/meta/test_dependency_guards.py` and `tests/meta/test_public_surface_guards.py` should participate in the phase gate so Phase 50 cannot accidentally expand the public contract or create a second root story.
- typed-budget verification must be machine-checkable rather than prose-only.

## Documentation / Governance Sync Expectations

### Must review for potential updates
- `.planning/baseline/PUBLIC_SURFACES.md`
- `.planning/baseline/DEPENDENCY_MATRIX.md`
- `.planning/baseline/VERIFICATION_MATRIX.md`
- `.planning/reviews/FILE_MATRIX.md`
- `.planning/reviews/RESIDUAL_LEDGER.md`
- `.planning/reviews/KILL_LIST.md`

### Likely unchanged unless wording drift is fixed
- `LiproRestFacade` as canonical REST child façade
- `request_gateway.py` and `endpoint_surface.py` as localized collaborators
- `services/execution.py` as formal shared service execution facade and non-residual asset

## Planning Risk Notes

- Over-tightening too early can create fake type certainty; boundary raw payload shapes must still be honest.
- Moving implementation between `result.py` and `result_policy.py` must preserve stable imports used by runtime/diagnostics/tests.
- diagnostics multi-coordinator capability flow must keep current degrade-and-continue semantics even if auth handling converges.
- guard work must avoid creating another sprawling “mega-guard”; Phase 50 should add focused, touched-zone honesty rather than a new monolith.

---

**Research verdict:** ready for planning.
