"""Tests for Lipro config flow.

These tests require pytest-homeassistant-custom-component to provide the 'hass' fixture.
Install with: pip install pytest-homeassistant-custom-component

Note: On Windows, this may require Microsoft C++ Build Tools.
"""

from __future__ import annotations

from unittest.mock import AsyncMock, patch

from pytest_homeassistant_custom_component.common import MockConfigEntry

from custom_components.lipro.const.base import DOMAIN
from custom_components.lipro.const.config import (
    CONF_PASSWORD_HASH,
    CONF_PHONE,
    CONF_PHONE_ID,
)
from custom_components.lipro.core.auth import AuthSessionSnapshot
from homeassistant import config_entries
from homeassistant.const import CONF_PASSWORD
from homeassistant.core import HomeAssistant
from homeassistant.data_entry_flow import FlowResultType


async def test_reauth_flow(
    hass: HomeAssistant,
    mock_setup_entry: AsyncMock,
    mock_lipro_client,
) -> None:
    """Test reauth flow."""
    # Create an existing entry using MockConfigEntry
    entry = MockConfigEntry(
        domain=DOMAIN,
        title="Lipro (138****0000)",
        data={
            CONF_PHONE: "13800000000",
            CONF_PASSWORD_HASH: "e10adc3949ba59abbe56e057f20f883e",
            CONF_PHONE_ID: "550e8400-e29b-41d4-a716-446655440000",
            "access_token": "expired_token",
            "refresh_token": "expired_refresh",
            "user_id": 10001,
        },
        unique_id="lipro_10001",
    )
    entry.add_to_hass(hass)

    result = await hass.config_entries.flow.async_init(
        DOMAIN,
        context={
            "source": config_entries.SOURCE_REAUTH,
            "entry_id": entry.entry_id,
        },
        data=entry.data,
    )

    assert result["type"] is FlowResultType.FORM
    assert result["step_id"] == "reauth_confirm"
    placeholders = result["description_placeholders"]
    assert placeholders is not None
    assert placeholders["phone"] == "138****0000"

    result = await hass.config_entries.flow.async_configure(
        result["flow_id"],
        {
            CONF_PASSWORD: "newpassword",
        },
    )

    assert result["type"] is FlowResultType.ABORT
    assert result["reason"] == "reauth_successful"

    # Verify entry was updated
    assert entry.data["access_token"] == "test_access_token"
    assert entry.data["refresh_token"] == "test_refresh_token"

async def test_reauth_flow_user_mismatch_shows_error(
    hass: HomeAssistant,
    mock_lipro_client,
) -> None:
    """Reauth should fail when login resolves to a different user_id."""
    entry = MockConfigEntry(
        domain=DOMAIN,
        title="Lipro (138****0000)",
        data={
            CONF_PHONE: "13800000000",
            CONF_PASSWORD_HASH: "e10adc3949ba59abbe56e057f20f883e",
            CONF_PHONE_ID: "550e8400-e29b-41d4-a716-446655440000",
            "access_token": "expired_token",
            "refresh_token": "expired_refresh",
            "user_id": 10001,
        },
        unique_id="lipro_10001",
    )
    entry.add_to_hass(hass)

    mock_lipro_client.login.return_value = {
        "access_token": "test_access_token",
        "refresh_token": "test_refresh_token",
        "user_id": 10002,
        "biz_id": "test_biz_id",
    }

    result = await hass.config_entries.flow.async_init(
        DOMAIN,
        context={
            "source": config_entries.SOURCE_REAUTH,
            "entry_id": entry.entry_id,
        },
        data=entry.data,
    )

    result = await hass.config_entries.flow.async_configure(
        result["flow_id"],
        {
            CONF_PASSWORD: "newpassword",
        },
    )

    assert result["type"] is FlowResultType.FORM
    assert result["step_id"] == "reauth_confirm"
    assert result["errors"] == {"base": "reauth_user_mismatch"}

    # Verify entry was not updated.
    assert entry.data["access_token"] == "expired_token"
    assert entry.data["refresh_token"] == "expired_refresh"

async def test_reauth_flow_invalid_auth(
    hass: HomeAssistant,
    mock_lipro_client_auth_error,
) -> None:
    """Test reauth flow with invalid credentials."""
    entry = MockConfigEntry(
        domain=DOMAIN,
        title="Lipro (138****0000)",
        data={
            CONF_PHONE: "13800000000",
            CONF_PASSWORD_HASH: "e10adc3949ba59abbe56e057f20f883e",
            CONF_PHONE_ID: "550e8400-e29b-41d4-a716-446655440000",
            "access_token": "expired_token",
            "refresh_token": "expired_refresh",
            "user_id": 10001,
        },
        unique_id="lipro_10001",
    )
    entry.add_to_hass(hass)

    result = await hass.config_entries.flow.async_init(
        DOMAIN,
        context={
            "source": config_entries.SOURCE_REAUTH,
            "entry_id": entry.entry_id,
        },
        data=entry.data,
    )

    result = await hass.config_entries.flow.async_configure(
        result["flow_id"],
        {
            CONF_PASSWORD: "wrongpassword",
        },
    )

    assert result["type"] is FlowResultType.FORM
    assert result["errors"] == {"base": "invalid_auth"}

async def test_reauth_flow_invalid_password_sets_field_error(
    hass: HomeAssistant,
    mock_lipro_client,
) -> None:
    """Reauth with invalid password format should return field-level error."""
    entry = MockConfigEntry(
        domain=DOMAIN,
        title="Lipro (138****0000)",
        data={
            CONF_PHONE: "13800000000",
            CONF_PASSWORD_HASH: "e10adc3949ba59abbe56e057f20f883e",
            CONF_PHONE_ID: "550e8400-e29b-41d4-a716-446655440000",
            "access_token": "expired_token",
            "refresh_token": "expired_refresh",
            "user_id": 10001,
        },
        unique_id="lipro_10001",
    )
    entry.add_to_hass(hass)

    result = await hass.config_entries.flow.async_init(
        DOMAIN,
        context={
            "source": config_entries.SOURCE_REAUTH,
            "entry_id": entry.entry_id,
        },
        data=entry.data,
    )

    result = await hass.config_entries.flow.async_configure(
        result["flow_id"],
        {CONF_PASSWORD: ""},
    )

    assert result["type"] is FlowResultType.FORM
    assert result["step_id"] == "reauth_confirm"
    assert result["errors"] == {CONF_PASSWORD: "invalid_password"}
    mock_lipro_client.login.assert_not_awaited()

async def test_reauth_flow_missing_phone_id(
    hass: HomeAssistant,
    mock_lipro_client,
) -> None:
    """Test reauth flow shows invalid_entry when phone_id is missing."""
    entry = MockConfigEntry(
        domain=DOMAIN,
        title="Lipro (138****0000)",
        data={
            CONF_PHONE: "13800000000",
            CONF_PASSWORD_HASH: "e10adc3949ba59abbe56e057f20f883e",
            # phone_id intentionally missing
            "access_token": "expired_token",
            "refresh_token": "expired_refresh",
            "user_id": 10001,
        },
        unique_id="lipro_10001",
    )
    entry.add_to_hass(hass)

    result = await hass.config_entries.flow.async_init(
        DOMAIN,
        context={
            "source": config_entries.SOURCE_REAUTH,
            "entry_id": entry.entry_id,
        },
        data=entry.data,
    )
    assert result["type"] is FlowResultType.FORM
    assert result["step_id"] == "reauth_confirm"

    result = await hass.config_entries.flow.async_configure(
        result["flow_id"],
        {
            CONF_PASSWORD: "newpassword",
        },
    )

    assert result["type"] is FlowResultType.FORM
    assert result["step_id"] == "reauth_confirm"
    assert result["errors"] == {"base": "invalid_entry"}
    mock_lipro_client.login.assert_not_awaited()


async def test_reauth_flow_invalid_auth_session_projection_maps_to_invalid_response(
    hass: HomeAssistant,
) -> None:
    """Reauth should fail closed when auth-session projection is malformed."""
    entry = MockConfigEntry(
        domain=DOMAIN,
        title="Lipro (138****0000)",
        data={
            CONF_PHONE: "13800000000",
            CONF_PASSWORD_HASH: "e10adc3949ba59abbe56e057f20f883e",
            CONF_PHONE_ID: "550e8400-e29b-41d4-a716-446655440000",
            "access_token": "expired_token",
            "refresh_token": "expired_refresh",
            "user_id": 10001,
        },
        unique_id="lipro_10001",
    )
    entry.add_to_hass(hass)

    with patch(
        "custom_components.lipro.config_flow.LiproConfigFlow._async_do_login",
        AsyncMock(
            return_value=AuthSessionSnapshot(
                access_token=None,
                refresh_token="refresh",
                user_id=10001,
                expires_at=123.0,
                phone_id="phone-id",
                biz_id="biz-id",
            )
        ),
    ):
        result = await hass.config_entries.flow.async_init(
            DOMAIN,
            context={
                "source": config_entries.SOURCE_REAUTH,
                "entry_id": entry.entry_id,
            },
            data=entry.data,
        )

        result = await hass.config_entries.flow.async_configure(
            result["flow_id"],
            {CONF_PASSWORD: "newpassword"},
        )

    assert result["type"] is FlowResultType.FORM
    assert result["step_id"] == "reauth_confirm"
    assert result["errors"] == {"base": "invalid_response"}
