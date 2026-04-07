---
phase: 11
status: passed
updated: 2026-03-14
---

# Phase 11 Verification

## Scope

本轮验证覆盖 `11-01` ~ `11-08` 的完整执行结果：

- `control/service_router.py` 成为真实 formal control-plane router implementation，`services/wiring.py` 降为显式 compat shell
- `LiproRestFacade`、runtime refresh path 与 orchestrator wiring 已收口到显式 formal surface
- runtime-access / diagnostics / status isolation 已统一到正式 control-plane/runtime story
- supplemental entity truth 与 firmware-update/OTA truth 已完成 helper-cluster 收口
- docs / phase assets / CI / release / issue / PR / security disclosure 已形成一致治理口径

## Commands

- `uv run ruff check .`
- `uv run python scripts/check_architecture_policy.py --check`
- `uv run python scripts/check_file_matrix.py --check`
- `uv run pytest -q tests/core/test_init.py tests/services/test_service_resilience.py tests/services/test_services_registry.py tests/core/api/test_protocol_contract_matrix.py tests/core/coordinator/runtime/test_device_runtime.py tests/core/coordinator/runtime/test_status_runtime.py tests/core/test_control_plane.py tests/core/test_coordinator.py tests/core/test_coordinator_integration.py tests/core/test_diagnostics.py tests/services/test_maintenance.py tests/services/test_device_lookup.py tests/services/test_services_diagnostics.py tests/core/test_system_health.py tests/meta/test_dependency_guards.py tests/meta/test_public_surface_guards.py tests/meta/test_governance_guards.py tests/meta/test_version_sync.py tests/platforms/test_switch.py tests/platforms/test_select.py tests/platforms/test_platform_entities_behavior.py tests/platforms/test_update.py tests/platforms/test_firmware_update_entity_edges.py tests/core/ota/test_firmware_manifest.py tests/benchmarks/test_coordinator_performance.py`

## Result

- `11-01` / `11-02` 已验证：formal router ownership、legacy wiring demotion 与 test-truth alignment 已稳定成立。
- `11-03` 已验证：developer architecture、baseline、file matrix、residual ledger 与 kill gate 已与代码事实一致。
- `11-04` 已验证：REST child dynamic surface、runtime `get_device_list()` production fallback 与 orchestrator ghost-surface probing 已收口。
- `11-05` 已验证：runtime locator、debug-mode policy、diagnostics degradation 与 status-executor failure isolation 已统一到 formal runtime-access story。
- `11-06` / `11-07` 已验证：supplemental entity truth、unknown-enum policy 与 OTA helper-cluster 收口均已落地，`firmware_update.py` 不再承载 OTA truth。
- `11-08` 已验证：release 复用 CI/version guard，开源协作入口与 security disclosure 已统一。
- `ruff`、architecture policy check、file-matrix check 与 Phase 11 closeout regression suite 全部通过；收官 pytest 套件结果为 `551 passed`。

## Requirement Mapping

- `CTRL-01` / `CTRL-02`：`custom_components/lipro/control/service_router.py` 已成为正式 service callback home，`custom_components/lipro/services/wiring.py` 只保留 compat shell，`tests/core/test_init.py`、`tests/services/test_service_resilience.py`、`tests/services/test_services_registry.py` 覆盖。
- `CTRL-03`：`docs/developer_architecture.md`、`.planning/reviews/FILE_MATRIX.md`、`.planning/reviews/RESIDUAL_LEDGER.md`、`.planning/reviews/KILL_LIST.md` 与 `.planning/baseline/PUBLIC_SURFACES.md` 已同步到新事实。
- `SURF-01`：`custom_components/lipro/core/api/client.py`、`custom_components/lipro/core/coordinator/runtime/device/snapshot.py`、`custom_components/lipro/core/coordinator/orchestrator.py` 已切到显式 formal surface；`tests/core/api/test_protocol_contract_matrix.py`、`tests/core/coordinator/runtime/test_device_runtime.py`、`tests/meta/test_public_surface_guards.py` 覆盖。
- `CTRL-04` / `RUN-01`：`custom_components/lipro/control/runtime_access.py`、`custom_components/lipro/control/diagnostics_surface.py`、`custom_components/lipro/core/coordinator/runtime/status/executor.py` 与 `custom_components/lipro/runtime_types.py` 已形成单一 runtime-access story 与 public protocol typing。
- `ENT-01`：`custom_components/lipro/helpers/platform.py`、`custom_components/lipro/switch.py`、`custom_components/lipro/select.py`、`custom_components/lipro/update.py` 已建立单一平台真源并消除 `hasattr()` / unknown-enum 误建模。
- `ENT-02`：`custom_components/lipro/entities/firmware_update.py`、`custom_components/lipro/core/ota/candidate.py`、`custom_components/lipro/core/ota/rows_cache.py`、`custom_components/lipro/core/ota/row_selector.py` 已完成职责重分配。
- `GOV-08`：`.github/workflows/ci.yml`、`.github/workflows/release.yml`、`.github/ISSUE_TEMPLATE/*`、`.github/pull_request_template.md`、`CONTRIBUTING.md`、`SECURITY.md` 与 meta guards 已统一到单一治理故事线。

## Final Verdict

## VERIFICATION PASSED

Phase 11 已把 control-plane、protocol/runtime surface、runtime-access、entity/OTA 与 governance/open-source coherence 统一收敛到北极星主链。
后续如需继续演进，应直接进入里程碑 closeout 或下一里程碑，而不是恢复 Phase 11 的 compat / addendum 叙事。
