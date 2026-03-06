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
    with pytest.raises(vol.Invalid, match="phone must be a string"):
        normalize_phone(value)


@pytest.mark.parametrize("value", ["12345", "12abc678", "++8613800012345"])
def test_normalize_phone_rejects_invalid_format(value: str) -> None:
    with pytest.raises(
        vol.Invalid,
        match=r"phone must be 6-20 digits, optionally prefixed with \+",
    ):
        normalize_phone(value)


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
    with pytest.raises(vol.Invalid, match="password must be a string"):
        validate_password(value)


def test_validate_password_rejects_empty_or_too_long() -> None:
    with pytest.raises(vol.Invalid, match="password length must be 1-128"):
        validate_password("")

    with pytest.raises(vol.Invalid, match="password length must be 1-128"):
        validate_password("x" * 129)


def test_validate_password_accepts_valid_value() -> None:
    assert validate_password("password123") == "password123"
