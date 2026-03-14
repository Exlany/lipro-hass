# Phase 13 Research

**Date:** 2026-03-14
**Status:** Final
**Plans / Waves:** 3 plans / 2 waves

## What The Review Confirmed

- 设备域的动态 `__getattr__` 已不再是必要技术前提，更多是历史委托残留；
- `RuntimeOrchestrator.build_runtimes()` 与 `status_service._query_items_by_binary_split()` 仍是高温热点，适合继续 helper 化；
- README / support / CODEOWNERS / quality-scale / devcontainer 已有资产，但缺少更强的结构化 meta guards；
- 用户明确偏好：不要为了测试继续保留 compat 冗余，而要清理得更干净。

## Risk Notes

- 设备域重构若误删叶子 surface，平台 / entity / diagnostics / tests 会大面积连锁失败；
- status fallback 逻辑若改坏，容易只在边界错误与批量回退场景下暴露；
- governance tests 若继续写成文案锁死，会把后续 phase 的正常回写变成伪阻塞。

## Chosen Strategy

1. `DeviceState` 通过显式 property 工厂收口叶子 surface；
2. `LiproDevice` 通过显式 facade property / method 集合替代动态委托，并让内部消费方优先走组合根；
3. `RuntimeOrchestrator` / `status_service` 用 helper / context / accumulator 切薄，不改变 public behavior；
4. meta guards 增加 README / support / CODEOWNERS / quality-scale / devcontainer 结构化断言，并软化对“当前 phase 状态文案”的硬编码。

## Validation Focus

- `uv run pytest -q tests/core/device/test_device.py tests/core/device/test_state.py tests/core/coordinator/runtime/test_device_runtime.py tests/core/test_device_refresh.py tests/core/api/test_api_status_service.py tests/core/api/test_api_status_service_regressions.py`
- `uv run pytest -q tests/meta/test_governance_guards.py tests/meta/test_public_surface_guards.py tests/meta/test_dependency_guards.py tests/meta/test_version_sync.py`
- `uv run ruff check .`
- `uv run mypy`
- `uv run pytest -q`
