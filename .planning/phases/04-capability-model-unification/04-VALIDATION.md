# Phase 04 Validation

**Validated:** 2026-03-13
**Status:** Passed

## Scope

验证 `Phase 4` 是否已经真正完成以下裁决：
- `CapabilityRegistry / CapabilitySnapshot` 成为正式 domain truth；
- 平台、实体、descriptor、device facade 不再并行维护第二套 capability rule system；
- `DeviceCapabilities` 仅剩显式 compat alias 身份；
- Phase 4 的治理、残留与 delete gate 已同步落表。

## Evidence

### Code / Architecture
- `custom_components/lipro/core/capability/models.py`
- `custom_components/lipro/core/capability/registry.py`
- `custom_components/lipro/core/device/device_snapshots.py`
- `custom_components/lipro/core/device/device_views.py`
- `custom_components/lipro/entities/base.py`
- `custom_components/lipro/entities/descriptors.py`
- `custom_components/lipro/{light,fan,binary_sensor,cover,climate,select,sensor,switch}.py`

### Governance
- `.planning/ROADMAP.md`
- `.planning/STATE.md`
- `.planning/REQUIREMENTS.md`
- `.planning/reviews/FILE_MATRIX.md`
- `.planning/reviews/RESIDUAL_LEDGER.md`
- `.planning/reviews/KILL_LIST.md`
- `.planning/baseline/PUBLIC_SURFACES.md`

## Runnable Proof

- `uv run ruff check custom_components/lipro/core/capability custom_components/lipro/core/device custom_components/lipro/entities custom_components/lipro/helpers/platform.py custom_components/lipro/{light.py,fan.py,binary_sensor.py,cover.py,climate.py,select.py,sensor.py,switch.py} tests/core/capability tests/core/device tests/core/test_device.py tests/platforms`
- `uv run pytest tests/core/capability tests/core/device tests/core/test_device.py tests/platforms/test_light.py tests/platforms/test_fan.py tests/platforms/test_sensor.py tests/platforms/test_switch.py tests/platforms/test_cover.py tests/platforms/test_climate.py tests/platforms/test_select.py tests/platforms/test_entity_behavior.py tests/platforms/test_platform_entities_behavior.py -q` → `427 passed`
- `uv run pytest tests/core/device/test_state.py tests/core/device/test_capabilities.py tests/core/capability/test_registry.py tests/core/device/test_device.py tests/core/test_device.py tests/platforms/test_light.py tests/platforms/test_fan.py tests/platforms/test_sensor.py tests/platforms/test_switch.py tests/platforms/test_cover.py tests/platforms/test_climate.py tests/platforms/test_select.py tests/platforms/test_entity_behavior.py tests/platforms/test_platform_entities_behavior.py -q` → `408 passed`
- `uv run pytest tests/meta/test_dependency_guards.py tests/meta/test_public_surface_guards.py -q` → `6 passed`

## Verdict

`Phase 4` 完成并通过验证：
- `DOM-01 ~ DOM-05` 已满足；
- capability truth 已形成单一正式主链；
- 下一阶段应转入 `Phase 5` 的 runtime public surface/invariants hardening。
