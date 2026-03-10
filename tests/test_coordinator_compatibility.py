"""Coverage for the composed coordinator runtime path."""

from __future__ import annotations

from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from pytest_homeassistant_custom_component.common import MockConfigEntry

from custom_components.lipro import async_setup_entry
from custom_components.lipro.const.base import DOMAIN
from custom_components.lipro.coordinator_v2 import CoordinatorV2


@pytest.mark.asyncio
async def test_async_setup_entry_uses_coordinator_v2_runtime_data(hass) -> None:
    entry = MockConfigEntry(domain=DOMAIN, data={"phone_id": "test-phone-id"})
    entry.add_to_hass(hass)
    client = MagicMock()
    auth_manager = MagicMock()
    legacy = MagicMock()
    legacy.async_config_entry_first_refresh = AsyncMock()
    legacy.async_shutdown = AsyncMock()
    legacy.state_service = MagicMock()
    legacy.command_service = MagicMock()
    legacy.device_refresh_service = MagicMock()
    legacy.mqtt_service = MagicMock()

    with (
        patch("custom_components.lipro.async_ensure_runtime_infra", new=AsyncMock()),
        patch(
            "custom_components.lipro.build_entry_auth_context",
            return_value=(client, auth_manager),
        ),
        patch("custom_components.lipro.async_authenticate_entry", new=AsyncMock()),
        patch("custom_components.lipro.get_entry_int_option", return_value=30),
        patch("custom_components.lipro.LiproDataUpdateCoordinator", return_value=legacy),
        patch("custom_components.lipro.persist_entry_tokens_if_changed"),
        patch.object(hass.config_entries, "async_forward_entry_setups", new=AsyncMock()),
        patch("custom_components.lipro.store_entry_options_snapshot"),
    ):
        assert await async_setup_entry(hass, entry) is True

    assert isinstance(entry.runtime_data, CoordinatorV2)


def test_coordinator_v2_exposes_injected_services() -> None:
    state_service = MagicMock()
    command_service = MagicMock()
    device_refresh_service = MagicMock()
    mqtt_service = MagicMock()

    coordinator = CoordinatorV2(
        state_service=state_service,
        command_service=command_service,
        device_refresh_service=device_refresh_service,
        mqtt_service=mqtt_service,
    )

    assert coordinator.state_service is state_service
    assert coordinator.command_service is command_service
    assert coordinator.device_refresh_service is device_refresh_service
    assert coordinator.mqtt_service is mqtt_service
