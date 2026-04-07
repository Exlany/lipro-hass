# Plan 63-05 Summary

## What Changed

- `custom_components/lipro/core/coordinator/types.py` 与 `custom_components/lipro/core/coordinator/runtime/command_runtime.py` 已为命令失败语义建立 typed summary：`reason` / `code` / `error_type` / `reauth_reason` / `failure_category` 现成为正式运行时仲裁字段，`Coordinator` 不再依赖 raw trace 里的 `error` 字符串键决定 reauth。
- `custom_components/lipro/core/coordinator/services/command_service.py` 已把稳定服务面收口为 normalized failure summary，并额外保留 `last_failure_trace` 供诊断/测试读取；`custom_components/lipro/core/coordinator/coordinator.py` 现通过 typed `reauth_reason` 做 `ConfigEntryAuthFailed` 仲裁。
- `custom_components/lipro/core/anonymous_share/share_client_support.py`、`share_client.py` 与 `share_client_flows.py` 已统一到 `SharePayload` / `WorkerResponsePayload` / `ResponseHeadersLike` 等 typed transport contracts：匿名分享链路不再以 `headers: Any` / `payload: dict[str, Any] | None` 作为正式接口，token payload normalization 与 response-code extraction 也已集中化。
- 命令运行时与匿名分享的新增 typed behavior 已补上 focused regression coverage：service/runtime/integration/share-client tests 均锁定了新 summary / payload contract 的 outward behavior。

## Validation

- `uv run ruff check custom_components/lipro/core/coordinator/types.py custom_components/lipro/core/coordinator/runtime/command_runtime.py custom_components/lipro/core/coordinator/services/command_service.py custom_components/lipro/core/coordinator/coordinator.py custom_components/lipro/core/anonymous_share/share_client_support.py custom_components/lipro/core/anonymous_share/share_client.py custom_components/lipro/core/anonymous_share/share_client_flows.py tests/core/coordinator/runtime/test_command_runtime.py tests/core/coordinator/services/test_command_service.py tests/core/test_coordinator_integration.py tests/core/test_share_client.py`
- `uv run pytest -q tests/core/test_command_result.py tests/core/test_coordinator_integration.py tests/core/test_share_client.py tests/core/anonymous_share/test_manager_submission.py`
- `uv run pytest -q tests/core/coordinator/runtime/test_command_runtime.py tests/core/coordinator/services/test_command_service.py tests/core/test_coordinator_integration.py tests/core/test_share_client.py tests/core/anonymous_share/test_manager_submission.py tests/core/coordinator/test_runtime_root.py`

## Outcome

- `TYP-16` satisfied：命令失败仲裁已从 stringly trace key 升级为 typed summary fields。
- `HOT-16` / `QLT-21` satisfied：anonymous-share transport contract 的 `Any` 泄漏继续缩小，运行时/分享热点的 inward typing 与回归可验证性同步增强。
