# Codebase Structure

**Analysis Date:** 2026-03-28

> Snapshot: `2026-03-28`
> Freshness: 基于仓库当前目录树、`README.md`、`docs/README.md`、`custom_components/lipro/manifest.json`、`.planning/{PROJECT.md,ROADMAP.md,REQUIREMENTS.md,STATE.md}` 与 `.planning/reviews/FILE_MATRIX.md` 的当前截面。
> Derived collaboration map: 本文件是受约束的协作图谱 / 派生视图，仅用于导航、审阅与后续实现对齐。
> Authority: 若与 `docs/NORTH_STAR_TARGET_ARCHITECTURE.md`、`.planning/{PROJECT.md,ROADMAP.md,REQUIREMENTS.md,STATE.md}`、`.planning/baseline/*.md`、`.planning/reviews/*.md` 或 `docs/developer_architecture.md` 冲突，以后者为准；本文件不得反向充当当前治理真源。

## Directory Layout

```text
[project-root]/
├── custom_components/lipro/   # Home Assistant integration source and formal plane homes
├── tests/                     # Unit, integration, meta-governance, fixtures, snapshots, benchmarks
├── docs/                      # North-star, developer architecture, ADRs, maintainer docs
├── scripts/                   # Architecture/file-matrix/tooling guards and helper scripts
├── .planning/                 # Governance baselines, reviews, milestones, derived codebase maps
├── .github/                   # CI, release, contributor templates, CODEOWNERS
├── blueprints/                # Home Assistant blueprint assets
├── pyproject.toml             # Python toolchain and project configuration
└── uv.lock                    # Locked Python dependency graph
```

## Directory Purposes

**`custom_components/lipro/`:**
- Purpose: integration production code and Home Assistant-facing entry modules.
- Contains: root adapters, platform files, `control/`, `core/`, `entities/`, `flow/`, `helpers/`, `services/`, translations, runtime contract files.
- Key files: `custom_components/lipro/__init__.py`, `custom_components/lipro/config_flow.py`, `custom_components/lipro/diagnostics.py`, `custom_components/lipro/system_health.py`, `custom_components/lipro/manifest.json`

**`custom_components/lipro/control/`:**
- Purpose: formal control-plane home.
- Contains: lifecycle orchestration, service registration/router, runtime access, diagnostics/system-health surfaces, redaction helpers.
- Key files: `custom_components/lipro/control/entry_lifecycle_controller.py`, `custom_components/lipro/control/service_registry.py`, `custom_components/lipro/control/service_router.py`, `custom_components/lipro/control/runtime_access.py`

**`custom_components/lipro/core/`:**
- Purpose: formal protocol, runtime, domain, auth, telemetry, and shared utility homes.
- Contains: `protocol/`, `api/`, `mqtt/`, `coordinator/`, `device/`, `capability/`, `command/`, `auth/`, `ota/`, `anonymous_share/`, `telemetry/`, `utils/`.
- Key files: `custom_components/lipro/core/protocol/facade.py`, `custom_components/lipro/core/api/rest_facade.py`, `custom_components/lipro/core/coordinator/coordinator.py`, `custom_components/lipro/core/device/device.py`

**`custom_components/lipro/core/coordinator/`:**
- Purpose: runtime root plus inward runtime/service decomposition.
- Contains: coordinator root, orchestrator, runtime wiring/context, focused runtimes under `runtime/`, and runtime public services under `services/`.
- Key files: `custom_components/lipro/core/coordinator/coordinator.py`, `custom_components/lipro/core/coordinator/orchestrator.py`, `custom_components/lipro/core/coordinator/runtime_wiring.py`, `custom_components/lipro/core/coordinator/services/__init__.py`

**`custom_components/lipro/services/`:**
- Purpose: control-plane helper territory for service contracts, request shaping, diagnostics/share/schedule helpers, and shared service execution.
- Contains: schemas/contracts, device lookup helpers, error translation, schedule/share helpers, diagnostics helper family.
- Key files: `custom_components/lipro/services/contracts.py`, `custom_components/lipro/services/execution.py`, `custom_components/lipro/services/share.py`, `custom_components/lipro/services/schedule.py`

**`custom_components/lipro/entities/`:**
- Purpose: domain-to-HA entity projection helpers shared by root platform files.
- Contains: `LiproEntity`, command mixins, descriptors, firmware update entity helpers.
- Key files: `custom_components/lipro/entities/base.py`, `custom_components/lipro/entities/commands.py`, `custom_components/lipro/entities/descriptors.py`

**`custom_components/lipro/flow/`:**
- Purpose: config-flow and options-flow helper modules.
- Contains: login helpers, schema builders, submission validators, credentials helpers, options flow.
- Key files: `custom_components/lipro/flow/login.py`, `custom_components/lipro/flow/schemas.py`, `custom_components/lipro/flow/submission.py`, `custom_components/lipro/flow/options_flow.py`

**`tests/`:**
- Purpose: assurance plane for behavior, topology, fixtures, and governance.
- Contains: `core/`, `flows/`, `services/`, `platforms/`, `integration/`, `meta/`, `fixtures/`, `snapshots/`, `benchmarks/`.
- Key files: `tests/meta/test_dependency_guards.py`, `tests/meta/test_public_surface_guards.py`, `tests/integration/test_mqtt_coordinator_integration.py`, `tests/core/test_init.py`

**`docs/`:**
- Purpose: human-facing architecture, ADR, troubleshooting, and maintainer guides.
- Contains: north-star architecture, developer architecture, ADRs, release runbook, contributor architecture change map.
- Key files: `docs/NORTH_STAR_TARGET_ARCHITECTURE.md`, `docs/developer_architecture.md`, `docs/adr/0001-coordinator-as-single-orchestration-root.md`

**`scripts/`:**
- Purpose: executable governance and repository integrity checks.
- Contains: architecture/file-matrix checks, translation checks, benchmark checks, evidence export helpers.
- Key files: `scripts/check_architecture_policy.py`, `scripts/check_file_matrix.py`, `scripts/check_translations.py`, `scripts/export_ai_debug_evidence_pack.py`

**`.planning/`:**
- Purpose: live governance truth, archived milestone assets, review ledgers, and derived collaboration maps.
- Contains: `baseline/`, `reviews/`, `milestones/`, `phases/`, `codebase/`, current planning docs.
- Key files: `.planning/PROJECT.md`, `.planning/ROADMAP.md`, `.planning/STATE.md`, `.planning/REQUIREMENTS.md`, `.planning/baseline/ARCHITECTURE_POLICY.md`, `.planning/reviews/FILE_MATRIX.md`

## Key File Locations

**Entry Points:**
- `custom_components/lipro/__init__.py`: Home Assistant component bootstrap, entry lifecycle adapter, and runtime infra/service sync entry.
- `custom_components/lipro/config_flow.py`: config flow adapter for user, reauth, and reconfigure flows.
- `custom_components/lipro/diagnostics.py`: diagnostics adapter entry.
- `custom_components/lipro/system_health.py`: system-health adapter entry.
- `custom_components/lipro/{light,fan,switch,cover,climate,binary_sensor,sensor,select,update}.py`: HA platform setup entry files.

**Configuration:**
- `pyproject.toml`: Python project metadata and tool configuration.
- `uv.lock`: locked dependency graph.
- `custom_components/lipro/manifest.json`: Home Assistant integration metadata.
- `.github/workflows/ci.yml`: CI verification route.
- `.planning/baseline/ARCHITECTURE_POLICY.md`: architecture enforcement truth.

**Core Logic:**
- `custom_components/lipro/core/protocol/facade.py`: unified protocol root.
- `custom_components/lipro/core/api/rest_facade.py`: REST child façade.
- `custom_components/lipro/core/coordinator/coordinator.py`: runtime root.
- `custom_components/lipro/core/device/device.py`: canonical device aggregate.
- `custom_components/lipro/control/runtime_access.py`: formal control-to-runtime read surface.

**Testing:**
- `tests/core/`: protocol/runtime/domain/control behavior tests.
- `tests/flows/`: config/options flow tests.
- `tests/services/`: service helper and service behavior tests.
- `tests/meta/`: architecture, public-surface, governance, and route guards.
- `tests/fixtures/`: canonical boundary and replay fixture families.

## Naming Conventions

**Files:**
- Home Assistant platform adapters use HA platform names at the package root: `light.py`, `fan.py`, `switch.py`, `cover.py`, `climate.py`, `binary_sensor.py`, `sensor.py`, `select.py`, `update.py`.
- Role suffixes describe responsibility: `*_surface.py`, `*_support.py`, `*_runtime.py`, `*_service.py`, `*_facade.py`, `*_decoder.py`.
- Stable export/import shells keep short names and minimal logic: `custom_components/lipro/coordinator_entry.py`, `custom_components/lipro/core/api/client.py`.
- Python modules and directories use `snake_case`; nested groups are semantic, not technical abstractions.

**Directories:**
- Top-level source grouping follows planes and usage: `control`, `core`, `entities`, `flow`, `helpers`, `services`.
- Deeper runtime decomposition stays adjacent to the formal owner: `custom_components/lipro/core/coordinator/runtime/command/`, `custom_components/lipro/core/coordinator/runtime/device/`, `custom_components/lipro/core/coordinator/runtime/mqtt/`.
- Support-only splits use descriptive sibling modules instead of new roots, for example `runtime_access_support_*` and `share_client_*`.

## Where to Add New Code

**New Protocol Change:**
- Primary code: `custom_components/lipro/core/protocol/`, `custom_components/lipro/core/api/`, or `custom_components/lipro/core/mqtt/` depending whether the change is root composition, REST orchestration, or concrete MQTT transport.
- Tests: `tests/core/protocol/`, `tests/core/api/`, `tests/core/mqtt/`, plus `tests/integration/test_protocol_replay_harness.py` or `tests/integration/test_mqtt_coordinator_integration.py` when the public path changes.

**New Runtime Behavior:**
- Primary code: `custom_components/lipro/core/coordinator/runtime/` and `custom_components/lipro/core/coordinator/services/`.
- Tests: `tests/core/coordinator/` and `tests/integration/` for runtime-public changes.

**New Control-Plane Feature:**
- Primary code: `custom_components/lipro/control/`.
- Tests: `tests/core/` or `tests/services/` depending whether the change is lifecycle/runtime-access or service-facing.

**New Platform Projection:**
- Implementation: root platform file in `custom_components/lipro/` plus shared entity logic in `custom_components/lipro/entities/` or `custom_components/lipro/helpers/platform.py`.
- Tests: `tests/platforms/` and `tests/entities/`.

**Utilities:**
- Shared cross-plane helpers: `custom_components/lipro/core/utils/`.
- Local support-only splits: place them beside the owning formal home, such as `custom_components/lipro/control/runtime_access_support_*.py` or `custom_components/lipro/core/anonymous_share/share_client_*.py`.

## Maintainability Notes

- Keep business logic out of `custom_components/lipro/__init__.py`, `custom_components/lipro/diagnostics.py`, `custom_components/lipro/system_health.py`, and `custom_components/lipro/config_flow.py`; they are intentionally thin adapters.
- Treat `custom_components/lipro/control/` and `custom_components/lipro/services/` as owner-plus-helper, not twin roots; new service registrations belong in `custom_components/lipro/control/service_registry.py`.
- Keep stable shells thin: `custom_components/lipro/core/api/client.py`, `custom_components/lipro/coordinator_entry.py`, and `custom_components/lipro/runtime_infra.py` are topology anchors, not new behavior homes.
- Current large modules worth careful decomposition-by-concern are `custom_components/lipro/core/coordinator/runtime/command_runtime.py`, `custom_components/lipro/core/anonymous_share/manager.py`, `custom_components/lipro/core/api/rest_facade.py`, `custom_components/lipro/control/runtime_access.py`, and `custom_components/lipro/entities/base.py`.
- Runtime and protocol authority are intentionally centralized; do not create parallel directories such as a second service root, a second protocol boundary family, or direct platform access to runtime internals.

## Special Directories

**`.planning/baseline/`:**
- Purpose: formal baseline truth for architecture, surfaces, authority, verification, and target topology.
- Generated: No
- Committed: Yes

**`.planning/reviews/`:**
- Purpose: file ownership, residual, kill-list, promoted asset, and audit evidence truth.
- Generated: No
- Committed: Yes

**`.planning/codebase/`:**
- Purpose: derived collaboration maps used for navigation and onboarding.
- Generated: No
- Committed: Yes

**`tests/fixtures/`:**
- Purpose: canonical fixture families for API contracts, external boundaries, protocol boundary decoders, replay, and evidence packs.
- Generated: No
- Committed: Yes

**`custom_components/lipro/headless/`:**
- Purpose: proof-only local boot seam for host-neutral auth/bootstrap consumers.
- Generated: No
- Committed: Yes

**`custom_components/lipro/select_internal/`:**
- Purpose: internal helper entities and mapping logic that support the public `select.py` platform without polluting the root platform contract.
- Generated: No
- Committed: Yes

**`custom_components/lipro/__pycache__/`, `tests/**/__pycache__/`, `lipro_smart_home.egg-info/`:**
- Purpose: local interpreter/build byproducts only.
- Generated: Yes
- Committed: No

---

*Structure analysis: 2026-03-27*


## Phase 90 Routing Freeze

- Current navigation must treat `core/api/rest_facade.py`, `core/api/request_policy.py`, `core/coordinator/runtime/{command_runtime.py,mqtt_runtime.py}`, and `core/anonymous_share/manager.py` as retained formal homes.
- `core/api/client.py` stays a stable import shell, while `__init__.py`, `control/runtime_access.py`, `entities/base.py`, and `entities/firmware_update.py` stay outward thin shells only.


## Phase 91 Boundary Structure

- `core/protocol/rest_port.py` remains the raw REST child-port layer, while canonical protocol verbs stay in `core/protocol/protocol_facade_rest_methods.py`.
- `runtime_types.py`, `core/coordinator/types.py`, and `core/coordinator/services/telemetry_service.py` now form the shared typed telemetry spine for control/runtime projections.
