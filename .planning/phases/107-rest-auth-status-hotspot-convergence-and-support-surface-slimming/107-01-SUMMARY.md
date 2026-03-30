---
requirements-completed: [HOT-46, ARC-27]
---

# 107-01 Summary

- `LiproRestFacade.__init__()` 已通过 `_build_endpoint_surface()` / `_build_request_gateway()` 收口 collaborator assembly，REST child-façade wiring 更显式。
- `status_fallback_support.py` 已引入 `_BinarySplitQueryContext` / `_BinarySplitAccumulator` 以及 focused binary-split helpers，fallback orchestration 不再集中在一段 broad mixed carrier。
- focused API regressions 继续冻结 REST outward surface 与 fallback semantics，无 public-surface drift。
