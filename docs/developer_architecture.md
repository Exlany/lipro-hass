# Lipro Developer Architecture

> Role: describe the current code layout, formal roots, and the shortest path for contributors.

## Quick Navigation

| Area | Path | Role |
| --- | --- | --- |
| Integration entry | `custom_components/lipro/__init__.py` | thin adapter that wires control and runtime |
| Protocol root | `custom_components/lipro/core/protocol/facade.py` | `LiproProtocolFacade`, the only protocol root |
| REST facade | `custom_components/lipro/core/api/rest_facade.py` | REST-facing protocol collaborators |
| MQTT facade | `custom_components/lipro/core/protocol/mqtt_facade.py` | MQTT-facing protocol collaborators |
| Runtime root | `custom_components/lipro/core/coordinator/coordinator.py` | `Coordinator`, the only runtime orchestration root |
| Runtime services | `custom_components/lipro/core/coordinator/services/` | polling, protocol, auth, telemetry, refresh helpers |
| Domain truth | `custom_components/lipro/core/device/`, `custom_components/lipro/core/capability/` | device aggregate and capability truth |
| Control plane | `custom_components/lipro/control/` | lifecycle, router, runtime access, diagnostics, system health |
| Service adapters | `custom_components/lipro/services/` | Home Assistant service schemas and thin helpers |
| Contributor docs | `CONTRIBUTING.md`, `docs/CONTRIBUTOR_ARCHITECTURE_CHANGE_MAP.md` | workflow and change boundaries |

## Formal Planes

### Protocol

- `LiproProtocolFacade` is the only formal protocol root.
- REST and MQTT live under the protocol plane as collaborators, not as alternate roots.
- Vendor payload normalization stays at the boundary.

### Runtime

- `Coordinator` is the only formal runtime root.
- Runtime collaborators under `core/coordinator/runtime/` own state refresh, command confirmation, and MQTT application flow.
- Runtime writes must not be bypassed from entities, services, or platform adapters.

### Domain

- `LiproDevice` is the device aggregate facade.
- Capability truth belongs to `CapabilityRegistry` and related domain models.
- Platform code projects domain truth into Home Assistant entities; it does not redefine it.

### Control

- `custom_components/lipro/control/` is the formal home for lifecycle, routing, diagnostics, system health, and runtime access.
- Root files such as `config_flow.py`, `diagnostics.py`, and `system_health.py` stay as thin adapters.
- `custom_components/lipro/services/` provides service declarations and helper logic, not a second control root.

### Assurance

- `tests/` and `scripts/` provide the active quality gates.
- Architecture, link, translation, and focused governance checks should be machine-verifiable.
- Local governance or scratch assets are not part of the release tree.

## Root-Level Homes That Matter

- `custom_components/lipro/runtime_infra.py`: shared runtime bootstrap and listener ownership
- `custom_components/lipro/runtime_types.py`: typed runtime contracts
- `custom_components/lipro/service_types.py`: shared service-facing typed contracts
- `custom_components/lipro/entry_auth.py`: config-entry auth/bootstrap helpers

## Rules That Should Not Regress

- Do not restore `LiproClient`, `LiproMqttClient`, `raw_client`, or similar legacy compat names.
- Do not let platform/entity code reach protocol internals or runtime private state directly.
- Do not turn root Home Assistant modules into business-logic homes.
- `custom_components/lipro/services/execution.py` remains a formal service execution facade; do not reintroduce bypass auth/runtime access paths.

## Suggested Validation

- `uv run ruff check .`
- `uv run ruff format --check .`
- `uv run python scripts/check_architecture_policy.py --check`
- `uv run python scripts/check_file_matrix.py --check`
- `uv run python scripts/check_markdown_links.py`
- `uv run python scripts/check_translations.py`
- `uv run pytest -q`

## Related Documents

- `docs/NORTH_STAR_TARGET_ARCHITECTURE.md`
- `docs/CONTRIBUTOR_ARCHITECTURE_CHANGE_MAP.md`
- `docs/adr/README.md`
- `README.md` / `README_zh.md`
