"""Compatibility bridge for the formal capability model."""

from __future__ import annotations

from typing import TYPE_CHECKING

from ..capability import CapabilityRegistry, CapabilitySnapshot

if TYPE_CHECKING:
    from .device import LiproDevice


class DeviceCapabilities(CapabilitySnapshot):
    """Backward-compatible capability snapshot exported by `core.device`."""

    __slots__ = ()

    @classmethod
    def from_snapshot(cls, snapshot: CapabilitySnapshot) -> DeviceCapabilities:
        """Build a compatibility snapshot from the canonical capability model."""
        return cls(
            device_type_hex=snapshot.device_type_hex,
            category=snapshot.category,
            platforms=snapshot.platforms,
            supports_color_temp=snapshot.supports_color_temp,
            max_fan_gear=snapshot.max_fan_gear,
            min_color_temp_kelvin=snapshot.min_color_temp_kelvin,
            max_color_temp_kelvin=snapshot.max_color_temp_kelvin,
        )

    @classmethod
    def from_device_profile(
        cls,
        *,
        device_type_hex: str,
        min_color_temp_kelvin: int,
        max_color_temp_kelvin: int,
        max_fan_gear: int = 1,
    ) -> DeviceCapabilities:
        """Build a compatibility snapshot from profile metadata."""
        return cls.from_snapshot(
            CapabilityRegistry.from_device_profile(
                device_type_hex=device_type_hex,
                min_color_temp_kelvin=min_color_temp_kelvin,
                max_color_temp_kelvin=max_color_temp_kelvin,
                max_fan_gear=max_fan_gear,
            )
        )

    @classmethod
    def from_device_type(cls, device_type_hex: str) -> DeviceCapabilities:
        """Build a compatibility snapshot when only the type hex is known."""
        return cls.from_snapshot(CapabilityRegistry.from_device_type(device_type_hex))

    @classmethod
    def from_device(cls, device: LiproDevice) -> DeviceCapabilities:
        """Build a compatibility snapshot from a live device aggregate."""
        return cls.from_snapshot(CapabilityRegistry.from_device(device))


__all__ = ["DeviceCapabilities"]
