"""Internal gear-preset helpers for the select platform."""

from __future__ import annotations

from collections.abc import Callable, Sequence
from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class GearPreset:
    """Normalized light-gear preset that keeps the original option index."""

    gear_index: int
    brightness: int
    temperature_percent: int


def coerce_int_like(value: object) -> int | None:
    """Convert one int-like gear field value safely."""
    if value is None:
        return None
    if isinstance(value, bool):
        return int(value)
    if isinstance(value, int):
        return value
    if isinstance(value, float):
        return int(value) if value.is_integer() else None
    if isinstance(value, str):
        normalized = value.strip()
        if not normalized:
            return None
        try:
            return int(normalized)
        except ValueError:
            return None
    return None


def extract_gear_preset(gear_index: int, gear: object) -> GearPreset | None:
    """Extract one valid preset while preserving its original gear index."""
    if not isinstance(gear, dict):
        return None

    brightness = coerce_int_like(gear.get("brightness"))
    temperature_percent = coerce_int_like(gear.get("temperature"))
    if brightness is None or temperature_percent is None:
        return None
    return GearPreset(
        gear_index=gear_index,
        brightness=brightness,
        temperature_percent=temperature_percent,
    )


def iter_valid_gear_presets(
    gear_list: Sequence[object],
    *,
    max_count: int,
) -> list[GearPreset]:
    """Return valid gear presets while preserving original option indexes."""
    presets: list[GearPreset] = []
    for gear_index, gear in enumerate(gear_list[:max_count]):
        preset = extract_gear_preset(gear_index, gear)
        if preset is not None:
            presets.append(preset)
    return presets


def resolve_current_gear_option(
    gear_list: Sequence[object],
    *,
    current_brightness: int | None,
    current_temperature_percent: int | None,
    max_count: int,
    options: Sequence[str],
) -> str | None:
    """Resolve the current option by exact brightness/temperature match."""
    for preset in iter_valid_gear_presets(gear_list, max_count=max_count):
        if (
            current_brightness == preset.brightness
            and current_temperature_percent == preset.temperature_percent
        ):
            return options[preset.gear_index]
    return None


def build_gear_attributes(
    gear_list: Sequence[object],
    *,
    max_count: int,
    preset_names: Sequence[str],
    percent_to_kelvin: Callable[[int], int],
    color_temp_range: tuple[int, int] | None,
) -> dict[str, object]:
    """Build extra-state attributes describing available gear presets."""
    attrs: dict[str, object] = {}
    for preset in iter_valid_gear_presets(gear_list, max_count=max_count):
        attrs[f"preset_{preset_names[preset.gear_index]}"] = (
            f"{preset.brightness}% / {percent_to_kelvin(preset.temperature_percent)}K"
        )

    if color_temp_range is not None:
        min_kelvin, max_kelvin = color_temp_range
        attrs["color_temp_range"] = f"{min_kelvin}K - {max_kelvin}K"
    return attrs


def available_gear_options(
    gear_count: int,
    *,
    max_count: int,
    option_names: Sequence[str],
) -> list[str]:
    """Return outward gear options capped by supported slot count."""
    if gear_count <= 0:
        return []
    supported_count = min(gear_count, max_count, len(option_names))
    return list(option_names[:supported_count])


def resolve_gear_option_index(
    option: str,
    *,
    option_names: Sequence[str],
) -> int | None:
    """Resolve one outward gear option name into its device slot index."""
    for index, candidate in enumerate(option_names):
        if candidate == option:
            return index
    return None
