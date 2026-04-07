---
phase: 61
slug: formal-home-slimming-for-large-but-correct-production-modules
status: planned
nyquist_compliant: true
wave_0_complete: false
created: 2026-03-22
---

# Phase 61 — Validation Strategy

## Test Infrastructure

| Property | Value |
|----------|-------|
| **Framework** | `uv run pytest -q ...` focused family regressions + touched governance guards |
| **Config file** | `pyproject.toml` |
| **Smoke command** | `uv run pytest -q tests/core/anonymous_share/test_manager_recording.py tests/core/anonymous_share/test_manager_submission.py tests/services/test_services_diagnostics.py tests/core/ota/test_ota_candidate.py tests/platforms/test_select_behavior.py tests/platforms/test_select_models.py` |
| **Phase gate command** | `uv run pytest -q tests/core/anonymous_share/test_manager_recording.py tests/core/anonymous_share/test_manager_submission.py tests/core/test_share_client.py tests/services/test_services_diagnostics.py tests/core/ota/test_ota_candidate.py tests/platforms/test_select_behavior.py tests/platforms/test_select_models.py tests/meta/test_dependency_guards.py tests/meta/test_governance_guards.py` |
| **Estimated runtime** | `~10-120s` |

## Wave Structure

- **Wave 1:** `61-01` anonymous-share slimming、`61-02` diagnostics slimming、`61-03` OTA candidate slimming、`61-04` select slimming 均可并行执行；它们的生产写集互不重叠。

## Per-Task Verification Map

| Task ID | Plan | Wave | Requirement | Test Type | Automated Command | Status |
|---------|------|------|-------------|-----------|-------------------|--------|
| 61-01-01 | 01 | 1 | HOT-15 | anonymous-share formal home stays stable after inward split | `uv run pytest -q tests/core/anonymous_share/test_manager_recording.py tests/core/anonymous_share/test_manager_submission.py` | ⬜ pending |
| 61-01-02 | 01 | 1 | TYP-15 | share-client submit/refresh paths keep typed outcome semantics | `uv run pytest -q tests/core/anonymous_share/test_manager_submission.py` | ⬜ pending |
| 61-02-01 | 02 | 1 | HOT-15 | diagnostics service family keeps one public import surface after slimming | `uv run pytest -q tests/services/test_services_diagnostics.py tests/core/test_init_service_handlers_debug_queries.py tests/meta/test_dependency_guards.py` | ⬜ pending |
| 61-02-02 | 02 | 1 | TYP-15 | developer-feedback / command-result helpers keep typed response contracts | `uv run pytest -q tests/services/test_services_diagnostics.py tests/core/api/test_api_diagnostics_service.py` | ⬜ pending |
| 61-03-01 | 03 | 1 | HOT-15 | OTA candidate outward API remains stable after helper extraction | `uv run pytest -q tests/core/ota/test_ota_candidate.py tests/platforms/test_update_install_flow.py tests/platforms/test_update.py tests/platforms/test_firmware_update_entity_edges.py` | ⬜ pending |
| 61-03-02 | 03 | 1 | TYP-15 | certification / install-policy seams keep typed outward behavior | `uv run pytest -q tests/core/ota/test_ota_candidate.py tests/core/ota/test_firmware_manifest.py tests/meta/test_firmware_support_manifest_repo_asset.py` | ⬜ pending |
| 61-04-01 | 04 | 1 | QLT-20 | select refactor yields focused runnable regressions and smaller failure radius | `uv run pytest -q tests/platforms/test_select_behavior.py tests/platforms/test_select_models.py tests/platforms/test_platform_entities_behavior.py` | ⬜ pending |
| 61-04-02 | 04 | 1 | QLT-20 | maintainability / no-growth evidence freezes touched hotspot posture | `uv run pytest -q tests/meta/test_governance_guards.py tests/meta/test_dependency_guards.py` | ⬜ pending |

## Manual-Only Verifications

- 确认 `manager.py`、`share_client.py`、`helpers.py`、`handlers.py`、`candidate.py`、`select.py` 仍是 outward homes，而不是把 import pressure 转移到新的 internal modules。
- 确认 diagnostics / OTA / select 的 focused regressions 真正按 concern boundary 收窄，而不是只把大测试平移成多个噪音文件。
- 确认本 phase 没有提前把 `Phase 62` 的 naming/discoverability 工作混进生产代码切分。

## Validation Sign-Off

- [x] All planned tasks have automated verification commands.
- [x] Commands use `uv run ...` consistently.
- [x] Wave design allows `61-01 .. 61-04` parallel execution because the production write sets are disjoint.
- [x] `nyquist_compliant: true` set in frontmatter.
- [ ] Execution evidence recorded.
