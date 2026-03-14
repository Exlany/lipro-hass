---
phase: 11-control-router-formalization-wiring-residual-demotion
plan: "04"
status: completed
completed: 2026-03-14
requirements:
  - SURF-01
---

# Summary 11-04

## Outcome

- `custom_components/lipro/core/api/client.py` 已移除 `_endpoint_exports` / `__getattr__` / `__dir__` 动态扩面，`LiproRestFacade` 改为显式 formal wrappers。
- `custom_components/lipro/core/coordinator/runtime/device/snapshot.py` 已只走 `get_devices(offset, limit)` canonical path，不再依赖 `get_device_list()` compat fallback。
- `custom_components/lipro/core/coordinator/orchestrator.py` 已统一走 `query_device_status(...)` formal contract，ghost child surface probing 被移除。

## Verification

- 见 `11-VERIFICATION.md` 的 Phase 11 closeout suite。
- 关键切片：`tests/core/api/test_protocol_contract_matrix.py`、`tests/core/coordinator/runtime/test_device_runtime.py`、`tests/core/test_coordinator.py`、`tests/meta/test_public_surface_guards.py`、`tests/benchmarks/test_coordinator_performance.py`。

## Governance Notes

- `SURF-01` 已收口到显式可枚举 surface；compat `get_device_list()` 不再定义 runtime production truth。
