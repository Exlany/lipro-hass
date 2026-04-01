---
phase: 129-rest-fallback-explicit-surface-convergence-and-api-hotspot-slimming
plan: "02"
summary: true
---

# Plan 129-02 Summary

## Completed

- `custom_components/lipro/core/api/status_fallback_support.py` 已把 `query_with_fallback_impl()` 的 primary-query 与 retriable batch fallback 显式切成 `_query_primary_rows()` / `_execute_retriable_batch_fallback()` 两段 internal seam；setup/context/orchestration 读取路径更直接。
- `custom_components/lipro/core/api/status_fallback.py` 继续保持唯一 outward fallback home；support seam 只承担 internal helper 角色，没有长出第二条 API/query story。
- `tests/core/api/test_api_status_service_fallback.py` 已新增 direct-success depth-0 regression；wrapper/fallback/regression suites 继续冻结 retriable / non-retriable / partial-result / await-count 语义。

## Outcome

- `HOT-59` 已满足：fallback support seam 更窄、更易读，同时保持单一 outward route truth。
- `TST-50` 已满足：focused regressions 能直接侦测 façade surface 回流与 fallback 语义回退。
