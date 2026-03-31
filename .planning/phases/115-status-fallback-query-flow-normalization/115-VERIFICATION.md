# Phase 115 Verification (Draft pre-bootstrap workspace)

## Scope
验证 `115-01` 是否把 `status_fallback` family 的空输入入口语义收敛为：无 I/O、空结果、fallback depth = `0`。

## Commands
- `uv run pytest -q tests/core/api/test_api_status_service_fallback.py`
- `uv run ruff check custom_components/lipro/core/api/status_fallback_support.py tests/core/api/test_api_status_service_fallback.py`

## Results
- `uv run pytest -q tests/core/api/test_api_status_service_fallback.py` → `15 passed in 0.38s`
- `uv run ruff check custom_components/lipro/core/api/status_fallback_support.py tests/core/api/test_api_status_service_fallback.py` → `All checks passed!`

## Verified end state
- `query_with_fallback()` 在空 `ids` 场景不再触发 `iot_request`。
- 调用方仍收到空结果 `[]`。
- `record_fallback_depth` 收到 `0`，与“没有发生 fallback”的路径一致。
- 既有 fallback regression 未被破坏。
