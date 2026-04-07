# 52-02 Summary

## Outcome

- `custom_components/lipro/core/api/request_policy.py` 现直接持有 `429` / Retry-After / busy / pacing / adaptive interval 的正式实现；busy retry loop 已从 `command_api_service.py` 回收到 `RequestPolicy`。
- `custom_components/lipro/core/api/transport_retry.py` 现只保留 replay loop，`429` 决策通过 `RequestPolicy.handle_rate_limit()` 注入，不再自带第二套 backoff 真相。
- `custom_components/lipro/core/api/transport_executor.py` 已收窄回 session/signing/HTTP execute/header/response validation；mapping/auth-aware request orchestration 不再 dual-home 于 executor。
- `custom_components/lipro/core/api/rest_facade_request_methods.py` 与 `request_gateway.py` 现由 `RestRequestGateway.dispatch_retry_aware_call()` 统一承接 retry-context preservation；`rest_facade.py` 的 orphan `_handle_rate_limit()` 与重复 dispatch helper 已删除。
- `custom_components/lipro/core/api/command_api_service.py` 仅保留 command payload shaping 与 target dispatch helper，不再拥有 busy retry 算法。

## Validation

- `uv run pytest tests/core/api/test_api_request_policy.py tests/core/api/test_api_command_service.py tests/core/api/test_api_transport_executor.py tests/core/api/test_api_command_surface.py -q`

## Notes

- `compute_exponential_retry_wait_time()` 仍暂留在 `request_policy.py`，其跨 plane 使用将于 `52-03` 的 residual/governance freeze 中被显式裁决。
- 本波次未新增 public surface；所有收口都保持在 localized collaborator 与 private seam 内完成。
