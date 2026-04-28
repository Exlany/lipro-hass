"""Tests for property key normalization helpers."""

from __future__ import annotations

from collections.abc import Mapping

from custom_components.lipro.core.utils.property_normalization import (
    normalize_properties,
)


def test_normalize_properties_skips_non_string_and_empty_keys() -> None:
    raw: Mapping[object, object] = {
        "fanOnOff": 1,
        "fanOnoff": 0,
        "": "skip-empty",
        None: "skip-none",
        123: "skip-int",
        "wifiSsid": "Home WiFi",
    }
    normalized = normalize_properties(raw)

    assert normalized == {
        "fanOnoff": 0,
        "wifi_ssid": "Home WiFi",
    }


def test_normalize_properties_keeps_canonical_value_when_alias_comes_later() -> None:
    normalized = normalize_properties(
        {
            "fanOnoff": 1,
            "fanOnOff": 0,
        }
    )

    assert normalized == {"fanOnoff": 1}
