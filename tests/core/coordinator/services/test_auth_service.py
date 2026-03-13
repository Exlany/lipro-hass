"""Tests for the coordinator auth service."""

from __future__ import annotations

from unittest.mock import AsyncMock, MagicMock

import pytest
from pytest_homeassistant_custom_component.common import MockConfigEntry

from custom_components.lipro.const.base import DOMAIN
from custom_components.lipro.core.coordinator.services.auth_service import (
    CoordinatorAuthService,
)
from homeassistant.exceptions import ConfigEntryAuthFailed


@pytest.mark.asyncio
async def test_auth_service_ensures_authenticated(hass) -> None:
    entry = MockConfigEntry(domain=DOMAIN, data={})
    entry.add_to_hass(hass)
    auth_manager = MagicMock(async_ensure_authenticated=AsyncMock())
    service = CoordinatorAuthService(
        hass=hass,
        auth_manager=auth_manager,
        config_entry=entry,
    )

    await service.async_ensure_authenticated()

    auth_manager.async_ensure_authenticated.assert_awaited_once_with()


@pytest.mark.asyncio
async def test_auth_service_triggers_reauth_and_raises(hass) -> None:
    entry = MockConfigEntry(domain=DOMAIN, data={})
    entry.add_to_hass(hass)
    entry.async_start_reauth = MagicMock()
    service = CoordinatorAuthService(
        hass=hass,
        auth_manager=MagicMock(),
        config_entry=entry,
    )

    with pytest.raises(ConfigEntryAuthFailed, match="auth_error"):
        await service.async_trigger_reauth("auth_error")

    entry.async_start_reauth.assert_called_once_with(hass)
