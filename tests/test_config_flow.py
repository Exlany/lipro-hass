"""Tests for Lipro config flow.

These tests require pytest-homeassistant-custom-component to provide the 'hass' fixture.
Install with: pip install pytest-homeassistant-custom-component

Note: On Windows, this may require Microsoft C++ Build Tools.
"""

from __future__ import annotations

from unittest.mock import AsyncMock, patch

from pytest_homeassistant_custom_component.common import MockConfigEntry

from custom_components.lipro.config_flow import CONF_PASSWORD_HASH
from custom_components.lipro.const import CONF_PHONE, CONF_PHONE_ID, DOMAIN
from custom_components.lipro.core.api import LiproApiError, LiproAuthError
from homeassistant import config_entries
from homeassistant.const import CONF_PASSWORD
from homeassistant.core import HomeAssistant
from homeassistant.data_entry_flow import AbortFlow, FlowResultType


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


async def test_form_user_recovers_after_invalid_auth(
    hass: HomeAssistant,
) -> None:
    """Test user flow can recover and finish after an auth error."""
    with patch(
        "custom_components.lipro.config_flow.LiproClient",
        autospec=True,
    ) as mock_client_class:
        mock_client = mock_client_class.return_value
        mock_client.login_with_hash = AsyncMock(
            side_effect=[
                LiproAuthError("Invalid credentials"),
                {
                    "access_token": "test_access_token",
                    "refresh_token": "test_refresh_token",
                    "user_id": 10001,
                    "biz_id": "test_biz_id",
                },
            ]
        )

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

        result = await hass.config_entries.flow.async_configure(
            result["flow_id"],
            {
                CONF_PHONE: "13800000000",
                CONF_PASSWORD: "correctpassword",
            },
        )
        await hass.async_block_till_done()

        assert result["type"] is FlowResultType.CREATE_ENTRY
        assert result["title"] == "Lipro (13800000000)"
        assert result["data"]["access_token"] == "test_access_token"
        assert mock_client.login_with_hash.await_count == 2


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


async def test_form_lipro_api_error_maps_to_unknown(
    hass: HomeAssistant,
) -> None:
    """Test form maps non-auth/non-connection LiproApiError to unknown."""
    with patch(
        "custom_components.lipro.config_flow.LiproClient",
        autospec=True,
    ) as mock_client_class:
        mock_client = mock_client_class.return_value
        mock_client.login_with_hash = AsyncMock(
            side_effect=LiproApiError("API failure")
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


async def test_form_abortflow_propagates(
    hass: HomeAssistant,
) -> None:
    """Test AbortFlow from login is propagated as flow abort."""
    with patch(
        "custom_components.lipro.config_flow.LiproClient",
        autospec=True,
    ) as mock_client_class:
        mock_client = mock_client_class.return_value
        mock_client.login_with_hash = AsyncMock(side_effect=AbortFlow("test_abort"))

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
        assert result["reason"] == "test_abort"


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


async def test_reauth_flow_missing_phone_id(
    hass: HomeAssistant,
    mock_lipro_client,
) -> None:
    """Test reauth flow shows unknown error when phone_id is missing."""
    entry = MockConfigEntry(
        domain=DOMAIN,
        title="Lipro (13800000000)",
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
    assert result["errors"] == {"base": "unknown"}
    mock_lipro_client.login_with_hash.assert_not_awaited()


async def test_reconfigure_flow_missing_phone_id(
    hass: HomeAssistant,
    mock_lipro_client,
) -> None:
    """Test reconfigure flow shows unknown error when phone_id is missing."""
    entry = MockConfigEntry(
        domain=DOMAIN,
        title="Lipro (13800000000)",
        data={
            CONF_PHONE: "13800000000",
            CONF_PASSWORD_HASH: "e10adc3949ba59abbe56e057f20f883e",
            # phone_id intentionally missing
            "access_token": "token",
            "refresh_token": "refresh",
            "user_id": 10001,
        },
        unique_id="lipro_10001",
    )
    entry.add_to_hass(hass)

    result = await hass.config_entries.flow.async_init(
        DOMAIN,
        context={
            "source": config_entries.SOURCE_RECONFIGURE,
            "entry_id": entry.entry_id,
        },
    )

    assert result["type"] is FlowResultType.FORM
    assert result["step_id"] == "reconfigure"

    result = await hass.config_entries.flow.async_configure(
        result["flow_id"],
        {
            CONF_PHONE: "13800000000",
            CONF_PASSWORD: "newpassword",
        },
    )

    assert result["type"] is FlowResultType.FORM
    assert result["step_id"] == "reconfigure"
    assert result["errors"] == {"base": "unknown"}
    mock_lipro_client.login_with_hash.assert_not_awaited()


async def test_reconfigure_flow_success(
    hass: HomeAssistant,
    mock_lipro_client,
) -> None:
    """Test reconfigure flow updates entry data and aborts successfully."""
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
        DOMAIN,
        context={
            "source": config_entries.SOURCE_RECONFIGURE,
            "entry_id": entry.entry_id,
        },
    )
    assert result["type"] is FlowResultType.FORM
    assert result["step_id"] == "reconfigure"

    result = await hass.config_entries.flow.async_configure(
        result["flow_id"],
        {
            CONF_PHONE: "13900000000",
            CONF_PASSWORD: "newpassword",
        },
    )
    await hass.async_block_till_done()

    assert result["type"] is FlowResultType.ABORT
    assert result["reason"] == "reconfigure_successful"
    assert entry.data[CONF_PHONE] == "13900000000"
    assert entry.data["access_token"] == "test_access_token"
    assert entry.data["refresh_token"] == "test_refresh_token"
    assert entry.data[CONF_PHONE_ID] == "550e8400-e29b-41d4-a716-446655440000"


async def test_reconfigure_flow_unique_id_mismatch(
    hass: HomeAssistant,
    mock_lipro_client,
) -> None:
    """Test reconfigure flow aborts when reconfigured account does not match."""
    entry = MockConfigEntry(
        domain=DOMAIN,
        title="Lipro (13800000000)",
        data={
            CONF_PHONE: "13800000000",
            CONF_PASSWORD_HASH: "e10adc3949ba59abbe56e057f20f883e",
            CONF_PHONE_ID: "550e8400-e29b-41d4-a716-446655440000",
            "access_token": "old_token",
            "refresh_token": "old_refresh",
            "user_id": 99999,
        },
        unique_id="lipro_99999",
    )
    entry.add_to_hass(hass)

    result = await hass.config_entries.flow.async_init(
        DOMAIN,
        context={
            "source": config_entries.SOURCE_RECONFIGURE,
            "entry_id": entry.entry_id,
        },
    )
    assert result["type"] is FlowResultType.FORM
    assert result["step_id"] == "reconfigure"

    result = await hass.config_entries.flow.async_configure(
        result["flow_id"],
        {
            CONF_PHONE: "13800000000",
            CONF_PASSWORD: "newpassword",
        },
    )

    assert result["type"] is FlowResultType.ABORT
    assert result["reason"] == "unique_id_mismatch"
    assert entry.data["user_id"] == 99999
    assert entry.data["access_token"] == "old_token"


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


async def test_options_flow_advanced_step(
    hass: HomeAssistant,
) -> None:
    """Test options flow advanced step and merged save behavior."""
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
        options={
            "scan_interval": 45,
            "mqtt_enabled": True,
            "enable_power_monitoring": True,
            "anonymous_share_enabled": True,
            "anonymous_share_errors": False,
            "power_query_interval": 60,
            "request_timeout": 20,
            "debug_mode": False,
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
            "scan_interval": 30,
            "mqtt_enabled": False,
            "enable_power_monitoring": False,
            "anonymous_share_enabled": True,
            "anonymous_share_errors": True,
            "show_advanced": True,
        },
    )
    assert result["type"] is FlowResultType.FORM
    assert result["step_id"] == "advanced"

    result = await hass.config_entries.options.async_configure(
        result["flow_id"],
        {
            "power_query_interval": 120,
            "request_timeout": 45,
            "debug_mode": True,
        },
    )
    assert result["type"] is FlowResultType.CREATE_ENTRY
    assert result["data"]["scan_interval"] == 30
    assert result["data"]["mqtt_enabled"] is False
    assert result["data"]["enable_power_monitoring"] is False
    assert result["data"]["power_query_interval"] == 120
    assert result["data"]["request_timeout"] == 45
    assert result["data"]["debug_mode"] is True
