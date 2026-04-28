"""Derived feature flags for ``DeviceExtras``."""

from __future__ import annotations

from typing import TYPE_CHECKING

from ...const.properties import (
    PROP_BODY_REACTIVE,
    PROP_FOCUS_MODE,
    PROP_IR_SWITCH,
    PROP_IS_SUPPORT_IR_SWITCH,
    PROP_SLEEP_AID_ENABLE,
    PROP_WAKE_UP_ENABLE,
)
from ..utils.coerce import coerce_boollike
from ..utils.identifiers import is_valid_iot_device_id, normalize_iot_device_id
from .extras_support import (
    _IOT_REMOTE_ID_PREFIX,
    _IR_REMOTE_DEVICE_DRIVER_ID,
    _IR_REMOTE_GATEWAY_SERIAL_PREFIX,
    panel_type_for_iot_name,
)

if TYPE_CHECKING:
    from .extras import DeviceExtras


def has_sleep_wake_features(self: DeviceExtras) -> bool:
    """Return whether sleep/wake automation keys are present."""
    return any(
        key in self._properties for key in (PROP_SLEEP_AID_ENABLE, PROP_WAKE_UP_ENABLE)
    )


def has_floor_lamp_features(self: DeviceExtras) -> bool:
    """Return whether floor-lamp specific feature keys are present."""
    return any(key in self._properties for key in (PROP_FOCUS_MODE, PROP_BODY_REACTIVE))


def is_ir_remote_device(self: DeviceExtras) -> bool:
    """Return whether this device represents an IR remote facade."""
    value = self._extra_data.get("is_ir_remote")
    if isinstance(value, bool):
        return value
    if isinstance(value, (int, str)):
        return coerce_boollike(value, context="DeviceExtras")
    return self._physical_model == "irRemote" or self._serial.startswith(
        _IR_REMOTE_GATEWAY_SERIAL_PREFIX
    )


def ir_remote_gateway_device_id(self: DeviceExtras) -> str | None:
    """Return the parent IR gateway device id when it can be resolved."""
    if self._serial.startswith(_IR_REMOTE_GATEWAY_SERIAL_PREFIX):
        gateway_id = self._serial.removeprefix(_IR_REMOTE_GATEWAY_SERIAL_PREFIX)
        return gateway_id if is_valid_iot_device_id(gateway_id) else None
    if not self.is_ir_remote_device:
        return None
    for row in self.rc_list:
        remote_id = str(row.get("driverId") or row.get("deviceId") or "").strip()
        if remote_id == _IR_REMOTE_DEVICE_DRIVER_ID:
            gateway_id = str(row.get("iotId") or row.get("id") or "").strip()
            if is_valid_iot_device_id(gateway_id):
                return gateway_id
        if remote_id.startswith(_IOT_REMOTE_ID_PREFIX):
            gateway_id = remote_id.removeprefix(_IOT_REMOTE_ID_PREFIX)
            if is_valid_iot_device_id(gateway_id):
                return gateway_id
    return None


def mesh_gateway_device_id(self: DeviceExtras) -> str | None:
    """Return the mesh gateway device id when learned from group status."""
    return normalize_iot_device_id(self._extra_data.get("gateway_device_id"))


def mesh_group_member_ids(self: DeviceExtras) -> list[str]:
    """Return normalized mesh-group member ids learned from group status."""
    raw_member_ids = self._extra_data.get("group_member_ids")
    if not isinstance(raw_member_ids, list):
        return []

    member_ids: list[str] = []
    seen: set[str] = set()
    for member_id in raw_member_ids:
        normalized = normalize_iot_device_id(member_id)
        if normalized is None or normalized in seen:
            continue
        seen.add(normalized)
        member_ids.append(normalized)
    return member_ids


def diagnostic_gateway_projection(self: DeviceExtras) -> dict[str, object] | None:
    """Return the explicit diagnostics projection for gateway/member topology."""
    gateway_device_id = mesh_gateway_device_id(self) or ir_remote_gateway_device_id(
        self
    )
    group_member_ids = mesh_group_member_ids(self)
    if gateway_device_id is None and not group_member_ids:
        return None

    projection: dict[str, object] = {}
    if gateway_device_id is not None:
        projection["gateway_device_id"] = gateway_device_id
    if group_member_ids:
        projection["group_member_ids"] = group_member_ids
    return projection


def supports_ir_switch(self: DeviceExtras) -> bool:
    """Return whether IR switch capability should be exposed."""
    if PROP_IS_SUPPORT_IR_SWITCH in self._properties:
        return coerce_boollike(
            self._properties.get(PROP_IS_SUPPORT_IR_SWITCH),
            context="DeviceExtras",
        )
    return self.is_ir_remote_device or PROP_IR_SWITCH in self._properties


def panel_type(self: DeviceExtras) -> int:
    """Return panel type discriminator used by panel state commands."""
    return panel_type_for_iot_name(self._iot_name)


__all__ = [
    "diagnostic_gateway_projection",
    "has_floor_lamp_features",
    "has_sleep_wake_features",
    "ir_remote_gateway_device_id",
    "is_ir_remote_device",
    "mesh_gateway_device_id",
    "mesh_group_member_ids",
    "panel_type",
    "supports_ir_switch",
]
