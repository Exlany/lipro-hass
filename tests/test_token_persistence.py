"""Tests for runtime token persistence callbacks."""

from __future__ import annotations

from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from pytest_homeassistant_custom_component.common import MockConfigEntry

from custom_components.lipro import _build_entry_auth_context
from custom_components.lipro.const import (
    CONF_ACCESS_TOKEN,
    CONF_EXPIRES_AT,
    CONF_PASSWORD_HASH,
    CONF_PHONE,
    CONF_PHONE_ID,
    CONF_REFRESH_TOKEN,
    CONF_USER_ID,
    DOMAIN,
)


@pytest.mark.asyncio
async def test_refresh_token_persists_config_entry_tokens(hass) -> None:
    """refresh_token should persist rotated tokens via auth-manager callback."""
    entry = MockConfigEntry(
        domain=DOMAIN,
        data={
            CONF_PHONE_ID: "phone-id",
            CONF_PHONE: "13800000000",
            CONF_PASSWORD_HASH: "hashed-password",
            CONF_ACCESS_TOKEN: "old_access",
            CONF_REFRESH_TOKEN: "old_refresh",
            CONF_USER_ID: 10001,
        },
    )
    entry.add_to_hass(hass)

    with patch(
        "custom_components.lipro.async_get_clientsession",
        return_value=MagicMock(),
    ):
        client, auth_manager = _build_entry_auth_context(hass, entry)

    async def _fake_refresh_access_token() -> dict[str, object]:
        client.set_tokens("new_access", "new_refresh", user_id=10001)
        return {
            CONF_ACCESS_TOKEN: "new_access",
            CONF_REFRESH_TOKEN: "new_refresh",
            CONF_USER_ID: 10001,
        }

    with (
        patch.object(
            client,
            "refresh_access_token",
            new=AsyncMock(side_effect=_fake_refresh_access_token),
        ),
        patch.object(hass.config_entries, "async_update_entry") as mock_update,
    ):
        await auth_manager.refresh_token()

    assert mock_update.call_count == 1
    _, kwargs = mock_update.call_args
    data = kwargs["data"]
    assert data[CONF_ACCESS_TOKEN] == "new_access"
    assert data[CONF_REFRESH_TOKEN] == "new_refresh"
    assert CONF_EXPIRES_AT in data

