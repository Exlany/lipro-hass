# Phase 126 Context

## Goal

在不改变 `services.diagnostics` outward import surface 的前提下，继续压薄 `helpers.py`：让 handler-facing pure mechanics 回到 `helper_support.py`，删除未使用 duplicate helper，并同步 `v1.36` current-route truth / plan / verification 资产。

## Inputs

- `.planning/reviews/V1_35_EVIDENCE_INDEX.md`
- `custom_components/lipro/services/diagnostics/helpers.py`
- `custom_components/lipro/services/diagnostics/helper_support.py`
- `custom_components/lipro/services/diagnostics/handlers.py`
- `custom_components/lipro/control/developer_router_support.py`
- `tests/services/test_services_diagnostics_capabilities.py`
- `tests/services/test_services_diagnostics_payloads.py`

## Constraints

- public diagnostics service import surface 不变；`custom_components/lipro/services/diagnostics/__init__.py` 继续作为 stable outward surface。
- 不重开 `service_router` topology；`service_router_diagnostics_handlers.py` 继续是 diagnostics/developer callback family home。
- 所有 Python / lint / pytest 命令统一使用 `uv run ...`。
