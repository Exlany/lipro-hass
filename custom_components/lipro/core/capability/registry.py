"""Canonical capability registry for Lipro device projections."""

from __future__ import annotations

from typing import TYPE_CHECKING

from ...const.categories import get_device_category
from .models import CapabilitySnapshot

if TYPE_CHECKING:
    from ..device.device import LiproDevice


def _positive_int(value: int, *, default: int) -> int:
    """Return a positive integer or the provided default."""
    return value if isinstance(value, int) and value > 0 else default


class CapabilityRegistry:
    """Build canonical capability snapshots from device metadata."""

    @classmethod
    def from_device(cls, device: LiproDevice) -> CapabilitySnapshot:
        """Build one snapshot from a live device aggregate."""
        return cls.from_device_profile(
            device_type_hex=device.device_type_hex,
            min_color_temp_kelvin=device.min_color_temp_kelvin,
            max_color_temp_kelvin=device.max_color_temp_kelvin,
            max_fan_gear=device.max_fan_gear,
        )

    @classmethod
    def from_device_profile(
        cls,
        *,
        device_type_hex: str,
        min_color_temp_kelvin: int,
        max_color_temp_kelvin: int,
        max_fan_gear: int = 1,
    ) -> CapabilitySnapshot:
        """Build one snapshot from normalized device profile metadata."""
        normalized_type = device_type_hex.lower()
        normalized_min = _positive_int(min_color_temp_kelvin, default=0)
        normalized_max = _positive_int(max_color_temp_kelvin, default=0)
        category = get_device_category(normalized_type)
        return CapabilitySnapshot(
            device_type_hex=normalized_type,
            category=category,
            supports_color_temp=normalized_min > 0 and normalized_max > 0,
            max_fan_gear=_positive_int(max_fan_gear, default=1),
            min_color_temp_kelvin=normalized_min,
            max_color_temp_kelvin=normalized_max,
        )

    @classmethod
    def from_device_type(cls, device_type_hex: str) -> CapabilitySnapshot:
        """Build one snapshot when only device type metadata is available."""
        return cls.from_device_profile(
            device_type_hex=device_type_hex,
            min_color_temp_kelvin=0,
            max_color_temp_kelvin=0,
        )


__all__ = ['CapabilityRegistry']
