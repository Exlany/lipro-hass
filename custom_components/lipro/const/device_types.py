"""Device type constants for the Lipro integration."""

from typing import Final

# Device type hex codes (used for API commands)
# These are the deviceType values sent in control commands
DEVICE_TYPE_LED: Final = "ff000001"
DEVICE_TYPE_CURTAIN: Final = "ff000002"
DEVICE_TYPE_PANEL: Final = "ff000003"
DEVICE_TYPE_FAN_LIGHT: Final = "ff000004"
DEVICE_TYPE_CEILING_LAMP: Final = "ff000005"
DEVICE_TYPE_OUTLET: Final = "ff000006"
DEVICE_TYPE_HEATER: Final = "ff000007"
DEVICE_TYPE_SENSOR_M1: Final = "ff000008"
DEVICE_TYPE_DESK_LAMP: Final = "ff000009"
DEVICE_TYPE_SENSOR_D1: Final = "ff00000a"
DEVICE_TYPE_GATEWAY: Final = "ff00000b"

# ============================================================================
# IMPORTANT: The 'type' field from API is Mesh protocol classification,
# NOT device function type! It is unreliable for determining device category.
#
# Examples from real API:
#   - type=1: Ceiling lamp (physicalModel="light")
#   - type=6: Light strip (physicalModel="light") - NOT outlet!
#   - type=9: Fan light (physicalModel="fanLight") - NOT desk lamp!
#
# ALWAYS use physicalModel field instead. This mapping is ONLY used as
# a last-resort fallback when physicalModel is not available.
# ============================================================================
DEVICE_TYPE_MAP: Final = {
    # These mappings are approximate and may not match actual device types
    # The 'type' field represents Mesh device classification, not function
    1: DEVICE_TYPE_LED,  # Ceiling lamps, general lights
    2: DEVICE_TYPE_CURTAIN,
    3: DEVICE_TYPE_PANEL,
    4: DEVICE_TYPE_LED,  # Downlights (single color temp)
    5: DEVICE_TYPE_LED,  # Spotlights (single color temp)
    6: DEVICE_TYPE_LED,  # Light strips (NOT outlet!)
    7: DEVICE_TYPE_HEATER,
    8: DEVICE_TYPE_SENSOR_M1,
    9: DEVICE_TYPE_FAN_LIGHT,  # Fan lights (NOT desk lamp!)
    10: DEVICE_TYPE_SENSOR_D1,
    11: DEVICE_TYPE_GATEWAY,
}

# Physical model to device type mapping
# physicalModel is the ONLY reliable source for determining device category
# The 'type' field is Mesh protocol classification, NOT device function type!
#
# DeviceModel.java enum values:
# - light: Downlight, ceiling light, light strip, etc.
# - fanLight: Fan light
# - curtain: Curtain
# - doorSensor: Door/window sensor
# - bodySensor: Motion sensor
# - heater: Heater/bathroom heater
# - gateway: Gateway
# - switch: Switch panel
# - outlet: Outlet
# - floorLight: Floor lamp/desk lamp (e.g., eye-care desk lamp)
# - irRemote: IR remote controller
PHYSICAL_MODEL_TO_DEVICE_TYPE: Final = {
    "light": DEVICE_TYPE_LED,  # Light devices
    "fanLight": DEVICE_TYPE_FAN_LIGHT,  # Fan light
    "curtain": DEVICE_TYPE_CURTAIN,  # Curtain
    "doorSensor": DEVICE_TYPE_SENSOR_D1,  # Door/window sensor
    "bodySensor": DEVICE_TYPE_SENSOR_M1,  # Motion sensor
    "heater": DEVICE_TYPE_HEATER,  # Heater/bathroom heater
    "gateway": DEVICE_TYPE_GATEWAY,  # Gateway
    "switch": DEVICE_TYPE_PANEL,  # Switch panel
    "outlet": DEVICE_TYPE_OUTLET,  # Outlet
    "floorLight": DEVICE_TYPE_DESK_LAMP,  # Floor lamp/desk lamp
    "irRemote": DEVICE_TYPE_GATEWAY,  # IR remote (not supported, mapped to gateway)
}

# iotName -> phyModel mapping from App's res/raw/device_models.txt (v2.24.3)
# Used as fallback when API doesn't return physicalModel field
# Note: iotName matching is case-insensitive (normalized to lowercase in coordinator)
IOT_NAME_TO_PHYSICAL_MODEL: Final = {
    # light - ceiling lamps (吸顶灯)
    "T2G2": "light",
    "T2T3": "light",
    "21O2": "light",
    "21Q1": "light",
    "T2T2": "light",
    "21G2": "light",
    "21O1": "light",
    "T2P8": "light",
    "22Q1": "light",
    "21A1": "light",
    "20X1": "light",  # 客厅吸顶灯E2 Max
    "23x1": "light",  # 客厅吸顶灯E2
    "23x2": "light",  # 客厅吸顶灯E2 Pro
    "23x3": "light",  # 卧室吸顶灯E2
    "24x1": "light",  # 智能吸顶灯A1 Pro
    "24x2": "light",  # 客厅吸顶灯A1 Pro
    "24x3": "light",  # 智能吸顶灯A1 Air
    "24x4": "light",  # 客厅吸顶灯E2S Pro
    # light - downlights/spotlights (筒灯/射灯)
    "T2P4": "light",
    "T2P5": "light",
    "T2P6": "light",
    "T2P3": "light",
    "T2PA": "light",
    "T2PB": "light",
    "T2PC": "light",
    "T2PD": "light",
    "r3p3": "light",  # 筒灯/射灯 E2 Pro
    "r3p5": "light",  # 灯带 E Pro
    "r4t2": "light",  # 明装筒灯E2 Pro
    # light - track lights (磁吸轨道灯)
    "r3g2": "light",  # 磁吸轨道灯 S 系列 (射灯/线条灯/格栅灯)
    "r3g3": "light",  # 磁吸轨道灯单色温系列
    # light - pendant lamps (吊灯)
    "T2S2": "light",
    "21P3": "light",
    "21P1": "light",
    "21P2": "light",
    "21G1": "light",
    "22Z1": "light",
    "23T2": "light",
    "24a2": "light",  # 护眼餐厅吊灯
    "25A1": "light",  # 护眼餐厅吊灯 Ultra
    # light - panel lights (面板灯)
    "E3B1": "light",
    "e4b1": "light",  # 面板灯 Pro
    # light - floor lamps (落地灯)
    "e4z3": "light",  # 护眼落地灯 Max (also supports floorLight features)
    # fanLight (风扇灯)
    "21F1": "fanLight",
    "23f4": "fanLight",  # 智能风扇灯E2 Pro
    # switch (开关面板)
    "21J8": "switch",
    "21JD": "switch",
    # outlet (插座)
    "21J9": "outlet",
    # curtain (窗帘)
    "21L1": "curtain",
    # sensor (传感器)
    "22N1": "doorSensor",
    "T2N2": "bodySensor",
    # heater (浴霸)
    "E3U1": "heater",
    "e3u1": "heater",  # 柔风浴霸E2 Pro (lowercase variant)
    # gateway (网关)
    "M2W1": "gateway",
}

# Model-level default fan gear upper-bounds.
# Used when product config does not provide maxFanGear.
# Keys are normalized lowercase iotName values.
IOT_NAME_TO_DEFAULT_MAX_FAN_GEAR: Final = {
    "21f1": 10,  # 智能风扇灯 E2 Max
    "23f4": 10,  # 智能风扇灯 E2 Pro
}
