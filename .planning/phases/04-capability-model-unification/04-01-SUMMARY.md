---
phase: 04-capability-model-unification
plan: "01"
status: completed
completed: 2026-03-12
requirements:
  - DOM-01
  - DOM-04
  - DOM-05
---

# Summary 04-01

## Outcome
- 建立 `custom_components/lipro/core/capability/`，正式落地 `CapabilityRegistry` 与 `CapabilitySnapshot`。
- `custom_components/lipro/core/device/capabilities.py` 已降级为 compat bridge，不再拥有独立 capability truth。
- `device_snapshots.py` 与 `device_views.py` 已接入 canonical capability model；`category` / `platforms` / `fan_speed_range` 统一围绕 snapshot 推导。
- 新增 `tests/core/capability/test_registry.py`，并扩展 device facade 回归，证明 formal capability root 已真实落地。
- 治理与 baseline 已同步到 `04-01`，为 `04-02` 的平台/实体迁移提供正式 handoff。

## Verification
- `uv run ruff check custom_components/lipro/core/capability custom_components/lipro/core/device/capabilities.py custom_components/lipro/core/device/device_snapshots.py custom_components/lipro/core/device/device_views.py tests/core/capability tests/core/device/test_capabilities.py tests/core/device/test_device.py`
- `uv run pytest tests/core/capability/test_registry.py tests/core/device/test_capabilities.py tests/core/device/test_device.py tests/core/test_device.py -q`
- `uv run pytest tests/platforms/test_fan.py tests/platforms/test_sensor.py tests/platforms/test_entity_behavior.py tests/platforms/test_platform_entities_behavior.py -q`
- `uv run pytest tests/meta/test_dependency_guards.py tests/meta/test_public_surface_guards.py -q`

## Governance Notes
- `FILE_MATRIX.md` 已新增 `core/capability` / `tests/core/capability` cluster，并把 `core/device` 标记为 `04-01 registry seeded`。
- `RESIDUAL_LEDGER.md` 已记录 `Capability duplication` 的 `04-01` delta。
- `KILL_LIST.md` 已显式登记 `DeviceCapabilities` legacy public name / compat bridge 的删除门槛。
