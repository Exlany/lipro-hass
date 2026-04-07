# 18-02 Summary

## Outcome

- `custom_components/lipro/const/categories.py` 只保留 host-neutral category truth，不再提供 HA platform mapping。
- `custom_components/lipro/core/capability/models.py` / `registry.py` 与 `custom_components/lipro/core/device/device.py` / `device_views.py` 移除 HA platform projection 残留。
- `custom_components/lipro/helpers/platform.py` 成为唯一 adapter-only HA platform projection home。
- `custom_components/lipro/light.py`、`cover.py`、`climate.py`、`switch.py` 统一改走 `device_supports_platform()`。
- 相关 core/platform/snapshot tests 已同步到新的 host-neutral truth。

## Verification

- `uv run pytest -q tests/core/test_categories.py tests/core/device/test_capabilities.py tests/core/capability/test_registry.py tests/core/test_device.py tests/core/device/test_device.py tests/platforms/test_entity_behavior.py tests/entities/test_descriptors.py tests/snapshots/test_device_snapshots.py`
