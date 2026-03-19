"""Tests for AnonymousShareManager."""

from __future__ import annotations

from unittest.mock import MagicMock

from custom_components.lipro.core.anonymous_share.manager import AnonymousShareManager

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _make_manager(enabled: bool = True) -> AnonymousShareManager:
    """Create an enabled AnonymousShareManager for testing."""
    mgr = AnonymousShareManager()
    if enabled:
        mgr.set_enabled(True, error_reporting=True, installation_id="test-id")
    return mgr


def _make_mock_device(
    *,
    iot_name: str = "lipro_led",
    physical_model: str = "light",
    device_type: int = 1,
    product_id: int = 100,
    is_group: bool = False,
    properties: dict[str, object] | None = None,
    firmware_version: str | None = "1.0.0",
    min_color_temp_kelvin: int = 2700,
    max_color_temp_kelvin: int = 6500,
    gear_list: list[object] | None = None,
    is_light: bool = True,
    is_fan_light: bool = False,
    is_curtain: bool = False,
    is_sensor: bool = False,
    is_heater: bool = False,
    is_switch: bool = False,
    is_outlet: bool = False,
    has_gear_presets: bool = False,
) -> MagicMock:
    """Create a lightweight mock LiproDevice."""
    device = MagicMock()
    device.iot_name = iot_name
    device.physical_model = physical_model
    device.device_type = device_type
    device.product_id = product_id
    device.is_group = is_group
    device.properties = properties or {}
    device.firmware_version = firmware_version
    device.min_color_temp_kelvin = min_color_temp_kelvin
    device.max_color_temp_kelvin = max_color_temp_kelvin
    device.gear_list = gear_list or []
    device.has_unknown_physical_model = False
    device.extras = MagicMock(has_gear_presets=has_gear_presets)
    capability_snapshot = MagicMock()
    capability_snapshot.is_light = is_light
    capability_snapshot.is_fan_light = is_fan_light
    capability_snapshot.is_curtain = is_curtain
    capability_snapshot.is_sensor = is_sensor
    capability_snapshot.is_heater = is_heater
    capability_snapshot.is_switch = is_switch
    capability_snapshot.is_outlet = is_outlet
    capability_snapshot.supports_color_temp = (
        min_color_temp_kelvin > 0 and max_color_temp_kelvin > 0
    )
    capability_snapshot.min_color_temp_kelvin = min_color_temp_kelvin
    capability_snapshot.max_color_temp_kelvin = max_color_temp_kelvin
    capability_snapshot.device_type_hex = f"ff{device_type:06x}"
    device.capabilities = capability_snapshot
    device.category = MagicMock()
    device.category.value = "light"
    return device


# ===========================================================================
# TestLooksSensitive
# ===========================================================================


