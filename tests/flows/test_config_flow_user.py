"""Tests for Lipro config flow.

These tests require pytest-homeassistant-custom-component to provide the 'hass' fixture.
Install with: pip install pytest-homeassistant-custom-component

Note: On Windows, this may require Microsoft C++ Build Tools.
"""

from __future__ import annotations

import asyncio
from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from pytest_homeassistant_custom_component.common import MockConfigEntry

from custom_components.lipro.config_flow import LiproConfigFlow
from custom_components.lipro.const.base import DOMAIN
from custom_components.lipro.const.config import (
    CONF_COMMAND_RESULT_VERIFY,
    CONF_PASSWORD_HASH,
    CONF_PHONE,
    CONF_PHONE_ID,
    CONF_REMEMBER_PASSWORD_HASH,
)
from custom_components.lipro.core.api import LiproApiError, LiproAuthError
from custom_components.lipro.core.auth import AuthSessionSnapshot
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
            CONF_REMEMBER_PASSWORD_HASH: True,
        },
    )
    await hass.async_block_till_done()

    assert result["type"] is FlowResultType.CREATE_ENTRY
    assert result["title"] == "Lipro (138****0000)"
    assert result["data"][CONF_PHONE] == "13800000000"
    # Password is stored as hash, not plain text
    assert result["data"][CONF_REMEMBER_PASSWORD_HASH] is True
    assert CONF_PASSWORD_HASH in result["data"]
    assert result["data"]["access_token"] == "test_access_token"
    assert result["data"]["refresh_token"] == "test_refresh_token"
    assert result["data"]["user_id"] == 10001
    assert CONF_PHONE_ID in result["data"]
    created_entry = hass.config_entries.async_entries(DOMAIN)[0]
    assert created_entry.options[CONF_COMMAND_RESULT_VERIFY] is True
    assert len(mock_setup_entry.mock_calls) == 1
    mock_lipro_client.login.assert_awaited_once()
    assert mock_lipro_client.login.await_args.kwargs["password_is_hashed"] is True

async def test_form_user_without_remember_password_does_not_store_hash(
    hass: HomeAssistant,
    mock_setup_entry: AsyncMock,
    mock_lipro_client,
) -> None:
    """Remember-password toggle should control whether password hash is persisted."""
    result = await hass.config_entries.flow.async_init(
        DOMAIN, context={"source": config_entries.SOURCE_USER}
    )
    assert result["type"] is FlowResultType.FORM
    assert result["step_id"] == "user"

    result = await hass.config_entries.flow.async_configure(
        result["flow_id"],
        {
            CONF_PHONE: "13800000000",
            CONF_PASSWORD: "testpassword",
            CONF_REMEMBER_PASSWORD_HASH: False,
        },
    )
    await hass.async_block_till_done()

    assert result["type"] is FlowResultType.CREATE_ENTRY
    assert result["data"][CONF_REMEMBER_PASSWORD_HASH] is False
    assert CONF_PASSWORD_HASH not in result["data"]

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

async def test_form_user_reuses_phone_id_across_retries(hass: HomeAssistant) -> None:
    """User flow should reuse phone_id when the user retries credentials."""
    from custom_components.lipro.core.api import LiproAuthError

    with patch(
        "custom_components.lipro.config_flow.LiproProtocolFacade",
        autospec=True,
    ) as mock_client_class:
        mock_client = mock_client_class.return_value
        mock_client.login = AsyncMock(
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
            DOMAIN,
            context={"source": config_entries.SOURCE_USER},
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
                CONF_PASSWORD: "testpassword",
            },
        )
        await hass.async_block_till_done()

        assert result["type"] is FlowResultType.CREATE_ENTRY
        assert len(mock_client_class.call_args_list) == 2
        phone_id_1 = mock_client_class.call_args_list[0].args[0]
        phone_id_2 = mock_client_class.call_args_list[1].args[0]
        assert phone_id_1 == phone_id_2

async def test_form_invalid_phone_sets_field_error(hass: HomeAssistant) -> None:
    """Invalid phone format should highlight the phone field."""
    result = await hass.config_entries.flow.async_init(
        DOMAIN, context={"source": config_entries.SOURCE_USER}
    )

    result = await hass.config_entries.flow.async_configure(
        result["flow_id"],
        {
            CONF_PHONE: "not-a-phone",
            CONF_PASSWORD: "testpassword",
        },
    )

    assert result["type"] is FlowResultType.FORM
    assert result["errors"] == {CONF_PHONE: "invalid_phone"}

async def test_form_invalid_password_sets_field_error(hass: HomeAssistant) -> None:
    """Invalid password format should highlight the password field."""
    result = await hass.config_entries.flow.async_init(
        DOMAIN, context={"source": config_entries.SOURCE_USER}
    )

    result = await hass.config_entries.flow.async_configure(
        result["flow_id"],
        {
            CONF_PHONE: "13800000000",
            CONF_PASSWORD: "",
        },
    )

    assert result["type"] is FlowResultType.FORM
    assert result["errors"] == {CONF_PASSWORD: "invalid_password"}

async def test_form_user_recovers_after_invalid_auth(
    hass: HomeAssistant,
) -> None:
    """Test user flow can recover and finish after an auth error."""
    with patch(
        "custom_components.lipro.config_flow.LiproProtocolFacade",
        autospec=True,
    ) as mock_client_class:
        mock_client = mock_client_class.return_value
        mock_client.login = AsyncMock(
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
        assert result["title"] == "Lipro (138****0000)"
        assert result["data"]["access_token"] == "test_access_token"
        assert mock_client.login.await_count == 2

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

async def test_form_malformed_login_response(
    hass: HomeAssistant,
) -> None:
    """Test form shows unknown error on malformed login response."""
    with patch(
        "custom_components.lipro.config_flow.LiproProtocolFacade",
        autospec=True,
    ) as mock_client_class:
        mock_client = mock_client_class.return_value
        mock_client.login = AsyncMock(side_effect=ValueError("bad payload"))

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

async def test_form_unexpected_error_maps_to_unknown(
    hass: HomeAssistant,
) -> None:
    """Test truly unexpected exceptions map to unknown form error."""
    with patch(
        "custom_components.lipro.config_flow.LiproProtocolFacade",
        autospec=True,
    ) as mock_client_class:
        mock_client = mock_client_class.return_value
        mock_client.login = AsyncMock(side_effect=RuntimeError("boom"))

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
        "custom_components.lipro.config_flow.LiproProtocolFacade",
        autospec=True,
    ) as mock_client_class:
        mock_client = mock_client_class.return_value
        mock_client.login = AsyncMock(side_effect=LiproApiError("API failure"))

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
        "custom_components.lipro.config_flow.LiproProtocolFacade",
        autospec=True,
    ) as mock_client_class:
        mock_client = mock_client_class.return_value
        mock_client.login = AsyncMock(side_effect=AbortFlow("test_abort"))

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

async def test_async_try_login_propagates_cancelled_error(
    hass: HomeAssistant,
) -> None:
    """CancelledError from login should always propagate."""
    flow = LiproConfigFlow()
    flow.hass = hass

    with (
        patch.object(
            flow,
            "_async_do_login",
            AsyncMock(side_effect=asyncio.CancelledError()),
        ),
        pytest.raises(asyncio.CancelledError),
    ):
        await flow._async_try_login(
            "13800000000",
            "hashed-password",
            "phone-id",
            {},
            "login",
        )

async def test_async_do_login_uses_shared_headless_boot_contract(
    hass: HomeAssistant,
) -> None:
    """Config flow login should inward to the shared headless boot seam."""
    flow = LiproConfigFlow()
    flow.hass = hass
    auth_session = AuthSessionSnapshot(
        access_token='access',
        refresh_token='refresh',
        user_id=10001,
        expires_at=123.0,
        phone_id='phone-id',
        biz_id='biz-id',
    )
    boot_context = MagicMock(name='boot_context')
    boot_context.async_login_with_password_hash = AsyncMock(return_value=auth_session)

    with (
        patch(
            'custom_components.lipro.config_flow.async_get_clientsession',
            return_value=MagicMock(name='session'),
        ) as mock_get_session,
        patch(
            'custom_components.lipro.config_flow.build_headless_boot_context',
            return_value=boot_context,
        ) as mock_build,
    ):
        result = await flow._async_do_login(
            '13800000000',
            'hashed-password',
            'phone-id',
        )

    assert result == auth_session
    mock_get_session.assert_called_once_with(hass)
    mock_build.assert_called_once()
    seed, session = mock_build.call_args.args
    assert seed.phone == '13800000000'
    assert seed.phone_id == 'phone-id'
    assert seed.password_hash == 'hashed-password'
    assert session is mock_get_session.return_value
    boot_context.async_login_with_password_hash.assert_awaited_once_with()

async def test_form_already_configured(
    hass: HomeAssistant,
    mock_setup_entry: AsyncMock,
    mock_lipro_client,
) -> None:
    """Test form aborts when account already configured."""
    # Create an existing entry using MockConfigEntry
    entry = MockConfigEntry(
        domain=DOMAIN,
        title="Lipro (138****0000)",
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
