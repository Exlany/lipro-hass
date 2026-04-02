"""Unit tests for declarative entity descriptors."""

from __future__ import annotations

from types import SimpleNamespace
from typing import Any, cast

import pytest

from custom_components.lipro.const.categories import DeviceCategory
from custom_components.lipro.core.capability import CapabilitySnapshot
from custom_components.lipro.entities.descriptors import (
    ConditionalAttr,
    DeviceAttr,
    KelvinToPercent,
    ScaledBrightness,
)


def _state_level(entity: Any) -> object:
    return entity.device.state.level


def _state_brightness(entity: Any) -> object:
    return entity.device.state.brightness


def _state_color_temp(entity: Any) -> object:
    return entity.device.state.color_temp


def _supports_color_temp(entity: Any) -> object:
    return entity.capabilities.supports_color_temp


class _StateProbe:
    def __init__(self, *, brightness: object, color_temp: int, level: int) -> None:
        self.brightness = brightness
        self.color_temp = color_temp
        self.level = level

    def kelvin_to_percent_for_device(self, kelvin: int) -> int:
        return max(0, min(100, round((kelvin - 2000) / 20)))


class _DescriptorProbe:
    raw_level = DeviceAttr[int](_state_level)
    doubled_level = DeviceAttr[int](
        _state_level,
        transform=lambda value: cast(int, value) * 2,
    )
    brightness = ScaledBrightness(_state_brightness)
    color_temp = ConditionalAttr[int](
        _state_color_temp,
        capability=_supports_color_temp,
    )
    color_temp_percent = KelvinToPercent(_state_color_temp)

    def __init__(
        self,
        *,
        supports_color_temp: bool,
        brightness: object,
        color_temp: int,
        level: int,
    ) -> None:
        self.device = SimpleNamespace(
            state=_StateProbe(
                brightness=brightness,
                color_temp=color_temp,
                level=level,
            )
        )
        self.capabilities = CapabilitySnapshot(
            device_type_hex="ff000001",
            category=DeviceCategory.LIGHT,
            supports_color_temp=supports_color_temp,
        )


def _make_probe(
    *,
    supports_color_temp: bool = True,
    brightness: object = 50,
    color_temp: int = 4200,
    level: int = 7,
) -> Any:
    return cast(
        Any,
        _DescriptorProbe(
            supports_color_temp=supports_color_temp,
            brightness=brightness,
            color_temp=color_temp,
            level=level,
        ),
    )


def test_device_attr_reads_nested_device_path() -> None:
    entity = _make_probe(level=11)

    assert entity.raw_level == 11


def test_device_attr_applies_transform() -> None:
    entity = _make_probe(level=9)

    assert entity.doubled_level == 18


def test_device_attr_returns_descriptor_for_class_access() -> None:
    assert isinstance(_DescriptorProbe.raw_level, DeviceAttr)
    assert isinstance(_DescriptorProbe.brightness, ScaledBrightness)


@pytest.mark.parametrize(
    ("raw", "expected"),
    [(-1, 0), (0, 0), (50, 128), (100, 255), (120, 255), ("bad", 0)],
)
def test_scaled_brightness_clamps_and_scales_values(raw: object, expected: int) -> None:
    entity = _make_probe(brightness=raw)

    assert entity.brightness == expected


def test_conditional_attr_reads_nested_capability_path() -> None:
    entity = _make_probe(supports_color_temp=True, color_temp=4200)

    assert entity.color_temp == 4200


def test_conditional_attr_returns_none_when_capability_disabled() -> None:
    entity = _make_probe(supports_color_temp=False, color_temp=4200)

    assert entity.color_temp is None


def test_kelvin_to_percent_uses_device_specific_conversion() -> None:
    entity = _make_probe(color_temp=3600)

    assert entity.color_temp_percent == 80
