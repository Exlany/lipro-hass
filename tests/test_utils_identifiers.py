"""Tests for shared identifier normalization helpers."""

from __future__ import annotations

from custom_components.lipro.core.utils.identifiers import (
    is_valid_iot_device_id,
    normalize_iot_device_id,
)


def test_normalize_iot_device_id_returns_canonical_lowercase() -> None:
    assert normalize_iot_device_id("03AB5CCD7C123456") == "03ab5ccd7c123456"
    assert normalize_iot_device_id(" 03ab5ccd7c123456 ") == "03ab5ccd7c123456"


def test_normalize_iot_device_id_returns_none_for_invalid_values() -> None:
    assert normalize_iot_device_id(None) is None
    assert normalize_iot_device_id("") is None
    assert normalize_iot_device_id("03ab") is None
    assert normalize_iot_device_id("03ab5ccd7c12345g") is None


def test_is_valid_iot_device_id_wrapper() -> None:
    assert is_valid_iot_device_id("03ab5ccd7c123456") is True
    assert is_valid_iot_device_id("03ab") is False
