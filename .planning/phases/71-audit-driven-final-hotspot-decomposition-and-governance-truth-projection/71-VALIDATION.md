# Phase 71 Validation Contract

## Wave Order

1. `71-01` terminal audit / validation contract / hotspot-route guards
2. `71-02` OTA diagnostics + firmware-install orchestration decomposition
3. `71-03` anonymous-share submit + request pacing + command-runtime thinning
4. `71-04` current-route / latest-archive truth single-source sync
5. `71-05` promoted assets + file matrix + final gate

## Per-Plan Focused Gates

- `71-01`
  - `uv run pytest -q tests/meta/test_phase71_hotspot_route_guards.py`
- `71-02`
  - `uv run pytest -q tests/core/api/test_api_diagnostics_service.py tests/platforms/test_update.py tests/platforms/test_update_entity_refresh.py tests/platforms/test_update_install_flow.py tests/meta/test_phase71_hotspot_route_guards.py`
- `71-03`
  - `uv run pytest -q tests/core/test_share_client.py tests/core/api/test_api_request_policy.py tests/core/coordinator/runtime/test_command_runtime.py tests/meta/test_phase71_hotspot_route_guards.py`
- `71-04`
  - `uv run pytest -q tests/meta/test_governance_release_contract.py tests/meta/test_governance_milestone_archives.py tests/meta/test_version_sync.py tests/meta/governance_followup_route_current_milestones.py tests/meta/test_phase71_hotspot_route_guards.py`
- `71-05`
  - `uv run ruff check .`
  - `uv run mypy --follow-imports=silent .`
  - `uv run python scripts/check_architecture_policy.py --check`
  - `uv run python scripts/check_file_matrix.py --check`

## Final Gate

- `uv run ruff check .`
- `uv run mypy --follow-imports=silent .`
- `uv run python scripts/check_architecture_policy.py --check`
- `uv run python scripts/check_file_matrix.py --check`
- `uv run pytest -q`

## Sign-off Checklist

- [x] OTA / firmware-update / share / pacing / command-runtime long flows are thinner without new outward roots
- [x] latest-archive / no-active-route truth is machine-checkable and distinct from previous archived baseline
- [x] latest archived pointer now resolves to `V1_19_EVIDENCE_INDEX.md`
- [x] phase-71 guards freeze touched hotspot/function budgets and route locality
- [x] planning / baseline / docs truth matches executed reality
