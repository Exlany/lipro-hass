"""Edge-case tests for integration entrypoint helpers."""

from __future__ import annotations

import asyncio
from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from pytest_homeassistant_custom_component.common import MockConfigEntry

from custom_components.lipro import async_reload_entry, async_unload_entry
from custom_components.lipro.const.base import DOMAIN
from custom_components.lipro.entry_options import (
    async_reload_entry_if_options_changed,
    remove_entry_options_snapshot,
    store_entry_options_snapshot,
)


def test_store_entry_options_snapshot_ignores_non_dict_snapshots(hass) -> None:
    entry = MockConfigEntry(domain=DOMAIN, options={"x": 1})
    hass.data[DOMAIN] = {"options_snapshots": "not-a-dict"}

    store_entry_options_snapshot(hass, entry)

    assert hass.data[DOMAIN]["options_snapshots"] == "not-a-dict"


def test_remove_entry_options_snapshot_pops_entry_id(hass) -> None:
    hass.data[DOMAIN] = {"options_snapshots": {"entry1": {"x": 1}}}

    remove_entry_options_snapshot(hass, "entry1")

    assert "entry1" not in hass.data[DOMAIN]["options_snapshots"]


@pytest.mark.asyncio
async def test_async_reload_entry_if_options_changed_returns_when_domain_data_not_dict(
    hass,
) -> None:
    entry = MockConfigEntry(domain=DOMAIN, options={"x": 1})
    hass.data[DOMAIN] = "not-a-dict"

    with patch.object(hass.config_entries, "async_reload", new_callable=AsyncMock) as r:
        await async_reload_entry_if_options_changed(hass, entry)

    r.assert_not_awaited()


@pytest.mark.asyncio
async def test_async_unload_entry_reraises_cancelled_error_from_shutdown(hass) -> None:
    entry = MockConfigEntry(domain=DOMAIN)
    entry.add_to_hass(hass)

    coordinator = MagicMock()
    coordinator.async_shutdown = AsyncMock(side_effect=asyncio.CancelledError)
    entry.runtime_data = coordinator

    with patch.object(
        hass.config_entries, "async_unload_platforms", new_callable=AsyncMock
    ) as unload_platforms:
        unload_platforms.return_value = True

        with pytest.raises(asyncio.CancelledError):
            await async_unload_entry(hass, entry)


@pytest.mark.asyncio
async def test_async_reload_entry_reraises_cancelled_error(hass) -> None:
    entry = MockConfigEntry(domain=DOMAIN)
    entry.add_to_hass(hass)

    with patch.object(
        hass.config_entries,
        "async_reload",
        new_callable=AsyncMock,
    ) as reload_entry:
        reload_entry.side_effect = asyncio.CancelledError

        with pytest.raises(asyncio.CancelledError):
            await async_reload_entry(hass, entry)
