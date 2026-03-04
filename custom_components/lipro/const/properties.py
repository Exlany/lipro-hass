"""Command and property constants for the Lipro integration."""

from typing import Final

# Commands
CMD_POWER_ON: Final = "POWER_ON"
CMD_POWER_OFF: Final = "POWER_OFF"
CMD_CHANGE_STATE: Final = "CHANGE_STATE"
CMD_CURTAIN_OPEN: Final = "CURTAIN_OPEN"
CMD_CURTAIN_CLOSE: Final = "CURTAIN_CLOSE"
CMD_CURTAIN_STOP: Final = "CURTAIN_STOP"

# Property keys - Common
PROP_POWER_STATE: Final = "powerState"
PROP_CONNECT_STATE: Final = "connectState"

# Property keys - Light
PROP_BRIGHTNESS: Final = "brightness"
PROP_TEMPERATURE: Final = "temperature"
PROP_FADE_STATE: Final = "fadeState"
PROP_GEAR_LIST: Final = "gearList"
PROP_LAST_GEAR_INDEX: Final = "lastGearIndex"

# Property keys - Natural Light (自然光灯 助眠/唤醒)
PROP_SLEEP_AID_ENABLE: Final = "sleepAidEnable"
PROP_WAKE_UP_ENABLE: Final = "wakeUpEnable"

# Property keys - Floor Lamp (落地灯)
PROP_FOCUS_MODE: Final = "focusMode"
PROP_BODY_REACTIVE: Final = "bodyReactive"

# Property keys - Bedside Light (床头灯)
PROP_BATTERY: Final = "battery"
PROP_CHARGING: Final = "charging"

# Property keys - Curtain
PROP_POSITION: Final = "position"
PROP_MOVING: Final = "moving"
PROP_DIRECTION: Final = "direction"

# Property keys - Fan
PROP_FAN_ONOFF: Final = "fanOnoff"
PROP_FAN_GEAR: Final = "fanGear"
PROP_FAN_MODE: Final = "fanMode"

# Property keys - Heater
PROP_HEATER_SWITCH: Final = "heaterSwitch"
PROP_HEATER_MODE: Final = "heaterMode"
PROP_WIND_GEAR: Final = "windGear"
PROP_LIGHT_MODE: Final = "lightMode"
PROP_AERATION_GEAR: Final = "aerationGear"
PROP_WIND_DIRECTION_MODE: Final = "windDirectionMode"

# Property keys - Sensor
PROP_DOOR_OPEN: Final = "doorOpen"
PROP_ACTIVATED: Final = "human"
PROP_DARK: Final = "dark"
PROP_LOW_BATTERY: Final = "lowBattery"

# Property keys - Network/Device Info (诊断信息)
PROP_IP: Final = "ip"
PROP_WIFI_SSID: Final = "wifi_ssid"
PROP_WIFI_RSSI: Final = "wifi_rssi"
PROP_NET_TYPE: Final = "net_type"
PROP_MAC: Final = "mac"
PROP_VERSION: Final = "version"

# Property keys - Mesh Network (Mesh 网络拓扑)
PROP_MESH_ADDRESS: Final = "address"
PROP_MESH_TYPE: Final = "meshType"
PROP_MESH_GATEWAY: Final = "gateway"
PROP_BLE_MAC: Final = "bleMac"

# Property keys - Metadata (元数据)
PROP_LATEST_SYNC_TIMESTAMP: Final = "latestSyncTimestamp"

# Fan modes
# Runtime/App semantics:
# 0 = 直吹风 (direct), 1 = 自然风 (natural), 2 = 循环风 (cycle), 3 = 柔风 (gentle wind)
FAN_MODE_DIRECT: Final = 0
FAN_MODE_NATURAL: Final = 1
FAN_MODE_CYCLE: Final = 2
FAN_MODE_GENTLE_WIND: Final = 3

# Heater modes
HEATER_MODE_DEFAULT: Final = 0
HEATER_MODE_DEMIST: Final = 1
HEATER_MODE_DRY: Final = 2
HEATER_MODE_GENTLE_WIND: Final = 3

# Light modes for heater
HEATER_LIGHT_OFF: Final = 0
HEATER_LIGHT_MAIN: Final = 1
HEATER_LIGHT_NIGHT: Final = 2

# Aeration (ventilation) gear for heater/bathroom heater
AERATION_OFF: Final = 0
AERATION_STRONG: Final = 1
AERATION_WEAK: Final = 2

# Wind direction modes for heater
WIND_DIRECTION_AUTO: Final = 1
WIND_DIRECTION_FIX: Final = 2

# Color temperature range (Kelvin) - DEFAULT fallback values
# Note: Actual device ranges vary by product (e.g., 3000-4000K, 3000-5000K)
# Device-specific ranges are loaded from product configs and stored in
# device.min_color_temp_kelvin / device.max_color_temp_kelvin
MIN_COLOR_TEMP_KELVIN: Final = 2700
MAX_COLOR_TEMP_KELVIN: Final = 6500
COLOR_TEMP_RANGE: Final = MAX_COLOR_TEMP_KELVIN - MIN_COLOR_TEMP_KELVIN  # 3800


def percent_to_kelvin(percent: int) -> int:
    """Convert API temperature percentage (0-100) to Kelvin (2700-6500).

    API uses 0=warmest(2700K), 100=coolest(6500K).
    Input is clamped to 0-100 range.
    """
    percent = max(0, min(100, percent))
    return MIN_COLOR_TEMP_KELVIN + int(percent * COLOR_TEMP_RANGE / 100)


def kelvin_to_percent(kelvin: int) -> int:
    """Convert Kelvin (2700-6500) to API temperature percentage (0-100).

    Input is clamped to valid Kelvin range, output is clamped to 0-100.
    """
    kelvin = max(MIN_COLOR_TEMP_KELVIN, min(MAX_COLOR_TEMP_KELVIN, kelvin))
    return max(
        0, min(100, round((kelvin - MIN_COLOR_TEMP_KELVIN) * 100 / COLOR_TEMP_RANGE))
    )


# Curtain direction values (from API)
DIRECTION_OPENING: Final = "1"
DIRECTION_CLOSING: Final = "0"

# Default color temperature percentage when property is missing
# 34% ≈ 4000K on the default 2700-6500K range (neutral white)
DEFAULT_COLOR_TEMP_PERCENT: Final = 34

# Brightness range
MIN_BRIGHTNESS: Final = 1
MAX_BRIGHTNESS: Final = 100
