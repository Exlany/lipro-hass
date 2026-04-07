# Phase 112 Verification

## Verdict

- `ARC-29`: passed
- `GOV-72`: passed

## Evidence

### 112-01 Maintainer docs normalization
- `docs/developer_architecture.md` 已明确承认 `v1.31` active route，并把 `runtime_infra.py`、`runtime_types.py`、`entry_auth.py` 登记为 sanctioned root-level homes。
- `docs/MAINTAINER_RELEASE_RUNBOOK.md` 已统一到 `.planning/reviews/V1_30_EVIDENCE_INDEX.md` 与 `.planning/v1.30-MILESTONE-AUDIT.md` 作为 latest archived pointer。

### 112-02 Runtime-access naming de-ambiguation
- `RuntimeCoordinatorView.runtime_coordinator` alias 已取代 targeted helper files 中的 `.coordinator.coordinator` 命名折返。
- `tests/core/test_runtime_access.py` 与 `tests/core/test_control_plane.py` 已冻结新的 alias-based naming contract。

### 112-03 Governance freeze and route-truth alignment
- `.planning/baseline/AUTHORITY_MATRIX.md` 已把 live selectors 与 archive chronology 明确分离，并把 latest archived evidence index 前推到 `V1_30`。
- `.planning/reviews/FILE_MATRIX.md` 已为 `entry_auth.py` / `runtime_infra.py` 补齐 sanctioned-home wording，并登记 `tests/meta/test_phase112_formal_home_governance_guards.py`。
- `.planning/baseline/VERIFICATION_MATRIX.md` 已收录 Phase 112 acceptance truth。
- active route machine truth 已从 `Phase 112 discussion-ready` 前推到 `Phase 112 complete / Phase 113 discussion-ready` 所需的 closeout basis。

## Commands

- `uv run pytest -q tests/meta/test_governance_release_docs.py tests/meta/test_governance_release_contract.py tests/core/test_runtime_access.py tests/core/test_control_plane.py tests/core/test_init_service_handlers_debug_queries.py`
  - `65 passed in 1.38s`
- `uv run python scripts/check_file_matrix.py --check`
  - passed
- `uv run pytest -q tests/meta/governance_current_truth.py tests/meta/test_governance_guards.py tests/meta/test_governance_route_handoff_smoke.py tests/meta/test_phase112_formal_home_governance_guards.py`
  - `18 passed in 3.98s`
- `uv run ruff check custom_components/lipro/control/runtime_access_types.py custom_components/lipro/control/runtime_access_support_views.py custom_components/lipro/control/runtime_access_support_devices.py custom_components/lipro/control/developer_router_support.py tests/core/test_runtime_access.py tests/core/test_control_plane.py tests/core/test_init_service_handlers_debug_queries.py tests/meta/test_governance_release_docs.py tests/meta/test_governance_release_contract.py tests/meta/governance_current_truth.py tests/meta/test_governance_guards.py tests/meta/test_governance_route_handoff_smoke.py tests/meta/test_phase112_formal_home_governance_guards.py tests/meta/governance_followup_route_current_milestones.py`
  - `All checks passed!`

## Conclusion

Phase 112 已把 formal-home discoverability、archived pointer truth 与 misleading naming residue 收口为同一条 maintainer/baseline/guard 主线；后续 phase 不应再回头修补 archived-only current-story 或 `.coordinator.coordinator` 这类噪音。
