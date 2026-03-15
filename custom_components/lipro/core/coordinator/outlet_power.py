"""Outlet power status update helpers."""

from __future__ import annotations

from typing import TYPE_CHECKING

from ..api import LiproApiError, LiproAuthError, LiproConnectionError
from .types import PropertyDict

if TYPE_CHECKING:
    from ..device.device import LiproDevice


def should_reraise_outlet_power_error(err: LiproApiError) -> bool:
    """Return True when outlet-power query errors must bubble up."""
    return isinstance(err, (LiproAuthError, LiproConnectionError))


def apply_outlet_power_info(
    device: LiproDevice | None,
    power_data: PropertyDict,
) -> bool:
    """Write outlet power payload to the formal device primitive when possible."""
    if device is None or not power_data:
        return False
    device.outlet_power_info = dict(power_data)
    return device.outlet_power_info is not None
