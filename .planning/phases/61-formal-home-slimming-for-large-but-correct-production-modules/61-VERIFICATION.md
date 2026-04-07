# Phase 61 Verification

status: passed

## Goal

- 验证 `Phase 61: Formal-home slimming for large-but-correct production modules` 是否完成 `HOT-15 / QLT-20 / TYP-15`：`anonymous_share`、diagnostics、OTA candidate 与 `select` 现已保持单一 outward roots，同时把厚重分支 inward split 到更窄的 internal collaborators，并用 focused tests / governance guards / file-matrix truth 证明收益可持续。

## Deliverable Presence

- `custom_components/lipro/core/anonymous_share/{manager.py,manager_submission.py,share_client.py,share_client_flows.py}` 现共同承载 anonymous-share submit / refresh lifecycle，`manager.py` 与 `share_client.py` 保持 outward roots。
- `custom_components/lipro/services/diagnostics/{helpers.py,handlers.py,feedback_handlers.py,command_result_handlers.py,capability_handlers.py}` 现共同承载 diagnostics helper/handler truth，`helpers.py` / `handlers.py` 保持 public story。
- `custom_components/lipro/core/ota/{candidate.py,candidate_support.py}` 与 `custom_components/lipro/{select.py,select_internal/gear.py}` 现分别承载 OTA/select inward split；`tests/platforms/test_select_behavior.py` 继续是 single runnable shell。
- `.planning/{PROJECT,ROADMAP,REQUIREMENTS,STATE}.md`、`.planning/baseline/VERIFICATION_MATRIX.md`、`.planning/reviews/{FILE_MATRIX,PROMOTED_PHASE_ASSETS,RESIDUAL_LEDGER}.md` 已同步记录 `Phase 61` closeout truth。

## Evidence Commands

- `uv run ruff check custom_components/lipro/core/anonymous_share/manager.py custom_components/lipro/core/anonymous_share/manager_submission.py custom_components/lipro/core/anonymous_share/share_client.py custom_components/lipro/core/anonymous_share/share_client_flows.py custom_components/lipro/services/diagnostics/helpers.py custom_components/lipro/services/diagnostics/handlers.py custom_components/lipro/services/diagnostics/feedback_handlers.py custom_components/lipro/services/diagnostics/command_result_handlers.py custom_components/lipro/services/diagnostics/capability_handlers.py custom_components/lipro/core/ota/candidate.py custom_components/lipro/core/ota/candidate_support.py custom_components/lipro/select.py custom_components/lipro/select_internal/gear.py tests/platforms/test_select_behavior.py tests/platforms/select_setup_behavior_cases.py tests/platforms/select_mapped_behavior_cases.py tests/platforms/select_gear_behavior_cases.py tests/meta/test_phase61_formal_home_budget_guards.py`
- `uv run python scripts/check_file_matrix.py --check`
- `uv run pytest -q tests/core/anonymous_share/test_manager_recording.py tests/core/anonymous_share/test_manager_submission.py tests/core/test_share_client.py tests/core/test_anonymous_share_storage.py tests/services/test_services_share.py tests/core/test_init_service_handlers_share_reports.py tests/services/test_services_diagnostics.py tests/core/test_init_service_handlers_debug_queries.py tests/core/api/test_api_diagnostics_service.py tests/meta/test_dependency_guards.py tests/core/ota/test_ota_candidate.py tests/core/ota/test_firmware_manifest.py tests/platforms/test_update.py tests/platforms/test_update_entity_refresh.py tests/platforms/test_update_install_flow.py tests/platforms/test_update_certification_policy.py tests/platforms/test_firmware_update_entity_edges.py tests/meta/test_firmware_support_manifest_repo_asset.py tests/platforms/test_select_behavior.py tests/platforms/test_select_models.py tests/platforms/test_platform_entities_behavior.py tests/meta/test_phase61_formal_home_budget_guards.py tests/meta/test_governance_guards.py tests/meta/test_public_surface_guards.py`

## Verdict

- `HOT-15` satisfied: large-but-correct production homes 已变成 thin outward roots + focused collaborators，而不是 giant mixed roots。
- `QLT-20` satisfied: select / diagnostics / OTA / anonymous-share now have focused tests and machine-enforced maintainability evidence.
- `TYP-15` satisfied: touched seams 保持 typed outward contracts、one-root story 与 honest governance truth；`Phase 62` 可以专注命名 / discoverability 收口，而无需继续先做 hotspot slimming。
