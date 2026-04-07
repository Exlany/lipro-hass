# Phase 107 Research

## Why This Slice First

`Phase 106` 的终审已经明确指出：`rest_facade.py`、`status_fallback_support.py` 与 `request_policy_support.py` 是当前 formal homes 内最适合继续 inward split、同时又不会扩大 public surface 的三处热点。

## Chosen Approach

1. **REST child-façade init convergence**
   - 用 `_build_endpoint_surface()` / `_build_request_gateway()` 收口 `LiproRestFacade.__init__()` 中的 collaborator assembly。
   - 保持 sanctioned properties，不恢复 mixin-style aggregation 或 dynamic delegation。

2. **Status fallback binary-split support decomposition**
   - 用 `_BinarySplitQueryContext` / `_BinarySplitAccumulator` + focused helper 函数收口 fallback orchestration。
   - 保持 outward batch/single fallback semantics 不变。

3. **Request-policy pacing cache localization**
   - 用 `_CommandPacingCaches` 吸收 per-target pacing caches / locks / trimming 协作。
   - 保持 request policy outward API 与 pacing semantics 不变。

4. **Governance projection**
   - 把 `v1.30 active route / Phase 107 complete / latest archived baseline = v1.29` 投射到 planning/baseline/review/docs truth 与 focused guards。
   - 不把 `Phase 107` prematurely promoted 成 milestone closeout bundle。
