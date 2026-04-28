"""Tests for shared identifier normalization helpers."""

from __future__ import annotations

from custom_components.lipro.core.utils.identifiers import (
    is_valid_iot_device_id,
    is_valid_mesh_group_id,
    normalize_iot_device_id,
    normalize_mesh_group_id,
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


def test_normalize_mesh_group_id_valid() -> None:
    assert normalize_mesh_group_id("mesh_group_1") == "mesh_group_1"
    assert normalize_mesh_group_id("  mesh_group_42  ") == "mesh_group_42"


def test_normalize_mesh_group_id_invalid() -> None:
    assert normalize_mesh_group_id(None) is None
    assert normalize_mesh_group_id("") is None
    assert normalize_mesh_group_id("   ") is None
    assert normalize_mesh_group_id("mesh_grp_1") is None
    assert normalize_mesh_group_id(123) is None


def test_is_valid_mesh_group_id() -> None:
    assert is_valid_mesh_group_id("mesh_group_1") is True
    assert is_valid_mesh_group_id("mesh_group_99999") is True
    assert is_valid_mesh_group_id("mesh_grp_1") is False
    assert is_valid_mesh_group_id("mesh_group_") is False
