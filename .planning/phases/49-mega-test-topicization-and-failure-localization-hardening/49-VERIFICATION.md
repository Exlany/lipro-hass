# Phase 49 Verification

status: passed

## Goal

- 验证 `Phase 49: Mega-test topicization and failure-localization hardening` 是否完成 `TST-09` / `QLT-17`：治理 / runtime / diagnostics / update megatests 已按 concern topicize，pure OTA helper 已回到 `tests/core/ota/*` 正式 home，且新的失败定位真相已同步写入治理文档与 machine-checkable guards。

## Evidence

- `tests/meta/test_governance_closeout_guards.py` 已退回 helper / smoke anchor；`tests/meta/test_governance_promoted_phase_assets.py`、`tests/meta/test_governance_followup_route.py`、`tests/meta/test_governance_milestone_archives.py` 与 `tests/meta/test_governance_phase_history*.py` 承担更窄、更可定位的治理 concern。
- `tests/core/coordinator/conftest.py`、`tests/core/coordinator/test_runtime_root.py`、`tests/core/coordinator/test_runtime_polling.py`、`tests/core/coordinator/test_update_flow.py` 把 runtime megatest concern inward；`tests/core/test_coordinator_entry.py` 与 `tests/core/test_init_runtime_setup_entry.py` 接住原 top-level coordinator smoke story。
- `tests/core/test_diagnostics.py` 现在只保留 shared helper / smoke anchor；config-entry、device、redaction 断言已拆到 `tests/core/test_diagnostics_{config_entry,device,redaction}.py`。
- `tests/core/ota/test_firmware_manifest.py`、`tests/core/ota/test_ota_candidate.py`、`tests/core/ota/test_ota_row_selector.py`、`tests/core/ota/test_ota_rows_cache.py` 已承接 remote advisory parser、install evaluation、row arbitration / scoring 与 rows-cache primitive；`tests/platforms/test_update.py` 则收窄为 setup + happy-path smoke，refresh / install / certification / background task 另有 topic suites。
- `.planning/reviews/FILE_MATRIX.md`、`.planning/codebase/TESTING.md`、`.planning/baseline/VERIFICATION_MATRIX.md`、`CONTRIBUTING.md`、`scripts/check_file_matrix.py` 以及 `tests/meta/test_{dependency_guards,public_surface_guards,toolchain_truth}.py` 已同步记录 Phase 49 新拓扑；旧 `tests/test_coordinator_public.py` / `tests/test_coordinator_runtime.py` 不再出现在 current truth。
- `RESIDUAL_LEDGER.md`、`KILL_LIST.md` 与 `AUTHORITY_MATRIX.md` 本 phase 保持 unchanged；`PROMOTED_PHASE_ASSETS.md` 仅因本 phase closeout promotion 而新增 `49-SUMMARY.md` / `49-VERIFICATION.md` allowlist。

## Validation

- `uv run pytest tests/core/ota/test_firmware_manifest.py tests/core/ota/test_ota_candidate.py tests/core/ota/test_ota_row_selector.py tests/core/ota/test_ota_rows_cache.py tests/platforms/test_update.py tests/platforms/test_update_entity_refresh.py tests/platforms/test_update_install_flow.py tests/platforms/test_update_certification_policy.py tests/platforms/test_update_background_tasks.py tests/platforms/test_update_task_callback.py tests/platforms/test_firmware_update_entity_edges.py tests/core/test_coordinator_entry.py tests/core/test_init_runtime_setup_entry.py -q` → `86 passed`
- `uv run pytest tests/meta/test_dependency_guards.py tests/meta/test_public_surface_guards.py tests/meta/test_toolchain_truth.py -q` → `58 passed`
- `uv run pytest tests/meta/test_governance_phase_history.py::test_phase_44_execution_evidence_is_consistent tests/meta/test_governance_phase_history_topology.py::test_phase_12_execution_truth_is_consistent -q` → `2 passed`
- `uv run pytest tests/meta/test_dependency_guards.py tests/meta/test_public_surface_guards.py tests/meta/test_governance*.py tests/meta/test_toolchain_truth.py tests/core/coordinator tests/core/test_coordinator.py tests/core/test_coordinator_integration.py tests/core/test_coordinator_entry.py tests/core/test_diagnostics*.py tests/core/test_init_runtime_setup_entry.py tests/core/ota/test_firmware_manifest.py tests/core/ota/test_ota_candidate.py tests/core/ota/test_ota_row_selector.py tests/core/ota/test_ota_rows_cache.py tests/platforms/test_update*.py tests/platforms/test_firmware_update_entity_edges.py -q` → `467 passed`
- `uv run ruff check scripts/check_file_matrix.py tests/core/ota/test_firmware_manifest.py tests/core/ota/test_ota_candidate.py tests/core/ota/test_ota_row_selector.py tests/core/ota/test_ota_rows_cache.py tests/meta/test_dependency_guards.py tests/meta/test_public_surface_guards.py tests/meta/test_toolchain_truth.py tests/platforms/test_update.py tests/platforms/test_update_entity_refresh.py tests/platforms/test_update_install_flow.py tests/platforms/test_update_certification_policy.py tests/platforms/test_update_background_tasks.py tests/platforms/test_firmware_update_entity_edges.py` → `passed`
- `uv run python scripts/check_file_matrix.py --check` → `passed`

## Notes

- `49-SUMMARY.md` / `49-VERIFICATION.md` 已提升进 `PROMOTED_PHASE_ASSETS.md`，具备长期治理 / CI closeout evidence 身份。
- `Phase 50` 是本轮后的默认下一步：本 phase 没有开始 REST typed-surface reduction，也没有触碰 command/result ownership convergence 的具体实现。
