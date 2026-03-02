"""Outlet power status update helpers."""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

from ..api import LiproApiError, LiproAuthError, LiproConnectionError

if TYPE_CHECKING:
    from . import LiproDevice


def should_reraise_outlet_power_error(err: LiproApiError) -> bool:
    """Return True when outlet-power query errors must bubble up."""
    return isinstance(err, (LiproAuthError, LiproConnectionError))


def apply_outlet_power_info(
    device: LiproDevice | None,
    power_data: dict[str, Any],
) -> bool:
    """Write outlet power payload to runtime model when possible."""
    if device is None or not power_data:
        return False
    device.extra_data["power_info"] = power_data
    return True
