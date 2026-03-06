"""Credential helpers for Lipro config flows."""

from __future__ import annotations

import re
from typing import Any

import voluptuous as vol

_PHONE_INPUT_PATTERN = re.compile(r"^\+?\d{6,20}$")
_MAX_PASSWORD_LEN: int = 128


def normalize_phone(phone: Any) -> str:
    """Normalize and validate user-provided phone value."""
    if not isinstance(phone, str):
        msg = "phone must be a string"
        raise vol.Invalid(msg)

    normalized = phone.strip()
    if not _PHONE_INPUT_PATTERN.fullmatch(normalized):
        msg = "phone must be 6-20 digits, optionally prefixed with +"
        raise vol.Invalid(msg)
    return normalized


def mask_phone_for_title(phone: str) -> str:
    """Mask a normalized phone number for config-entry titles."""
    normalized = phone.strip()
    if not normalized:
        return "***"

    prefix = "+" if normalized.startswith("+") else ""
    digits = normalized.lstrip("+")

    if len(digits) <= 4:
        return f"{prefix}***"
    if len(digits) <= 8:
        return f"{prefix}{digits[:2]}***{digits[-2:]}"
    return f"{prefix}{digits[:3]}****{digits[-4:]}"


def validate_password(password: Any) -> str:
    """Validate user-provided password value."""
    if not isinstance(password, str):
        msg = "password must be a string"
        raise vol.Invalid(msg)
    if not password or len(password) > _MAX_PASSWORD_LEN:
        msg = f"password length must be 1-{_MAX_PASSWORD_LEN}"
        raise vol.Invalid(msg)
    return password
