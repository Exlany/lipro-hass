from collections.abc import Mapping
from typing import Any

class DeviceState:
    properties: dict[str, Any]
    min_color_temp_kelvin: int
    max_color_temp_kelvin: int
    max_fan_gear: int
    _supports_color_temp: bool

    is_on: bool
    fade_state: bool
    sleep_aid_enabled: bool
    wake_up_enabled: bool
    focus_mode_enabled: bool
    body_reactive_enabled: bool
    panel_led_enabled: bool
    panel_memory_enabled: bool
    panel_pair_key_full: bool
    ir_switch_enabled: bool
    is_charging: bool
    is_moving: bool
    fan_is_on: bool
    heater_is_on: bool
    door_is_open: bool
    is_activated: bool
    is_dark: bool
    low_battery: bool
    brightness: int
    fan_mode: int
    heater_mode: int
    wind_gear: int
    light_mode: int
    wind_direction_mode: int
    aeration_gear: int
    supports_color_temp: bool
    is_connected: bool
    color_temp: int
    battery_level: int | None
    has_battery: bool
    position: int
    direction: str | None
    fan_gear: int
    aeration_is_on: bool

    def __init__(
        self,
        properties: dict[str, Any] = ...,
        min_color_temp_kelvin: int = ...,
        max_color_temp_kelvin: int = ...,
        max_fan_gear: int = ...,
        _supports_color_temp: bool = ...,
    ) -> None: ...
    @classmethod
    def from_api_data(
        cls,
        properties: Mapping[str, Any],
        *,
        min_color_temp_kelvin: int,
        max_color_temp_kelvin: int,
        max_fan_gear: int,
        supports_color_temp: bool,
    ) -> DeviceState: ...
    def update_from_properties(self, properties: Mapping[str, Any]) -> None: ...
    def get_property(self, key: str, default: Any = ...) -> Any: ...
    def get_bool_property(self, key: str, default: bool = ...) -> bool: ...
    def get_int_property(self, key: str, default: int = ...) -> int: ...
    def get_float_property(self, key: str, default: float = ...) -> float: ...
    def get_optional_int_property(self, key: str) -> int | None: ...
    def get_str_property(self, key: str) -> str | None: ...
    def percent_to_kelvin_for_device(self, percent: int) -> int: ...
    def kelvin_to_percent_for_device(self, kelvin: int) -> int: ...

DEVICE_STATE_EXPORTED_ATTRIBUTES: tuple[str, ...]
