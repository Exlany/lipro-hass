---
phase: 91
slug: protocol-runtime-decomposition-and-typed-boundary-hardening
nyquist_compliant: true
wave_0_complete: true
updated: 2026-03-28
---

# Phase 91 Validation Contract

## Wave Order

1. `91-01` protocol live-path canonicalization
2. `91-02` typed-boundary / telemetry contract hardening
3. `91-03` governance freeze and route-handoff verification

## Per-Plan Focused Gates

- `91-01`
  - `uv run pytest -q tests/core/api/test_protocol_contract_facade_runtime.py tests/core/api/test_protocol_contract_boundary_decoders.py` → `passed`
  - `uv run ruff check custom_components/lipro/core/protocol/protocol_facade_rest_methods.py custom_components/lipro/core/protocol/rest_port.py custom_components/lipro/core/coordinator/runtime/device/snapshot.py custom_components/lipro/core/coordinator/orchestrator.py tests/core/api/test_protocol_contract_facade_runtime.py` → `passed`
- `91-02`
  - `uv run ruff check custom_components/lipro/runtime_types.py custom_components/lipro/core/coordinator/types.py custom_components/lipro/core/protocol/boundary/result.py custom_components/lipro/core/protocol/boundary/schema_registry.py custom_components/lipro/core/protocol/boundary/rest_decoder_support.py custom_components/lipro/core/protocol/boundary/rest_decoder.py custom_components/lipro/core/protocol/boundary/mqtt_decoder.py custom_components/lipro/core/command/trace.py custom_components/lipro/core/protocol/protocol_facade_rest_methods.py custom_components/lipro/core/coordinator/runtime/command_runtime.py custom_components/lipro/core/coordinator/runtime/mqtt_runtime.py custom_components/lipro/core/coordinator/runtime/status_runtime.py custom_components/lipro/core/coordinator/runtime/command/confirmation.py custom_components/lipro/core/coordinator/services/telemetry_service.py custom_components/lipro/entities/firmware_update.py` → `passed`
  - `uv run pytest -q tests/core/coordinator/runtime/test_runtime_telemetry_methods.py tests/core/coordinator/runtime/test_command_runtime_orchestration.py tests/core/test_runtime_access.py tests/platforms/test_firmware_update_entity_edges.py` → `passed`
  - `uv run mypy custom_components/lipro/runtime_types.py custom_components/lipro/core/coordinator/types.py custom_components/lipro/core/protocol/boundary/result.py custom_components/lipro/core/protocol/boundary/schema_registry.py custom_components/lipro/core/protocol/boundary/rest_decoder_support.py custom_components/lipro/core/protocol/boundary/rest_decoder.py custom_components/lipro/core/protocol/boundary/mqtt_decoder.py custom_components/lipro/core/command/trace.py custom_components/lipro/core/protocol/protocol_facade_rest_methods.py custom_components/lipro/core/coordinator/runtime/command_runtime.py custom_components/lipro/core/coordinator/runtime/mqtt_runtime.py custom_components/lipro/core/coordinator/runtime/status_runtime.py custom_components/lipro/core/coordinator/runtime/command/confirmation.py custom_components/lipro/core/coordinator/services/telemetry_service.py custom_components/lipro/entities/firmware_update.py` → `passed`
- `91-03`
  - `uv run pytest -q tests/meta/test_phase90_hotspot_map_guards.py tests/meta/test_phase91_typed_boundary_guards.py tests/meta/test_dependency_guards.py tests/meta/test_public_surface_guards.py tests/meta/test_governance_route_handoff_smoke.py tests/meta/governance_followup_route_current_milestones.py tests/meta/test_governance_bootstrap_smoke.py` → `passed`
  - `uv run python scripts/check_file_matrix.py --check` → `passed`
  - `node "$HOME/.codex/get-shit-done/bin/gsd-tools.cjs" init progress` → `passed`
  - `node "$HOME/.codex/get-shit-done/bin/gsd-tools.cjs" state json` → `passed`
  - `node "$HOME/.codex/get-shit-done/bin/gsd-tools.cjs" phase-plan-index 91` → `passed`

## Final Gate

- `uv run pytest -q tests/meta` → `passed`
- `uv run ruff check .` → `passed`
- `uv run mypy` → `passed`
- `node "$HOME/.codex/get-shit-done/bin/gsd-tools.cjs" init progress` → `Phase 91 = complete`, `summary_count = 3`
- `node "$HOME/.codex/get-shit-done/bin/gsd-tools.cjs" state json` → `v1.25 active`, `2/4 phases`, `6/6 plans`, `status = complete`
- `node "$HOME/.codex/get-shit-done/bin/gsd-tools.cjs" phase-plan-index 91` → `incomplete = []`

## Sign-off Checklist

- [x] protocol live canonicalization is enforced at the protocol root and no longer duplicated by runtime consumers
- [x] typed-boundary / telemetry / trace contracts stay narrow and machine-checkable
- [x] protected thin shells remain outward-only; no orchestration backflow was introduced
- [x] current-route truth, file matrix, residual/kill ledgers, and focused guards now reduce the next step to `$gsd-discuss-phase 92`
