# Phase 104 Verification

## Requirement Coverage

| Requirement | Verdict | Evidence |
| --- | --- | --- |
| `HOT-44` | passed | `custom_components/lipro/control/service_router_handlers.py`, `custom_components/lipro/control/service_router_{command,schedule,share,diagnostics,maintenance}_handlers.py`, `104-01-SUMMARY.md` |
| `HOT-45` | passed | `custom_components/lipro/core/coordinator/runtime/command_runtime.py`, `custom_components/lipro/core/coordinator/runtime/command_runtime_support.py`, `custom_components/lipro/core/coordinator/runtime/command_runtime_outcome_support.py`, `104-02-SUMMARY.md` |
| `TST-36` | pending re-verify | focused service-router/runtime suites + governance guards + file-matrix / quality gates |

## Focused Gates

- `uv run pytest -q tests/core/test_init_service_handlers_commands.py tests/core/test_init_service_handlers_schedules.py tests/core/test_init_service_handlers_share_reports.py tests/core/test_init_service_handlers_sensor_feedback.py tests/core/test_init_service_handlers_debug_queries.py tests/core/test_init_runtime_registry_refresh.py tests/services/test_service_resilience.py tests/core/coordinator/runtime/test_command_runtime.py tests/core/test_runtime_telemetry_methods.py tests/core/coordinator/services/test_command_service.py tests/core/coordinator/services/test_telemetry_service.py`
- `uv run pytest -q tests/meta/test_phase104_service_router_runtime_split_guards.py tests/meta/test_phase103_root_thinning_guards.py tests/meta/test_governance_route_handoff_smoke.py tests/meta/governance_followup_route_current_milestones.py`
- `uv run ruff check custom_components/lipro/control/service_router_handlers.py custom_components/lipro/control/service_router_command_handlers.py custom_components/lipro/control/service_router_schedule_handlers.py custom_components/lipro/control/service_router_share_handlers.py custom_components/lipro/control/service_router_diagnostics_handlers.py custom_components/lipro/control/service_router_maintenance_handlers.py custom_components/lipro/core/coordinator/runtime/command_runtime.py custom_components/lipro/core/coordinator/runtime/command_runtime_support.py custom_components/lipro/core/coordinator/runtime/command_runtime_outcome_support.py tests/core/coordinator/runtime/test_command_runtime.py tests/core/coordinator/runtime/test_command_runtime_outcome_support.py tests/meta/governance_current_truth.py tests/meta/test_phase103_root_thinning_guards.py tests/meta/test_phase104_service_router_runtime_split_guards.py tests/meta/test_governance_route_handoff_smoke.py tests/meta/governance_followup_route_current_milestones.py scripts/check_file_matrix_registry_classifiers.py scripts/check_file_matrix_registry_overrides.py`

## Repo-wide Gates

- `uv run python scripts/check_file_matrix.py --write`
- `uv run python scripts/check_file_matrix.py --check`
- `uv run pytest -q tests/meta`
- `uv run ruff check .`
- `uv run mypy`
- `uv run python scripts/check_architecture_policy.py --check`
- `uv run python scripts/check_markdown_links.py`
- `uv run pytest -q`
