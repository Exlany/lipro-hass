"""Support helpers for the `DeviceExtras` family."""

from __future__ import annotations

import json
from typing import Any

_IOT_REMOTE_ID_PREFIX = "rmt_id_"
_IR_REMOTE_DEVICE_DRIVER_ID = "00000000"
_IR_REMOTE_GATEWAY_SERIAL_PREFIX = "rmt_id_appremote_realremote_"
_SWITCH_L_IOT_NAME = "21jd"


def load_json_list(value: object) -> list[Any]:
    """Parse one JSON string/list into a plain list."""
    if isinstance(value, list):
        return value
    if not isinstance(value, str) or not value.strip():
        return []
    try:
        parsed = json.loads(value)
    except (TypeError, ValueError):
        return []
    return parsed if isinstance(parsed, list) else []



def load_json_dict_list(value: object) -> list[dict[str, Any]]:
    """Parse one JSON string/list into a list of dictionaries."""
    return [row for row in load_json_list(value) if isinstance(row, dict)]



def panel_type_for_iot_name(iot_name: str) -> int:
    """Return panel type discriminator used by panel state commands."""
    return int(iot_name.casefold() == _SWITCH_L_IOT_NAME)


__all__ = [
    "_IOT_REMOTE_ID_PREFIX",
    "_IR_REMOTE_DEVICE_DRIVER_ID",
    "_IR_REMOTE_GATEWAY_SERIAL_PREFIX",
    "load_json_dict_list",
    "load_json_list",
    "panel_type_for_iot_name",
]
