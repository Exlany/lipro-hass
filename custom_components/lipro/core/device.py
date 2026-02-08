"""Device abstraction for Lipro integration."""

from __future__ import annotations

from dataclasses import dataclass, field
import json
import logging
import re
from typing import Any

from ..const import (
    DEVICE_TYPE_MAP,
    PHYSICAL_MODEL_TO_DEVICE_TYPE,
    PROP_ACTIVATED,
    PROP_AERATION_GEAR,
    PROP_BATTERY,
    PROP_BLE_MAC,
    PROP_BODY_REACTIVE,
    PROP_BRIGHTNESS,
    PROP_CHARGING,
    PROP_CONNECT_STATE,
    PROP_DARK,
    PROP_DIRECTION,
    PROP_DOOR_OPEN,
    PROP_FADE_STATE,
    PROP_FAN_GEAR,
    PROP_FAN_MODE,
    PROP_FAN_ONOFF,
    PROP_FAN_ONOFF_ALT,
    PROP_FOCUS_MODE,
    PROP_GEAR_LIST,
    PROP_HEATER_MODE,
    PROP_HEATER_SWITCH,
    PROP_IP,
    PROP_LAST_GEAR_INDEX,
    PROP_LATEST_SYNC_TIMESTAMP,
    PROP_LIGHT_MODE,
    PROP_LOW_BATTERY,
    PROP_MAC,
    PROP_MESH_ADDRESS,
    PROP_MESH_GATEWAY,
    PROP_MESH_TYPE,
    PROP_MOVING,
    PROP_NET_TYPE,
    PROP_POSITION,
    PROP_POWER_STATE,
    PROP_SLEEP_AID_ENABLE,
    PROP_TEMPERATURE,
    PROP_VERSION,
    PROP_WAKE_UP_ENABLE,
    PROP_WIFI_RSSI,
    PROP_WIFI_SSID,
    PROP_WIND_DIRECTION_MODE,
    PROP_WIND_GEAR,
    DeviceCategory,
    get_device_category,
    get_platforms_for_category,
    percent_to_kelvin,
)

_LOGGER = logging.getLogger(__name__)

# IoT Device ID format: "03ab" + 12 hex chars (MAC without colons)
# "03ab" is Lipro/Meizu manufacturer ID (939 in decimal)
# Example: "03ab5ccd7cxxxxxx" (5ccd7c is Meizu's OUI)
_IOT_DEVICE_ID_PATTERN = re.compile(r"^03ab[0-9a-f]{12}$")

# Mesh group ID format: "mesh_group_" + digits (e.g., "mesh_group_10001")
_MESH_GROUP_ID_PATTERN = re.compile(r"^mesh_group_\d+$")


def is_valid_iot_device_id(device_id: str) -> bool:
    """Validate IoT device ID format.

    Args:
        device_id: The device ID to validate.

    Returns:
        True if valid IoT device ID format (03ab + 12 hex chars).

    """
    return bool(_IOT_DEVICE_ID_PATTERN.match(device_id))


def is_valid_mesh_group_id(group_id: str) -> bool:
    """Validate Mesh group ID format.

    Args:
        group_id: The group ID to validate.

    Returns:
        True if valid Mesh group ID format (mesh_group_ + digits).

    """
    return bool(_MESH_GROUP_ID_PATTERN.match(group_id))


@dataclass
class LiproDevice:
    """Represents a Lipro device."""

    device_id: int
    serial: str  # IoT Device ID, format: "03ab" + MAC (e.g., "03ab5ccd7cxxxxxx")
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
    min_color_temp_kelvin: int = 2700
    max_color_temp_kelvin: int = 6500
    # Cache for parsed gear_list (cleared on property update)
    _gear_list_cache: list[dict[str, int]] | None = field(
        default=None, repr=False, compare=False
    )

    @property
    def device_type_hex(self) -> str:
        """Get device type as hex string.

        Priority:
        1. physical_model - The ONLY reliable source for device category
        2. device_type (type field) - Fallback only, often inaccurate

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
            # Record unknown physical model for anonymous share
            _record_unknown_device_type(
                self.physical_model, self.device_type, self.iot_name
            )

        # Priority 2: Fall back to type field (may be inaccurate)
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
    def category(self) -> DeviceCategory:
        """Get the device category based on device type."""
        return get_device_category(self.device_type_hex)

    @property
    def is_light(self) -> bool:
        """Check if device is a light (not including fan lights)."""
        return self.category == DeviceCategory.LIGHT

    @property
    def is_fan_light(self) -> bool:
        """Check if device is a fan light."""
        return self.category == DeviceCategory.FAN_LIGHT

    @property
    def is_curtain(self) -> bool:
        """Check if device is a curtain."""
        return self.category == DeviceCategory.CURTAIN

    @property
    def is_switch(self) -> bool:
        """Check if device is a switch or outlet."""
        return self.category in (DeviceCategory.SWITCH, DeviceCategory.OUTLET)

    @property
    def is_heater(self) -> bool:
        """Check if device is a heater."""
        return self.category == DeviceCategory.HEATER

    @property
    def is_sensor(self) -> bool:
        """Check if device is a sensor."""
        return self.category in (DeviceCategory.BODY_SENSOR, DeviceCategory.DOOR_SENSOR)

    @property
    def is_body_sensor(self) -> bool:
        """Check if device is a body/motion sensor."""
        return self.category == DeviceCategory.BODY_SENSOR

    @property
    def is_door_sensor(self) -> bool:
        """Check if device is a door/window sensor."""
        return self.category == DeviceCategory.DOOR_SENSOR

    @property
    def is_gateway(self) -> bool:
        """Check if device is a gateway."""
        return self.category == DeviceCategory.GATEWAY

    @property
    def supports_color_temp(self) -> bool:
        """Check if device supports color temperature adjustment.

        Returns False if maxTemperature is 0 (single color temperature device).
        """
        return self.max_color_temp_kelvin > 0 and self.min_color_temp_kelvin > 0

    # =========================================================================
    # Property Getters with Type Conversion
    # =========================================================================

    def get_property(self, key: str, default: Any = None) -> Any:
        """Get a property value."""
        return self.properties.get(key, default)

    def get_bool_property(self, key: str, default: bool = False) -> bool:
        """Get a boolean property value.

        Handles various API response formats:
        - Boolean: True/False
        - String: "1"/"0", "true"/"false", "True"/"False"
        - Integer: 1/0
        """
        value = self.properties.get(key)
        if value is None:
            return default
        if isinstance(value, bool):
            return value
        if isinstance(value, str):
            # Handle both "true"/"false" and "1"/"0" string formats
            return value.lower() in ("1", "true", "yes", "on")
        return bool(value)

    def get_int_property(self, key: str, default: int = 0) -> int:
        """Get an integer property value."""
        value = self.properties.get(key)
        if value is None:
            return default
        try:
            return int(value)
        except (ValueError, TypeError):
            return default

    def get_float_property(self, key: str, default: float = 0.0) -> float:
        """Get a float property value."""
        value = self.properties.get(key)
        if value is None:
            return default
        try:
            return float(value)
        except (ValueError, TypeError):
            return default

    # Common state properties
    @property
    def is_on(self) -> bool:
        """Check if device is on."""
        return self.get_bool_property(PROP_POWER_STATE)

    @property
    def is_connected(self) -> bool:
        """Check if device is connected."""
        return self.get_bool_property(PROP_CONNECT_STATE, True)

    @property
    def brightness(self) -> int:
        """Get brightness (0-100)."""
        return self.get_int_property(PROP_BRIGHTNESS, 100)

    @property
    def color_temp(self) -> int:
        """Get color temperature in Kelvin.

        API stores temperature as percentage (0=warmest, 100=coolest).
        Uses device-specific color temp range if available.
        """
        percent = self.get_int_property(PROP_TEMPERATURE, 34)

        # Use device-specific range if available
        if self.supports_color_temp:
            temp_range = self.max_color_temp_kelvin - self.min_color_temp_kelvin
            if temp_range <= 0:
                return self.min_color_temp_kelvin
            return self.min_color_temp_kelvin + int(percent * temp_range / 100)

        # Fallback to global defaults (2700-6500K)
        return percent_to_kelvin(percent)

    @property
    def fade_state(self) -> bool:
        """Get fade/transition state for light."""
        return self.get_bool_property(PROP_FADE_STATE)

    @property
    def gear_list(self) -> list[dict[str, int]]:
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
                result = json.loads(value)
            else:
                result = value
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
        return self.get_bool_property(PROP_SLEEP_AID_ENABLE)

    @property
    def wake_up_enabled(self) -> bool:
        """Check if wake up mode is enabled."""
        return self.get_bool_property(PROP_WAKE_UP_ENABLE)

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
        return self.get_bool_property(PROP_FOCUS_MODE)

    @property
    def body_reactive_enabled(self) -> bool:
        """Check if body reactive (motion sensing) is enabled."""
        return self.get_bool_property(PROP_BODY_REACTIVE)

    @property
    def has_floor_lamp_features(self) -> bool:
        """Check if device has floor lamp features."""
        return (
            PROP_FOCUS_MODE in self.properties or PROP_BODY_REACTIVE in self.properties
        )

    # Bedside Light properties (床头灯)
    @property
    def battery_level(self) -> int | None:
        """Get battery level (0-100), or None if not a battery device."""
        if PROP_BATTERY not in self.properties:
            return None
        return self.get_int_property(PROP_BATTERY, 0)

    @property
    def is_charging(self) -> bool:
        """Check if device is charging."""
        return self.get_bool_property(PROP_CHARGING)

    @property
    def has_battery(self) -> bool:
        """Check if device has battery."""
        return PROP_BATTERY in self.properties

    # Curtain properties
    @property
    def position(self) -> int:
        """Get curtain position (0-100)."""
        return self.get_int_property(PROP_POSITION, 0)

    @property
    def is_moving(self) -> bool:
        """Check if curtain is moving."""
        return self.get_bool_property(PROP_MOVING)

    @property
    def direction(self) -> str | None:
        """Get curtain movement direction."""
        direction = self.get_property(PROP_DIRECTION)
        if direction == "1":
            return "opening"
        if direction == "0":
            return "closing"
        return None

    # Fan properties
    @property
    def fan_is_on(self) -> bool:
        """Check if fan is on.

        Status query returns 'fanOnOff' (capital O), control uses 'fanOnoff'.
        """
        return self.get_bool_property(PROP_FAN_ONOFF) or self.get_bool_property(
            PROP_FAN_ONOFF_ALT
        )

    @property
    def fan_gear(self) -> int:
        """Get fan gear/speed (1-6)."""
        return self.get_int_property(PROP_FAN_GEAR, 1)

    @property
    def fan_mode(self) -> int:
        """Get fan mode (0=natural, 1=sleep, 2=normal)."""
        return self.get_int_property(PROP_FAN_MODE, 0)

    # Heater properties
    @property
    def heater_is_on(self) -> bool:
        """Check if heater is on."""
        return self.get_bool_property(PROP_HEATER_SWITCH)

    @property
    def heater_mode(self) -> int:
        """Get heater mode."""
        return self.get_int_property(PROP_HEATER_MODE, 0)

    @property
    def wind_gear(self) -> int:
        """Get wind gear."""
        return self.get_int_property(PROP_WIND_GEAR, 0)

    @property
    def light_mode(self) -> int:
        """Get light mode for heater."""
        return self.get_int_property(PROP_LIGHT_MODE, 0)

    @property
    def wind_direction_mode(self) -> int:
        """Get wind direction mode (1=auto, 2=fixed)."""
        return self.get_int_property(PROP_WIND_DIRECTION_MODE, 1)

    @property
    def aeration_gear(self) -> int:
        """Get aeration/ventilation gear (0=off, 1=strong, 2=weak)."""
        return self.get_int_property(PROP_AERATION_GEAR, 0)

    @property
    def aeration_is_on(self) -> bool:
        """Check if aeration/ventilation is on."""
        return self.aeration_gear > 0

    # Sensor properties
    @property
    def door_is_open(self) -> bool:
        """Check if door is open (door sensor)."""
        return self.get_bool_property(PROP_DOOR_OPEN)

    @property
    def is_activated(self) -> bool:
        """Check if motion detected (body sensor)."""
        return self.get_bool_property(PROP_ACTIVATED)

    @property
    def is_dark(self) -> bool:
        """Check if environment is dark."""
        return self.get_bool_property(PROP_DARK)

    @property
    def low_battery(self) -> bool:
        """Check if battery is low."""
        return self.get_bool_property(PROP_LOW_BATTERY)

    # =========================================================================
    # Network/Device Info Properties (诊断信息)
    # =========================================================================

    @property
    def ip_address(self) -> str | None:
        """Get device IP address."""
        return self.get_property(PROP_IP)

    @property
    def wifi_ssid(self) -> str | None:
        """Get connected WiFi SSID."""
        return self.get_property(PROP_WIFI_SSID)

    @property
    def wifi_rssi(self) -> int | None:
        """Get WiFi signal strength (RSSI in dBm)."""
        value = self.get_property(PROP_WIFI_RSSI)
        if value is None:
            return None
        try:
            return int(value)
        except (ValueError, TypeError):
            return None

    @property
    def net_type(self) -> str | None:
        """Get network type (e.g., 'wifi')."""
        return self.get_property(PROP_NET_TYPE)

    @property
    def mac_address(self) -> str | None:
        """Get device MAC address."""
        return self.get_property(PROP_MAC)

    @property
    def firmware_version(self) -> str | None:
        """Get device firmware version."""
        return self.get_property(PROP_VERSION)

    @property
    def latest_sync_timestamp(self) -> int | None:
        """Get latest sync timestamp (milliseconds)."""
        value = self.get_property(PROP_LATEST_SYNC_TIMESTAMP)
        if value is None:
            return None
        try:
            return int(value)
        except (ValueError, TypeError):
            return None

    # =========================================================================
    # Mesh Network Properties (Mesh 网络拓扑)
    # =========================================================================

    @property
    def mesh_address(self) -> int | None:
        """Get Mesh network address."""
        value = self.get_property(PROP_MESH_ADDRESS)
        if value is None:
            return None
        try:
            return int(value)
        except (ValueError, TypeError):
            return None

    @property
    def mesh_type(self) -> int | None:
        """Get Mesh device type (1=standard)."""
        value = self.get_property(PROP_MESH_TYPE)
        if value is None:
            return None
        try:
            return int(value)
        except (ValueError, TypeError):
            return None

    @property
    def is_mesh_gateway(self) -> bool:
        """Check if device is a Mesh gateway."""
        return self.get_bool_property(PROP_MESH_GATEWAY)

    @property
    def ble_mac(self) -> str | None:
        """Get BLE MAC address."""
        return self.get_property(PROP_BLE_MAC)

    def update_properties(self, properties: dict[str, Any]) -> None:
        """Update device properties.

        Args:
            properties: New properties to merge.

        """
        # Clear gear_list cache if gearList property is being updated
        if PROP_GEAR_LIST in properties:
            self._gear_list_cache = None

        self.properties.update(properties)
        # Update availability based on connection state
        if PROP_CONNECT_STATE in properties:
            self.available = self.is_connected

    @classmethod
    def from_api_data(cls, data: dict[str, Any]) -> LiproDevice:
        """Create a device from API response data.

        Args:
            data: Device data from API.

        Returns:
            LiproDevice instance.

        """
        return cls(
            device_id=data.get("deviceId", 0),
            serial=data.get("serial", ""),
            name=data.get("deviceName", "Unknown"),
            device_type=data.get("type", 1),
            iot_name=data.get("iotName", ""),
            room_id=data.get("roomId"),
            room_name=data.get("roomName"),
            is_group=data.get("isGroup", False) or data.get("group", False),
            product_id=data.get("productId"),
            physical_model=data.get("physicalModel"),
        )


def parse_properties_list(properties_list: list[dict[str, str]]) -> dict[str, Any]:
    """Parse properties list from API response.

    Args:
        properties_list: List of {key, value} dicts.

    Returns:
        Dictionary of property key-value pairs.

    """
    if not properties_list:
        return {}

    result = {}
    for prop in properties_list:
        key = prop.get("key")
        value = prop.get("value")
        if key:
            result[key] = value
    return result


def _record_unknown_device_type(
    physical_model: str | None,
    type_id: int,
    iot_name: str = "",
) -> None:
    """Record unknown device type for anonymous share.

    Args:
        physical_model: The physical model string.
        type_id: The numeric type ID.
        iot_name: The IoT name/model.

    """
    try:
        from .anonymous_share import get_anonymous_share_manager

        share_manager = get_anonymous_share_manager()
        share_manager.record_unknown_device_type(physical_model, type_id, iot_name)
    except (ImportError, AttributeError, RuntimeError):
        # Silently ignore if anonymous share module is not available
        _LOGGER.debug("Anonymous share not available for recording unknown device type")
