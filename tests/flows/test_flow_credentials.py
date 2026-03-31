"""Tests for config-flow credential helpers."""

from __future__ import annotations

import pytest
import voluptuous as vol

from custom_components.lipro.flow.credentials import (
    mask_phone_for_title,
    normalize_phone,
    validate_password,
)


def test_normalize_phone_accepts_trimmed_plus_number() -> None:
    assert normalize_phone(" +8613800012345 ") == "+8613800012345"


@pytest.mark.parametrize("value", [123456, None, object()])
def test_normalize_phone_rejects_non_string(value: object) -> None:
    with pytest.raises(vol.Invalid, match="Phone number must be text"):
        normalize_phone(value)


@pytest.mark.parametrize("value", ["12345", "12abc678", "++8613800012345"])
def test_normalize_phone_rejects_invalid_format(value: str) -> None:
    with pytest.raises(
        vol.Invalid,
        match=r"Phone number must be 6-20 digits \(optionally starting with \+\)",
    ):
        normalize_phone(value)


def test_normalize_phone_rejects_too_long_input() -> None:
    """Test that overly long input is rejected (DoS protection)."""
    with pytest.raises(vol.Invalid, match="Phone number too long"):
        normalize_phone("+" + "1" * 50)


@pytest.mark.parametrize("value", ["138000'; DROP", '138000"', "138000/**/", "138000--"])
def test_normalize_phone_rejects_non_phone_characters(value: str) -> None:
    """Test that non-phone characters are rejected by the format contract."""
    with pytest.raises(
        vol.Invalid,
        match=r"Phone number must be 6-20 digits \(optionally starting with \+\)",
    ):
        normalize_phone(value)


def test_normalize_phone_accepts_valid_numbers() -> None:
    """Test that valid phone numbers are accepted."""
    assert normalize_phone("13800012345") == "13800012345"
    assert normalize_phone("+8613800012345") == "+8613800012345"
    assert normalize_phone("  123456  ") == "123456"


def test_mask_phone_for_title_returns_stars_for_blank_input() -> None:
    assert mask_phone_for_title("   ") == "***"


@pytest.mark.parametrize(
    ("phone", "expected"),
    [
        ("+1234", "+***"),
        ("12345678", "12***78"),
        ("+8613800012345", "+861****2345"),
    ],
)
def test_mask_phone_for_title_handles_length_buckets(phone: str, expected: str) -> None:
    assert mask_phone_for_title(phone) == expected


@pytest.mark.parametrize("value", [None, 12345, object()])
def test_validate_password_rejects_non_string(value: object) -> None:
    with pytest.raises(vol.Invalid, match="Password must be text"):
        validate_password(value)


def test_validate_password_rejects_too_short() -> None:
    """Test that passwords shorter than 6 characters are rejected."""
    with pytest.raises(vol.Invalid, match="Password too short"):
        validate_password("")

    with pytest.raises(vol.Invalid, match="Password too short"):
        validate_password("12345")


def test_validate_password_rejects_too_long() -> None:
    """Test that passwords longer than 128 characters are rejected."""
    with pytest.raises(vol.Invalid, match="Password too long"):
        validate_password("x" * 129)


def test_validate_password_rejects_null_bytes() -> None:
    """Test that passwords with null bytes are rejected (security risk)."""
    with pytest.raises(vol.Invalid, match="contains invalid characters"):
        validate_password("password\x00admin")


@pytest.mark.parametrize("value", ["password\x01\x02", "password\nadmin", "password\tadmin", "password\radmin"])
def test_validate_password_rejects_control_chars(value: str) -> None:
    """Test that passwords with control characters are rejected."""
    with pytest.raises(vol.Invalid, match="contains invalid characters"):
        validate_password(value)


def test_validate_password_accepts_valid_value() -> None:
    """Test that valid passwords are accepted."""
    assert validate_password("password123") == "password123"
    assert validate_password("123456") == "123456"
    assert validate_password("a" * 128) == "a" * 128
    assert validate_password("P@ssw0rd!#$%") == "P@ssw0rd!#$%"
