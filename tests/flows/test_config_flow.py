"""Tests for Lipro config flow.

These tests require pytest-homeassistant-custom-component to provide the 'hass' fixture.
Install with: pip install pytest-homeassistant-custom-component

Note: On Windows, this may require Microsoft C++ Build Tools.
"""

from __future__ import annotations

import asyncio
from unittest.mock import AsyncMock, patch

import pytest
from pytest_homeassistant_custom_component.common import MockConfigEntry
import voluptuous as vol

from custom_components.lipro.config_flow import LiproConfigFlow
from custom_components.lipro.const.base import DOMAIN
from custom_components.lipro.const.config import (
    CONF_COMMAND_RESULT_VERIFY,
    CONF_DEBUG_MODE,
    CONF_DEVICE_FILTER_DID_LIST,
    CONF_DEVICE_FILTER_DID_MODE,
    CONF_DEVICE_FILTER_HOME_LIST,
    CONF_DEVICE_FILTER_HOME_MODE,
    CONF_DEVICE_FILTER_MODEL_LIST,
    CONF_DEVICE_FILTER_MODEL_MODE,
    CONF_DEVICE_FILTER_SSID_LIST,
    CONF_DEVICE_FILTER_SSID_MODE,
    CONF_LIGHT_TURN_ON_ON_ADJUST,
    CONF_PASSWORD_HASH,
    CONF_PHONE,
    CONF_PHONE_ID,
    CONF_POWER_QUERY_INTERVAL,
    CONF_REMEMBER_PASSWORD_HASH,
    CONF_ROOM_AREA_SYNC_FORCE,
    DEFAULT_COMMAND_RESULT_VERIFY,
    DEFAULT_POWER_QUERY_INTERVAL,
    DEVICE_FILTER_MODE_EXCLUDE,
    DEVICE_FILTER_MODE_INCLUDE,
    DEVICE_FILTER_MODE_OFF,
    MAX_DEVICE_FILTER_LIST_CHARS,
)
from custom_components.lipro.core.api import LiproApiError, LiproAuthError
from custom_components.lipro.flow.schemas import (
    STEP_REAUTH_DATA_SCHEMA,
    STEP_USER_DATA_SCHEMA,
    build_reconfigure_data_schema as _build_reconfigure_data_schema,
)
from homeassistant import config_entries
from homeassistant.const import CONF_PASSWORD
from homeassistant.core import HomeAssistant
from homeassistant.data_entry_flow import AbortFlow, FlowResultType
from homeassistant.helpers import selector


def _get_schema_field(schema: vol.Schema, key: str):
    """Return field validator for a voluptuous schema key."""
    for field, validator in schema.schema.items():
        if isinstance(field, (vol.Required, vol.Optional)) and field.schema == key:
            return validator
    return None


def _get_schema_marker(schema: vol.Schema, key: str):
    """Return marker metadata (required/optional) for a voluptuous schema key."""
    for field in schema.schema:
        if isinstance(field, (vol.Required, vol.Optional)) and field.schema == key:
            return field
    return None


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
        "custom_components.lipro.config_flow.LiproClient",
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
    assert result["errors"] == {CONF_PHONE: "invalid_auth"}


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
    assert result["errors"] == {CONF_PASSWORD: "invalid_auth"}


async def test_form_user_recovers_after_invalid_auth(
    hass: HomeAssistant,
) -> None:
    """Test user flow can recover and finish after an auth error."""
    with patch(
        "custom_components.lipro.config_flow.LiproClient",
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
        "custom_components.lipro.config_flow.LiproClient",
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
        "custom_components.lipro.config_flow.LiproClient",
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
        "custom_components.lipro.config_flow.LiproClient",
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
        "custom_components.lipro.config_flow.LiproClient",
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
    assert result["errors"] == {CONF_PASSWORD: "invalid_auth"}
    mock_lipro_client.login.assert_not_awaited()


async def test_reauth_flow_missing_phone_id(
    hass: HomeAssistant,
    mock_lipro_client,
) -> None:
    """Test reauth flow shows unknown error when phone_id is missing."""
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
    assert result["errors"] == {"base": "unknown"}
    mock_lipro_client.login.assert_not_awaited()


async def test_reconfigure_flow_missing_phone_id(
    hass: HomeAssistant,
    mock_lipro_client,
) -> None:
    """Test reconfigure flow shows unknown error when phone_id is missing."""
    entry = MockConfigEntry(
        domain=DOMAIN,
        title="Lipro (138****0000)",
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
    mock_lipro_client.login.assert_not_awaited()


async def test_reconfigure_flow_invalid_phone_sets_field_error(
    hass: HomeAssistant,
    mock_lipro_client,
) -> None:
    """Reconfigure should validate phone format before login."""
    entry = MockConfigEntry(
        domain=DOMAIN,
        title="Lipro (138****0000)",
        data={
            CONF_PHONE: "13800000000",
            CONF_PASSWORD_HASH: "e10adc3949ba59abbe56e057f20f883e",
            CONF_PHONE_ID: "550e8400-e29b-41d4-a716-446655440000",
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

    result = await hass.config_entries.flow.async_configure(
        result["flow_id"],
        {
            CONF_PHONE: "not-a-phone",
            CONF_PASSWORD: "newpassword",
        },
    )

    assert result["type"] is FlowResultType.FORM
    assert result["step_id"] == "reconfigure"
    assert result["errors"] == {CONF_PHONE: "invalid_auth"}
    mock_lipro_client.login.assert_not_awaited()


async def test_reconfigure_flow_invalid_password_sets_field_error(
    hass: HomeAssistant,
    mock_lipro_client,
) -> None:
    """Reconfigure should validate password format before login."""
    entry = MockConfigEntry(
        domain=DOMAIN,
        title="Lipro (138****0000)",
        data={
            CONF_PHONE: "13800000000",
            CONF_PASSWORD_HASH: "e10adc3949ba59abbe56e057f20f883e",
            CONF_PHONE_ID: "550e8400-e29b-41d4-a716-446655440000",
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

    result = await hass.config_entries.flow.async_configure(
        result["flow_id"],
        {
            CONF_PHONE: "13800000000",
            CONF_PASSWORD: "",
        },
    )

    assert result["type"] is FlowResultType.FORM
    assert result["step_id"] == "reconfigure"
    assert result["errors"] == {CONF_PASSWORD: "invalid_auth"}
    mock_lipro_client.login.assert_not_awaited()


async def test_reconfigure_flow_success(
    hass: HomeAssistant,
    mock_lipro_client,
) -> None:
    """Test reconfigure flow updates entry data and aborts successfully."""
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
        title="Lipro (138****0000)",
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
        title="Lipro (138****0000)",
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
    assert CONF_LIGHT_TURN_ON_ON_ADJUST not in result["data"]


async def test_options_flow_defaults_invalid_device_filter_modes_to_off_on_save(
    hass: HomeAssistant,
) -> None:
    """Options flow should coerce invalid device-filter modes to off on save."""
    entry = MockConfigEntry(
        domain=DOMAIN,
        title="Lipro (138****0000)",
        data={
            CONF_PHONE: "13800000000",
            CONF_PASSWORD_HASH: "e10adc3949ba59abbe56e057f20f883e",
            CONF_PHONE_ID: "550e8400-e29b-41d4-a716-446655440000",
            "access_token": "test_token",
            "refresh_token": "test_refresh",
            "user_id": 10001,
        },
        options={
            CONF_DEVICE_FILTER_HOME_MODE: "INCLUDE",
            CONF_DEVICE_FILTER_HOME_LIST: "Home A",
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
    assert result["data"][CONF_DEVICE_FILTER_HOME_MODE] == DEVICE_FILTER_MODE_OFF


async def test_options_flow_advanced_schema_defaults_invalid_mode_to_off(
    hass: HomeAssistant,
) -> None:
    """Advanced step should coerce invalid stored mode defaults to off."""
    entry = MockConfigEntry(
        domain=DOMAIN,
        title="Lipro (138****0000)",
        data={
            CONF_PHONE: "13800000000",
            CONF_PASSWORD_HASH: "e10adc3949ba59abbe56e057f20f883e",
            CONF_PHONE_ID: "550e8400-e29b-41d4-a716-446655440000",
            "access_token": "test_token",
            "refresh_token": "test_refresh",
            "user_id": 10001,
        },
        options={
            CONF_DEVICE_FILTER_HOME_MODE: "INCLUDE",
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

    data_schema = result["data_schema"]
    assert data_schema is not None
    marker = _get_schema_marker(data_schema, CONF_DEVICE_FILTER_HOME_MODE)
    assert isinstance(marker, vol.Required)
    default = marker.default() if callable(marker.default) else marker.default
    assert default == DEVICE_FILTER_MODE_OFF
    command_result_verify_marker = _get_schema_marker(
        data_schema, CONF_COMMAND_RESULT_VERIFY
    )
    assert isinstance(command_result_verify_marker, vol.Required)
    command_result_verify_default = (
        command_result_verify_marker.default()
        if callable(command_result_verify_marker.default)
        else command_result_verify_marker.default
    )
    assert command_result_verify_default is DEFAULT_COMMAND_RESULT_VERIFY

    power_query_interval_marker = _get_schema_marker(
        data_schema, CONF_POWER_QUERY_INTERVAL
    )
    assert isinstance(power_query_interval_marker, vol.Required)
    power_query_interval_default = (
        power_query_interval_marker.default()
        if callable(power_query_interval_marker.default)
        else power_query_interval_marker.default
    )
    assert power_query_interval_default == DEFAULT_POWER_QUERY_INTERVAL


async def test_options_flow_advanced_step(
    hass: HomeAssistant,
) -> None:
    """Test options flow advanced step and merged save behavior."""
    entry = MockConfigEntry(
        domain=DOMAIN,
        title="Lipro (138****0000)",
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
            CONF_LIGHT_TURN_ON_ON_ADJUST: True,
            CONF_ROOM_AREA_SYNC_FORCE: False,
            CONF_COMMAND_RESULT_VERIFY: False,
            "anonymous_share_enabled": True,
            "anonymous_share_errors": False,
            "power_query_interval": 60,
            "request_timeout": 20,
            CONF_DEBUG_MODE: False,
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
            CONF_DEBUG_MODE: True,
            CONF_LIGHT_TURN_ON_ON_ADJUST: False,
            CONF_ROOM_AREA_SYNC_FORCE: True,
            CONF_COMMAND_RESULT_VERIFY: True,
            CONF_DEVICE_FILTER_HOME_MODE: DEVICE_FILTER_MODE_INCLUDE,
            CONF_DEVICE_FILTER_HOME_LIST: "My Home",
            CONF_DEVICE_FILTER_MODEL_MODE: DEVICE_FILTER_MODE_EXCLUDE,
            CONF_DEVICE_FILTER_MODEL_LIST: "gateway",
            CONF_DEVICE_FILTER_SSID_MODE: DEVICE_FILTER_MODE_OFF,
            CONF_DEVICE_FILTER_SSID_LIST: "",
            CONF_DEVICE_FILTER_DID_MODE: DEVICE_FILTER_MODE_INCLUDE,
            CONF_DEVICE_FILTER_DID_LIST: "03ab5ccd7c000001,03ab5ccd7c000002",
        },
    )
    assert result["type"] is FlowResultType.CREATE_ENTRY
    assert result["data"]["scan_interval"] == 30
    assert result["data"]["mqtt_enabled"] is False
    assert result["data"]["enable_power_monitoring"] is False
    assert result["data"][CONF_LIGHT_TURN_ON_ON_ADJUST] is False
    assert result["data"][CONF_ROOM_AREA_SYNC_FORCE] is True
    assert result["data"][CONF_COMMAND_RESULT_VERIFY] is True
    assert result["data"]["power_query_interval"] == 120
    assert result["data"]["request_timeout"] == 45
    assert result["data"][CONF_DEBUG_MODE] is True
    assert result["data"][CONF_DEVICE_FILTER_HOME_MODE] == DEVICE_FILTER_MODE_INCLUDE
    assert result["data"][CONF_DEVICE_FILTER_HOME_LIST] == "My Home"
    assert result["data"][CONF_DEVICE_FILTER_MODEL_MODE] == DEVICE_FILTER_MODE_EXCLUDE
    assert result["data"][CONF_DEVICE_FILTER_MODEL_LIST] == "gateway"
    assert result["data"][CONF_DEVICE_FILTER_SSID_MODE] == DEVICE_FILTER_MODE_OFF
    assert result["data"][CONF_DEVICE_FILTER_SSID_LIST] == ""
    assert result["data"][CONF_DEVICE_FILTER_DID_MODE] == DEVICE_FILTER_MODE_INCLUDE
    assert (
        result["data"][CONF_DEVICE_FILTER_DID_LIST]
        == "03ab5ccd7c000001,03ab5ccd7c000002"
    )


async def test_options_flow_truncates_device_filter_list_string_inputs(
    hass: HomeAssistant,
) -> None:
    """Options flow should hard-cap device-filter list field length."""
    entry = MockConfigEntry(
        domain=DOMAIN,
        title="Lipro (138****0000)",
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
            CONF_DEBUG_MODE: True,
            CONF_LIGHT_TURN_ON_ON_ADJUST: False,
            CONF_ROOM_AREA_SYNC_FORCE: True,
            CONF_COMMAND_RESULT_VERIFY: True,
            CONF_DEVICE_FILTER_HOME_MODE: DEVICE_FILTER_MODE_OFF,
            CONF_DEVICE_FILTER_HOME_LIST: "",
            CONF_DEVICE_FILTER_MODEL_MODE: DEVICE_FILTER_MODE_OFF,
            CONF_DEVICE_FILTER_MODEL_LIST: "",
            CONF_DEVICE_FILTER_SSID_MODE: DEVICE_FILTER_MODE_OFF,
            CONF_DEVICE_FILTER_SSID_LIST: "",
            CONF_DEVICE_FILTER_DID_MODE: DEVICE_FILTER_MODE_INCLUDE,
            CONF_DEVICE_FILTER_DID_LIST: "x" * (MAX_DEVICE_FILTER_LIST_CHARS + 10),
        },
    )

    assert result["type"] is FlowResultType.CREATE_ENTRY
    assert (
        len(result["data"][CONF_DEVICE_FILTER_DID_LIST]) == MAX_DEVICE_FILTER_LIST_CHARS
    )


async def test_options_flow_coerces_non_string_device_filter_lists(
    hass: HomeAssistant,
) -> None:
    """Options flow should normalize non-string device-filter list values."""
    entry = MockConfigEntry(
        domain=DOMAIN,
        title="Lipro (138****0000)",
        data={
            CONF_PHONE: "13800000000",
            CONF_PASSWORD_HASH: "e10adc3949ba59abbe56e057f20f883e",
            CONF_PHONE_ID: "550e8400-e29b-41d4-a716-446655440000",
            "access_token": "test_token",
            "refresh_token": "test_refresh",
            "user_id": 10001,
        },
        options={
            CONF_DEVICE_FILTER_DID_LIST: ["a", "b"],
            CONF_DEVICE_FILTER_MODEL_LIST: ["x" * (MAX_DEVICE_FILTER_LIST_CHARS + 10)],
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
    assert result["data"][CONF_DEVICE_FILTER_DID_LIST] == "a, b"
    assert (
        len(result["data"][CONF_DEVICE_FILTER_MODEL_LIST])
        == MAX_DEVICE_FILTER_LIST_CHARS
    )
