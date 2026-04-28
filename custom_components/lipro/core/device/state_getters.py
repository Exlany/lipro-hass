"""Low-level property getters for `DeviceState`."""

from __future__ import annotations

import logging
from typing import TYPE_CHECKING, Any

from ..utils.coerce import coerce_boollike

if TYPE_CHECKING:
    from .state import DeviceState

_LOGGER = logging.getLogger(__name__)


def get_property(self: DeviceState, key: str, default: Any = None) -> Any:
    """Return one raw property value."""
    return self.properties.get(key, default)


def get_bool_property(self: DeviceState, key: str, default: bool = False) -> bool:
    """Return one boolean-like property value."""
    value = self.properties.get(key)
    if value is None:
        return default
    if isinstance(value, (bool, int, float, str)):
        return coerce_boollike(value, logger=_LOGGER, context="API")
    return bool(value)


def get_int_property(self: DeviceState, key: str, default: int = 0) -> int:
    """Return one integer property value."""
    try:
        return int(self.properties.get(key, default))
    except TypeError, ValueError:
        return default


def get_float_property(self: DeviceState, key: str, default: float = 0.0) -> float:
    """Return one float property value."""
    try:
        return float(self.properties.get(key, default))
    except TypeError, ValueError:
        return default


def get_optional_int_property(self: DeviceState, key: str) -> int | None:
    """Return one optional integer property value."""
    value = self.properties.get(key)
    if value is None:
        return None
    try:
        return int(value)
    except TypeError, ValueError:
        return None


def get_str_property(self: DeviceState, key: str) -> str | None:
    """Return one string property value when present."""
    value = self.properties.get(key)
    return None if value is None else str(value)


__all__ = [
    "get_bool_property",
    "get_float_property",
    "get_int_property",
    "get_optional_int_property",
    "get_property",
    "get_str_property",
]
