"""Submission helpers for Lipro config-flow steps."""

from __future__ import annotations

from collections.abc import Mapping
from dataclasses import dataclass
import logging

import voluptuous as vol

from homeassistant.config_entries import ConfigEntry
from homeassistant.const import CONF_PASSWORD

from ..const.config import (
    CONF_PASSWORD_HASH,
    CONF_PHONE,
    CONF_PHONE_ID,
    CONF_REMEMBER_PASSWORD_HASH,
    CONF_USER_ID,
    DEFAULT_REMEMBER_PASSWORD_HASH,
)
from .credentials import mask_phone_for_title, normalize_phone, validate_password
from .login import hash_password

type FlowErrors = dict[str, str]


@dataclass(frozen=True, slots=True)
class UserFlowSubmission:
    """Validated payload for the user config-flow step."""

    phone: str
    password_hash: str
    remember_password_hash: bool


@dataclass(frozen=True, slots=True)
class ExistingEntrySubmission:
    """Validated payload for reauth/reconfigure entry-bound steps."""

    phone: str
    phone_id: str
    password_hash: str
    remember_password_hash: bool


def _validate_phone_input(
    raw_phone: object,
    *,
    logger: logging.Logger,
    context_name: str,
) -> tuple[str | None, str | None]:
    """Validate one phone field and return normalized value or field error."""
    try:
        return normalize_phone(raw_phone), None
    except vol.Invalid as err:
        logger.debug("Phone validation failed during %s: %s", context_name, err)
        return None, "invalid_phone"


def _validate_password_input(
    raw_password: object,
    *,
    logger: logging.Logger,
    context_name: str,
) -> tuple[str | None, str | None]:
    """Validate one password field and return value or field error."""
    try:
        return validate_password(raw_password), None
    except vol.Invalid as err:
        logger.debug("Password validation failed during %s: %s", context_name, err)
        return None, "invalid_password"


def _resolve_entry_phone_id(
    entry: ConfigEntry,
    *,
    logger: logging.Logger,
    context_name: str,
) -> str | None:
    """Return one stored phone_id only when the persisted entry data is valid."""
    raw_phone_id = entry.data.get(CONF_PHONE_ID)
    if isinstance(raw_phone_id, str) and raw_phone_id:
        return raw_phone_id

    logger.error(
        "Missing or invalid phone_id in %s entry, please remove and re-add the integration",
        context_name,
    )
    return None


def resolve_entry_remember_password_hash(entry_data: Mapping[str, object]) -> bool:
    """Resolve whether one entry should persist the password hash."""
    return bool(
        entry_data.get(
            CONF_REMEMBER_PASSWORD_HASH,
            CONF_PASSWORD_HASH in entry_data,
        )
    )


def resolve_reauth_expected_user_id(reauth_entry: ConfigEntry) -> int | None:
    """Resolve the expected user ID for reauth consistency checks."""
    raw_user_id = reauth_entry.data.get(CONF_USER_ID)
    if isinstance(raw_user_id, int) and not isinstance(raw_user_id, bool):
        return raw_user_id

    if not isinstance(reauth_entry.unique_id, str) or not reauth_entry.unique_id:
        return None

    unique_id = reauth_entry.unique_id.strip()
    if not unique_id.startswith("lipro_"):
        return None

    suffix = unique_id.removeprefix("lipro_").strip()
    if not suffix.isdecimal():
        return None
    return int(suffix)


def build_reauth_description_placeholders(
    reauth_entry: ConfigEntry,
) -> dict[str, str]:
    """Build reauth form placeholders from one config entry."""
    raw_phone = reauth_entry.data.get(CONF_PHONE, "")
    masked_phone = (
        mask_phone_for_title(raw_phone) if isinstance(raw_phone, str) else "***"
    )
    return {"phone": masked_phone}


def validate_user_submission(
    user_input: Mapping[str, object],
    *,
    logger: logging.Logger,
) -> tuple[UserFlowSubmission | None, FlowErrors]:
    """Validate user-step input and project it to one typed submission."""
    errors: FlowErrors = {}

    phone, phone_error = _validate_phone_input(
        user_input.get(CONF_PHONE),
        logger=logger,
        context_name="user",
    )
    if phone_error is not None:
        errors[CONF_PHONE] = phone_error

    password, password_error = _validate_password_input(
        user_input.get(CONF_PASSWORD),
        logger=logger,
        context_name="user",
    )
    if password_error is not None:
        errors[CONF_PASSWORD] = password_error

    if errors or phone is None or password is None:
        return None, errors

    remember_password_hash = bool(
        user_input.get(
            CONF_REMEMBER_PASSWORD_HASH,
            DEFAULT_REMEMBER_PASSWORD_HASH,
        )
    )
    return (
        UserFlowSubmission(
            phone=phone,
            password_hash=hash_password(password),
            remember_password_hash=remember_password_hash,
        ),
        errors,
    )


def validate_reauth_submission(
    reauth_entry: ConfigEntry,
    user_input: Mapping[str, object],
    *,
    logger: logging.Logger,
) -> tuple[ExistingEntrySubmission | None, FlowErrors]:
    """Validate reauth-step input and bind it to the stored entry identity."""
    errors: FlowErrors = {}

    raw_phone = reauth_entry.data.get(CONF_PHONE, "")
    phone_id = _resolve_entry_phone_id(
        reauth_entry,
        logger=logger,
        context_name="reauth",
    )
    if not raw_phone or phone_id is None:
        logger.error(
            "Missing phone or phone_id in reauth entry, "
            "please remove and re-add the integration"
        )
        errors["base"] = "unknown"
        return None, errors

    phone, phone_error = _validate_phone_input(
        raw_phone,
        logger=logger,
        context_name="reauth",
    )
    if phone_error is not None or phone is None:
        errors["base"] = "unknown"
        return None, errors

    password, password_error = _validate_password_input(
        user_input.get(CONF_PASSWORD),
        logger=logger,
        context_name="reauth",
    )
    if password_error is not None or password is None:
        errors[CONF_PASSWORD] = "invalid_password"
        return None, errors

    return (
        ExistingEntrySubmission(
            phone=phone,
            phone_id=phone_id,
            password_hash=hash_password(password),
            remember_password_hash=resolve_entry_remember_password_hash(
                reauth_entry.data
            ),
        ),
        errors,
    )


def validate_reconfigure_submission(
    reconfigure_entry: ConfigEntry,
    user_input: Mapping[str, object],
    *,
    logger: logging.Logger,
) -> tuple[ExistingEntrySubmission | None, FlowErrors]:
    """Validate reconfigure-step input and bind it to the target entry."""
    errors: FlowErrors = {}

    phone, phone_error = _validate_phone_input(
        user_input.get(CONF_PHONE),
        logger=logger,
        context_name="reconfigure",
    )
    if phone_error is not None:
        errors[CONF_PHONE] = phone_error

    password, password_error = _validate_password_input(
        user_input.get(CONF_PASSWORD),
        logger=logger,
        context_name="reconfigure",
    )
    if password_error is not None:
        errors[CONF_PASSWORD] = password_error

    if errors or phone is None or password is None:
        return None, errors

    phone_id = _resolve_entry_phone_id(
        reconfigure_entry,
        logger=logger,
        context_name="reconfigure",
    )
    if phone_id is None:
        errors["base"] = "unknown"
        return None, errors

    remember_password_hash = bool(
        user_input.get(
            CONF_REMEMBER_PASSWORD_HASH,
            resolve_entry_remember_password_hash(reconfigure_entry.data),
        )
    )
    return (
        ExistingEntrySubmission(
            phone=phone,
            phone_id=phone_id,
            password_hash=hash_password(password),
            remember_password_hash=remember_password_hash,
        ),
        errors,
    )
