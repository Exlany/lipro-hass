# Phase 41 Architecture & Code Audit Shard

## Architecture Verdict

- Mainline verdict: **largely aligned** with north-star; strongest areas are protocol/runtime/domain separation and thin HA adapters.
- Best evidence: `custom_components/lipro/core/protocol/facade.py:39`, `custom_components/lipro/core/coordinator/coordinator.py:53`, `custom_components/lipro/core/device/device.py:41`, `custom_components/lipro/__init__.py:356`.

## Plane Boundary Findings

- `High`: `control/` ↔ `services/` remains a sticky bidirectional cluster, see `custom_components/lipro/services/registrations.py:9`, `custom_components/lipro/services/device_lookup.py:14`, `custom_components/lipro/control/service_router_handlers.py:58`.
- `Medium`: `RuntimeAccess` still uses reflection / MagicMock-aware probing, see `custom_components/lipro/control/runtime_access.py:23`, `custom_components/lipro/control/runtime_access.py:24`, `custom_components/lipro/control/runtime_access.py:70`.
- `Medium`: `services/maintenance.py` still mixes public service helpers with runtime infra, see `custom_components/lipro/services/maintenance.py:41`, `custom_components/lipro/services/maintenance.py:116`.
- `Medium`: schedule service still depends on protocol-layer codec/type helpers, see `custom_components/lipro/services/schedule.py:12`, `custom_components/lipro/services/schedule.py:13`, `custom_components/lipro/services/schedule.py:14`.

## Hotspots

- `scripts/check_file_matrix.py:1` — 969 LOC, governance hotspot
- `custom_components/lipro/core/protocol/boundary/rest_decoder_support.py:1` — boundary helper cluster too dense
- `custom_components/lipro/core/api/diagnostics_api_service.py:139` — long OTA diagnostic fallback chain
- `custom_components/lipro/core/anonymous_share/share_client.py:153` — long upload/error path
- `custom_components/lipro/control/runtime_access.py:1` — concentrated control read-model logic

## Naming and Residual Findings

- ADR and code comments still leak `Client` / `mixin` era wording, see `docs/adr/README.md:47`, `docs/adr/0004-explicit-lightweight-boundaries.md:17`, `custom_components/lipro/core/api/endpoints/devices.py:13`, `custom_components/lipro/core/api/endpoints/misc.py:32`.
- `custom_components/lipro/core/auth/manager.py:28` and nearby comments still carry legacy phrasing.
- Same-name objects across layers increase navigation cost, e.g. `AnonymousShareManager` and `MqttConnectionManager`.
