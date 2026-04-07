# Summary 115-01

## What changed
- 为 `custom_components/lipro/core/api/status_fallback_support.py` 的 `query_with_fallback_impl()` 增加了空 `ids` 短路，避免空输入仍走 setup 构建与 primary batch 请求。
- 为 `tests/core/api/test_api_status_service_fallback.py` 增加 public entry regression，冻结空输入场景的无 I/O / 空结果 / fallback depth = `0` 语义。

## Why it changed
- `query_items_by_binary_split_impl()` 已经对空输入短路，而 `query_with_fallback_impl()` 之前仍会继续进入 primary batch 路径，入口语义不一致。
- 这一差异虽然不是 `v1.31` closeout blocker，但它会让 fallback family 的认知模型出现噪音；本次除了补齐行为，也把它冻结成后续 `HOT-48` 重构不得回退的 contract。

## Verification
- `uv run pytest -q tests/core/api/test_api_status_service_fallback.py`
- `uv run ruff check custom_components/lipro/core/api/status_fallback_support.py tests/core/api/test_api_status_service_fallback.py`

## Outcome
- `status_fallback` family 现在对空输入有一致的显式入口语义，可作为 `Phase 115` 后续继续瘦身的稳定起点。
