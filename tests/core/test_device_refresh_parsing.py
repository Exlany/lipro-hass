"""Tests for device-refresh filter config parsing."""

from __future__ import annotations

from custom_components.lipro.const.config import (
    CONF_DEVICE_FILTER_DID_LIST,
    CONF_DEVICE_FILTER_DID_MODE,
    CONF_DEVICE_FILTER_HOME_LIST,
    CONF_DEVICE_FILTER_HOME_MODE,
    CONF_DEVICE_FILTER_MODEL_LIST,
    CONF_DEVICE_FILTER_MODEL_MODE,
    CONF_DEVICE_FILTER_SSID_LIST,
    CONF_DEVICE_FILTER_SSID_MODE,
    DEVICE_FILTER_MODE_EXCLUDE,
    DEVICE_FILTER_MODE_INCLUDE,
    DEVICE_FILTER_MODE_OFF,
)
from custom_components.lipro.core.coordinator.runtime.device.filter import (
    DeviceFilterConfig,
    parse_filter_config,
)


def test_parse_filter_config_empty():
    """Test parsing empty filter config returns default OFF rules."""
    config = parse_filter_config({})

    assert isinstance(config, DeviceFilterConfig)
    assert config.home.mode == DEVICE_FILTER_MODE_OFF
    assert config.model.mode == DEVICE_FILTER_MODE_OFF
    assert config.ssid.mode == DEVICE_FILTER_MODE_OFF
    assert config.did.mode == DEVICE_FILTER_MODE_OFF


def test_parse_filter_config_with_include_rules():
    """Test parsing filter config with include rules."""
    config = parse_filter_config(
        {
            CONF_DEVICE_FILTER_DID_MODE: DEVICE_FILTER_MODE_INCLUDE,
            CONF_DEVICE_FILTER_DID_LIST: "device1,device2",
            CONF_DEVICE_FILTER_MODEL_MODE: DEVICE_FILTER_MODE_INCLUDE,
            CONF_DEVICE_FILTER_MODEL_LIST: "light,switch",
        }
    )

    assert config.did.mode == DEVICE_FILTER_MODE_INCLUDE
    assert "device1" in config.did.values
    assert "device2" in config.did.values

    assert config.model.mode == DEVICE_FILTER_MODE_INCLUDE
    assert "light" in config.model.values
    assert "switch" in config.model.values


def test_parse_filter_config_with_exclude_rules():
    """Test parsing filter config with exclude rules."""
    config = parse_filter_config(
        {
            CONF_DEVICE_FILTER_HOME_MODE: DEVICE_FILTER_MODE_EXCLUDE,
            CONF_DEVICE_FILTER_HOME_LIST: "home1",
            CONF_DEVICE_FILTER_SSID_MODE: DEVICE_FILTER_MODE_EXCLUDE,
            CONF_DEVICE_FILTER_SSID_LIST: "guest_wifi",
        }
    )

    assert config.home.mode == DEVICE_FILTER_MODE_EXCLUDE
    assert "home1" in config.home.values

    assert config.ssid.mode == DEVICE_FILTER_MODE_EXCLUDE
    assert "guest_wifi" in config.ssid.values


def test_parse_filter_config_normalizes_to_lowercase():
    """Test that filter values are normalized to lowercase."""
    config = parse_filter_config(
        {
            CONF_DEVICE_FILTER_MODEL_MODE: DEVICE_FILTER_MODE_INCLUDE,
            CONF_DEVICE_FILTER_MODEL_LIST: "Light,SWITCH,FanLight",
        }
    )

    assert "light" in config.model.values
    assert "switch" in config.model.values
    assert "fanlight" in config.model.values
    assert "Light" not in config.model.values


def test_parse_filter_config_handles_multiple_separators():
    """Test parsing with comma, newline, and semicolon separators."""
    config = parse_filter_config(
        {
            CONF_DEVICE_FILTER_DID_MODE: DEVICE_FILTER_MODE_INCLUDE,
            CONF_DEVICE_FILTER_DID_LIST: "device1,device2\ndevice3;device4",
        }
    )

    assert len(config.did.values) == 4
    assert "device1" in config.did.values
    assert "device2" in config.did.values
    assert "device3" in config.did.values
    assert "device4" in config.did.values


def test_parse_filter_config_normalizes_mode_case_and_mixed_separators():
    """Runtime filter parsing should match UI-side codec normalization."""
    config = parse_filter_config(
        {
            CONF_DEVICE_FILTER_HOME_MODE: " INCLUDE ",
            CONF_DEVICE_FILTER_HOME_LIST: "Main Home\r\nGuest Home;Lobby",
        }
    )

    assert config.home.mode == DEVICE_FILTER_MODE_INCLUDE
    assert config.home.values == frozenset({"main home", "guest home", "lobby"})
