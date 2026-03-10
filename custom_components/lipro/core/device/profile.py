"""Profile/type helpers for the thin ``LiproDevice`` facade."""

from __future__ import annotations

from ...const.api import DEFAULT_MAX_FAN_GEAR
from ...const.categories import DeviceCategory, get_platforms_for_category
from ...const.device_types import (
    DEVICE_TYPE_MAP,
    IOT_NAME_TO_DEFAULT_MAX_FAN_GEAR,
    IOT_NAME_TO_PHYSICAL_MODEL,
    PHYSICAL_MODEL_TO_DEVICE_TYPE,
)


def default_max_fan_gear_for_iot_name(iot_name: str) -> int:
    """Return device-model fan gear default for one IoT model name."""
    if not iot_name:
        return DEFAULT_MAX_FAN_GEAR
    value = IOT_NAME_TO_DEFAULT_MAX_FAN_GEAR.get(iot_name.lower())
    return value if isinstance(value, int) and value > 0 else DEFAULT_MAX_FAN_GEAR



def resolve_device_type_hex(
    *,
    device_type: int,
    iot_name: str,
    physical_model: str | None,
) -> str:
    """Resolve one device type hex using physical model first."""
    if physical_model and (resolved := PHYSICAL_MODEL_TO_DEVICE_TYPE.get(physical_model)):
        return resolved
    if iot_name:
        normalized = IOT_NAME_TO_PHYSICAL_MODEL.get(iot_name) or IOT_NAME_TO_PHYSICAL_MODEL.get(iot_name.lower())
        if normalized and (resolved := PHYSICAL_MODEL_TO_DEVICE_TYPE.get(normalized)):
            return resolved
    return DEVICE_TYPE_MAP.get(device_type, f"ff{device_type:06x}")



def resolve_platforms(category: DeviceCategory) -> list[str]:
    """Return Home Assistant platforms for one device category."""
    return get_platforms_for_category(category)


__all__ = [
    "default_max_fan_gear_for_iot_name",
    "resolve_device_type_hex",
    "resolve_platforms",
]
