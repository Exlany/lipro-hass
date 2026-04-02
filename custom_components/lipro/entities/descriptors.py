"""Generic descriptors for declarative entity property definitions.

This module provides type-safe descriptors that eliminate boilerplate property
getters in entity classes. Descriptors use explicit resolver callables instead
of dotted string paths, keeping entity reads honest and easy to audit.

Key features:
- Full mypy type safety via Generic[T] + @overload
- Automatic unit conversions (0-100 → 0-255 for brightness)
- Conditional attributes (only when capability snapshot declares support)
- Explicit resolver callables instead of runtime reflection
"""

from __future__ import annotations

from collections.abc import Callable
from typing import TYPE_CHECKING, Generic, TypeVar, cast, overload

if TYPE_CHECKING:
    from typing import Self

    from .base import LiproEntity

T = TypeVar("T")
EntityResolver = Callable[[object], object]
CapabilityResolver = Callable[[object], object]


def _default_brightness_resolver(entity: LiproEntity) -> object:
    """Read raw brightness from device state."""
    return entity.device.state.brightness


def _default_color_temp_resolver(entity: LiproEntity) -> object:
    """Read raw color temperature from device state."""
    return entity.device.state.color_temp


class DeviceAttr(Generic[T]):
    """Generic descriptor for reading entity values with optional transformation.

    Type-safe descriptor that reads from an explicit resolver and optionally
    transforms the resolved value. Uses @overload to ensure mypy correctly
    infers the return type.

    Examples:
        class LiproLight(LiproEntity, LightEntity):
            is_on = DeviceAttr[bool](lambda entity: entity.device.state.is_on)
            brightness = DeviceAttr[int](
                lambda entity: entity.device.state.brightness,
                transform=lambda value: int(cast(int, value) * 2.55),
            )

    Args:
        resolver: Explicit callable that reads the source value from one entity
        transform: Optional transformation function applied to the value
    """

    def __init__(
        self,
        resolver: EntityResolver,
        *,
        transform: Callable[[object], T] | None = None,
    ) -> None:
        """Initialize device attribute descriptor."""
        self.resolver = resolver
        self.transform = transform
        self.name: str = ""

    def __set_name__(self, owner: type, name: str) -> None:
        """Store the attribute name when descriptor is assigned to class."""
        self.name = name

    @overload
    def __get__(self, obj: None, objtype: type) -> Self: ...

    @overload
    def __get__(self, obj: LiproEntity, objtype: type | None = None) -> T: ...

    def __get__(self, obj: LiproEntity | None, objtype: type | None = None) -> T | Self:
        """Get attribute value from entity with optional transformation."""
        if obj is None:
            return self

        value = self.resolver(obj)
        if self.transform is not None:
            return self.transform(value)
        return cast(T, value)


class ScaledBrightness(DeviceAttr[int | None]):
    """Brightness descriptor with automatic 0-100 → 0-255 scaling."""

    def __init__(self, resolver: EntityResolver = _default_brightness_resolver) -> None:
        """Initialize scaled brightness descriptor."""

        def scale_brightness(value: object) -> int:
            """Scale 0-100 to 0-255 with clamping."""
            if not isinstance(value, int):
                return 0
            clamped = max(0, min(100, value))
            return round(clamped * 255 / 100)

        super().__init__(resolver, transform=scale_brightness)


class ConditionalAttr(DeviceAttr[T | None]):
    """Conditional descriptor that returns None when entity lacks capability."""

    def __init__(
        self,
        resolver: EntityResolver,
        *,
        capability: CapabilityResolver,
        transform: Callable[[object], T] | None = None,
    ) -> None:
        """Initialize conditional attribute descriptor."""
        super().__init__(resolver, transform=transform)
        self.capability = capability

    @overload
    def __get__(self, obj: None, objtype: type) -> Self: ...

    @overload
    def __get__(self, obj: LiproEntity, objtype: type | None = None) -> T | None: ...

    def __get__(
        self, obj: LiproEntity | None, objtype: type | None = None
    ) -> T | None | Self:
        """Get attribute value only if entity capability exists."""
        if obj is None:
            return self

        if not self.capability(obj):
            return None

        return super().__get__(obj, objtype)


class KelvinToPercent(DeviceAttr[int]):
    """Color temperature descriptor with automatic kelvin → percent conversion."""

    def __init__(
        self, resolver: EntityResolver = _default_color_temp_resolver
    ) -> None:
        """Initialize kelvin-to-percent descriptor."""
        super().__init__(resolver, transform=None)

    @overload
    def __get__(self, obj: None, objtype: type) -> Self: ...

    @overload
    def __get__(self, obj: LiproEntity, objtype: type | None = None) -> int: ...

    def __get__(
        self, obj: LiproEntity | None, objtype: type | None = None
    ) -> int | Self:
        """Get color temperature as percentage using device kelvin range."""
        if obj is None:
            return self

        kelvin = super().__get__(obj, objtype)
        return obj.device.state.kelvin_to_percent_for_device(cast(int, kelvin))


__all__ = [
    "ConditionalAttr",
    "DeviceAttr",
    "KelvinToPercent",
    "ScaledBrightness",
]
