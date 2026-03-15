"""Factory helpers for constructing ``LiproDevice`` instances."""

from __future__ import annotations

from typing import TYPE_CHECKING, Any, TypeVar

from ...const.device_types import PHYSICAL_MODEL_TO_DEVICE_TYPE
from ..utils.coerce import coerce_boollike
from ..utils.identifiers import is_valid_iot_device_id, is_valid_mesh_group_id
from .identity import DeviceIdentity
from .profile import default_max_fan_gear_for_iot_name

if TYPE_CHECKING:
    from .device import LiproDevice

LiproDeviceT = TypeVar("LiproDeviceT", bound="LiproDevice")


def has_unknown_physical_model(physical_model: str | None) -> bool:
    """Return whether a physical model is present but unknown to mappings."""
    return bool(physical_model and physical_model not in PHYSICAL_MODEL_TO_DEVICE_TYPE)


def has_valid_iot_id(serial: str, *, is_group: bool) -> bool:
    """Return whether the serial is a valid device or mesh-group id."""
    if is_group:
        return is_valid_mesh_group_id(serial)
    return is_valid_iot_device_id(serial)


def build_device_from_api_data(
    cls: type[LiproDeviceT],
    data: dict[str, Any],
) -> LiproDeviceT:
    """Build one device facade from a raw API payload."""
    identity = DeviceIdentity.from_api_data(data)
    is_group = coerce_boollike(
        data.get("isGroup", False),
        context="API",
    ) or coerce_boollike(data.get("group", False), context="API")
    extra_data: dict[str, object] = (
        {"is_ir_remote": coerce_boollike(data.get("isIrRemote"), context="API")}
        if "isIrRemote" in data
        else {}
    )
    default_max_fan_gear = default_max_fan_gear_for_iot_name(identity.iot_name)
    return cls(
        device_number=identity.device_number,
        serial=identity.serial,
        name=identity.name,
        device_type=identity.device_type,
        iot_name=identity.iot_name,
        room_id=identity.room_id,
        room_name=identity.room_name,
        is_group=is_group,
        product_id=identity.product_id,
        physical_model=identity.physical_model,
        default_max_fan_gear_in_model=default_max_fan_gear,
        max_fan_gear=default_max_fan_gear,
        extra_data=extra_data,
    )


__all__ = [
    "build_device_from_api_data",
    "has_unknown_physical_model",
    "has_valid_iot_id",
]
