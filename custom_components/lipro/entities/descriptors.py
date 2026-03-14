"""Generic descriptors for declarative entity property definitions.

This module provides type-safe descriptors that eliminate boilerplate property
getters in entity classes. Descriptors automatically read from device state
and support optional transformations.

Key features:
- Full mypy type safety via Generic[T] + @overload
- Automatic unit conversions (0-100 → 0-255 for brightness)
- Conditional attributes (only when capability snapshot declares support)
- Zero runtime overhead compared to manual properties
"""

from __future__ import annotations

from collections.abc import Callable
from typing import TYPE_CHECKING, Any, Generic, TypeVar, overload

if TYPE_CHECKING:
    from typing import Self

    from .base import LiproEntity

T = TypeVar("T")


def _resolve_attr_path(source: object, path: str) -> object:
    """Resolve one dotted attribute path from the given source object."""
    value = source
    for part in path.split("."):
        value = getattr(value, part)
    return value


class DeviceAttr(Generic[T]):
    """Generic descriptor for reading device attributes with optional transformation.

    Type-safe descriptor that reads from device state and optionally transforms
    the value. Uses @overload to ensure mypy correctly infers the return type.

    Examples:
        class LiproLight(LiproEntity, LightEntity):
            is_on = DeviceAttr[bool]("state.is_on")
            brightness = DeviceAttr[int]("state.brightness", transform=lambda x: int(x * 2.55))

    Args:
        attr: Device attribute path (e.g., "state.is_on", "state.brightness")
        transform: Optional transformation function applied to the value
    """

    def __init__(
        self,
        attr: str,
        *,
        transform: Callable[[Any], T] | None = None,
    ) -> None:
        """Initialize device attribute descriptor.

        Args:
            attr: Attribute path on device (supports dot notation)
            transform: Optional transformation function
        """
        self.attr = attr
        self.transform = transform
        self.name: str = ""  # Set by __set_name__

    def __set_name__(self, owner: type, name: str) -> None:
        """Store the attribute name when descriptor is assigned to class."""
        self.name = name

    @overload
    def __get__(self, obj: None, objtype: type) -> Self: ...

    @overload
    def __get__(self, obj: LiproEntity, objtype: type | None = None) -> T: ...

    def __get__(self, obj: LiproEntity | None, objtype: type | None = None) -> T | Self:
        """Get attribute value from device with optional transformation.

        Args:
            obj: Entity instance (None for class access)
            objtype: Owner class type

        Returns:
            Descriptor itself for class access, transformed value for instance access
        """
        if obj is None:
            return self

        value = _resolve_attr_path(obj.device, self.attr)
        if self.transform is not None:
            return self.transform(value)
        return value  # type: ignore[return-value]


class ScaledBrightness(DeviceAttr[int | None]):
    """Brightness descriptor with automatic 0-100 → 0-255 scaling.

    Converts device brightness (0-100 percent) to Home Assistant brightness
    (0-255 scale) with proper clamping.

    Example:
        class LiproLight(LiproEntity, LightEntity):
            brightness = ScaledBrightness()  # Reads from device.state.brightness
    """

    def __init__(self, attr: str = "state.brightness") -> None:
        """Initialize scaled brightness descriptor.

        Args:
            attr: Device attribute path (default: "state.brightness")
        """

        def scale_brightness(value: int) -> int:
            """Scale 0-100 to 0-255 with clamping."""
            clamped = max(0, min(100, value))
            return round(clamped * 255 / 100)

        super().__init__(attr, transform=scale_brightness)


class ConditionalAttr(DeviceAttr[T | None]):
    """Conditional descriptor that returns None when device lacks capability.

    Only returns the attribute value when the specified capability snapshot path
    evaluates to truthy. Otherwise returns None, allowing HA to hide unsupported
    features.

    Example:
        class LiproLight(LiproEntity, LightEntity):
            color_temp_kelvin = ConditionalAttr[int](
                "color_temp",
                capability="capabilities.supports_color_temp"
            )
    """

    def __init__(
        self,
        attr: str,
        *,
        capability: str,
        transform: Callable[[Any], T] | None = None,
    ) -> None:
        """Initialize conditional attribute descriptor.

        Args:
            attr: Device attribute path
            capability: Capability snapshot path to check
            transform: Optional transformation function
        """
        super().__init__(attr, transform=transform)
        self.capability = capability

    @overload
    def __get__(self, obj: None, objtype: type) -> Self: ...

    @overload
    def __get__(self, obj: LiproEntity, objtype: type | None = None) -> T | None: ...

    def __get__(
        self, obj: LiproEntity | None, objtype: type | None = None
    ) -> T | None | Self:
        """Get attribute value only if device has capability.

        Args:
            obj: Entity instance (None for class access)
            objtype: Owner class type

        Returns:
            Descriptor for class access, value if capability exists, None otherwise
        """
        if obj is None:
            return self

        if not _resolve_attr_path(obj, self.capability):
            return None

        return super().__get__(obj, objtype)


class KelvinToPercent(DeviceAttr[int]):
    """Color temperature descriptor with automatic kelvin → percent conversion.

    Converts device color temperature (kelvin) to Home Assistant percentage
    using device-specific min/max kelvin range.

    Example:
        class LiproLight(LiproEntity, LightEntity):
            color_temp = KelvinToPercent("color_temp_kelvin")
    """

    def __init__(self, attr: str = "color_temp") -> None:
        """Initialize kelvin-to-percent descriptor.

        Args:
            attr: Device attribute path (default: "color_temp")
        """
        super().__init__(attr, transform=None)  # Transform applied in __get__

    @overload
    def __get__(self, obj: None, objtype: type) -> Self: ...

    @overload
    def __get__(self, obj: LiproEntity, objtype: type | None = None) -> int: ...

    def __get__(
        self, obj: LiproEntity | None, objtype: type | None = None
    ) -> int | Self:
        """Get color temperature as percentage using device kelvin range.

        Args:
            obj: Entity instance (None for class access)
            objtype: Owner class type

        Returns:
            Descriptor for class access, percentage value for instance access
        """
        if obj is None:
            return self

        kelvin = super().__get__(obj, objtype)
        return obj.device.state.kelvin_to_percent_for_device(kelvin)


__all__ = [
    "ConditionalAttr",
    "DeviceAttr",
    "KelvinToPercent",
    "ScaledBrightness",
]
