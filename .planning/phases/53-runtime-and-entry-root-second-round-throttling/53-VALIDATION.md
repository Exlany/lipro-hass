---
phase: 53
slug: runtime-and-entry-root-second-round-throttling
status: passed
nyquist_compliant: true
wave_0_complete: true
created: 2026-03-21
---

# Phase 53 — Validation Strategy

## Test Infrastructure

| Property | Value |
|----------|-------|
| **Framework** | `pytest` + runtime/control focused regressions + meta guards |
| **Config file** | `pyproject.toml` |
| **Smoke command** | `uv run pytest -q tests/core/test_coordinator.py tests/core/coordinator/test_runtime_root.py -k "register_entity or unregister_entity or shutdown"` |
| **Quick run command** | `uv run pytest -q tests/core/test_coordinator.py tests/core/test_coordinator_entry.py tests/core/coordinator/test_runtime_root.py tests/core/coordinator/test_update_flow.py tests/core/test_init_runtime_setup_entry.py tests/core/test_init_runtime_setup_entry_failures.py tests/core/test_init_runtime_registry_refresh.py tests/core/test_init_runtime_unload_reload.py tests/core/test_control_plane.py` |
| **Phase gate command** | `uv run pytest -q tests/core/test_coordinator.py tests/core/test_coordinator_entry.py tests/core/coordinator/test_runtime_root.py tests/core/coordinator/test_update_flow.py tests/core/test_init_runtime_setup_entry.py tests/core/test_init_runtime_setup_entry_failures.py tests/core/test_init_runtime_registry_refresh.py tests/core/test_init_runtime_unload_reload.py tests/core/test_control_plane.py tests/meta/test_public_surface_guards.py tests/meta/test_dependency_guards.py tests/meta/test_modularization_surfaces.py && uv run python scripts/check_file_matrix.py --check` |
| **Estimated runtime** | `~60-100s` |

## Wave Structure

- **Wave 1:** `53-01` coordinator runtime throttling
- **Wave 2:** `53-02` entry lifecycle support decomposition
- **Wave 3:** `53-03` root adapter lazy wiring compression + guard/baseline freeze

## Per-Task Verification Map

| Task ID | Plan | Wave | Requirement | Test Type | Automated Command | Status |
|---------|------|------|-------------|-----------|-------------------|--------|
| 53-01-01 | 01 | 1 | HOT-12 | runtime root / entity lifecycle / update cycle | `uv run pytest -q tests/core/test_coordinator.py tests/core/test_coordinator_entry.py tests/core/coordinator/test_runtime_root.py tests/core/coordinator/test_update_flow.py` | ⬜ pending |
| 53-02-01 | 02 | 2 | HOT-12 | setup/unload/reload lifecycle behavior | `uv run pytest -q tests/core/test_init_runtime_setup_entry.py tests/core/test_init_runtime_setup_entry_failures.py tests/core/test_init_runtime_registry_refresh.py tests/core/test_init_runtime_unload_reload.py` | ⬜ pending |
| 53-03-01 | 03 | 3 | HOT-12 | control-plane adapter / lazy wiring / guards | `uv run pytest -q tests/core/test_control_plane.py tests/meta/test_public_surface_guards.py tests/meta/test_dependency_guards.py tests/meta/test_modularization_surfaces.py && uv run python scripts/check_file_matrix.py --check` | ⬜ pending |

## Wave Commands

### Wave 1 Gate
- `uv run pytest -q tests/core/test_coordinator.py tests/core/test_coordinator_entry.py tests/core/coordinator/test_runtime_root.py tests/core/coordinator/test_update_flow.py`

### Wave 2 Gate
- `uv run pytest -q tests/core/test_init_runtime_setup_entry.py tests/core/test_init_runtime_setup_entry_failures.py tests/core/test_init_runtime_registry_refresh.py tests/core/test_init_runtime_unload_reload.py`

### Wave 3 Gate
- `uv run pytest -q tests/core/test_control_plane.py tests/meta/test_public_surface_guards.py tests/meta/test_dependency_guards.py tests/meta/test_modularization_surfaces.py`
- `uv run python scripts/check_file_matrix.py --check`

## Manual-Only Verifications

- 确认 `Coordinator` 仍是唯一 runtime orchestration root；entity bookkeeping 与 bootstrapping 下沉后没有新增 bypass seam。
- 确认 `EntryLifecycleController` 仍是 setup / unload / reload 的唯一 control-plane owner；support helper 只承接 mechanics。
- 确认 `custom_components/lipro/__init__.py` 仍只是 HA adapter thin root；新增 support seam 不成为 public import home。
- 确认 `runtime_infra.py`、`core/coordinator/lifecycle.py` 与任何新增 support-only file 只在 docs/tests 中以 internal/support seam 被叙述。

## Validation Sign-Off

- [x] All planned tasks have automated verification commands.
- [x] Commands use `uv run ...` consistently.
- [x] Wave order follows `runtime root throttling -> lifecycle decomposition -> root adapter compression + truth freeze`.
- [x] `nyquist_compliant: true` set in frontmatter.
- [x] Execution evidence recorded.

**Approval:** execution verified and ready for promotion.
