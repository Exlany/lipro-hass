"""Unit tests for options flow helper functions."""

from __future__ import annotations

from custom_components.lipro.const.config import (
    DEFAULT_DEVICE_FILTER_MODE,
    MAX_DEVICE_FILTER_LIST_ITEMS,
)
from custom_components.lipro.flow.options_flow import (
    _coerce_device_filter_list_option,
    _normalize_device_filter_mode_option,
)


def test_coerce_device_filter_list_option_caps_items() -> None:
    values = [f"v{i}" for i in range(MAX_DEVICE_FILTER_LIST_ITEMS + 2)]

    result = _coerce_device_filter_list_option(values)

    assert "v0" in result
    assert f"v{MAX_DEVICE_FILTER_LIST_ITEMS + 1}" not in result
    assert len(result.split(", ")) == MAX_DEVICE_FILTER_LIST_ITEMS


def test_coerce_device_filter_list_option_non_stringish_returns_empty() -> None:
    assert _coerce_device_filter_list_option(123) == ""


def test_normalize_device_filter_mode_option_invalid_returns_default() -> None:
    assert _normalize_device_filter_mode_option("unknown") == DEFAULT_DEVICE_FILTER_MODE
    assert _normalize_device_filter_mode_option(123) == DEFAULT_DEVICE_FILTER_MODE
