"""Parsed payload accessors for ``DeviceExtras``."""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

from ...const.properties import (
    PROP_GEAR_LIST,
    PROP_LAST_GEAR_INDEX,
    PROP_PANEL_INFO,
    PROP_RC_LIST,
)
from .extras_support import load_json_dict_list, load_json_list

if TYPE_CHECKING:
    from .extras import DeviceExtras


def gear_list(self: DeviceExtras) -> list[Any]:
    """Return parsed gear-list presets."""
    if self._gear_list_cache is None:
        self._gear_list_cache = load_json_list(self._properties.get(PROP_GEAR_LIST))
    return self._gear_list_cache


def last_gear_index(self: DeviceExtras) -> int:
    """Return last selected preset index."""
    try:
        return int(self._properties.get(PROP_LAST_GEAR_INDEX, -1))
    except TypeError, ValueError:
        return -1


def has_gear_presets(self: DeviceExtras) -> bool:
    """Return whether gear-list presets exist."""
    return bool(self.gear_list)


def panel_info(self: DeviceExtras) -> list[dict[str, Any]]:
    """Return parsed panel binding metadata."""
    return load_json_dict_list(self._properties.get(PROP_PANEL_INFO))


def rc_list(self: DeviceExtras) -> list[dict[str, Any]]:
    """Return parsed IR remote binding rows."""
    return load_json_dict_list(self._properties.get(PROP_RC_LIST))


__all__ = [
    "gear_list",
    "has_gear_presets",
    "last_gear_index",
    "panel_info",
    "rc_list",
]
