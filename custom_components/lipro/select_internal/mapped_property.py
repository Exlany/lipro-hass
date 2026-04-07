"""Internal mapped-property helpers for the select platform."""

from __future__ import annotations

from collections.abc import Mapping
from dataclasses import dataclass


def coerce_mapped_value(raw_value: object) -> int | None:
    """Convert one mapped-property raw value into an integer enum value."""
    if raw_value is None:
        return None
    if isinstance(raw_value, bool):
        return int(raw_value)
    if isinstance(raw_value, int):
        return raw_value
    if isinstance(raw_value, float):
        return int(raw_value) if raw_value.is_integer() else None
    if isinstance(raw_value, str):
        normalized = raw_value.strip()
        if not normalized:
            return None
        try:
            return int(normalized)
        except ValueError:
            return None
    return None


@dataclass(frozen=True, slots=True)
class MappedPropertySnapshot:
    """Normalized state for one mapped-property select."""

    raw_value: object | None
    normalized_value: int | None
    option: str | None

    def build_unknown_attributes(self, *, property_key: str) -> dict[str, object]:
        """Expose raw enum state when it does not map to a known option."""
        if self.raw_value is None or self.option is not None:
            return {}
        return {
            "property_key": property_key,
            "raw_value": self.raw_value,
        }


def build_mapped_property_snapshot(
    properties: Mapping[str, object],
    *,
    property_key: str,
    value_to_option: Mapping[int, str],
) -> MappedPropertySnapshot:
    """Normalize one mapped-property select state snapshot."""
    raw_value = properties.get(property_key)
    normalized_value = coerce_mapped_value(raw_value)
    option = None
    if normalized_value is not None:
        option = value_to_option.get(normalized_value)
    return MappedPropertySnapshot(
        raw_value=raw_value,
        normalized_value=normalized_value,
        option=option,
    )
