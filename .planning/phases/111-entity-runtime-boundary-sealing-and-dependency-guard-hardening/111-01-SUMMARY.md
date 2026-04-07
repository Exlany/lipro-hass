# Summary 111-01

## What changed
- 移除 `custom_components/lipro/entities/base.py` 对 concrete `Coordinator` 的 direct import、generic binding 与 concrete cast。
- 以本地 `DataUpdateCoordinator` typed bridge 满足 `CoordinatorEntity` 的 HA 基类约束，entity 正式运行时协作继续只经 `LiproRuntimeCoordinator`。
- `device` 属性改为通过 `runtime_coordinator.get_device(...)` 读取最新设备快照，避免直接沿 `self.coordinator` 暗示 concrete runtime root。

## Why it changed
- 收口 `ARC-28` 指出的 north-star 违规点：entity adapters 不应再依赖 concrete runtime coordinator。
- 保持最小 runtime verb surface，不通过新增 outward wrapper / leaked handle 取巧。

## Verification
- `uv run pytest -q tests/platforms/test_entity_base.py tests/platforms/test_firmware_update_entity_edges.py tests/platforms/test_update_install_flow.py`
- `34 passed in 1.13s`
- `uv run ruff check custom_components/lipro/entities/base.py custom_components/lipro/entities/firmware_update.py tests/platforms/test_entity_base.py tests/platforms/test_firmware_update_entity_edges.py tests/platforms/test_update_install_flow.py`
- `All checks passed!`
- `uv run mypy custom_components/lipro/entities/base.py custom_components/lipro/entities/firmware_update.py`
- `Success: no issues found in 2 source files`

## Outcome
- entity typed bridge 已脱离 concrete runtime root。
- outward behavior 未漂移，`LiproRuntimeCoordinator` 仍是 entity runtime 协作的唯一正式 surface。
