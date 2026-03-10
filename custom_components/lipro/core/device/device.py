"""Thin composable device facade for the Lipro integration."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, ClassVar

from ...const.api import DEFAULT_MAX_FAN_GEAR
from ...const.properties import MAX_COLOR_TEMP_KELVIN, MIN_COLOR_TEMP_KELVIN
from . import device_runtime, device_views
from .device_delegation import DEVICE_DELEGATED_ATTRIBUTES, resolve_device_attribute
from .device_factory import build_device_from_api_data
from .extras import DeviceExtras
from .state import DeviceState


@dataclass(slots=True)
class LiproDevice:
    """Backward-compatible device facade backed by focused components."""

    device_number: int
    serial: str
    name: str
    device_type: int
    iot_name: str
    room_id: int | None = None
    room_name: str | None = None
    is_group: bool = False
    product_id: int | None = None
    physical_model: str | None = None
    properties: dict[str, Any] = field(default_factory=dict)
    extra_data: dict[str, Any] = field(default_factory=dict)
    available: bool = True
    min_color_temp_kelvin: int = MIN_COLOR_TEMP_KELVIN
    max_color_temp_kelvin: int = MAX_COLOR_TEMP_KELVIN
    default_max_fan_gear_in_model: int = DEFAULT_MAX_FAN_GEAR
    max_fan_gear: int = DEFAULT_MAX_FAN_GEAR
    has_unknown_physical_model: bool = False
    _state_cache: DeviceState | None = field(
        default=None, init=False, repr=False, compare=False
    )
    _extras_cache: DeviceExtras | None = field(
        default=None, init=False, repr=False, compare=False
    )
    _delegated_attributes: ClassVar[dict[str, str]] = DEVICE_DELEGATED_ATTRIBUTES

    identity = property(device_views.identity)
    capabilities = property(device_views.capabilities)
    network_info = property(device_views.network_info)
    device_type_hex = property(device_views.device_type_hex)
    category = property(device_views.category)
    platforms = property(device_views.platforms)
    unique_id = property(device_views.unique_id)
    iot_device_id = property(device_views.iot_device_id)
    has_valid_iot_id = property(device_views.has_valid_iot_id_property)
    panel_type = property(device_views.panel_type)
    fan_speed_range = property(device_views.fan_speed_range)

    def __post_init__(self) -> None:
        """Normalize incoming device properties after dataclass initialization."""
        device_runtime.initialize_device(self)

    @property
    def state(self) -> DeviceState:
        """Return the mutable state view bound to this device."""
        return device_runtime.get_device_state(self)

    @property
    def extras(self) -> DeviceExtras:
        """Return device-specific structured extras and cached payloads."""
        return device_runtime.get_device_extras(self)

    def update_properties(self, properties: dict[str, Any]) -> None:
        """Merge normalized properties into the live facade state."""
        device_runtime.update_device_properties(self, properties)

    @classmethod
    def from_api_data(cls, data: dict[str, Any]) -> LiproDevice:
        """Build a device facade from one raw API payload."""
        return build_device_from_api_data(cls, data)

    def __getattr__(self, name: str) -> Any:
        """Resolve delegated compatibility attributes lazily."""
        return resolve_device_attribute(self, name)


__all__ = ["LiproDevice"]
