from typing import Any

from custom_components.lipro.const.categories import DeviceCategory
from custom_components.lipro.core.capability import CapabilitySnapshot
from custom_components.lipro.core.device.extras import DeviceExtras
from custom_components.lipro.core.device.identity import DeviceIdentity
from custom_components.lipro.core.device.network_info import DeviceNetworkInfo
from custom_components.lipro.core.device.state import DeviceState

type DevicePropertyMap = dict[str, object]
type DeviceExtraDataMap = dict[str, object]
type OutletPowerInfo = dict[str, object]

class LiproDevice:
    device_number: int
    serial: str
    name: str
    device_type: int
    iot_name: str
    room_id: int | None
    room_name: str | None
    is_group: bool
    product_id: int | None
    physical_model: str | None
    properties: DevicePropertyMap
    extra_data: DeviceExtraDataMap
    available: bool
    min_color_temp_kelvin: int
    max_color_temp_kelvin: int
    default_max_fan_gear_in_model: int
    max_fan_gear: int
    has_unknown_physical_model: bool
    _state_cache: DeviceState | None
    _extras_cache: DeviceExtras | None
    _outlet_power_info: OutletPowerInfo | None

    is_light: bool
    is_fan_light: bool
    is_curtain: bool
    is_switch: bool
    is_outlet: bool
    is_heater: bool
    is_sensor: bool
    is_body_sensor: bool
    is_door_sensor: bool
    is_gateway: bool
    supports_color_temp: bool

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
    is_connected: bool
    color_temp: int
    battery_level: int | None
    has_battery: bool
    position: int
    direction: str | None
    fan_gear: int
    aeration_is_on: bool

    ip_address: str | None
    wifi_ssid: str | None
    wifi_rssi: int | None
    net_type: str | None
    mac_address: str | None
    firmware_version: str | None
    latest_sync_timestamp: int | None
    mesh_address: int | None
    mesh_type: int | None
    is_mesh_gateway: bool
    ble_mac: str | None
    connection_quality: str

    gear_list: list[Any]
    last_gear_index: int
    has_gear_presets: bool
    has_sleep_wake_features: bool
    has_floor_lamp_features: bool
    panel_info: list[dict[str, Any]]
    panel_type: int
    fan_speed_range: tuple[int, int]
    is_ir_remote_device: bool
    ir_remote_gateway_device_id: str | None
    rc_list: list[dict[str, Any]]
    supports_ir_switch: bool

    def __init__(
        self,
        device_number: int,
        serial: str,
        name: str,
        device_type: int,
        iot_name: str,
        room_id: int | None = ...,
        room_name: str | None = ...,
        is_group: bool = ...,
        product_id: int | None = ...,
        physical_model: str | None = ...,
        properties: DevicePropertyMap = ...,
        extra_data: DeviceExtraDataMap = ...,
        available: bool = ...,
        min_color_temp_kelvin: int = ...,
        max_color_temp_kelvin: int = ...,
        default_max_fan_gear_in_model: int = ...,
        max_fan_gear: int = ...,
        has_unknown_physical_model: bool = ...,
    ) -> None: ...

    @property
    def identity(self) -> DeviceIdentity: ...

    @property
    def capabilities(self) -> CapabilitySnapshot: ...

    @property
    def state(self) -> DeviceState: ...

    @property
    def network_info(self) -> DeviceNetworkInfo: ...

    @property
    def extras(self) -> DeviceExtras: ...

    @property
    def is_online(self) -> bool: ...

    @property
    def outlet_power_info(self) -> OutletPowerInfo | None: ...

    @outlet_power_info.setter
    def outlet_power_info(self, value: OutletPowerInfo | None) -> None: ...

    def mark_mqtt_update(self, *, timestamp: float | None = ...) -> None: ...

    @property
    def device_type_hex(self) -> str: ...

    @property
    def category(self) -> DeviceCategory: ...

    @property
    def platforms(self) -> list[str]: ...

    @property
    def unique_id(self) -> str: ...

    @property
    def iot_device_id(self) -> str: ...

    @property
    def has_valid_iot_id(self) -> bool: ...

    def get_property(self, key: str, default: Any = ...) -> Any: ...

    def get_bool_property(self, key: str, default: bool = ...) -> bool: ...

    def get_int_property(self, key: str, default: int = ...) -> int: ...

    def get_float_property(self, key: str, default: float = ...) -> float: ...

    def get_optional_int_property(self, key: str) -> int | None: ...

    def get_str_property(self, key: str) -> str | None: ...

    def percent_to_kelvin_for_device(self, percent: int) -> int: ...

    def kelvin_to_percent_for_device(self, kelvin: int) -> int: ...

    def update_properties(self, properties: DevicePropertyMap) -> None: ...

    def has_recent_mqtt_update(self, *, stale_window_seconds: float = ...) -> bool: ...

    @classmethod
    def from_api_data(cls, data: DevicePropertyMap) -> LiproDevice: ...
