# Phase 29 Verification

status: passed

## Goal

- 核验 `Phase 29: rest child façade slimming and test topicization` 是否完成 `HOT-06` / `RES-05` / `TST-03`：在不引入第二 REST root 的前提下，把 `LiproRestFacade` 从 request/auth/transport/command/capability 过载面继续切薄，并把 API regressions 迁回 focused suites 与 machine-checked truth。
- 终审结论：**`HOT-06`、`RES-05` 与 `TST-03` 已完成；REST child façade 继续保持单一正式主链，同时 API topicization 与 file-matrix truth 已同步收口。**

## Reviewed Assets

- Phase 资产：`29-CONTEXT.md`、`29-RESEARCH.md`、`29-VALIDATION.md`
- 已生成 summaries：`29-01-SUMMARY.md`、`29-02-SUMMARY.md`、`29-03-SUMMARY.md`
- synced truth：`custom_components/lipro/core/api/{client.py,client_transport.py,client_auth_recovery.py,endpoints/payloads.py}`、`tests/core/api/{test_api.py,test_api_client_transport.py,test_auth_recovery_telemetry.py,test_api_request_policy.py,test_api_diagnostics_service.py,test_api_schedule_service.py,test_api_schedule_endpoints.py}`、`tests/core/test_command_dispatch.py`、`tests/meta/{test_public_surface_guards.py,test_modularization_surfaces.py,test_governance_closeout_guards.py}`、`.planning/reviews/FILE_MATRIX.md`、`scripts/check_file_matrix.py`

## Must-Haves

- **1. REST child façade visibly slimmer without a second root — PASS**
  - `client.py` 保持 `LiproRestFacade` 作为唯一正式 REST child façade。
  - request/auth/result handling 明确下沉到 `client_transport.py`、`client_auth_recovery.py` 与 endpoint adapter；未引入 compat façade 或 parallel boundary pipeline。

- **2. Command / pacing story anchored on focused owner homes — PASS**
  - busy-retry / pacing 继续由 `RequestPolicy` 与 command family 持有，`client.py` 只保留最薄 bridge。
  - command/pacing/busy regressions 已从巨型 `test_api.py` 中抽出主题切片，并保持黑盒行为覆盖。

- **3. Capability regressions and governance truth are topicized — PASS**
  - diagnostics / schedule / power / mqtt capability 回归以 dedicated REST suites 为主，而不再只依赖 `test_api.py -k ...`。
  - `FILE_MATRIX` 与 modularization/public-surface guards 已同步 slimmer REST story，并显式声明 typed / exception cleanup 继续由 `Phase 30/31` 承接。

## Evidence

- `uv run pytest -q tests/core/api/test_api.py tests/core/api/test_auth_recovery_telemetry.py tests/core/api/test_api_request_policy.py tests/core/api/test_api_command_service.py tests/core/api/test_helper_modules.py tests/core/api/test_api_client_transport.py` → `185 passed`
- `uv run pytest -q tests/core/api/test_api.py tests/core/test_command_dispatch.py tests/core/api/test_protocol_contract_matrix.py -k "command or pacing or busy"` → `34 passed, 139 deselected`
- `uv run pytest -q tests/core/api/test_api_diagnostics_service.py tests/core/api/test_api_schedule_service.py tests/core/api/test_api_schedule_endpoints.py tests/core/api/test_api.py tests/meta/test_public_surface_guards.py tests/meta/test_modularization_surfaces.py tests/meta/test_governance_closeout_guards.py` → `171 passed`
- `uv run pytest -q tests/core/api/test_api.py tests/core/api/test_api_client_transport.py tests/core/api/test_auth_recovery_telemetry.py tests/core/test_command_dispatch.py tests/core/api/test_protocol_contract_matrix.py tests/core/api/test_api_diagnostics_service.py tests/core/api/test_api_schedule_service.py tests/core/api/test_api_schedule_endpoints.py tests/meta/test_public_surface_guards.py tests/meta/test_modularization_surfaces.py tests/meta/test_governance_closeout_guards.py && uv run python scripts/check_file_matrix.py --check` → `238 passed`

## Risks / Notes

- `Phase 29` 有意没有把 typed-contract cleanup 过早塞入 REST modularization；这是为 `Phase 30/31` 保留干净 ownership，而非遗漏。
- façade 保留的少量兼容 wrapper 仍只服务 formal path，不得在后续 phase 被重新扩张成 shadow layer。
