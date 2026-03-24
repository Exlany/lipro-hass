# Phase 70 Validation Contract

## Wave Order

1. `70-01` validation foundations / audit report / hotspot-governance guards
2. `70-02` runtime access support inward split
3. `70-03` anonymous-share + OTA helper convergence
4. `70-04` governance test topicization + archive freeze
5. `70-05` planning/docs/baseline sync + final gate

## Per-Plan Focused Gates

- `70-01`
  - `uv run pytest -q tests/meta/test_phase70_governance_hotspot_guards.py`
- `70-02`
  - `uv run pytest -q tests/meta/test_phase69_support_budget_guards.py tests/meta/test_phase70_governance_hotspot_guards.py tests/core/test_control_plane.py tests/core/test_diagnostics.py tests/core/test_system_health.py tests/meta/test_dependency_guards.py`
- `70-03`
  - `uv run pytest -q tests/meta/test_phase68_hotspot_budget_guards.py tests/core/test_share_client.py tests/core/api/test_api_diagnostics_service.py tests/platforms/test_update.py tests/platforms/test_update_entity_refresh.py tests/core/ota/test_ota_rows_cache.py`
- `70-04`
  - `uv run pytest -q tests/meta/test_version_sync.py tests/meta/test_governance_release_contract.py tests/meta/test_governance_milestone_archives.py tests/meta/governance_followup_route_current_milestones.py tests/meta/test_phase70_governance_hotspot_guards.py`
- `70-05`
  - `uv run ruff check . && uv run mypy --follow-imports=silent . && uv run python scripts/check_architecture_policy.py --check && uv run python scripts/check_file_matrix.py --check`

## Final Gate

- `uv run ruff check .`
- `uv run mypy --follow-imports=silent .`
- `uv run python scripts/check_architecture_policy.py --check`
- `uv run python scripts/check_file_matrix.py --check`
- `uv run pytest -q tests/meta/test_phase68_hotspot_budget_guards.py tests/meta/test_phase69_support_budget_guards.py tests/meta/test_phase70_governance_hotspot_guards.py tests/core/test_share_client.py tests/core/api/test_api_diagnostics_service.py tests/platforms/test_update.py tests/platforms/test_update_entity_refresh.py tests/core/ota/test_ota_rows_cache.py tests/meta/test_version_sync.py tests/meta/test_governance_release_contract.py tests/meta/test_governance_milestone_archives.py tests/meta/governance_followup_route_current_milestones.py`

## Sign-off Checklist

- [ ] hotspots are slimmer without new outward roots
- [ ] OTA selection uses shared helper rather than entity-local choreography
- [ ] archive/current version truth has clear ownership boundary
- [ ] governance tests gained better failure localization
- [ ] planning/review/baseline/docs truth matches executed reality
