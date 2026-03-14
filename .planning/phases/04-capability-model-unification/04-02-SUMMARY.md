---
phase: 04-capability-model-unification
plan: "02"
status: completed
completed: 2026-03-13
requirements:
  - DOM-02
  - DOM-03
  - DOM-04
---

# Summary 04-02

## Outcome
- 平台与实体消费者已显式改用 capability projection：`light/fan/binary_sensor/cover/climate/select/sensor/switch` 的筛选与条件分支不再靠散落的第二套 category/platform logic。
- `LiproEntity` 已暴露 `capabilities` 正式入口，descriptor 条件判断改为消费 capability snapshot，而不是再从 entity/device 侧隐式探测。
- `CapabilitySnapshot` 已补齐 `supports_platform()` 与 `is_panel` 等平台/面板投影能力，consumer 不必再落回 `device_type_hex` / `category == ...` 的重复判断。

## Verification
- `uv run ruff check custom_components/lipro/core/capability custom_components/lipro/entities/base.py custom_components/lipro/entities/descriptors.py custom_components/lipro/helpers/platform.py custom_components/lipro/{light.py,fan.py,binary_sensor.py,cover.py,climate.py,select.py,sensor.py,switch.py} tests/core/capability/test_registry.py tests/platforms/test_entity_behavior.py`
- `uv run pytest tests/core/capability/test_registry.py tests/platforms/test_light.py tests/platforms/test_fan.py tests/platforms/test_sensor.py tests/platforms/test_entity_behavior.py tests/platforms/test_platform_entities_behavior.py tests/core/device/test_capabilities.py tests/core/device/test_device.py tests/core/test_device.py -q`

## Handoff
- `04-03` 只做 closeout：删除死 helper、收紧 compat 访问面、更新 residual/kill/validation；不再重新设计 capability surface。
