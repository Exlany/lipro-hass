"""Tests for the coordinator auth service."""

from __future__ import annotations

from unittest.mock import AsyncMock, MagicMock

import pytest
from pytest_homeassistant_custom_component.common import MockConfigEntry

from custom_components.lipro.const.base import DOMAIN
from custom_components.lipro.core.coordinator.services.auth_service import (
    CoordinatorAuthService,
)
from custom_components.lipro.runtime_types import RuntimeReauthReason


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
async def test_auth_service_triggers_reauth_without_raising(hass) -> None:
    entry = MockConfigEntry(domain=DOMAIN, data={})
    entry.add_to_hass(hass)
    entry.async_start_reauth = MagicMock()
    service = CoordinatorAuthService(
        hass=hass,
        auth_manager=MagicMock(),
        config_entry=entry,
    )

    await service.async_trigger_reauth(RuntimeReauthReason.AUTH_ERROR)

    entry.async_start_reauth.assert_called_once_with(hass)


@pytest.mark.asyncio
async def test_auth_service_rejects_unknown_reauth_reason(hass) -> None:
    entry = MockConfigEntry(domain=DOMAIN, data={})
    entry.add_to_hass(hass)
    entry.async_start_reauth = MagicMock()
    service = CoordinatorAuthService(
        hass=hass,
        auth_manager=MagicMock(),
        config_entry=entry,
    )

    with pytest.raises(ValueError):
        await service.async_trigger_reauth("unsupported")

    entry.async_start_reauth.assert_not_called()
