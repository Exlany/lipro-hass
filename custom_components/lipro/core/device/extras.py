"""Derived device extras kept outside the thin ``LiproDevice`` facade."""

from __future__ import annotations

from collections.abc import Mapping
from typing import Any

from . import extras_features, extras_payloads


class DeviceExtras:
    """Resolve device-specific structured extras and cached payloads."""

    def __init__(
        self,
        properties: Mapping[str, Any],
        extra_data: Mapping[str, Any],
        *,
        serial: str,
        iot_name: str,
        physical_model: str | None,
    ) -> None:
        """Bind raw properties plus static metadata used by extra helpers."""
        self._properties = properties
        self._extra_data = extra_data
        self._serial = serial
        self._iot_name = iot_name
        self._physical_model = physical_model
        self._gear_list_cache: list[Any] | None = None

    def clear_caches(self) -> None:
        """Clear derived caches after property mutation."""
        self._gear_list_cache = None

    def is_bound_to(
        self,
        properties: Mapping[str, Any],
        extra_data: Mapping[str, Any],
    ) -> bool:
        """Return whether cached extras still point at the live device mappings."""
        return self._properties is properties and self._extra_data is extra_data

    gear_list = property(extras_payloads.gear_list)
    last_gear_index = property(extras_payloads.last_gear_index)
    has_gear_presets = property(extras_payloads.has_gear_presets)
    panel_info = property(extras_payloads.panel_info)
    rc_list = property(extras_payloads.rc_list)
    has_sleep_wake_features = property(extras_features.has_sleep_wake_features)
    has_floor_lamp_features = property(extras_features.has_floor_lamp_features)
    is_ir_remote_device = property(extras_features.is_ir_remote_device)
    ir_remote_gateway_device_id = property(extras_features.ir_remote_gateway_device_id)
    supports_ir_switch = property(extras_features.supports_ir_switch)
    panel_type = property(extras_features.panel_type)


__all__ = ["DeviceExtras"]
