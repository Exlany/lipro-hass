"""Tests for Lipro config flow.

These tests require pytest-homeassistant-custom-component to provide the 'hass' fixture.
Install with: pip install pytest-homeassistant-custom-component

Note: On Windows, this may require Microsoft C++ Build Tools.
"""

from __future__ import annotations

from custom_components.lipro.const.config import CONF_PHONE, CONF_REMEMBER_PASSWORD_HASH
from custom_components.lipro.flow.schemas import (
    STEP_REAUTH_DATA_SCHEMA,
    STEP_USER_DATA_SCHEMA,
    build_reconfigure_data_schema as _build_reconfigure_data_schema,
)
from homeassistant.const import CONF_PASSWORD
from homeassistant.helpers import selector

from .support import _get_schema_field


def test_user_schema_uses_text_and_password_selectors() -> None:
    """User step schema should keep HA selectors for regression safety."""
    phone_field = _get_schema_field(STEP_USER_DATA_SCHEMA, CONF_PHONE)
    password_field = _get_schema_field(STEP_USER_DATA_SCHEMA, CONF_PASSWORD)
    remember_field = _get_schema_field(
        STEP_USER_DATA_SCHEMA, CONF_REMEMBER_PASSWORD_HASH
    )

    assert isinstance(phone_field, selector.TextSelector)
    assert isinstance(password_field, selector.TextSelector)
    assert remember_field is bool
    assert password_field.config.get("type") in {
        selector.TextSelectorType.PASSWORD,
        selector.TextSelectorType.PASSWORD.value,
    }

def test_reauth_and_reconfigure_schema_use_password_selector() -> None:
    """Reauth/reconfigure schema should keep password selector."""
    reauth_password = _get_schema_field(STEP_REAUTH_DATA_SCHEMA, CONF_PASSWORD)
    reconfigure_password = _get_schema_field(
        _build_reconfigure_data_schema(
            "13800000000",
            default_remember_password_hash=False,
        ),
        CONF_PASSWORD,
    )

    assert isinstance(reauth_password, selector.TextSelector)
    assert isinstance(reconfigure_password, selector.TextSelector)
    assert reauth_password.config.get("type") in {
        selector.TextSelectorType.PASSWORD,
        selector.TextSelectorType.PASSWORD.value,
    }
    assert reconfigure_password.config.get("type") in {
        selector.TextSelectorType.PASSWORD,
        selector.TextSelectorType.PASSWORD.value,
    }
