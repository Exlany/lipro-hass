"""Coverage for the native coordinator runtime entry path."""

from __future__ import annotations

from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from pytest_homeassistant_custom_component.common import MockConfigEntry

from custom_components.lipro import async_setup_entry
from custom_components.lipro.const.base import DOMAIN


@pytest.mark.asyncio
async def test_async_setup_entry_uses_native_coordinator_runtime_data(hass) -> None:
    entry = MockConfigEntry(domain=DOMAIN, data={"phone_id": "test-phone-id"})
    entry.add_to_hass(hass)
    client = MagicMock()
    auth_manager = MagicMock()
    coordinator = MagicMock()
    coordinator.async_config_entry_first_refresh = AsyncMock()
    coordinator.async_shutdown = AsyncMock()

    with (
        patch("custom_components.lipro.async_ensure_runtime_infra", new=AsyncMock()),
        patch(
            "custom_components.lipro.build_entry_auth_context",
            return_value=(client, auth_manager),
        ),
        patch("custom_components.lipro.async_authenticate_entry", new=AsyncMock()),
        patch("custom_components.lipro.get_entry_int_option", return_value=30),
        patch("custom_components.lipro.Coordinator", return_value=coordinator) as ctor,
        patch("custom_components.lipro.persist_entry_tokens_if_changed"),
        patch.object(hass.config_entries, "async_forward_entry_setups", new=AsyncMock()),
        patch("custom_components.lipro.store_entry_options_snapshot"),
    ):
        assert await async_setup_entry(hass, entry) is True

    assert entry.runtime_data is coordinator
    coordinator.async_config_entry_first_refresh.assert_awaited_once_with()
    assert ctor.call_count == 1
