"""Immutable identity snapshot for one Lipro device."""

from __future__ import annotations

from collections.abc import Mapping
from dataclasses import dataclass


@dataclass(frozen=True)
class DeviceIdentity:
    """Immutable device identity fields extracted from API payloads."""

    device_number: int
    serial: str
    name: str
    device_type: int
    iot_name: str
    room_id: int | None = None
    room_name: str | None = None
    product_id: int | None = None
    physical_model: str | None = None

    @classmethod
    def from_api_data(cls, data: Mapping[str, object]) -> DeviceIdentity:
        """Build an immutable identity snapshot from one API payload."""
        return cls(
            device_number=_coerce_int(data.get("deviceId"), default=0),
            serial=_coerce_str(data.get("serial"), default=""),
            name=_coerce_str(data.get("deviceName"), default="Unknown"),
            device_type=_coerce_int(data.get("type"), default=1),
            iot_name=_coerce_str(data.get("iotName"), default=""),
            room_id=_coerce_optional_int(data.get("roomId")),
            room_name=_coerce_optional_str(data.get("roomName")),
            product_id=_coerce_optional_int(data.get("productId")),
            physical_model=_coerce_optional_str(data.get("physicalModel")),
        )


def _coerce_int(value: object, *, default: int) -> int:
    """Return an integer field value or a safe default."""
    if isinstance(value, bool):
        return default
    if isinstance(value, int):
        return value
    if isinstance(value, float) and value.is_integer():
        return int(value)
    if isinstance(value, str):
        normalized = value.strip()
        if normalized.lstrip("-").isdigit():
            return int(normalized)
    return default


def _coerce_optional_int(value: object) -> int | None:
    """Return an optional integer field when the payload carries one."""
    if value is None:
        return None
    return _coerce_int(value, default=0)


def _coerce_str(value: object, *, default: str) -> str:
    """Return a string field value or a safe default."""
    return value if isinstance(value, str) else default


def _coerce_optional_str(value: object) -> str | None:
    """Return an optional string field when the payload carries one."""
    return value if isinstance(value, str) else None


__all__ = ["DeviceIdentity"]
