---
phase: 04-capability-model-unification
plan: "03"
status: completed
completed: 2026-03-13
requirements:
  - DOM-01
  - DOM-02
  - DOM-03
  - DOM-04
  - DOM-05
---

# Summary 04-03

## Outcome
- `device.capabilities` 已回到正式 `CapabilitySnapshot`，`DeviceCapabilities` 缩减为显式 compat alias，不再处于生产主链。
- `DeviceState.supports_color_temp` 已改为消费 capability truth 注入值，不再自行从 kelvin range 推导第二套能力判断。
- `core/device/profile.py` 中的 `resolve_platforms()` 已删除，平台映射不再保留影子 helper。
- Phase 4 的 platform/entity/device/state closeout 已形成完整治理与验证记录。

## Verification
- `uv run ruff check custom_components/lipro/core/device/state.py custom_components/lipro/core/device/state_accessors.py custom_components/lipro/core/device/device_runtime.py custom_components/lipro/core/device/profile.py tests/core/device/test_state.py`
- `uv run pytest tests/core/device/test_state.py tests/core/device/test_capabilities.py tests/core/capability/test_registry.py tests/core/device/test_device.py tests/core/test_device.py tests/platforms/test_light.py tests/platforms/test_fan.py tests/platforms/test_sensor.py tests/platforms/test_switch.py tests/platforms/test_cover.py tests/platforms/test_climate.py tests/platforms/test_select.py tests/platforms/test_entity_behavior.py tests/platforms/test_platform_entities_behavior.py -q`

## Closeout
- `Capability duplication` 作为生产主链 residual 已关闭；剩余仅保留 `DeviceCapabilities` 旧 public name compat alias，删除留给 `Phase 7`。
- `Phase 5` 可以把 capability model 当作稳定领域输入，而不必再补 runtime 侧 category/platform 解释逻辑。
