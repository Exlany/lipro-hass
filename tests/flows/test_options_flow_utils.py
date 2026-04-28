"""Unit tests for options flow helper functions."""

from __future__ import annotations

from custom_components.lipro.const.config import (
    CONF_DEVICE_FILTER_DID_LIST,
    CONF_DEVICE_FILTER_DID_MODE,
    CONF_MQTT_ENABLED,
    CONF_SCAN_INTERVAL,
    DEFAULT_DEVICE_FILTER_MODE,
    DEFAULT_MQTT_ENABLED,
    DEFAULT_SCAN_INTERVAL,
    MAX_DEVICE_FILTER_LIST_ITEMS,
)
from custom_components.lipro.flow.options_flow import (
    _coerce_device_filter_list_option,
    _extract_persisted_options,
    _normalize_device_filter_mode_option,
    _resolve_bool_option_default,
    _resolve_int_option_default,
)


def test_coerce_device_filter_list_option_caps_items() -> None:
    values = [f"v{i}" for i in range(MAX_DEVICE_FILTER_LIST_ITEMS + 2)]

    result = _coerce_device_filter_list_option(values)

    assert "v0" in result
    assert f"v{MAX_DEVICE_FILTER_LIST_ITEMS + 1}" not in result
    assert len(result.split(", ")) == MAX_DEVICE_FILTER_LIST_ITEMS


def test_coerce_device_filter_list_option_non_stringish_returns_empty() -> None:
    assert _coerce_device_filter_list_option(123) == ""


def test_normalize_device_filter_mode_option_normalizes_case() -> None:
    assert _normalize_device_filter_mode_option(" INCLUDE ") == "include"


def test_normalize_device_filter_mode_option_invalid_returns_default() -> None:
    assert _normalize_device_filter_mode_option("unknown") == DEFAULT_DEVICE_FILTER_MODE
    assert _normalize_device_filter_mode_option(123) == DEFAULT_DEVICE_FILTER_MODE


def test_coerce_device_filter_list_option_normalizes_newlines_and_semicolons() -> None:
    result = _coerce_device_filter_list_option("Home A\r\nHome B; Home C")

    assert result == "Home A, Home B, Home C"


def test_resolve_bool_option_default_rejects_non_bool_values() -> None:
    assert (
        _resolve_bool_option_default(
            {CONF_MQTT_ENABLED: "true"},
            CONF_MQTT_ENABLED,
            DEFAULT_MQTT_ENABLED,
        )
        is DEFAULT_MQTT_ENABLED
    )


def test_resolve_int_option_default_rejects_bool_values() -> None:
    assert (
        _resolve_int_option_default(
            {CONF_SCAN_INTERVAL: True},
            CONF_SCAN_INTERVAL,
            DEFAULT_SCAN_INTERVAL,
        )
        == DEFAULT_SCAN_INTERVAL
    )


def test_extract_persisted_options_normalizes_supported_values() -> None:
    result = _extract_persisted_options(
        {
            CONF_MQTT_ENABLED: False,
            CONF_SCAN_INTERVAL: 60,
            CONF_DEVICE_FILTER_DID_MODE: " INCLUDE ",
            CONF_DEVICE_FILTER_DID_LIST: ["03ab5ccd7c000001", "03ab5ccd7c000002"],
            "ignored": object(),
        }
    )

    assert result == {
        CONF_MQTT_ENABLED: False,
        CONF_SCAN_INTERVAL: 60,
        CONF_DEVICE_FILTER_DID_MODE: "include",
        CONF_DEVICE_FILTER_DID_LIST: "03ab5ccd7c000001, 03ab5ccd7c000002",
    }
