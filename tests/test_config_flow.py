"""Tests for Lipro config flow.

These tests require pytest-homeassistant-custom-component to provide the 'hass' fixture.
Install with: pip install pytest-homeassistant-custom-component

Note: On Windows, this may require Microsoft C++ Build Tools.
"""

from __future__ import annotations

from unittest.mock import AsyncMock, patch

import pytest

# Check if full HA test environment is available
try:
    from pytest_homeassistant_custom_component.common import MockConfigEntry

    HAS_HA_TEST_ENV = True
except ImportError:
    HAS_HA_TEST_ENV = False

# Skip all tests if HA test environment is not available
pytestmark = pytest.mark.skipif(
    not HAS_HA_TEST_ENV,
    reason="Requires pytest-homeassistant-custom-component",
)

from custom_components.lipro.config_flow import CONF_PASSWORD_HASH
from custom_components.lipro.const import CONF_PHONE, CONF_PHONE_ID, DOMAIN
from homeassistant import config_entries
from homeassistant.const import CONF_PASSWORD
from homeassistant.core import HomeAssistant
from homeassistant.data_entry_flow import FlowResultType


async def test_form_user(
    hass: HomeAssistant,
    mock_setup_entry: AsyncMock,
    mock_lipro_client,
) -> None:
    """Test user config flow shows form and creates entry."""
    result = await hass.config_entries.flow.async_init(
        DOMAIN, context={"source": config_entries.SOURCE_USER}
    )
    assert result["type"] is FlowResultType.FORM
    assert result["step_id"] == "user"
    assert result["errors"] == {}

    result = await hass.config_entries.flow.async_configure(
        result["flow_id"],
        {
            CONF_PHONE: "13800000000",
            CONF_PASSWORD: "testpassword",
        },
    )
    await hass.async_block_till_done()

    assert result["type"] is FlowResultType.CREATE_ENTRY
    assert result["title"] == "Lipro (13800000000)"
    assert result["data"][CONF_PHONE] == "13800000000"
    # Password is stored as hash, not plain text
    assert CONF_PASSWORD_HASH in result["data"]
    assert result["data"]["access_token"] == "test_access_token"
    assert result["data"]["refresh_token"] == "test_refresh_token"
    assert result["data"]["user_id"] == 10001
    assert CONF_PHONE_ID in result["data"]
    assert len(mock_setup_entry.mock_calls) == 1


async def test_form_invalid_auth(
    hass: HomeAssistant,
    mock_lipro_client_auth_error,
) -> None:
    """Test form shows error on invalid auth."""
    result = await hass.config_entries.flow.async_init(
        DOMAIN, context={"source": config_entries.SOURCE_USER}
    )

    result = await hass.config_entries.flow.async_configure(
        result["flow_id"],
        {
            CONF_PHONE: "13800000000",
            CONF_PASSWORD: "wrongpassword",
        },
    )

    assert result["type"] is FlowResultType.FORM
    assert result["errors"] == {"base": "invalid_auth"}


async def test_form_cannot_connect(
    hass: HomeAssistant,
    mock_lipro_client_connection_error,
) -> None:
    """Test form shows error on connection failure."""
    result = await hass.config_entries.flow.async_init(
        DOMAIN, context={"source": config_entries.SOURCE_USER}
    )

    result = await hass.config_entries.flow.async_configure(
        result["flow_id"],
        {
            CONF_PHONE: "13800000000",
            CONF_PASSWORD: "testpassword",
        },
    )

    assert result["type"] is FlowResultType.FORM
    assert result["errors"] == {"base": "cannot_connect"}


async def test_form_unknown_error(
    hass: HomeAssistant,
) -> None:
    """Test form shows error on unknown exception."""
    with patch(
        "custom_components.lipro.config_flow.LiproClient",
        autospec=True,
    ) as mock_client_class:
        mock_client = mock_client_class.return_value
        mock_client.login_with_hash = AsyncMock(
            side_effect=Exception("Unexpected error")
        )

        result = await hass.config_entries.flow.async_init(
            DOMAIN, context={"source": config_entries.SOURCE_USER}
        )

        result = await hass.config_entries.flow.async_configure(
            result["flow_id"],
            {
                CONF_PHONE: "13800000000",
                CONF_PASSWORD: "testpassword",
            },
        )

        assert result["type"] is FlowResultType.FORM
        assert result["errors"] == {"base": "unknown"}


async def test_form_already_configured(
    hass: HomeAssistant,
    mock_setup_entry: AsyncMock,
    mock_lipro_client,
) -> None:
    """Test form aborts when account already configured."""
    # Create an existing entry using MockConfigEntry
    entry = MockConfigEntry(
        domain=DOMAIN,
        title="Lipro (13800000000)",
        data={
            CONF_PHONE: "13800000000",
            CONF_PASSWORD_HASH: "e10adc3949ba59abbe56e057f20f883e",
            CONF_PHONE_ID: "550e8400-e29b-41d4-a716-446655440000",
            "access_token": "old_token",
            "refresh_token": "old_refresh",
            "user_id": 10001,
        },
        unique_id="lipro_10001",
    )
    entry.add_to_hass(hass)

    result = await hass.config_entries.flow.async_init(
        DOMAIN, context={"source": config_entries.SOURCE_USER}
    )

    result = await hass.config_entries.flow.async_configure(
        result["flow_id"],
        {
            CONF_PHONE: "13800000000",
            CONF_PASSWORD: "testpassword",
        },
    )

    assert result["type"] is FlowResultType.ABORT
    assert result["reason"] == "already_configured"


async def test_reauth_flow(
    hass: HomeAssistant,
    mock_setup_entry: AsyncMock,
    mock_lipro_client,
) -> None:
    """Test reauth flow."""
    # Create an existing entry using MockConfigEntry
    entry = MockConfigEntry(
        domain=DOMAIN,
        title="Lipro (13800000000)",
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


async def test_reauth_flow_invalid_auth(
    hass: HomeAssistant,
    mock_lipro_client_auth_error,
) -> None:
    """Test reauth flow with invalid credentials."""
    entry = MockConfigEntry(
        domain=DOMAIN,
        title="Lipro (13800000000)",
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


async def test_options_flow(
    hass: HomeAssistant,
) -> None:
    """Test options flow."""
    entry = MockConfigEntry(
        domain=DOMAIN,
        title="Lipro (13800000000)",
        data={
            CONF_PHONE: "13800000000",
            CONF_PASSWORD_HASH: "e10adc3949ba59abbe56e057f20f883e",
            CONF_PHONE_ID: "550e8400-e29b-41d4-a716-446655440000",
            "access_token": "test_token",
            "refresh_token": "test_refresh",
            "user_id": 10001,
        },
        unique_id="lipro_10001",
    )
    entry.add_to_hass(hass)

    result = await hass.config_entries.options.async_init(entry.entry_id)

    assert result["type"] is FlowResultType.FORM
    assert result["step_id"] == "init"

    result = await hass.config_entries.options.async_configure(
        result["flow_id"],
        {
            "scan_interval": 60,
            "anonymous_share_enabled": False,
            "anonymous_share_errors": True,
        },
    )

    assert result["type"] is FlowResultType.CREATE_ENTRY
    assert result["data"]["scan_interval"] == 60
