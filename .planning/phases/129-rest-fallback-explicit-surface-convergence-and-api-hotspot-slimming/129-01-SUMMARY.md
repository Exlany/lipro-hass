---
phase: 129-rest-fallback-explicit-surface-convergence-and-api-hotspot-slimming
plan: "01"
summary: true
---

# Plan 129-01 Summary

## Completed

- `custom_components/lipro/core/api/rest_facade.py` 已将 `_session_state_property()`、`_component_method()` 与 `_component_async_method()` 的正式 surface 使用点回收为显式 `@property` 与 narrow local wrappers；`LiproRestFacade` 的 state / collaborator access path 现可直接审阅。
- outward request/auth/endpoint story 继续经 `rest_facade_request_methods.py` 与 `rest_facade_endpoint_methods.py` 绑定；未引入第二条 façade home，也未回退到 `__getattr__` / hidden delegation。
- `tests/core/api/test_protocol_contract_facade_runtime.py` 已新增 no-helper-magic guard，冻结 `_session_state_property` / `_component_method` / `_component_async_method` 不得回流。

## Outcome

- `ARC-40` 已满足：REST child façade 的组合边界更显式，review / debug 可读性更高。
- `QLT-52` 已满足其 Phase 129 范围：helper magic 不再遮蔽正式 surface，命名与职责锚点更稳定。
