# 56-01 Summary

## Outcome

- `custom_components/lipro/core/utils/backoff.py` 现成为 neutral shared exponential-backoff primitive home，与现有 `core/utils/retry_after.py` 一起构成诚实的 retry primitive 边界。
- `custom_components/lipro/core/api/request_policy.py` 不再导出 generic backoff helper，只通过 private import 复用该 primitive；`RequestPolicy` 继续保留 API-local `429` / busy / pacing truth。
- `custom_components/lipro/core/api/request_policy_support.py` 继续只保留 support-only 身份，generic backoff 真源已迁出。
- `tests/core/api/test_api_request_policy.py` 已新增 guard，锁定 `request_policy` module 不再暴露 generic helper export。

## Validation

- `uv run pytest -q tests/core/api/test_api_request_policy.py`

## Notes

- 本计划只纠正 helper owner truth，不改写 API-local rate-limit / busy behavior。
