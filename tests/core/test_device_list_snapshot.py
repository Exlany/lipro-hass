"""Tests for device list snapshot pure helpers."""

from __future__ import annotations

from unittest.mock import MagicMock, patch

from custom_components.lipro.const.categories import DeviceCategory
from custom_components.lipro.const.config import (
    DEVICE_FILTER_MODE_EXCLUDE,
    DEVICE_FILTER_MODE_OFF,
)
from custom_components.lipro.core.coordinator.runtime.device import filter as filter_module
from custom_components.lipro.core.coordinator.runtime.device.filter import (
    DeviceFilter,
    DeviceFilterConfig,
    DeviceFilterRule,
)


def test_parse_filter_rule_stops_when_item_cap_is_zero(monkeypatch) -> None:
    """Test that filter rule parsing respects item cap."""
    monkeypatch.setattr(filter_module, "MAX_DEVICE_FILTER_LIST_ITEMS", 0)

    rule = filter_module._parse_filter_rule(mode="include", list_str="home_a,home_b")
    assert rule.values == frozenset()


def test_parse_filter_rule_truncates_long_list_string(monkeypatch) -> None:
    """Test that filter rule parsing truncates long strings."""
    monkeypatch.setattr(filter_module, "MAX_DEVICE_FILTER_LIST_CHARS", 5)

    rule = filter_module._parse_filter_rule(mode="include", list_str="ABCDE12345")
    assert rule.values == frozenset({"abcde"})


def test_collect_property_values_supports_mapping_payload() -> None:
    """Test property value collection from mapping."""
    properties = {"wifi_ssid": "HomeWiFi", "ssid": "Backup", "ignored": "noop"}

    assert filter_module._collect_property_values(properties, ("wifi_ssid", "ssid")) == {
        "homewifi",
        "backup",
    }


def test_collect_property_values_skips_invalid_and_untracked_list_rows() -> None:
    """Test property value collection skips invalid entries."""
    properties = [
        123,
        {"key": "other", "value": "Nope"},
        {"key": "wifi_ssid", "value": "MainWiFi"},
    ]

    assert filter_module._collect_property_values(properties, ("wifi_ssid", "ssid")) == {"mainwifi"}


def test_collect_ssid_values_merges_device_info_mapping_values() -> None:
    """Test SSID collection merges deviceInfo."""
    values = filter_module._collect_ssid_values(
        {
            "wifi_ssid": "MainWiFi",
            "deviceInfo": {"ssid": "GuestWiFi"},
        }
    )

    assert values == {"mainwifi", "guestwifi"}


def test_collect_ssid_values_ignores_non_json_device_info_text() -> None:
    """Test SSID collection handles non-JSON deviceInfo."""
    values = filter_module._collect_ssid_values(
        {
            "ssid": "RouterWiFi",
            "deviceInfo": "wifi_ssid:GuestWiFi",
        }
    )

    assert values == {"routerwifi"}


def test_collect_ssid_values_handles_device_info_json_errors() -> None:
    """Test SSID collection handles JSON parse errors."""
    values = filter_module._collect_ssid_values(
        {
            "ssid": "RouterWiFi",
            "deviceInfo": "{not valid json}",
        }
    )

    assert values == {"routerwifi"}


def test_device_filter_allows_all_when_mode_is_off() -> None:
    """Test DeviceFilter allows all devices when filter is off."""
    config = DeviceFilterConfig(
        home=DeviceFilterRule(mode=DEVICE_FILTER_MODE_OFF, values=frozenset({"blocked"}))
    )
    device_filter = DeviceFilter(config=config)

    assert device_filter.is_device_included({"homeName": "anything"}) is True


def test_device_filter_returns_true_without_active_rules() -> None:
    """Test DeviceFilter allows all devices without active rules."""
    config = DeviceFilterConfig()
    device_filter = DeviceFilter(config=config)

    assert device_filter.is_device_included({"serial": "03ab5ccd7c000001"}) is True


def test_device_filter_treats_exclude_empty_values_as_noop() -> None:
    """Test DeviceFilter treats exclude with empty values as no-op."""
    config = DeviceFilterConfig(
        home=DeviceFilterRule(
            mode=DEVICE_FILTER_MODE_EXCLUDE,
            values=frozenset(),
        )
    )
    device_filter = DeviceFilter(config=config)

    assert device_filter.is_device_included({"homeName": "Main Home"}) is True
