"""Topical tests for maintenance service helpers."""

from __future__ import annotations

from types import SimpleNamespace
from unittest.mock import AsyncMock, MagicMock

import pytest
from homeassistant.exceptions import ServiceValidationError

from custom_components.lipro.const.base import DOMAIN
from custom_components.lipro.services.maintenance import async_handle_refresh_devices
from tests.helpers.service_call import service_call


@pytest.mark.asyncio
async def test_async_handle_refresh_devices_uses_runtime_access_entry_pairs() -> None:
    hass = MagicMock()
    coordinator = MagicMock()
    coordinator.device_refresh_service.async_refresh_devices = AsyncMock()
    runtime_entry = SimpleNamespace(entry_id="entry-1")
    runtime_pairs = MagicMock(return_value=[(runtime_entry, coordinator)])

    result = await async_handle_refresh_devices(
        hass,
        service_call(hass, {}),
        domain=DOMAIN,
        attr_entry_id="entry_id",
        iter_runtime_entry_coordinators=runtime_pairs,
    )

    assert result == {"success": True, "refreshed_entries": 1}
    runtime_pairs.assert_called_once_with(hass, entry_id=None)
    coordinator.device_refresh_service.async_refresh_devices.assert_awaited_once_with()


@pytest.mark.asyncio
async def test_async_handle_refresh_devices_scopes_requested_entry_id() -> None:
    hass = MagicMock()
    coordinator = MagicMock()
    coordinator.device_refresh_service.async_refresh_devices = AsyncMock()
    runtime_entry = SimpleNamespace(entry_id="entry-2")
    runtime_pairs = MagicMock(return_value=[(runtime_entry, coordinator)])

    result = await async_handle_refresh_devices(
        hass,
        service_call(hass, {"entry_id": "entry-2"}),
        domain=DOMAIN,
        attr_entry_id="entry_id",
        iter_runtime_entry_coordinators=runtime_pairs,
    )

    assert result == {
        "success": True,
        "refreshed_entries": 1,
        "requested_entry_id": "entry-2",
    }
    runtime_pairs.assert_called_once_with(hass, entry_id="entry-2")
    coordinator.device_refresh_service.async_refresh_devices.assert_awaited_once_with()


@pytest.mark.asyncio
async def test_async_handle_refresh_devices_rejects_unknown_entry_id() -> None:
    hass = MagicMock()
    runtime_pairs = MagicMock(return_value=[])

    with pytest.raises(ServiceValidationError) as error:
        await async_handle_refresh_devices(
            hass,
            service_call(hass, {"entry_id": "missing-entry"}),
            domain=DOMAIN,
            attr_entry_id="entry_id",
            iter_runtime_entry_coordinators=runtime_pairs,
        )

    runtime_pairs.assert_called_once_with(hass, entry_id="missing-entry")
    assert error.value.translation_key == "entry_not_found"
    assert error.value.translation_placeholders == {"entry_id": "missing-entry"}
