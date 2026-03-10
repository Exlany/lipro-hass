"""Tests for device list snapshot pure helpers."""

from __future__ import annotations

from unittest.mock import patch

from custom_components.lipro.const.categories import DeviceCategory
from custom_components.lipro.const.config import (
    DEVICE_FILTER_MODE_EXCLUDE,
    DEVICE_FILTER_MODE_OFF,
)
from custom_components.lipro.core.coordinator.runtime.device import filter as snapshot
from custom_components.lipro.core.coordinator.runtime.device.filter import (
    DeviceFilterConfig,
    DeviceFilterRule,
    _collect_property_values,
    _collect_ssid_values,
    _parse_filter_values,
    _rule_allows_values,
    is_device_included_by_filter,
)
from custom_components.lipro.core.coordinator.runtime.device.snapshot import (
    build_fetched_device_snapshot,
)


def test_parse_filter_values_stops_when_item_cap_is_zero(monkeypatch) -> None:
    monkeypatch.setattr(snapshot, "MAX_DEVICE_FILTER_LIST_ITEMS", 0)

    assert _parse_filter_values("home_a,home_b") == frozenset()


def test_parse_filter_values_truncates_non_string_iterable_items(monkeypatch) -> None:
    class _LongValue:
        def __str__(self) -> str:
            return "ABCDE12345"

    monkeypatch.setattr(snapshot, "MAX_DEVICE_FILTER_LIST_CHARS", 5)

    assert _parse_filter_values([_LongValue()]) == frozenset({"abcde"})


def test_parse_filter_values_truncates_scalar_non_iterable_values(monkeypatch) -> None:
    class _LongScalar:
        def __str__(self) -> str:
            return "WIFI-NAME"

    monkeypatch.setattr(snapshot, "MAX_DEVICE_FILTER_LIST_CHARS", 4)

    assert _parse_filter_values(_LongScalar()) == frozenset({"wifi"})


def test_collect_property_values_supports_mapping_payload() -> None:
    properties = {"wifi_ssid": "HomeWiFi", "ssid": "Backup", "ignored": "noop"}

    assert _collect_property_values(properties, ("wifi_ssid", "ssid")) == {
        "homewifi",
        "backup",
    }


def test_collect_property_values_skips_invalid_and_untracked_list_rows() -> None:
    properties = [
        123,
        {"key": "other", "value": "Nope"},
        {"key": "wifi_ssid", "value": "MainWiFi"},
    ]

    assert _collect_property_values(properties, ("wifi_ssid", "ssid")) == {"mainwifi"}


def test_collect_ssid_values_merges_device_info_mapping_values() -> None:
    values = _collect_ssid_values(
        {
            "wifi_ssid": "MainWiFi",
            "deviceInfo": {"ssid": "GuestWiFi"},
        }
    )

    assert values == {"mainwifi", "guestwifi"}


def test_collect_ssid_values_ignores_non_json_device_info_text() -> None:
    values = _collect_ssid_values(
        {
            "ssid": "RouterWiFi",
            "deviceInfo": "wifi_ssid:GuestWiFi",
        }
    )

    assert values == {"routerwifi"}


def test_collect_ssid_values_handles_device_info_json_errors() -> None:
    values = _collect_ssid_values(
        {
            "ssid": "RouterWiFi",
            "deviceInfo": "{not valid json}",
        }
    )

    assert values == {"routerwifi"}


def test_rule_allows_values_returns_true_when_mode_is_off() -> None:
    rule = DeviceFilterRule(mode=DEVICE_FILTER_MODE_OFF, values=frozenset({"blocked"}))

    assert _rule_allows_values(rule, {"anything"}) is True


def test_rule_allows_values_defaults_to_true_for_unknown_mode() -> None:
    rule = DeviceFilterRule(mode="unknown", values=frozenset({"blocked"}))

    assert _rule_allows_values(rule, {"blocked"}) is True


def test_is_device_included_by_filter_returns_true_without_active_rules() -> None:
    assert (
        is_device_included_by_filter(
            {"serial": "03ab5ccd7c000001"}, DeviceFilterConfig()
        )
        is True
    )


def test_is_device_included_by_filter_treats_exclude_empty_values_as_noop() -> None:
    config = DeviceFilterConfig(
        home=DeviceFilterRule(
            mode=DEVICE_FILTER_MODE_EXCLUDE,
            values=frozenset(),
        )
    )

    assert is_device_included_by_filter({"homeName": "Main Home"}, config) is True


def test_build_fetched_device_snapshot_keeps_gateway_only_in_diagnostics() -> None:
    class _GatewayDevice:
        serial = "03ab0000000000aa"
        name = "Gateway Device"
        is_group = False
        has_valid_iot_id = True
        iot_device_id = serial

        @property
        def is_gateway(self) -> bool:
            return True

        @property
        def category(self):
            return DeviceCategory.GATEWAY

    with patch(
        "custom_components.lipro.core.coordinator.device_list_snapshot.LiproDevice.from_api_data"
    ) as from_api:
        from_api.return_value = _GatewayDevice()
        fetched_snapshot = build_fetched_device_snapshot([{}])

    assert fetched_snapshot.devices == {}
    assert fetched_snapshot.device_by_id == {}
    assert fetched_snapshot.iot_ids == []
    assert fetched_snapshot.group_ids == []
    assert fetched_snapshot.outlet_ids == []
    assert fetched_snapshot.cloud_serials == set()
    assert set(fetched_snapshot.diagnostic_gateway_devices) == {"03ab0000000000aa"}
