# Architecture

**Analysis Date:** 2026-04-01

> Snapshot: `2026-04-01`
> Freshness: 基于 `docs/NORTH_STAR_TARGET_ARCHITECTURE.md`、`docs/developer_architecture.md`、`.planning/{PROJECT.md,ROADMAP.md,REQUIREMENTS.md,STATE.md}`、`.planning/baseline/*.md`、`.planning/reviews/*.md` 与 `custom_components/lipro/**` 的当前截面。
> Derived collaboration map: 本文件是受约束的协作图谱 / 派生视图，仅用于导航、审阅与后续实现对齐。
> Authority: 若与 `docs/NORTH_STAR_TARGET_ARCHITECTURE.md`、`.planning/{PROJECT.md,ROADMAP.md,REQUIREMENTS.md,STATE.md}`、`.planning/baseline/*.md`、`.planning/reviews/*.md` 或 `docs/developer_architecture.md` 冲突，以后者为准；本文件不得反向充当当前治理真源。

## Pattern Overview

## Phase 125 Execution Notes

- `custom_components/lipro/runtime_types.py` 继续是 sanctioned outward contract home；`ScheduleMeshDeviceLike`、`CommandProperties` 与 `DeviceRefreshServiceLike` 现回到同一 formal truth，不再由下游 runtime/service helper 各自 shadow。
- `custom_components/lipro/config_flow.py` 仍是 thin HA adapter；Phase 125 把 `flow/step_handlers.py` 的 step protocol 直接绑到 private helper seam，删除了 public pass-through wrapper 壳层。
- `custom_components/lipro/entry_auth.py` 继续承担 persisted auth-seed read/write single-source truth；单次中转 helper 已被压平，formal home 没有漂移。
- governance current-route truth 已沉淀到 `.planning/baseline/GOVERNANCE_REGISTRY.json::planning_route`，五份 selector docs 现在只是 projection / consistency target。


**Overall:** Five-plane, explicit-composition, single-main-chain Home Assistant integration

**Key Characteristics:**
- `custom_components/lipro/__init__.py`, `custom_components/lipro/config_flow.py`, `custom_components/lipro/diagnostics.py`, and `custom_components/lipro/system_health.py` stay as thin HA adapters.
- `custom_components/lipro/core/protocol/facade.py` defines `LiproProtocolFacade` as the only formal protocol root; REST and MQTT remain child façades in `custom_components/lipro/core/api/rest_facade.py` and `custom_components/lipro/core/protocol/mqtt_facade.py`.
- `custom_components/lipro/core/coordinator/coordinator.py` defines `Coordinator` as the only runtime orchestration root; construction is pushed inward to `custom_components/lipro/core/coordinator/orchestrator.py` and `custom_components/lipro/core/coordinator/runtime_wiring.py`.
- `custom_components/lipro/control/` is the formal control home; `custom_components/lipro/services/` provides helper declarations and request-shaping helpers, not a second root.
- `custom_components/lipro/core/device/`, `custom_components/lipro/core/capability/`, and `custom_components/lipro/core/command/` carry domain truth that platform files project into Home Assistant.
- `tests/`, `.planning/baseline/`, `.planning/reviews/`, and `scripts/check_architecture_policy.py` form an active assurance plane that guards structure and authority.

## Layers

**HA Adapter Layer:**
- Purpose: expose Home Assistant-required module names and callback signatures.
- Location: `custom_components/lipro/__init__.py`, `custom_components/lipro/config_flow.py`, `custom_components/lipro/diagnostics.py`, `custom_components/lipro/system_health.py`, `custom_components/lipro/{light,fan,switch,cover,climate,binary_sensor,sensor,select,update}.py`
- Contains: setup entrypoints, config-flow adapter, diagnostics/system-health adapters, platform setup shells.
- Depends on: `custom_components/lipro/control/`, `custom_components/lipro/flow/`, `custom_components/lipro/helpers/platform.py`, `custom_components/lipro/entities/`, `custom_components/lipro/runtime_types.py`
- Used by: Home Assistant integration bootstrap and platform loading.

**Control Plane:**
- Purpose: own lifecycle orchestration, service registration, runtime read access, diagnostics, and system-health projection.
- Location: `custom_components/lipro/control/`
- Contains: `entry_lifecycle_controller.py`, `entry_lifecycle_support.py`, `entry_root_wiring.py`, `service_registry.py`, `service_router.py`, `runtime_access.py`, `diagnostics_surface.py`, `system_health_surface.py`, `redaction.py`
- Depends on: `custom_components/lipro/runtime_infra.py`, `custom_components/lipro/runtime_types.py`, `custom_components/lipro/services/`, runtime public surfaces, and telemetry exporters.
- Used by: HA root adapters and service callback registration.

**Runtime Plane:**
- Purpose: orchestrate polling, MQTT lifecycle, command dispatch, state mutation, confirmation tracking, and runtime public services.
- Location: `custom_components/lipro/core/coordinator/`
- Contains: `coordinator.py`, `orchestrator.py`, `runtime_context.py`, `runtime_wiring.py`, `runtime/`, `services/`, `lifecycle.py`
- Depends on: `custom_components/lipro/core/protocol/`, `custom_components/lipro/core/auth/`, `custom_components/lipro/core/device/`, `custom_components/lipro/core/command/`, `custom_components/lipro/core/utils/`
- Used by: control-plane lifecycle setup, entities, diagnostics, and system-health readers.

**Protocol Plane:**
- Purpose: isolate external IO, request policy, auth recovery, MQTT transport, and payload normalization at the boundary.
- Location: `custom_components/lipro/core/protocol/`, `custom_components/lipro/core/api/`, `custom_components/lipro/core/mqtt/`, `custom_components/lipro/core/anonymous_share/`, `custom_components/lipro/core/ota/`
- Contains: unified protocol root, REST/MQTT façades, boundary decoders, transport/pacing/auth-recovery helpers, anonymous-share client, OTA query helpers.
- Depends on: `aiohttp`, `aiomqtt`, `custom_components/lipro/core/utils/`, and `custom_components/lipro/const/`
- Used by: runtime root, config flow login path, headless proof seam, diagnostics, and telemetry.

**Domain Plane:**
- Purpose: hold normalized device truth, capability truth, command intent models, and entity projection helpers.
- Location: `custom_components/lipro/core/device/`, `custom_components/lipro/core/capability/`, `custom_components/lipro/core/command/`, `custom_components/lipro/entities/`, `custom_components/lipro/helpers/platform.py`
- Contains: `LiproDevice`, `CapabilityRegistry`, device state/extras helpers, command result helpers, entity base and descriptors, platform projection rules.
- Depends on: runtime-managed normalized state and `custom_components/lipro/const/`
- Used by: runtime plane, platform adapters, and diagnostics builders.

**Assurance Plane:**
- Purpose: enforce architecture policy, surface boundaries, fixture authority, and closeout status.
- Location: `tests/`, `.planning/baseline/`, `.planning/reviews/`, `docs/NORTH_STAR_TARGET_ARCHITECTURE.md`, `docs/developer_architecture.md`, `scripts/check_architecture_policy.py`, `scripts/check_file_matrix.py`
- Contains: focused runtime/protocol/control tests, meta guards, fixtures, authority matrices, file ownership ledgers, and review evidence.
- Depends on: declared governance truth and actual code topology.
- Used by: CI in `.github/workflows/ci.yml` and release guarding in `.github/workflows/release.yml`.

## Data Flow

**Config Entry Bootstrap:**
1. Home Assistant enters `custom_components/lipro/__init__.py` and calls `async_setup()` or `async_setup_entry()`.
2. `custom_components/lipro/__init__.py` lazily resolves protocol/auth/coordinator constructors and assembles dependencies through `custom_components/lipro/control/entry_root_wiring.py`.
3. `custom_components/lipro/control/entry_lifecycle_controller.py` delegates setup mechanics to `custom_components/lipro/control/entry_lifecycle_support.py`.
4. Entry auth bootstrap builds `LiproProtocolFacade` and `LiproAuthManager`, then `custom_components/lipro/core/coordinator/coordinator.py` builds the runtime root.
5. Shared infra and services are synchronized through `custom_components/lipro/runtime_infra.py` and `custom_components/lipro/control/service_registry.py`, then platforms are forwarded.

**Command & Service Path:**
1. A user action enters through a platform entity in `custom_components/lipro/{light,fan,switch,cover,climate,select,update}.py` or a service callback in `custom_components/lipro/control/service_router.py`.
2. Entities dispatch through `custom_components/lipro/entities/base.py`; services dispatch through `custom_components/lipro/control/service_router_handlers.py`, which now owns command/schedule/share/maintenance callbacks directly while `custom_components/lipro/control/service_router_diagnostics_handlers.py` remains the developer/diagnostics collaborator home.
3. Shared coordinator-auth handling runs through `custom_components/lipro/services/execution.py`.
4. Runtime command or schedule services in `custom_components/lipro/core/coordinator/services/` call the protocol root.
5. `custom_components/lipro/core/api/rest_facade.py` applies request policy, auth recovery, transport execution, and mapping validation before runtime confirmation/refresh closes the loop.

**Refresh & MQTT Path:**
1. `custom_components/lipro/core/coordinator/coordinator.py` owns the scheduled update cycle.
2. `custom_components/lipro/core/coordinator/runtime_wiring.py` wires polling, state, telemetry, device refresh, and MQTT services.
3. REST responses are normalized in `custom_components/lipro/core/protocol/boundary/`; MQTT transport stays localized in `custom_components/lipro/core/mqtt/transport.py` and is wrapped by `custom_components/lipro/core/protocol/mqtt_facade.py`.
4. Runtime collaborators update `LiproDevice` aggregates through `StateRuntime` and device refresh services.
5. `Coordinator` publishes updated state to entities and runtime-access readers.

**State Management:**
- Mutable runtime state lives in `CoordinatorStateContainers` from `custom_components/lipro/core/coordinator/factory.py` and is exposed outward through `Coordinator`, runtime services, and typed protocols in `custom_components/lipro/runtime_types.py`.
- Device truth is centralized in `custom_components/lipro/core/device/device.py`; control reads should use `custom_components/lipro/control/runtime_access.py` instead of coordinator internals.

## Key Abstractions

**LiproProtocolFacade:**
- Purpose: define the single protocol-plane root above REST and MQTT child façades.
- Examples: `custom_components/lipro/core/protocol/facade.py`, `custom_components/lipro/core/protocol/protocol_facade_rest_methods.py`
- Pattern: explicit composition root with shared session state, request policy, telemetry, and diagnostics context.

**Coordinator:**
- Purpose: define the single runtime orchestration root for polling, MQTT, command confirmation, and state publication.
- Examples: `custom_components/lipro/core/coordinator/coordinator.py`, `custom_components/lipro/coordinator_entry.py`
- Pattern: root coordinator plus inward wiring, runtimes, and service layer.

**LiproDevice:**
- Purpose: hold the canonical device aggregate exposed to runtime, entities, diagnostics, and projections.
- Examples: `custom_components/lipro/core/device/device.py`, `custom_components/lipro/core/device/state.py`, `custom_components/lipro/core/capability/registry.py`
- Pattern: thin aggregate façade over composed state/extras/capability helpers.

**RuntimeAccess:**
- Purpose: give control-plane code a typed, stable runtime locator and snapshot surface.
- Examples: `custom_components/lipro/control/runtime_access.py`, `custom_components/lipro/control/runtime_access_support.py`, `custom_components/lipro/control/runtime_access_types.py`
- Pattern: formal outward home plus inward support-module splits.

**ServiceRegistry & ServiceRouter:**
- Purpose: separate HA service lifecycle ownership from callback implementation details.
- Examples: `custom_components/lipro/control/service_registry.py`, `custom_components/lipro/control/service_router.py`, `custom_components/lipro/control/service_router_handlers.py`
- Pattern: formal owner plus handler/support collaborators plus helper-only `custom_components/lipro/services/` modules.

**Boundary Decoder Registry:**
- Purpose: keep vendor payload decode and normalization at the protocol edge.
- Examples: `custom_components/lipro/core/protocol/boundary/__init__.py`, `custom_components/lipro/core/protocol/boundary/rest_decoder.py`, `custom_components/lipro/core/protocol/boundary/mqtt_decoder.py`
- Pattern: canonical registry/family home; downstream planes consume normalized shapes only.

## Entry Points

**Home Assistant bootstrap:**
- Location: `custom_components/lipro/__init__.py`
- Triggers: integration setup, entry setup, unload, reload.
- Responsibilities: thin adapter, lazy constructor loading, lifecycle controller assembly, runtime infra/service sync.

**Config flow:**
- Location: `custom_components/lipro/config_flow.py`, `custom_components/lipro/flow/`
- Triggers: user login, reauth, reconfigure, options.
- Responsibilities: validate input, build headless boot context, project auth session to config-entry data.

**Diagnostics and system health:**
- Location: `custom_components/lipro/diagnostics.py`, `custom_components/lipro/system_health.py`
- Triggers: HA diagnostics download and system-health inspection.
- Responsibilities: stay adapter-thin and delegate to control-plane surfaces with redaction.

**Platform setup:**
- Location: `custom_components/lipro/{light,fan,switch,cover,climate,binary_sensor,sensor,select,update}.py`
- Triggers: HA platform forwarding from entry setup.
- Responsibilities: map devices to HA entities through `custom_components/lipro/helpers/platform.py` and `custom_components/lipro/entities/`.

**Headless proof seam:**
- Location: `custom_components/lipro/headless/boot.py`
- Triggers: config-flow login helpers and proof/integration consumers.
- Responsibilities: expose a local boot context without becoming a second runtime or protocol root.

## Error Handling

**Strategy:** classify failures at the owning plane, translate them at the boundary, and preserve cancel semantics throughout setup, runtime, and service paths.

**Patterns:**
- Lifecycle failures are classified in `custom_components/lipro/control/entry_lifecycle_failures.py` and logged by `custom_components/lipro/control/entry_lifecycle_controller.py`.
- REST auth/retry/rate-limit handling stays in `custom_components/lipro/core/api/auth_recovery.py`, `custom_components/lipro/core/api/request_policy.py`, and `custom_components/lipro/core/api/transport_executor.py`.
- MQTT transport-stage failures are recorded inside `custom_components/lipro/core/protocol/mqtt_facade.py` instead of leaking transport semantics upward.
- Service-layer auth failure and reauth initiation are centralized in `custom_components/lipro/services/execution.py`.
- Logging avoids sensitive leakage through `custom_components/lipro/core/utils/log_safety.py`, `custom_components/lipro/core/utils/redaction.py`, and `custom_components/lipro/control/redaction.py`.

## Cross-Cutting Concerns

**Logging:** redacted, layered logging lives in `custom_components/lipro/core/utils/log_safety.py`, `custom_components/lipro/core/utils/redaction.py`, `custom_components/lipro/control/redaction.py`, and router support helpers.
**Validation:** Home Assistant form/service schemas live in `custom_components/lipro/flow/schemas.py` and `custom_components/lipro/services/contracts.py`; payload validation lives in `custom_components/lipro/core/protocol/boundary/`.
**Authentication:** config-entry auth bootstrap lives in `custom_components/lipro/entry_auth.py` and `custom_components/lipro/flow/login.py`; runtime auth ownership lives in `custom_components/lipro/core/auth/manager.py` and `custom_components/lipro/core/coordinator/services/auth_service.py`.

## Boundary Notes

**Formal boundaries:**
- Control code reads runtime state through `custom_components/lipro/control/runtime_access.py`; do not add new direct `entry.runtime_data` or coordinator-internal probing elsewhere.
- Protocol normalization belongs in `custom_components/lipro/core/protocol/boundary/`; do not decode vendor payloads inside runtime, entities, or control helpers.
- Concrete MQTT transport stays localized in `custom_components/lipro/core/mqtt/transport.py`; callers should enter through `custom_components/lipro/core/protocol/mqtt_facade.py` or `custom_components/lipro/core/protocol/facade.py`.
- Public runtime contracts belong in `custom_components/lipro/runtime_types.py`; platforms and control helpers should code against those protocols instead of coordinator internals.

## Residual & Convergence

**Current residual posture:** `.planning/reviews/RESIDUAL_LEDGER.md` records zero active residual families, but several intentional thin shells remain as stable topology anchors.

**Localized shells to keep thin:**
- `custom_components/lipro/core/api/client.py` is a stable import home for `LiproRestFacade`; keep behavior in `custom_components/lipro/core/api/rest_facade.py`.
- `custom_components/lipro/coordinator_entry.py` is an export shell for `Coordinator`; keep runtime behavior in `custom_components/lipro/core/coordinator/`.
- `custom_components/lipro/runtime_infra.py` is the outward formal home, while `custom_components/lipro/runtime_infra_device_registry.py` holds support-only listener mechanics.
- `custom_components/lipro/headless/boot.py` is proof-only and should not acquire HA lifecycle, runtime-access, or coordinator ownership.
- `custom_components/lipro/services/execution.py` is a formal shared service-execution facade even though it originated from a historical seam; keep it focused on auth/error choreography.

**Convergence guidance:**
- Add new control-plane behavior under `custom_components/lipro/control/`; use `custom_components/lipro/services/` only for declarations, diagnostics/share/schedule helpers, request shaping, and error translation.
- Add new runtime support by splitting inward next to the formal home, following existing patterns such as `runtime_access_support_*`, `share_client_*`, or `custom_components/lipro/core/coordinator/runtime/*`, instead of creating a new top-level plane.
- Add new boundary normalization in `custom_components/lipro/core/protocol/boundary/` and keep `custom_components/lipro/core/api/` and `custom_components/lipro/core/mqtt/` focused on transport and call orchestration.
- If a hotspot grows, decompose it by concern without moving ownership; current large files include `custom_components/lipro/core/coordinator/runtime/command_runtime.py`, `custom_components/lipro/core/anonymous_share/manager.py`, `custom_components/lipro/core/api/rest_facade.py`, `custom_components/lipro/control/runtime_access.py`, and `custom_components/lipro/entities/base.py`.

---

*Architecture analysis: 2026-03-27*


## Phase 90 Freeze Snapshot

- `custom_components/lipro/core/api/client.py` is only the stable import shell; `rest_facade.py` remains the REST child-façade composition home.
- `command_runtime.py`, `request_policy.py`, `mqtt_runtime.py`, and `anonymous_share/manager.py` remain formal homes that may still split inward without changing outward ownership.
- `custom_components/lipro/__init__.py`, `control/runtime_access.py`, `entities/base.py`, and `entities/firmware_update.py` remain protected thin shells; new orchestration must move inward, not back outward.


## Phase 91 Canonical Boundary Snapshot

- `protocol_facade_rest_methods.py` now performs live canonicalization at the protocol root, while `rest_port.py` stays a raw child-facing port.
- `runtime_types.py` and `core/coordinator/types.py` now anchor shared telemetry / trace truth instead of ad-hoc dynamic runtime dicts.
- Protected thin shells remain outward-only: orchestration moved inward, not back into `__init__.py`, `runtime_access.py`, or entity adapters.
