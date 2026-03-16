"""Thin composable device facade for the Lipro integration."""

from __future__ import annotations

from dataclasses import dataclass, field
from time import monotonic

from ...const.api import DEFAULT_MAX_FAN_GEAR
from ...const.properties import MAX_COLOR_TEMP_KELVIN, MIN_COLOR_TEMP_KELVIN
from . import device_runtime, device_views
from .device_factory import build_device_from_api_data
from .extras import DeviceExtras
from .state import DeviceState

type DevicePropertyMap = dict[str, object]
type DeviceExtraDataMap = dict[str, object]
type OutletPowerInfo = dict[str, object]


def _component_property(component_name: str, attr_name: str) -> property:
    """Create one explicit facade property backed by a composed helper."""

    def _getter(self: LiproDevice) -> object:
        return getattr(getattr(self, component_name), attr_name)

    return property(_getter)


def _component_method(component_name: str, method_name: str):
    """Create one explicit facade method backed by a composed helper."""

    def _method(self: LiproDevice, *args: object, **kwargs: object) -> object:
        return getattr(getattr(self, component_name), method_name)(*args, **kwargs)

    _method.__name__ = method_name
    return _method


@dataclass(slots=True)
class LiproDevice:
    """Thin device facade backed by focused components."""

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
    properties: DevicePropertyMap = field(default_factory=dict)
    extra_data: DeviceExtraDataMap = field(default_factory=dict)
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
    _last_mqtt_update_at: float = field(
        default=0.0, init=False, repr=False, compare=False
    )
    _outlet_power_info: OutletPowerInfo | None = field(
        default=None, init=False, repr=False, compare=False
    )

    identity = property(device_views.identity)
    capabilities = property(device_views.capabilities)
    network_info = property(device_views.network_info)
    device_type_hex = property(device_views.device_type_hex)
    category = property(device_views.category)
    unique_id = property(device_views.unique_id)
    iot_device_id = property(device_views.iot_device_id)
    has_valid_iot_id = property(device_views.has_valid_iot_id_property)
    panel_type = property(device_views.panel_type)
    fan_speed_range = property(device_views.fan_speed_range)

    is_light = _component_property("capabilities", "is_light")
    is_fan_light = _component_property("capabilities", "is_fan_light")
    is_curtain = _component_property("capabilities", "is_curtain")
    is_switch = _component_property("capabilities", "is_switch")
    is_outlet = _component_property("capabilities", "is_outlet")
    is_heater = _component_property("capabilities", "is_heater")
    is_sensor = _component_property("capabilities", "is_sensor")
    is_body_sensor = _component_property("capabilities", "is_body_sensor")
    is_door_sensor = _component_property("capabilities", "is_door_sensor")
    is_gateway = _component_property("capabilities", "is_gateway")

    is_on = _component_property("state", "is_on")
    fade_state = _component_property("state", "fade_state")
    sleep_aid_enabled = _component_property("state", "sleep_aid_enabled")
    wake_up_enabled = _component_property("state", "wake_up_enabled")
    focus_mode_enabled = _component_property("state", "focus_mode_enabled")
    body_reactive_enabled = _component_property("state", "body_reactive_enabled")
    panel_led_enabled = _component_property("state", "panel_led_enabled")
    panel_memory_enabled = _component_property("state", "panel_memory_enabled")
    panel_pair_key_full = _component_property("state", "panel_pair_key_full")
    ir_switch_enabled = _component_property("state", "ir_switch_enabled")
    is_charging = _component_property("state", "is_charging")
    is_moving = _component_property("state", "is_moving")
    fan_is_on = _component_property("state", "fan_is_on")
    heater_is_on = _component_property("state", "heater_is_on")
    door_is_open = _component_property("state", "door_is_open")
    is_activated = _component_property("state", "is_activated")
    is_dark = _component_property("state", "is_dark")
    low_battery = _component_property("state", "low_battery")
    brightness = _component_property("state", "brightness")
    fan_mode = _component_property("state", "fan_mode")
    heater_mode = _component_property("state", "heater_mode")
    wind_gear = _component_property("state", "wind_gear")
    light_mode = _component_property("state", "light_mode")
    wind_direction_mode = _component_property("state", "wind_direction_mode")
    aeration_gear = _component_property("state", "aeration_gear")
    supports_color_temp = _component_property("state", "supports_color_temp")
    is_connected = _component_property("state", "is_connected")
    color_temp = _component_property("state", "color_temp")
    battery_level = _component_property("state", "battery_level")
    has_battery = _component_property("state", "has_battery")
    position = _component_property("state", "position")
    direction = _component_property("state", "direction")
    fan_gear = _component_property("state", "fan_gear")
    aeration_is_on = _component_property("state", "aeration_is_on")
    get_property = _component_method("state", "get_property")
    get_bool_property = _component_method("state", "get_bool_property")
    get_int_property = _component_method("state", "get_int_property")
    get_float_property = _component_method("state", "get_float_property")
    get_optional_int_property = _component_method("state", "get_optional_int_property")
    get_str_property = _component_method("state", "get_str_property")
    percent_to_kelvin_for_device = _component_method(
        "state", "percent_to_kelvin_for_device"
    )
    kelvin_to_percent_for_device = _component_method(
        "state", "kelvin_to_percent_for_device"
    )

    ip_address = _component_property("network_info", "ip_address")
    wifi_ssid = _component_property("network_info", "wifi_ssid")
    wifi_rssi = _component_property("network_info", "wifi_rssi")
    net_type = _component_property("network_info", "net_type")
    mac_address = _component_property("network_info", "mac_address")
    firmware_version = _component_property("network_info", "firmware_version")
    latest_sync_timestamp = _component_property("network_info", "latest_sync_timestamp")
    mesh_address = _component_property("network_info", "mesh_address")
    mesh_type = _component_property("network_info", "mesh_type")
    is_mesh_gateway = _component_property("network_info", "is_mesh_gateway")
    ble_mac = _component_property("network_info", "ble_mac")
    connection_quality = _component_property("network_info", "connection_quality")

    gear_list = _component_property("extras", "gear_list")
    last_gear_index = _component_property("extras", "last_gear_index")
    has_gear_presets = _component_property("extras", "has_gear_presets")
    has_sleep_wake_features = _component_property("extras", "has_sleep_wake_features")
    has_floor_lamp_features = _component_property("extras", "has_floor_lamp_features")
    panel_info = _component_property("extras", "panel_info")
    is_ir_remote_device = _component_property("extras", "is_ir_remote_device")
    ir_remote_gateway_device_id = _component_property(
        "extras", "ir_remote_gateway_device_id"
    )
    rc_list = _component_property("extras", "rc_list")
    supports_ir_switch = _component_property("extras", "supports_ir_switch")

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

    @property
    def outlet_power_info(self) -> OutletPowerInfo | None:
        """Return the formal outlet-power primitive with legacy fallback."""
        if self._outlet_power_info is not None:
            return self._outlet_power_info
        legacy_power_info = self.extra_data.get("power_info")
        if isinstance(legacy_power_info, dict):
            return legacy_power_info
        return None

    @outlet_power_info.setter
    def outlet_power_info(self, value: OutletPowerInfo | None) -> None:
        """Persist the formal outlet-power primitive and clear legacy side-car state."""
        self._outlet_power_info = None if value is None else dict(value)
        self.extra_data.pop("power_info", None)

    @property
    def is_online(self) -> bool:
        """Return whether the device is currently connected."""
        return self.state.is_connected

    def mark_mqtt_update(self, *, timestamp: float | None = None) -> None:
        """Record that the device received an MQTT property update."""
        self._last_mqtt_update_at = monotonic() if timestamp is None else timestamp

    def has_recent_mqtt_update(self, *, stale_window_seconds: float = 180.0) -> bool:
        """Return True when an MQTT update arrived within the stale window."""
        if self._last_mqtt_update_at <= 0.0:
            return False
        return monotonic() - self._last_mqtt_update_at <= stale_window_seconds

    def update_properties(self, properties: DevicePropertyMap) -> None:
        """Merge normalized properties into the live facade state."""
        device_runtime.update_device_properties(self, properties)

    @classmethod
    def from_api_data(cls, data: DevicePropertyMap) -> LiproDevice:
        """Build a device facade from one raw API payload."""
        return build_device_from_api_data(cls, data)


__all__ = ["LiproDevice"]
