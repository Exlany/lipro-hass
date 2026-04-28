"""Identifier normalization helpers shared across core modules."""

from __future__ import annotations

import re
from typing import Any, Final

from ...const.base import IOT_DEVICE_ID_PREFIX

_IOT_DEVICE_ID_PATTERN: Final = re.compile(
    rf"^{re.escape(IOT_DEVICE_ID_PREFIX)}[0-9a-f]{{12}}$",
    re.IGNORECASE,
)
_MESH_GROUP_ID_PREFIX: Final = "mesh_group_"
_MESH_GROUP_ID_PATTERN: Final = re.compile(r"^mesh_group_\d+$")


def normalize_iot_device_id(device_id: Any) -> str | None:
    """Normalize and validate IoT device IDs.

    Returns canonical lowercase ID if valid, otherwise ``None``.
    """
    if not isinstance(device_id, str):
        return None
    normalized = device_id.strip().lower()
    if not normalized:
        return None
    if not _IOT_DEVICE_ID_PATTERN.fullmatch(normalized):
        return None
    return normalized


def is_valid_iot_device_id(device_id: str) -> bool:
    """Return True when ``device_id`` matches the expected IoT ID pattern."""
    return bool(_IOT_DEVICE_ID_PATTERN.fullmatch(device_id))


def is_mesh_group_id_prefix(identifier: Any) -> bool:
    """Return True when ``identifier`` looks like a mesh-group serial/id."""
    return isinstance(identifier, str) and identifier.strip().lower().startswith(
        _MESH_GROUP_ID_PREFIX
    )


def normalize_mesh_group_id(group_id: Any) -> str | None:
    """Normalize and validate mesh group IDs.

    Returns a stripped ID if valid, otherwise ``None``.
    """
    if not isinstance(group_id, str):
        return None
    normalized = group_id.strip()
    if not normalized:
        return None
    if not _MESH_GROUP_ID_PATTERN.fullmatch(normalized):
        return None
    return normalized


def is_valid_mesh_group_id(group_id: str) -> bool:
    """Return True when ``group_id`` matches the expected mesh-group pattern."""
    return bool(_MESH_GROUP_ID_PATTERN.fullmatch(group_id))
