---
phase: 94
slug: typed-payload-contraction-and-domain-bag-narrowing
nyquist_compliant: true
wave_0_complete: true
updated: 2026-03-28
---

# Phase 94 Validation Contract

## Wave Order

1. `94-01` domain bag / entity generic / property-normalization contraction
2. `94-02` diagnostics / REST helper mapping contract tightening
3. `94-03` no-growth guard, closeout proof, and route handoff

## Focused Gates

- `94-01`
  - `uv run pytest -q tests/core/test_property_normalization.py tests/core/test_entry_update_listener.py tests/core/test_init_edge_cases.py tests/core/test_anonymous_share_cov_missing.py` → `passed`
  - `uv run ruff check custom_components/lipro/domain_data.py custom_components/lipro/entry_options.py custom_components/lipro/core/anonymous_share/registry.py custom_components/lipro/entities/base.py custom_components/lipro/core/utils/property_normalization.py tests/core/test_property_normalization.py tests/core/test_anonymous_share_cov_missing.py` → `passed`
  - `uv run mypy custom_components/lipro/domain_data.py custom_components/lipro/entry_options.py custom_components/lipro/core/anonymous_share/registry.py custom_components/lipro/entities/base.py custom_components/lipro/core/utils/property_normalization.py` → `passed`
- `94-02`
  - `uv run pytest -q tests/core/api/test_api_command_service.py tests/core/api/test_api_status_service_fallback.py tests/core/api/test_api_transport_executor.py tests/core/test_diagnostics.py tests/core/test_diagnostics_config_entry.py tests/core/test_diagnostics_device.py` → `passed`
  - `uv run ruff check custom_components/lipro/control/diagnostics_surface.py custom_components/lipro/diagnostics.py custom_components/lipro/core/api/command_api_service.py custom_components/lipro/core/api/status_fallback.py custom_components/lipro/core/api/status_service.py custom_components/lipro/core/api/transport_core.py tests/core/api/test_api_transport_executor.py` → `passed`
  - `uv run mypy custom_components/lipro/control/diagnostics_surface.py custom_components/lipro/diagnostics.py custom_components/lipro/core/api/command_api_service.py custom_components/lipro/core/api/status_fallback.py custom_components/lipro/core/api/status_service.py custom_components/lipro/core/api/transport_core.py` → `passed`
- `94-03`
  - `uv run pytest -q tests/meta/test_phase94_typed_boundary_guards.py` → `passed`
  - `uv run pytest -q tests/meta` → `passed (527 passed)`
  - `uv run python scripts/check_file_matrix.py --check` → `passed`
  - `uv run ruff check .` → `passed`
  - `uv run mypy` → `passed`

## GSD Route Evidence

- `node "$HOME/.codex/get-shit-done/bin/gsd-tools.cjs" state json` → `milestone = v1.26`, `current_phase = 95`, `status = active`, `completed_phases = 1`, `completed_plans = 3`
- `node "$HOME/.codex/get-shit-done/bin/gsd-tools.cjs" init progress` → `Phase 94 summary_count = 3`, `current_phase = 95`, `Phase 95 = execution-ready target`
- `node "$HOME/.codex/get-shit-done/bin/gsd-tools.cjs" phase-plan-index 94` → `incomplete = []`

## Sign-off Checklist

- [x] domain bag / property normalization / anonymous-share registry no longer expose broad `Any` seams
- [x] entity base no longer carries `CoordinatorEntity[Any]`
- [x] diagnostics / transport / status helpers stay on honest JSON-like / mapping / logger contracts
- [x] focused no-growth guard and planning route truth reduce the next action to `$gsd-execute-phase 95`
