# Phase 61 Summary

## What Changed

- `anonymous_share` family 已沿单一 formal-home story inward slimming：`manager.py` / `share_client.py` 继续承担 outward roots，submit / refresh / report clusters 迁入 focused collaborators。
- diagnostics service homes 已从 mixed helper/handler clusters 收敛到 `helpers.py` / `handlers.py` + `feedback_handlers.py` / `command_result_handlers.py` / `capability_handlers.py` 的更窄 topology。
- OTA candidate 与 select platform 现都保留单一 outward roots：`candidate.py` + `candidate_support.py`、`select.py` + `select_internal/gear.py`；`test_select_behavior.py` 也已变成 thin runnable shell。
- `tests/meta/test_phase61_formal_home_budget_guards.py` 与重写后的 `.planning/reviews/FILE_MATRIX.md` 已把 touched hotspot 的 no-growth / support-locality posture 机器化冻结。

## Validation

- `uv run ruff check custom_components/lipro/core/anonymous_share/manager.py custom_components/lipro/core/anonymous_share/manager_submission.py custom_components/lipro/core/anonymous_share/share_client.py custom_components/lipro/core/anonymous_share/share_client_flows.py custom_components/lipro/services/diagnostics/helpers.py custom_components/lipro/services/diagnostics/handlers.py custom_components/lipro/services/diagnostics/feedback_handlers.py custom_components/lipro/services/diagnostics/command_result_handlers.py custom_components/lipro/services/diagnostics/capability_handlers.py custom_components/lipro/core/ota/candidate.py custom_components/lipro/core/ota/candidate_support.py custom_components/lipro/select.py custom_components/lipro/select_internal/gear.py tests/platforms/test_select_behavior.py tests/platforms/select_setup_behavior_cases.py tests/platforms/select_mapped_behavior_cases.py tests/platforms/select_gear_behavior_cases.py tests/meta/test_phase61_formal_home_budget_guards.py`
- `uv run python scripts/check_file_matrix.py --check`
- `uv run pytest -q tests/core/anonymous_share/test_manager_recording.py tests/core/anonymous_share/test_manager_submission.py tests/core/test_share_client.py tests/core/test_anonymous_share_storage.py tests/services/test_services_share.py tests/core/test_init_service_handlers_share_reports.py tests/services/test_services_diagnostics.py tests/core/test_init_service_handlers_debug_queries.py tests/core/api/test_api_diagnostics_service.py tests/meta/test_dependency_guards.py tests/core/ota/test_ota_candidate.py tests/core/ota/test_firmware_manifest.py tests/platforms/test_update.py tests/platforms/test_update_entity_refresh.py tests/platforms/test_update_install_flow.py tests/platforms/test_update_certification_policy.py tests/platforms/test_firmware_update_entity_edges.py tests/meta/test_firmware_support_manifest_repo_asset.py tests/platforms/test_select_behavior.py tests/platforms/test_select_models.py tests/platforms/test_platform_entities_behavior.py tests/meta/test_phase61_formal_home_budget_guards.py tests/meta/test_governance_guards.py tests/meta/test_public_surface_guards.py` (`322 passed`)

## Outcome

- `HOT-15` satisfied: large-but-correct production formal homes 现已沿 inward collaborator seams 收薄，且没有长出第二 public root / compat shell story。
- `QLT-20` satisfied: select behavior 已 topicize 成 thin shell + focused suites，Phase 61 guard 也把 hotspot no-growth posture 固定下来。
- `TYP-15` satisfied: anonymous-share / diagnostics / OTA / select touched seams 均维持 typed outward contracts，没有回流 `Any` / broad catch / helper-owned fallback 叙事。
