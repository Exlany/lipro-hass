# Phase 73 Validation Contract

## Wave Order

1. `73-01` service-router forwarding family 收口
2. `73-02` diagnostics/helper convergence + runtime_access projection 收薄
3. `73-03` schedule runtime surface / platform-entity typed contract formalization
4. `73-04` focused guards、route truth、validation closeout

## Per-Plan Focused Gates

- `73-01`
  - `uv run pytest -q tests/core/test_init_service_handlers.py tests/core/test_init_service_handlers_commands.py tests/core/test_init_service_handlers_debug_queries.py tests/services/test_services_registry.py`
- `73-02`
  - `uv run pytest -q tests/core/test_runtime_access.py tests/core/test_diagnostics.py tests/core/test_system_health.py tests/services/test_services_diagnostics.py`
- `73-03`
  - `uv run pytest -q tests/core/coordinator/test_runtime_root.py tests/core/test_init_service_handlers_schedules.py tests/services/test_services_schedule.py tests/platforms/test_entity_base.py tests/platforms/test_platform_entities_behavior.py tests/platforms/test_fan_entity_behavior.py tests/platforms/test_light_entity_behavior.py tests/platforms/test_select_behavior.py`
- `73-04`
  - `uv run pytest -q tests/meta/test_phase73_service_runtime_convergence_guards.py tests/meta/test_governance_release_contract.py tests/meta/test_governance_milestone_archives.py tests/meta/test_version_sync.py tests/meta/governance_followup_route_current_milestones.py`

## Final Gate

- `uv run ruff check .`
- `uv run mypy --follow-imports=silent .`
- `uv run python scripts/check_architecture_policy.py --check`
- `uv run python scripts/check_file_matrix.py --check`
- `uv run pytest -q`

## Sign-off Checklist

- [ ] `service_router` forwarding family 继续保持 thin callback home，不回流第二条 service story
- [ ] `runtime_access.py` 继续只属于 control-plane outward read home，platform/entity 不借它自救
- [ ] `services/schedule.py` 继续只经 `coordinator.schedule_service` 触达 schedule runtime surface
- [ ] `helpers/platform.py` / `entities/base.py` 只消费显式 runtime contract，不回到 raw `.devices` / probe-style fallback
- [ ] current-route / next-command / focused guards 已共同承认 `v1.20 / Phase 73 complete / next = Phase 74`
