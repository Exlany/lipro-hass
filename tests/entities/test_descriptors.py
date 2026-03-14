"""Unit tests for declarative entity descriptors."""

from __future__ import annotations

from types import SimpleNamespace
from typing import Any, cast

from custom_components.lipro.const.categories import DeviceCategory
from custom_components.lipro.core.capability import CapabilitySnapshot
from custom_components.lipro.entities.descriptors import ConditionalAttr


class _DescriptorProbe:
    color_temp = ConditionalAttr[int](
        "color_temp",
        capability="capabilities.supports_color_temp",
    )

    def __init__(self, *, supports_color_temp: bool, color_temp: int) -> None:
        self.device = SimpleNamespace(color_temp=color_temp)
        self.capabilities = CapabilitySnapshot(
            device_type_hex="ff000001",
            category=DeviceCategory.LIGHT,
            platforms=("light",),
            supports_color_temp=supports_color_temp,
        )


def test_conditional_attr_reads_nested_capability_path() -> None:
    """ConditionalAttr should consult canonical capability snapshot paths."""
    entity = cast(Any, _DescriptorProbe(supports_color_temp=True, color_temp=4200))
    assert entity.color_temp == 4200


def test_conditional_attr_returns_none_when_capability_disabled() -> None:
    """ConditionalAttr should hide values when capability snapshot says no."""
    entity = cast(Any, _DescriptorProbe(supports_color_temp=False, color_temp=4200))
    assert entity.color_temp is None
