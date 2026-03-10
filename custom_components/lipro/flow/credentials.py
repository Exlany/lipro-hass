"""Credential helpers for Lipro config flows."""

from __future__ import annotations

import re
from typing import Any

import voluptuous as vol

_PHONE_INPUT_PATTERN = re.compile(r"^\+?\d{6,20}$")
_MAX_PASSWORD_LEN: int = 128
_MIN_PASSWORD_LEN: int = 6
_MAX_PHONE_LEN: int = 30


def normalize_phone(phone: Any) -> str:
    """Normalize and validate user-provided phone value.

    Validates:
    - Type must be string
    - Length must not exceed 30 chars (防止过长输入)
    - Format must be 6-20 digits with optional + prefix
    - No SQL injection characters allowed

    Args:
        phone: User input phone number

    Returns:
        Normalized phone string

    Raises:
        vol.Invalid: If validation fails
    """
    if not isinstance(phone, str):
        msg = "Phone number must be text"
        raise vol.Invalid(msg)

    normalized = phone.strip()

    # 防止过长输入（DoS攻击）
    if len(normalized) > _MAX_PHONE_LEN:
        msg = f"Phone number too long (max {_MAX_PHONE_LEN} characters)"
        raise vol.Invalid(msg)

    # 防止SQL注入和特殊字符
    if any(char in normalized for char in ("'", '"', ";", "--", "/*", "*/")):
        msg = "Phone number contains invalid characters"
        raise vol.Invalid(msg)

    if not _PHONE_INPUT_PATTERN.fullmatch(normalized):
        msg = "Phone number must be 6-20 digits (optionally starting with +)"
        raise vol.Invalid(msg)

    return normalized


def mask_phone_for_title(phone: str) -> str:
    """Mask a normalized phone number for config-entry titles.

    Args:
        phone: Normalized phone number

    Returns:
        Masked phone string for display
    """
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
    """Validate user-provided password value.

    Validates:
    - Type must be string
    - Length must be 6-128 characters
    - No null bytes or control characters

    Args:
        password: User input password

    Returns:
        Validated password string

    Raises:
        vol.Invalid: If validation fails
    """
    if not isinstance(password, str):
        msg = "Password must be text"
        raise vol.Invalid(msg)

    # 检查长度
    if len(password) < _MIN_PASSWORD_LEN:
        msg = f"Password too short (minimum {_MIN_PASSWORD_LEN} characters)"
        raise vol.Invalid(msg)

    if len(password) > _MAX_PASSWORD_LEN:
        msg = f"Password too long (maximum {_MAX_PASSWORD_LEN} characters)"
        raise vol.Invalid(msg)

    # 防止空字节和控制字符（安全风险）
    if "\x00" in password or any(ord(c) < 32 and c not in "\t\n\r" for c in password):
        msg = "Password contains invalid characters"
        raise vol.Invalid(msg)

    return password
