"""Tests for runtime token persistence callbacks."""

from __future__ import annotations

import logging
from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from pytest_homeassistant_custom_component.common import MockConfigEntry

from custom_components.lipro.const.base import DOMAIN
from custom_components.lipro.const.config import (
    CONF_ACCESS_TOKEN,
    CONF_EXPIRES_AT,
    CONF_PASSWORD_HASH,
    CONF_PHONE,
    CONF_PHONE_ID,
    CONF_REFRESH_TOKEN,
    CONF_USER_ID,
)
from custom_components.lipro.core import LiproAuthManager, LiproProtocolFacade
from custom_components.lipro.entry_auth import build_entry_auth_context

_HASHED_VALUE = "hashed-value"

_TEST_LOGGER = logging.getLogger(__name__)


def test_build_entry_auth_context_reuses_shared_headless_boot_contract(hass) -> None:
    """Entry auth should only add HA callback glue on top of the shared boot seam."""
    entry = MockConfigEntry(
        domain=DOMAIN,
        data={
            CONF_PHONE_ID: "phone-id",
            CONF_PHONE: "13800000000",
            CONF_PASSWORD_HASH: _HASHED_VALUE,
            CONF_ACCESS_TOKEN: "old_access",
            CONF_REFRESH_TOKEN: "old_refresh",
            CONF_USER_ID: 10001,
        },
    )
    entry.add_to_hass(hass)
    boot_context = MagicMock(name="boot_context")
    boot_context.protocol = MagicMock(name="protocol")
    boot_context.auth_manager = MagicMock(name="auth_manager")

    with patch(
        "custom_components.lipro.entry_auth.build_headless_boot_context",
        return_value=boot_context,
    ) as mock_build:
        protocol, auth_manager = build_entry_auth_context(
            hass,
            entry,
            get_client_session=lambda _: MagicMock(name="session"),
            protocol_factory=LiproProtocolFacade,
            auth_manager_factory=LiproAuthManager,
            logger=_TEST_LOGGER,
        )

    assert protocol is boot_context.protocol
    assert auth_manager is boot_context.auth_manager
    mock_build.assert_called_once()
    boot_context.auth_manager.set_tokens_updated_callback.assert_called_once()


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

    client, auth_manager = build_entry_auth_context(
        hass,
        entry,
        get_client_session=lambda _: MagicMock(),
        protocol_factory=LiproProtocolFacade,
        auth_manager_factory=LiproAuthManager,
        logger=_TEST_LOGGER,
    )

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
