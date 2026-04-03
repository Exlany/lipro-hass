# Phase 141 Verification

status: passed

## Focused Commands

- `uv run ruff check custom_components/lipro/control/service_router.py custom_components/lipro/control/service_router_support.py tests/core/test_init_service_handlers_device_resolution.py tests/core/test_init_service_handlers_share_reports.py tests/core/test_init_service_handlers_sensor_feedback.py tests/services/test_services_registry.py tests/meta/test_phase123_service_router_reconvergence_guards.py`
- `uv run pytest -q tests/core/test_init_service_handlers_device_resolution.py tests/core/test_init_service_handlers_share_reports.py tests/core/test_init_service_handlers_sensor_feedback.py tests/services/test_services_registry.py tests/meta/test_phase123_service_router_reconvergence_guards.py`
- `uv run ruff check custom_components/lipro/control/entry_root_support.py custom_components/lipro/control/entry_root_wiring.py custom_components/lipro/__init__.py tests/core/test_entry_root_wiring.py tests/core/test_init_runtime_registry_refresh.py tests/meta/test_phase103_root_thinning_guards.py`
- `uv run pytest -q tests/core/test_entry_root_wiring.py tests/core/test_init_runtime_registry_refresh.py tests/meta/test_phase103_root_thinning_guards.py`
- `uv run ruff check custom_components/lipro/runtime_types.py custom_components/lipro/control/runtime_access_types.py custom_components/lipro/control/entry_lifecycle_support.py custom_components/lipro/control/runtime_access_support_devices.py custom_components/lipro/control/runtime_access_support_views.py custom_components/lipro/control/runtime_access_support_telemetry.py custom_components/lipro/services/command.py custom_components/lipro/services/execution.py tests/meta/test_runtime_contract_truth.py tests/meta/dependency_guards_service_runtime.py tests/core/test_runtime_access.py tests/core/test_auth.py tests/core/test_command_dispatch.py tests/core/coordinator/services/test_auth_service.py`
- `uv run pytest -q tests/meta/test_runtime_contract_truth.py tests/meta/dependency_guards_service_runtime.py tests/core/test_runtime_access.py tests/core/test_auth.py tests/core/test_command_dispatch.py tests/core/coordinator/services/test_auth_service.py`
- `uv run ruff check custom_components/lipro/core/device custom_components/lipro/control/diagnostics_surface.py tests/core/device/test_device.py tests/core/test_outlet_power.py tests/core/test_outlet_power_runtime.py tests/core/coordinator/runtime/test_device_runtime.py tests/core/test_diagnostics_config_entry.py tests/platforms/test_sensor.py tests/platforms/test_entity_behavior.py tests/core/coordinator/test_runtime_polling.py tests/core/coordinator/runtime/test_state_runtime.py`
- `uv run pytest -q tests/core/device/test_device.py tests/core/test_outlet_power.py tests/core/test_outlet_power_runtime.py tests/core/coordinator/runtime/test_device_runtime.py tests/core/test_diagnostics_config_entry.py tests/platforms/test_sensor.py tests/platforms/test_entity_behavior.py tests/core/coordinator/test_runtime_polling.py tests/core/coordinator/runtime/test_state_runtime.py`
- `uv run pytest -q tests/core/test_init_service_handlers_device_resolution.py tests/services/test_services_registry.py tests/core/test_entry_root_wiring.py tests/meta/test_runtime_contract_truth.py tests/core/device/test_device.py tests/core/test_outlet_power.py tests/core/test_outlet_power_runtime.py tests/core/coordinator/runtime/test_device_runtime.py tests/core/test_diagnostics_config_entry.py tests/meta/test_phase123_service_router_reconvergence_guards.py tests/meta/test_phase103_root_thinning_guards.py tests/meta/dependency_guards_service_runtime.py tests/meta/governance_followup_route_current_milestones.py tests/meta/test_governance_route_handoff_smoke.py tests/meta/test_governance_release_contract.py tests/meta/test_governance_release_docs.py tests/meta/test_governance_promoted_phase_assets.py tests/meta/test_governance_release_continuity.py tests/meta/test_version_sync.py tests/meta/test_phase140_governance_source_freshness_guards.py`
- `uv run python scripts/check_file_matrix.py --check`
- `uv run python scripts/check_architecture_policy.py --check`
- `uv run ruff check custom_components/lipro/control custom_components/lipro/runtime_types.py custom_components/lipro/core/device tests`

## Results

- `141-01` focused verification passed: `24 passed`。
- `141-02` focused verification passed: `12 passed`。
- `141-03` focused verification passed: `80 passed`。
- `141-04` focused verification passed: `152 passed`。
- final governance / closeout verification passed: `177 passed`。
- `uv run python scripts/check_file_matrix.py --check`、`uv run python scripts/check_architecture_policy.py --check` 与最终 `uv run ruff check custom_components/lipro/control custom_components/lipro/runtime_types.py custom_components/lipro/core/device tests` 全部通过。
- current route 现以 machine-checkable proof 承认 `Phase 141 complete / closeout-ready`。
