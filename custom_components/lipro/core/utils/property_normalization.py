"""Property key normalization for Lipro payload variants.

The Lipro cloud API and MQTT payloads sometimes use multiple spellings for the
same logical field (e.g. ``fanOnOff`` vs ``fanOnoff``). Keep the integration's
internal state canonical by normalizing keys at ingestion/update boundaries.
"""

from __future__ import annotations

from collections.abc import Mapping
from typing import Final, TypeVar

_PROPERTY_KEY_ALIASES: Final[dict[str, str]] = {
    # Fan power - status query uses camel-case O, control uses "fanOnoff".
    "fanOnOff": "fanOnoff",
    # Curtain payload variants.
    "progress": "position",
    "state": "moving",
    # Diagnostics/network fields.
    "wifiSsid": "wifi_ssid",
    "wifiRssi": "wifi_rssi",
    "netType": "net_type",
}

PropertyValueT = TypeVar("PropertyValueT")


def normalize_property_key(key: str) -> str:
    """Return canonical property key for one raw key."""
    return _PROPERTY_KEY_ALIASES.get(key, key)


def normalize_properties(
    properties: Mapping[str, PropertyValueT] | Mapping[object, PropertyValueT] | None,
) -> dict[str, PropertyValueT]:
    """Normalize a property mapping into canonical keys.

    Canonical keys win when both canonical and alias keys are present.
    """
    if not properties:
        return {}

    normalized: dict[str, PropertyValueT] = {}
    for raw_key, value in properties.items():
        if not isinstance(raw_key, str) or not raw_key:
            continue

        canonical = normalize_property_key(raw_key)

        # Prefer explicit canonical keys when present in the same payload.
        if canonical in normalized and canonical != raw_key:
            continue
        normalized[canonical] = value

    return normalized


__all__ = ["normalize_properties"]
