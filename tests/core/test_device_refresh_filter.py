"""Tests for device-refresh filter semantics."""

from __future__ import annotations

from unittest.mock import patch

from custom_components.lipro.const.config import (
    DEVICE_FILTER_MODE_EXCLUDE,
    DEVICE_FILTER_MODE_INCLUDE,
    DEVICE_FILTER_MODE_OFF,
)
from custom_components.lipro.core.coordinator.runtime.device.filter import (
    DeviceFilter,
    DeviceFilterConfig,
    DeviceFilterRule,
)


def test_device_filter_has_active_filter_returns_false_when_all_off():
    """Test _has_active_filter returns False when all rules are OFF."""
    config = DeviceFilterConfig()
    device_filter = DeviceFilter(config=config)

    assert not device_filter._has_active_filter()


def test_device_filter_has_active_filter_returns_true_when_any_active():
    """Test _has_active_filter returns True when any rule is active."""
    config = DeviceFilterConfig(
        did=DeviceFilterRule(
            mode=DEVICE_FILTER_MODE_INCLUDE, values=frozenset({"device1"})
        )
    )
    device_filter = DeviceFilter(config=config)

    assert device_filter._has_active_filter()


def test_device_filter_is_device_included_no_filter():
    """Test device is included when no filter is active."""
    config = DeviceFilterConfig()
    device_filter = DeviceFilter(config=config)

    assert device_filter.is_device_included({"serial": "03ab000000000001"})


def test_device_filter_is_device_included_by_did_include():
    """Test device inclusion by DID include rule."""
    config = DeviceFilterConfig(
        did=DeviceFilterRule(
            mode=DEVICE_FILTER_MODE_INCLUDE,
            values=frozenset({"03ab000000000001", "03ab000000000002"}),
        )
    )
    device_filter = DeviceFilter(config=config)

    assert device_filter.is_device_included({"serial": "03ab000000000001"})
    assert device_filter.is_device_included({"serial": "03ab000000000002"})
    assert not device_filter.is_device_included({"serial": "03ab000000000003"})


def test_device_filter_is_device_included_by_did_exclude():
    """Test device exclusion by DID exclude rule."""
    config = DeviceFilterConfig(
        did=DeviceFilterRule(
            mode=DEVICE_FILTER_MODE_EXCLUDE,
            values=frozenset({"03ab000000000001"}),
        )
    )
    device_filter = DeviceFilter(config=config)

    assert not device_filter.is_device_included({"serial": "03ab000000000001"})
    assert device_filter.is_device_included({"serial": "03ab000000000002"})


def test_device_filter_is_device_included_by_model_include():
    """Test device inclusion by model include rule."""
    config = DeviceFilterConfig(
        model=DeviceFilterRule(
            mode=DEVICE_FILTER_MODE_INCLUDE,
            values=frozenset({"light", "switch"}),
        )
    )
    device_filter = DeviceFilter(config=config)

    assert device_filter.is_device_included({"serial": "xxx", "physicalModel": "light"})
    assert device_filter.is_device_included(
        {"serial": "xxx", "physicalModel": "switch"}
    )
    assert not device_filter.is_device_included(
        {"serial": "xxx", "physicalModel": "outlet"}
    )


def test_device_filter_is_device_included_by_home_include():
    """Test device inclusion by home include rule."""
    config = DeviceFilterConfig(
        home=DeviceFilterRule(
            mode=DEVICE_FILTER_MODE_INCLUDE,
            values=frozenset({"home1", "home2"}),
        )
    )
    device_filter = DeviceFilter(config=config)

    assert device_filter.is_device_included({"serial": "xxx", "homeName": "Home1"})
    assert device_filter.is_device_included({"serial": "xxx", "homeName": "HOME2"})
    assert not device_filter.is_device_included({"serial": "xxx", "homeName": "Home3"})


def test_device_filter_is_device_included_by_ssid_exclude():
    """Test device exclusion by SSID exclude rule."""
    config = DeviceFilterConfig(
        ssid=DeviceFilterRule(
            mode=DEVICE_FILTER_MODE_EXCLUDE,
            values=frozenset({"guest_wifi"}),
        )
    )
    device_filter = DeviceFilter(config=config)

    assert not device_filter.is_device_included(
        {"serial": "xxx", "deviceInfo": '{"wifi_ssid":"guest_wifi"}'}
    )
    assert device_filter.is_device_included(
        {"serial": "xxx", "deviceInfo": '{"wifi_ssid":"main_wifi"}'}
    )


def test_device_filter_invalid_device_info_json_is_ignored_for_ssid_rules():
    """Malformed deviceInfo JSON should degrade to no-SSID-match instead of failing."""
    config = DeviceFilterConfig(
        ssid=DeviceFilterRule(
            mode=DEVICE_FILTER_MODE_EXCLUDE,
            values=frozenset({"guest_wifi"}),
        )
    )
    device_filter = DeviceFilter(config=config)

    assert device_filter.is_device_included(
        {"serial": "xxx", "deviceInfo": '{"wifi_ssid":"guest_wifi"'}
    )


def test_device_filter_is_device_included_multiple_rules_all_must_pass():
    """Test that device must pass ALL active filter rules."""
    config = DeviceFilterConfig(
        did=DeviceFilterRule(
            mode=DEVICE_FILTER_MODE_INCLUDE,
            values=frozenset({"03ab000000000001"}),
        ),
        model=DeviceFilterRule(
            mode=DEVICE_FILTER_MODE_INCLUDE,
            values=frozenset({"light"}),
        ),
    )
    device_filter = DeviceFilter(config=config)

    assert device_filter.is_device_included(
        {"serial": "03ab000000000001", "physicalModel": "light"}
    )
    assert not device_filter.is_device_included(
        {"serial": "03ab000000000002", "physicalModel": "light"}
    )
    assert not device_filter.is_device_included(
        {"serial": "03ab000000000001", "physicalModel": "switch"}
    )


def test_device_filter_skips_ssid_check_when_mode_off():
    """Test that SSID filter is skipped when mode is OFF."""
    config = DeviceFilterConfig(
        did=DeviceFilterRule(
            mode=DEVICE_FILTER_MODE_INCLUDE,
            values=frozenset({"03ab5ccd7c000001"}),
        ),
        ssid=DeviceFilterRule(mode=DEVICE_FILTER_MODE_OFF),
    )
    device_filter = DeviceFilter(config=config)

    with patch(
        "custom_components.lipro.core.coordinator.runtime.device.filter.json.loads"
    ) as json_loads:
        assert device_filter.is_device_included(
            {
                "serial": "03ab5ccd7c000001",
                "deviceInfo": '{"wifi_ssid":"MyWiFi"}',
            }
        )
        json_loads.assert_not_called()
