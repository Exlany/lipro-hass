"""Device abstraction for Lipro integration."""

from __future__ import annotations

from collections.abc import Mapping, Sequence
from dataclasses import dataclass, field
import json
import logging
from typing import Any

from ...const.api import DEFAULT_MAX_FAN_GEAR
from ...const.categories import DeviceCategory, get_platforms_for_category
from ...const.device_types import (
    DEVICE_TYPE_MAP,
    IOT_NAME_TO_DEFAULT_MAX_FAN_GEAR,
    IOT_NAME_TO_PHYSICAL_MODEL,
    PHYSICAL_MODEL_TO_DEVICE_TYPE,
)
from ...const.properties import (
    MAX_COLOR_TEMP_KELVIN,
    MIN_COLOR_TEMP_KELVIN,
    PROP_BODY_REACTIVE,
    PROP_CONNECT_STATE,
    PROP_FOCUS_MODE,
    PROP_GEAR_LIST,
    PROP_IR_SWITCH,
    PROP_IS_SUPPORT_IR_SWITCH,
    PROP_LAST_GEAR_INDEX,
    PROP_PANEL_INFO,
    PROP_RC_LIST,
    PROP_SLEEP_AID_ENABLE,
    PROP_WAKE_UP_ENABLE,
)
from ..utils.coerce import coerce_boollike
from ..utils.identifiers import is_valid_iot_device_id, is_valid_mesh_group_id
from ..utils.property_normalization import normalize_properties
from .capabilities import DeviceCapabilities
from .identity import DeviceIdentity
from .network_info import DeviceNetworkInfo
from .state import DeviceState

_LOGGER = logging.getLogger(__name__)
_IOT_REMOTE_ID_PREFIX = "rmt_id_"
_IR_REMOTE_DEVICE_DRIVER_ID = "00000000"


def _coerce_api_bool(value: Any) -> bool:
    """Normalize API boolean-like values.

    Handles backend variants such as bool, int(1/0), and strings.
    """
    return coerce_boollike(value, logger=_LOGGER, context="API")


@dataclass
class LiproDevice:
    """Represents a Lipro device."""

    device_number: int  # API "deviceId" (numeric), NOT a unique identifier
    serial: str  # "03ab"+MAC for devices, "mesh_group_xxxxx" for groups
    name: str
    device_type: int
    iot_name: str
    room_id: int | None = None
    room_name: str | None = None
    is_group: bool = False
    product_id: int | None = None
    physical_model: str | None = None
    properties: dict[str, Any] = field(default_factory=dict)
    extra_data: dict[str, Any] = field(default_factory=dict)  # For power info, etc.
    available: bool = True
    # Color temperature range from product config (Kelvin)
    # 0 means single color temperature (no adjustment supported)
    min_color_temp_kelvin: int = MIN_COLOR_TEMP_KELVIN
    max_color_temp_kelvin: int = MAX_COLOR_TEMP_KELVIN
    # Fan gear range (from product config or default)
    default_max_fan_gear_in_model: int = DEFAULT_MAX_FAN_GEAR
    max_fan_gear: int = DEFAULT_MAX_FAN_GEAR
    # Flag that physical_model exists but is not recognized by integration tables.
    has_unknown_physical_model: bool = False
    # Cache for parsed gear_list (cleared on property update)
    _gear_list_cache: list[Any] | None = field(default=None, repr=False, compare=False)

    def __post_init__(self) -> None:
        """Normalize payload variants into canonical internal state."""
        self.properties = normalize_properties(self.properties)
        self.has_unknown_physical_model = bool(
            self.physical_model
            and not PHYSICAL_MODEL_TO_DEVICE_TYPE.get(self.physical_model)
        )
        if PROP_CONNECT_STATE in self.properties:
            self.available = self.is_connected

    @property
    def identity(self) -> DeviceIdentity:
        """Return one immutable snapshot of device identity fields."""
        return DeviceIdentity(
            device_number=self.device_number,
            serial=self.serial,
            name=self.name,
            device_type=self.device_type,
            iot_name=self.iot_name,
            room_id=self.room_id,
            room_name=self.room_name,
            product_id=self.product_id,
            physical_model=self.physical_model,
        )

    @property
    def device_type_hex(self) -> str:
        """Get device type as hex string.

        Priority:
        1. physical_model - The ONLY reliable source for device category
        2. iot_name -> built-in model table (from App's device_models.txt)
        3. device_type (type field) - Fallback only, often inaccurate

        IMPORTANT: The 'type' field from API is Mesh protocol classification,
        NOT device function type! Real API examples:
        - type=6 with physicalModel="light" -> Light strip (NOT outlet!)
        - type=9 with physicalModel="fanLight" -> Fan light (NOT desk lamp!)
        - Always trust physicalModel over type field
        """
        # Priority 1: Use physical_model (the only reliable source)
        if self.physical_model:
            device_type = PHYSICAL_MODEL_TO_DEVICE_TYPE.get(self.physical_model)
            if device_type:
                return device_type
            _LOGGER.warning(
                "Unknown physicalModel '%s' for device %s, falling back to type field",
                self.physical_model,
                self.name,
            )

        # Priority 2: Look up iotName in built-in model table
        if self.iot_name:
            phy_model = IOT_NAME_TO_PHYSICAL_MODEL.get(
                self.iot_name
            ) or IOT_NAME_TO_PHYSICAL_MODEL.get(self.iot_name.lower())
            if phy_model:
                device_type = PHYSICAL_MODEL_TO_DEVICE_TYPE.get(phy_model)
                if device_type:
                    _LOGGER.debug(
                        "Device %s: resolved type via iotName=%s -> %s",
                        self.name,
                        self.iot_name,
                        phy_model,
                    )
                    return device_type

        # Priority 3: Fall back to type field (may be inaccurate)
        return DEVICE_TYPE_MAP.get(self.device_type, f"ff{self.device_type:06x}")

    @property
    def platforms(self) -> list[str]:
        """Get HA platforms for this device."""
        return get_platforms_for_category(self.category)

    @property
    def unique_id(self) -> str:
        """Get unique ID for this device."""
        return f"lipro_{self.serial}"

    @property
    def iot_device_id(self) -> str:
        """Get IoT device ID for API calls.

        This is an alias for `serial`. The IoT device ID format is:
        "03ab" + BLE_MAC.lower().replace(":", "")

        Example: BLE MAC "5C:CD:7C:XX:XX:XX" -> IoT ID "03ab5ccd7cxxxxxx"

        The "03ab" prefix is Lipro/Meizu manufacturer ID (939 in decimal).
        """
        return self.serial

    @property
    def has_valid_iot_id(self) -> bool:
        """Check if device has a valid IoT device ID format.

        Returns:
            True if serial matches IoT device ID format or Mesh group ID format.

        """
        if self.is_group:
            return is_valid_mesh_group_id(self.serial)
        return is_valid_iot_device_id(self.serial)

    # =========================================================================
    # Device Category Properties
    # =========================================================================

    @property
    def capabilities(self) -> DeviceCapabilities:
        """Return one structured snapshot of derived category/capability flags."""
        return DeviceCapabilities.from_device_profile(
            device_type_hex=self.device_type_hex,
            min_color_temp_kelvin=self.min_color_temp_kelvin,
            max_color_temp_kelvin=self.max_color_temp_kelvin,
        )

    @property
    def category(self) -> DeviceCategory:
        """Get the device category based on device type."""
        return self.capabilities.category

    @property
    def is_light(self) -> bool:
        """Check if device is a light (not including fan lights)."""
        return self.capabilities.is_light

    @property
    def is_fan_light(self) -> bool:
        """Check if device is a fan light."""
        return self.capabilities.is_fan_light

    @property
    def is_curtain(self) -> bool:
        """Check if device is a curtain."""
        return self.capabilities.is_curtain

    @property
    def is_switch(self) -> bool:
        """Check if device is a switch or outlet."""
        return self.capabilities.is_switch

    @property
    def is_outlet(self) -> bool:
        """Check if device is an outlet."""
        return self.capabilities.is_outlet

    @property
    def is_heater(self) -> bool:
        """Check if device is a heater."""
        return self.capabilities.is_heater

    @property
    def is_sensor(self) -> bool:
        """Check if device is a sensor."""
        return self.capabilities.is_sensor

    @property
    def is_body_sensor(self) -> bool:
        """Check if device is a body/motion sensor."""
        return self.capabilities.is_body_sensor

    @property
    def is_door_sensor(self) -> bool:
        """Check if device is a door/window sensor."""
        return self.capabilities.is_door_sensor

    @property
    def is_gateway(self) -> bool:
        """Check if device is a gateway."""
        return self.capabilities.is_gateway

    @property
    def supports_color_temp(self) -> bool:
        """Check if device supports color temperature adjustment.

        Returns False if maxTemperature is 0 (single color temperature device).
        """
        return self.capabilities.supports_color_temp

    # =========================================================================
    # Property Getters with Type Conversion
    # =========================================================================

    @property
    def state(self) -> DeviceState:
        """Return one helper object for mutable state/property resolution."""
        return DeviceState(
            properties=self.properties,
            min_color_temp_kelvin=self.min_color_temp_kelvin,
            max_color_temp_kelvin=self.max_color_temp_kelvin,
            max_fan_gear=self.max_fan_gear,
        )

    def get_property(self, key: str, default: Any = None) -> Any:
        """Get a property value."""
        return self.state.get_property(key, default)

    @staticmethod
    def _coerce_int(value: Any) -> int | None:
        """Convert a value to int, returning None on failure."""
        try:
            return int(value)
        except (TypeError, ValueError):
            return None

    @staticmethod
    def _coerce_float(value: Any) -> float | None:
        """Convert a value to float, returning None on failure."""
        try:
            return float(value)
        except (TypeError, ValueError):
            return None

    def get_bool_property(self, key: str, default: bool = False) -> bool:
        """Get a boolean property value.

        Handles various API response formats:
        - Boolean: True/False
        - String: "1"/"0", "true"/"false", "True"/"False"
        - Integer: 1/0
        """
        return self.state.get_bool_property(key, default)

    def get_int_property(self, key: str, default: int = 0) -> int:
        """Get an integer property value."""
        return self.state.get_int_property(key, default)

    def get_float_property(self, key: str, default: float = 0.0) -> float:
        """Get a float property value."""
        return self.state.get_float_property(key, default)

    def get_optional_int_property(self, key: str) -> int | None:
        """Get an optional integer property value (returns None if missing)."""
        return self.state.get_optional_int_property(key)

    def get_str_property(self, key: str) -> str | None:
        """Get a string property value, or None if missing."""
        return self.state.get_str_property(key)

    # Common state properties
    @property
    def is_on(self) -> bool:
        """Check if device is on."""
        return self.state.is_on

    @property
    def is_connected(self) -> bool:
        """Check if device is connected."""
        return self.state.is_connected

    @property
    def brightness(self) -> int:
        """Get brightness (0-100)."""
        return self.state.brightness

    @property
    def color_temp(self) -> int:
        """Get color temperature in Kelvin.

        API stores temperature as percentage (0=warmest, 100=coolest).
        Uses device-specific color temp range if available.
        """
        return self.state.color_temp

    def percent_to_kelvin_for_device(self, percent: int) -> int:
        """Convert API temperature percentage to Kelvin using device-specific range.

        Args:
            percent: Temperature percentage (0-100).

        Returns:
            Color temperature in Kelvin.

        """
        return self.state.percent_to_kelvin_for_device(percent)

    def kelvin_to_percent_for_device(self, kelvin: int) -> int:
        """Convert Kelvin to API temperature percentage using device-specific range.

        Args:
            kelvin: Color temperature in Kelvin.

        Returns:
            Temperature percentage (0-100), clamped.

        """
        return self.state.kelvin_to_percent_for_device(kelvin)

    @property
    def fade_state(self) -> bool:
        """Get fade/transition state for light."""
        return self.state.fade_state

    @property
    def gear_list(self) -> list[Any]:
        """Get light gear presets.

        Returns:
            List of gear presets, each with 'temperature' (0-100%)
            and 'brightness' (0-100). Empty list if not available.

        """
        # Return cached value if available
        if self._gear_list_cache is not None:
            return self._gear_list_cache

        value = self.properties.get(PROP_GEAR_LIST)
        if not value:
            return []
        try:
            if isinstance(value, str):
                stripped = value.lstrip()
                if not stripped or stripped[0] not in "{[":
                    return []
                result = json.loads(value)
            else:
                result = value
            if not isinstance(result, list):
                return []
            # Cache the parsed result
            self._gear_list_cache = result
            return result
        except (json.JSONDecodeError, TypeError):
            return []

    @property
    def last_gear_index(self) -> int:
        """Get last used gear index (0-based)."""
        return self.get_int_property(PROP_LAST_GEAR_INDEX, -1)

    @property
    def has_gear_presets(self) -> bool:
        """Check if device has gear presets."""
        return len(self.gear_list) > 0

    # Natural Light properties (自然光灯)
    @property
    def sleep_aid_enabled(self) -> bool:
        """Check if sleep aid mode is enabled."""
        return self.state.sleep_aid_enabled

    @property
    def wake_up_enabled(self) -> bool:
        """Check if wake up mode is enabled."""
        return self.state.wake_up_enabled

    @property
    def has_sleep_wake_features(self) -> bool:
        """Check if device has sleep/wake features (Natural Light)."""
        return (
            PROP_SLEEP_AID_ENABLE in self.properties
            or PROP_WAKE_UP_ENABLE in self.properties
        )

    # Floor Lamp properties (落地灯)
    @property
    def focus_mode_enabled(self) -> bool:
        """Check if focus mode is enabled."""
        return self.state.focus_mode_enabled

    @property
    def body_reactive_enabled(self) -> bool:
        """Check if body reactive (motion sensing) is enabled."""
        return self.state.body_reactive_enabled

    @property
    def has_floor_lamp_features(self) -> bool:
        """Check if device has floor lamp features."""
        return (
            PROP_FOCUS_MODE in self.properties or PROP_BODY_REACTIVE in self.properties
        )

    # Switch panel properties (开关面板)
    @property
    def panel_led_enabled(self) -> bool:
        """Check if the panel indicator LED is enabled."""
        return self.state.panel_led_enabled

    @property
    def panel_memory_enabled(self) -> bool:
        """Check if panel power-loss memory is enabled."""
        return self.state.panel_memory_enabled

    @property
    def panel_type(self) -> int:
        """Get panel type discriminator required by panel commands."""
        return 1 if self.iot_name.casefold() == "21jd" else 0

    @property
    def panel_pair_key_full(self) -> bool:
        """Return whether panel bind slots are reported full."""
        return self.state.panel_pair_key_full

    @property
    def panel_info(self) -> list[dict[str, Any]]:
        """Return parsed panelInfo payload when available."""
        value = self.properties.get(PROP_PANEL_INFO)
        if not value:
            return []
        try:
            if isinstance(value, str):
                stripped = value.lstrip()
                if not stripped or stripped[0] not in "[{":
                    return []
                parsed = json.loads(value)
            else:
                parsed = value
        except (json.JSONDecodeError, TypeError):
            return []
        if not isinstance(parsed, list):
            return []
        return [item for item in parsed if isinstance(item, dict)]

    # Infrared / gateway properties (红外 / 网关)
    @property
    def is_ir_remote_device(self) -> bool:
        """Return True when this runtime device represents an IR remote asset."""
        if self.extra_data.get("is_ir_remote") is True:
            return True
        return self.physical_model == "irRemote" or self.serial.startswith(
            _IOT_REMOTE_ID_PREFIX
        )

    @property
    def ir_remote_gateway_device_id(self) -> str | None:
        """Return parent gateway device ID parsed from IR remote serial when known."""
        if not self.serial.startswith(_IOT_REMOTE_ID_PREFIX):
            return None
        parts = self.serial.split("_")
        if len(parts) <= 4:
            return None
        gateway_device_id = parts[4].strip()
        if (
            not gateway_device_id
            or gateway_device_id == _IR_REMOTE_DEVICE_DRIVER_ID
        ):
            return None
        return gateway_device_id

    @property
    def rc_list(self) -> list[dict[str, Any]]:
        """Return parsed gateway rcList payload when available."""
        value = self.properties.get(PROP_RC_LIST)
        if not value:
            return []
        try:
            if isinstance(value, str):
                stripped = value.lstrip()
                if not stripped or stripped[0] not in "[{":
                    return []
                parsed = json.loads(value)
            else:
                parsed = value
        except (json.JSONDecodeError, TypeError):
            return []
        if not isinstance(parsed, list):
            return []
        return [item for item in parsed if isinstance(item, dict)]

    @property
    def supports_ir_switch(self) -> bool:
        """Return True when IR switch capability is exposed by runtime data."""
        return (
            PROP_IS_SUPPORT_IR_SWITCH in self.properties
            or PROP_IR_SWITCH in self.properties
        )

    @property
    def ir_switch_enabled(self) -> bool:
        """Return current IR switch state when available."""
        return self.state.ir_switch_enabled

    # Bedside Light properties (床头灯)
    @property
    def battery_level(self) -> int | None:
        """Get battery level (0-100), or None if not a battery device."""
        return self.state.battery_level

    @property
    def is_charging(self) -> bool:
        """Check if device is charging."""
        return self.state.is_charging

    @property
    def has_battery(self) -> bool:
        """Check if device has battery."""
        return self.state.has_battery

    # Curtain properties
    @property
    def position(self) -> int:
        """Get curtain position (0-100)."""
        return self.state.position

    @property
    def is_moving(self) -> bool:
        """Check if curtain is moving."""
        return self.state.is_moving

    @property
    def direction(self) -> str | None:
        """Get curtain movement direction."""
        return self.state.direction

    # Fan properties
    @property
    def fan_is_on(self) -> bool:
        """Check if fan is on."""
        return self.state.fan_is_on

    @property
    def fan_speed_range(self) -> tuple[int, int]:
        """Get fan speed range (min_gear, max_gear)."""
        return (1, self.max_fan_gear)

    @property
    def fan_gear(self) -> int:
        """Get fan gear/speed, clamped to device range."""
        return self.state.fan_gear

    @property
    def fan_mode(self) -> int:
        """Get fan mode (0=direct, 1=natural, 2=cycle, 3=gentle_wind)."""
        return self.state.fan_mode

    # Heater properties
    @property
    def heater_is_on(self) -> bool:
        """Check if heater is on."""
        return self.state.heater_is_on

    @property
    def heater_mode(self) -> int:
        """Get heater mode."""
        return self.state.heater_mode

    @property
    def wind_gear(self) -> int:
        """Get wind gear."""
        return self.state.wind_gear

    @property
    def light_mode(self) -> int:
        """Get light mode for heater."""
        return self.state.light_mode

    @property
    def wind_direction_mode(self) -> int:
        """Get wind direction mode (1=auto, 2=fixed)."""
        return self.state.wind_direction_mode

    @property
    def aeration_gear(self) -> int:
        """Get aeration/ventilation gear (0=off, 1=strong, 2=weak)."""
        return self.state.aeration_gear

    @property
    def aeration_is_on(self) -> bool:
        """Check if aeration/ventilation is on."""
        return self.state.aeration_is_on

    # Sensor properties
    @property
    def door_is_open(self) -> bool:
        """Check if door is open (door sensor)."""
        return self.state.door_is_open

    @property
    def is_activated(self) -> bool:
        """Check if motion detected (body sensor)."""
        return self.state.is_activated

    @property
    def is_dark(self) -> bool:
        """Check if environment is dark."""
        return self.state.is_dark

    @property
    def low_battery(self) -> bool:
        """Check if battery is low."""
        return self.state.low_battery

    # =========================================================================
    # Network/Device Info Properties (诊断信息)
    # =========================================================================

    @property
    def network_info(self) -> DeviceNetworkInfo:
        """Return one structured snapshot of network and diagnostics fields."""
        return DeviceNetworkInfo.from_properties(self.properties)

    @property
    def ip_address(self) -> str | None:
        """Get device IP address."""
        return self.network_info.ip_address

    @property
    def wifi_ssid(self) -> str | None:
        """Get connected WiFi SSID."""
        return self.network_info.wifi_ssid

    @property
    def wifi_rssi(self) -> int | None:
        """Get WiFi signal strength (RSSI in dBm)."""
        return self.network_info.wifi_rssi

    @property
    def net_type(self) -> str | None:
        """Get network type (e.g., 'wifi')."""
        return self.network_info.net_type

    @property
    def mac_address(self) -> str | None:
        """Get device MAC address."""
        return self.network_info.mac_address

    @property
    def firmware_version(self) -> str | None:
        """Get device firmware version."""
        return self.network_info.firmware_version

    @property
    def latest_sync_timestamp(self) -> int | None:
        """Get latest sync timestamp (milliseconds)."""
        return self.network_info.latest_sync_timestamp

    # =========================================================================
    # Mesh Network Properties (Mesh 网络拓扑)
    # =========================================================================

    @property
    def mesh_address(self) -> int | None:
        """Get Mesh network address."""
        return self.network_info.mesh_address

    @property
    def mesh_type(self) -> int | None:
        """Get Mesh device type (1=standard)."""
        return self.network_info.mesh_type

    @property
    def is_mesh_gateway(self) -> bool:
        """Check if device is a Mesh gateway."""
        return self.network_info.is_mesh_gateway

    @property
    def ble_mac(self) -> str | None:
        """Get BLE MAC address."""
        return self.network_info.ble_mac

    def update_properties(self, properties: dict[str, Any]) -> None:
        """Update device properties.

        Args:
            properties: New properties to merge.

        """
        normalized = normalize_properties(properties)

        # Clear gear_list cache if gearList property is being updated
        if PROP_GEAR_LIST in normalized:
            self._gear_list_cache = None

        self.properties.update(normalized)
        # Update availability based on connection state
        if PROP_CONNECT_STATE in normalized:
            self.available = self.is_connected

    @classmethod
    def from_api_data(cls, data: dict[str, Any]) -> LiproDevice:
        """Create a device from API response data.

        Args:
            data: Device data from API.

        Returns:
            LiproDevice instance.

        """
        identity = DeviceIdentity.from_api_data(data)
        iot_name = identity.iot_name
        default_max_fan_gear_in_model = DEFAULT_MAX_FAN_GEAR
        if iot_name:
            model_default_max_fan_gear = IOT_NAME_TO_DEFAULT_MAX_FAN_GEAR.get(
                iot_name.lower()
            )
            if (
                isinstance(model_default_max_fan_gear, int)
                and model_default_max_fan_gear > 0
            ):
                default_max_fan_gear_in_model = model_default_max_fan_gear

        extra_data: dict[str, Any] = {}
        if "isIrRemote" in data:
            extra_data["is_ir_remote"] = _coerce_api_bool(data.get("isIrRemote"))

        return cls(
            device_number=identity.device_number,
            serial=identity.serial,
            name=identity.name,
            device_type=identity.device_type,
            iot_name=identity.iot_name,
            room_id=identity.room_id,
            room_name=identity.room_name,
            is_group=_coerce_api_bool(data.get("isGroup", False))
            or _coerce_api_bool(data.get("group", False)),
            product_id=identity.product_id,
            physical_model=identity.physical_model,
            default_max_fan_gear_in_model=default_max_fan_gear_in_model,
            max_fan_gear=default_max_fan_gear_in_model,
            extra_data=extra_data,
        )


def parse_properties_list(
    properties_list: Sequence[object] | None,
) -> dict[str, Any]:
    """Parse properties list from API response.

    Args:
        properties_list: List of {key, value} dicts.

    Returns:
        Dictionary of property key-value pairs.

    """
    if not properties_list:
        return {}

    result: dict[str, Any] = {}
    for prop in properties_list:
        if not isinstance(prop, Mapping):
            continue
        key = prop.get("key")
        value = prop.get("value")
        if isinstance(key, str) and key:
            result[key] = value
    return normalize_properties(result)
