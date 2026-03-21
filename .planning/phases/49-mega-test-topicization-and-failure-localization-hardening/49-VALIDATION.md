---
phase: 49
slug: mega-test-topicization-and-failure-localization-hardening
status: draft
nyquist_compliant: true
wave_0_complete: true
created: 2026-03-21
---

# Phase 49 — Validation Strategy

## Test Infrastructure

| Property | Value |
|----------|-------|
| **Framework** | `pytest` + governance scripts |
| **Config file** | `pyproject.toml` |
| **Smoke command** | `uv run pytest -q tests/meta/test_governance_closeout_guards.py -k promoted_phase_assets_manifest_enforces_explicit_ci_evidence tests/core/test_coordinator.py -k delegates_to_update_cycle_collaborator tests/core/test_diagnostics.py -k delegates_device_lookup_to_runtime_access tests/platforms/test_update.py -k version_compare_error_is_conservative` |
| **Quick run command** | `uv run pytest -q tests/meta/test_governance_closeout_guards.py tests/core/test_coordinator.py tests/core/test_diagnostics.py tests/platforms/test_update.py` |
| **Phase gate command** | `uv run python scripts/check_file_matrix.py --check && uv run pytest -q tests/meta/test_dependency_guards.py tests/meta/test_public_surface_guards.py tests/meta/test_governance*.py tests/core/coordinator tests/core/test_diagnostics*.py tests/core/ota/test_ota_utils.py tests/core/ota/test_ota_candidate.py tests/core/ota/test_ota_row_selector.py tests/platforms/test_update*.py tests/platforms/test_firmware_update_entity_edges.py` |
| **Estimated runtime** | `~60-120s` |

## Wave Structure

- **Wave 1:** `49-01` governance megaguard concern-family split；`49-02` coordinator / diagnostics topicization
- **Wave 2:** `49-03` update-platform megatest decomposition + stray top-level test re-home
- **Wave 3:** `49-04` assertion ids / failure summaries / final topology truth freeze

## Per-Task Verification Map

| Task ID | Plan | Wave | Requirement | Test Type | Automated Command | Status |
|---------|------|------|-------------|-----------|-------------------|--------|
| 49-01-01 | 01 | 1 | TST-09, QLT-17 | governance | `uv run pytest -q tests/meta/test_governance_closeout_guards.py tests/meta/test_governance_promoted_phase_assets.py tests/meta/test_governance_milestone_archives.py tests/meta/test_governance_followup_route.py tests/meta/test_governance_phase_history.py tests/meta/test_governance_phase_history_runtime.py tests/meta/test_toolchain_truth.py tests/meta/test_governance_release_contract.py tests/meta/test_version_sync.py && uv run python scripts/check_file_matrix.py --check` | ⬜ pending |
| 49-02-01 | 02 | 1 | TST-09, QLT-17 | runtime / diagnostics | `uv run pytest -q tests/core/test_coordinator.py tests/core/coordinator tests/core/test_coordinator_integration.py tests/core/test_diagnostics*.py tests/core/test_control_plane.py` | ⬜ pending |
| 49-03-01 | 03 | 2 | TST-09, QLT-17 | platform / ota / re-home | `uv run pytest -q tests/core/ota/test_ota_utils.py tests/core/ota/test_ota_candidate.py tests/core/ota/test_ota_row_selector.py tests/platforms/test_update*.py tests/platforms/test_firmware_update_entity_edges.py tests/core/test_coordinator_entry.py tests/core/test_init_runtime_setup_entry.py` | ⬜ pending |
| 49-04-01 | 04 | 3 | TST-09, QLT-17 | localization / guards | `uv run pytest -q tests/meta/test_dependency_guards.py tests/meta/test_public_surface_guards.py tests/meta/test_governance*.py tests/core/coordinator tests/core/test_diagnostics*.py tests/core/ota/test_ota_utils.py tests/core/ota/test_ota_candidate.py tests/core/ota/test_ota_row_selector.py tests/platforms/test_update*.py tests/platforms/test_firmware_update_entity_edges.py && uv run python scripts/check_file_matrix.py --check` | ⬜ pending |

## Wave Commands

### Wave 1 Gate

- `uv run pytest -q tests/meta/test_governance_closeout_guards.py tests/meta/test_governance_promoted_phase_assets.py tests/meta/test_governance_milestone_archives.py tests/meta/test_governance_followup_route.py tests/meta/test_governance_phase_history.py tests/meta/test_governance_phase_history_runtime.py tests/meta/test_toolchain_truth.py tests/meta/test_governance_release_contract.py tests/meta/test_version_sync.py`
- `uv run pytest -q tests/core/test_coordinator.py tests/core/coordinator tests/core/test_coordinator_integration.py tests/core/test_diagnostics*.py tests/core/test_control_plane.py`

### Wave 2 Gate

- `uv run pytest -q tests/core/ota/test_ota_utils.py tests/core/ota/test_ota_candidate.py tests/core/ota/test_ota_row_selector.py tests/platforms/test_update*.py tests/platforms/test_firmware_update_entity_edges.py tests/core/test_coordinator_entry.py tests/core/test_init_runtime_setup_entry.py`

### Wave 3 Gate

- `uv run pytest -q tests/meta/test_dependency_guards.py tests/meta/test_public_surface_guards.py tests/meta/test_governance*.py tests/core/coordinator tests/core/test_diagnostics*.py tests/core/ota/test_ota_utils.py tests/core/ota/test_ota_candidate.py tests/core/ota/test_ota_row_selector.py tests/platforms/test_update*.py tests/platforms/test_firmware_update_entity_edges.py`
- `uv run python scripts/check_file_matrix.py --check`

## Manual-Only Verifications

- 确认治理 megaguard 拆分后没有放松 exact token / promoted-asset / follow-up route 的硬约束。
- 确认 `tests/test_coordinator_public.py`、`tests/test_coordinator_runtime.py` re-home 后，不再留下第二条顶层测试故事线。
- 确认 update-platform 拆分先把 pure-helper case 回迁 `tests/core/ota/*`，而不是继续让 platform adapter 代持 domain helper 真相。
- 确认新增 `pytest` ids / assertion messages 真实暴露 concern，不是把抽象 case 序号换个格式继续输出。

## Validation Sign-Off

- [x] All planned tasks have automated verification commands.
- [x] Commands use `uv run ...` consistently.
- [x] Wave order follows `governance+runtime topicization -> platform re-home -> localization freeze`.
- [x] `nyquist_compliant: true` set in frontmatter.
- [ ] Execution evidence pending.

**Approval:** ready for execution after plan verification
