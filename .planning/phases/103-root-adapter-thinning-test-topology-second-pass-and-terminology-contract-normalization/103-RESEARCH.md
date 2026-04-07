# Phase 103 Research

## Repository-Wide Audit Inputs

- 主代理终极审阅结论：当前最大技术风险不是方向错误，而是热点复杂度与术语认知债。
- production 热点子代理：优先收窄 `custom_components/lipro/__init__.py`，次优先 `service_router_handlers.py` / `command_runtime.py`。
- tests/governance 子代理：优先拆 `tests/conftest.py` 的 topicized routing 与 coordinator double，随后推进治理守卫表驱动化。

## Selected Scope

为了让 active route 先走出第一步且不制造大回归面，`Phase 103` 选择：
1. 先薄化 HA 根入口
2. 先拆 `tests/conftest.py` 的两块巨石职责
3. 先把术语契约文档化并投射进 developer architecture

## Deferred to Later Phases

- `custom_components/lipro/control/service_router_handlers.py` family split → `Phase 104`
- `custom_components/lipro/core/coordinator/runtime/command_runtime.py` second-pass inward split → `Phase 104`
- `tests/meta` / `scripts/check_*` deeper datafication → `Phase 105`
