# Plan 138-04 Summary

- `ConnectStatusOutcome` / `ConnectStatusQueryResult` 已提升为正式 shared API contract，不再只停留在 `status_service.py` 私有 helper。
- `query_connect_status()` 现沿 `status_service -> endpoint_surface -> rest_port -> protocol facade` 返回 typed result，`API_ERROR / WRAPPED_NON_MAPPING / EMPTY_MAPPING / EMPTY_SANITIZED / SUCCESS` 不再被统一抹平成 `{}`。
- focused service/device/protocol tests 与共享 mock 已同步改写，确保 closeout 证据不再依赖旧的 contract flattening。
