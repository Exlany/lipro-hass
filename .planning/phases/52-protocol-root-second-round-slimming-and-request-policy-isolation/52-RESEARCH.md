# Phase 52 — Research Notes

**Date:** 2026-03-21
**Status:** Complete
**Sources:** roadmap/requirements/state + `Phase 35/50/51` evidence + targeted protocol/request-policy reread + parallel subagent findings

## Key Findings

### 1. `LiproProtocolFacade` is still the protocol-plane density hotspot
- `custom_components/lipro/core/protocol/facade.py` is still `475` lines and carries both root-owned duties and a long REST forwarding tail.
- The file mixes shared state / telemetry / diagnostics / contracts ownership, REST child wiring, MQTT attach/build/snapshot mechanics, and a large cluster of one-line pass-through protocol methods.
- This is no longer a “wrong architecture” problem, but it is still a “too many protocol concerns visible in one root body” problem.
- The best next move is not another façade, but **topicized inward extraction**: keep the `LiproProtocolFacade` public methods stable while moving forwarding clusters behind support-only bound-method seams or narrower child-facing ports.

### 2. `_RestFacadePort` works, but it is still too wide
- `custom_components/lipro/core/protocol/rest_port.py` already gives the protocol root one typed child-façade seam.
- However, the protocol still sees a broad `23`-method port covering auth, status, commands, misc endpoints, OTA, schedules, and diagnostics-adjacent helpers.
- That keeps protocol-root thinking at “whole REST child surface” granularity instead of concern-local granularity.
- Phase 52 should narrow what the root needs to know, likely by splitting the port into smaller concern ports or equivalent localized contracts.

### 3. MQTT attach/diagnostics mechanics are still visible in the protocol-root body
- `build_mqtt_facade()`, `_bind_active_mqtt_facade()`, `_build_protocol_diagnostics_snapshot()`, and `protocol_diagnostics_snapshot()` are legitimate root duties, but their internal mechanics still sit directly in `facade.py`.
- The root should continue to own the formal entrypoints and truth, but the mechanical binding/snapshot assembly can still move inward to a localized support collaborator.
- This is especially important because `session_state.bind_mqtt_biz_id(...)`, MQTT-connected status, and auth-recovery telemetry are cross-cutting protocol truths that should stay explicit without bloating the root body.

### 4. Request-policy truth is still split across too many files
- `custom_components/lipro/core/api/request_policy.py` is intended to be the pacing / busy / retry / backoff home.
- But `custom_components/lipro/core/api/transport_retry.py` still carries its own 429 handling flow, and `custom_components/lipro/core/api/rest_facade.py` still exposes an orphan `_handle_rate_limit()` bridge.
- Busy-retry mechanics are also still materially implemented in `custom_components/lipro/core/api/command_api_service.py`, while `RequestPolicy` acts partly as a callback injector.
- This is the clearest remaining request-policy isolation gap: policy truth exists, but it is not yet the undisputed implementation home.

### 5. Mapping/auth-aware request ownership is effectively dual-homed
- `custom_components/lipro/core/api/request_gateway.py` and `custom_components/lipro/core/api/transport_executor.py` both own overlapping request-flow stories for smart-home/IoT mapping requests.
- `RestTransportExecutor` is currently more than a transport executor; it also performs mapping request orchestration.
- `RestRequestGateway` is also more than a thin adapter; it mirrors request orchestration that partially overlaps executor behavior.
- The cleaner target state is:
  - `RestTransportExecutor` = session/signing/HTTP execution/header building/response validation
  - `RestRequestGateway` = mapping/auth-aware request flow + retry-context preservation
  - `RequestPolicy` = pacing / busy / 429 / wait/backoff policy truth

### 6. Retry-context preservation is expressed in too many layers
- Retry-aware wrapper logic exists in `rest_facade_request_methods.py`, `rest_facade.py`, `request_gateway.py`, and endpoint adapters.
- This is low-grade duplication rather than catastrophic drift, but it makes request behavior harder to reason about and easier to regress.
- Phase 52 should choose one localized home for “preserve retry args or omit them” logic and remove the mirrored wrappers elsewhere.

### 7. There is one cross-plane residual worth explicitly deciding on
- `compute_exponential_retry_wait_time()` currently lives in `request_policy.py`, but its callers include command/runtime/MQTT-adjacent code.
- That makes one API-owned policy utility serve as a quasi-shared backoff truth outside the strict REST/request-policy family.
- Phase 52 can either:
  - move it to a neutral utility home if budget permits, or
  - explicitly defer it and record it as a residual/no-return item rather than silently letting the leak persist.

## Hotspot Inventory

| Area | Primary files | Problem shape | Recommended formal home |
|------|---------------|---------------|-------------------------|
| Protocol root forwarding density | `core/protocol/facade.py`, `core/protocol/rest_port.py` | root body still sees too much child surface and too many concern clusters | `LiproProtocolFacade` public surface preserved; forwarding groups move behind support-only topic seams and narrower ports |
| MQTT attach/diagnostics mechanics | `core/protocol/facade.py`, `core/protocol/mqtt_facade.py` | valid root duties, but mechanical binding/snapshot code still bloats root body | localized non-exported support collaborator under `core/protocol/` |
| 429/backoff ownership | `core/api/request_policy.py`, `core/api/transport_retry.py`, `core/api/rest_facade.py` | 429 handling truth duplicated and bridged across multiple layers | `RequestPolicy` owns decision truth; `TransportRetry` only loops/replays |
| Busy/pacing ownership | `core/api/request_policy.py`, `core/api/command_api_service.py` | busy retry algorithm partly lives outside the formal policy home | `RequestPolicy` owns algorithm; command service becomes payload/dispatch helper only |
| Mapping/auth-aware request flow | `core/api/request_gateway.py`, `core/api/transport_executor.py` | request orchestration effectively dual-homed | `RestRequestGateway` owns mapping/auth-aware flow; executor narrows to transport concerns |
| Retry-context wrappers | `core/api/rest_facade.py`, `core/api/rest_facade_request_methods.py`, `core/api/request_gateway.py` | same decision expressed in several wrappers | one localized retry-context dispatch home |
| Generic backoff residual | `core/api/request_policy.py` plus runtime/MQTT callers | API-owned helper leaks outside strict request-policy family | neutral util home or explicit deferred residual |

## Recommended Wave Shape

### Wave 1 — slim the protocol root without changing its identity
- Narrow the protocol root’s view of the REST child surface.
- Topicize the REST forwarding clusters in `LiproProtocolFacade` so the root keeps its formal methods but loses bulk forwarding ballast.
- Localize MQTT attach/diagnostics mechanics without moving the formal entrypoints out of the root.

### Wave 2 — isolate request-policy implementation truth
- Collapse 429 handling into `RequestPolicy` and strip duplicated decision logic from `TransportRetry` / `rest_facade.py` bridges.
- Move busy/pacing algorithm ownership fully into `RequestPolicy`.
- Keep `command_api_service.py` as command helper / dispatcher, not a policy home.

### Wave 3 — collapse request ownership and freeze the new truth
- Make `RestRequestGateway` the single localized home for mapping/auth-aware request orchestration.
- Narrow `RestTransportExecutor` back to transport/signing/validation responsibilities.
- Add or adjust focused regressions/guards so protocol-root identity, request-policy ownership, and dependency direction stay machine-checkable.
- If the generic backoff leak cannot be removed safely in this phase, record it explicitly in planning/review truth rather than leaving it implicit.

## No-Return Rules

- Do **not** introduce a second protocol façade, wrapper, manager, or package export.
- Do **not** resurrect `__getattr__`, mixin aggregation, or implicit delegation as a slimming tactic.
- Do **not** let runtime/control/platform code depend on new protocol internals or concrete transport classes.
- Do **not** turn localized collaborators into public storylines in docs, exports, or tests.
- Do **not** move pacing/retry/busy/429 truth upward into runtime, control, diagnostics, or service helpers.
- Do **not** silently keep duplicated policy logic once a formal home has been chosen.

## Validation Guidance

### Wave 1 candidate gate
- `uv run pytest tests/core/api/test_protocol_contract_matrix.py tests/core/api/test_api_transport_and_schedule.py tests/meta/test_public_surface_guards.py -q`

### Wave 2 candidate gate
- `uv run pytest tests/core/api/test_api_request_policy.py tests/core/api/test_api_command_service.py tests/core/api/test_api_command_surface.py -k "429 or rate_limit or busy or CHANGE_STATE or pacing" -q`

### Wave 3 candidate gate
- `uv run pytest tests/core/api/test_api_transport_executor.py tests/core/api/test_api_command_surface.py tests/core/api/test_protocol_contract_matrix.py tests/meta/test_public_surface_guards.py tests/meta/test_dependency_guards.py -q`

## Planning Recommendation

Phase 52 should remain a **3-plan phase**:
1. protocol-root topicization and root-body slimming,
2. request-policy implementation isolation,
3. regression/guard/docs truth freeze.

That keeps `ARC-08` focused on protocol-plane formal-root convergence, while leaving broader hotspot/helper/typing work to `Phase 53 -> 55`.
