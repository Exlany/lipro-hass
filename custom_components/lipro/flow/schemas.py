"""Voluptuous schemas for the Lipro config flow."""

from __future__ import annotations

import voluptuous as vol

from homeassistant.const import CONF_PASSWORD
from homeassistant.helpers import selector

from ..const.config import (
    CONF_PHONE,
    CONF_REMEMBER_PASSWORD_HASH,
    DEFAULT_REMEMBER_PASSWORD_HASH,
)


def text_selector() -> selector.TextSelector:
    """Create a plain text selector."""
    return selector.TextSelector(
        selector.TextSelectorConfig(type=selector.TextSelectorType.TEXT)
    )


def password_selector() -> selector.TextSelector:
    """Create a password selector."""
    return selector.TextSelector(
        selector.TextSelectorConfig(type=selector.TextSelectorType.PASSWORD)
    )


STEP_USER_DATA_SCHEMA = vol.Schema(
    {
        vol.Required(CONF_PHONE): text_selector(),
        vol.Required(CONF_PASSWORD): password_selector(),
        vol.Optional(
            CONF_REMEMBER_PASSWORD_HASH,
            default=DEFAULT_REMEMBER_PASSWORD_HASH,
        ): bool,
    },
)
STEP_REAUTH_DATA_SCHEMA = vol.Schema({vol.Required(CONF_PASSWORD): password_selector()})


def build_reconfigure_data_schema(
    default_phone: str,
    *,
    default_remember_password_hash: bool,
) -> vol.Schema:
    """Build schema for the reconfigure step."""
    return vol.Schema(
        {
            vol.Required(CONF_PHONE, default=default_phone): text_selector(),
            vol.Required(CONF_PASSWORD): password_selector(),
            vol.Optional(
                CONF_REMEMBER_PASSWORD_HASH,
                default=default_remember_password_hash,
            ): bool,
        },
    )
