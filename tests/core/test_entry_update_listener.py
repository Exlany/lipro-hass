"""Tests for config-entry update listener behavior."""

from __future__ import annotations

from unittest.mock import AsyncMock, patch

import pytest
from pytest_homeassistant_custom_component.common import MockConfigEntry

from custom_components.lipro.const.base import DOMAIN
from custom_components.lipro.const.config import (
    CONF_ACCESS_TOKEN,
    CONF_PHONE,
    CONF_PHONE_ID,
    CONF_SCAN_INTERVAL,
)
from custom_components.lipro.entry_options import (
    async_reload_entry_if_options_changed,
    remove_entry_options_snapshot,
    store_entry_options_snapshot,
)


@pytest.mark.asyncio
async def test_update_listener_skips_reload_on_data_update(hass) -> None:
    """Token persistence updates entry.data and must not reload the entry."""
    entry = MockConfigEntry(
        domain=DOMAIN,
        data={
            CONF_PHONE_ID: "phone-id",
            CONF_PHONE: "13800000000",
        },
        options={CONF_SCAN_INTERVAL: 30},
    )
    entry.add_to_hass(hass)
    store_entry_options_snapshot(hass, entry)
    entry.add_update_listener(async_reload_entry_if_options_changed)

    mock_reload = AsyncMock()
    with patch.object(hass.config_entries, "async_reload", mock_reload):
        hass.config_entries.async_update_entry(
            entry,
            data={
                **entry.data,
                CONF_ACCESS_TOKEN: "new_access",
            },
        )
        await hass.async_block_till_done()

    mock_reload.assert_not_awaited()


@pytest.mark.asyncio
async def test_update_listener_reloads_on_options_update(hass) -> None:
    """Options changes should still trigger a reload."""
    entry = MockConfigEntry(
        domain=DOMAIN,
        data={
            CONF_PHONE_ID: "phone-id",
            CONF_PHONE: "13800000000",
        },
        options={CONF_SCAN_INTERVAL: 30},
    )
    entry.add_to_hass(hass)
    store_entry_options_snapshot(hass, entry)
    entry.add_update_listener(async_reload_entry_if_options_changed)

    mock_reload = AsyncMock()
    with patch.object(hass.config_entries, "async_reload", mock_reload):
        hass.config_entries.async_update_entry(
            entry,
            options={CONF_SCAN_INTERVAL: 60},
        )
        await hass.async_block_till_done()

    mock_reload.assert_awaited_once_with(entry.entry_id)


def test_snapshot_helpers_ignore_non_dict_domain_data(hass) -> None:
    """Snapshot helpers should no-op when hass.data[DOMAIN] is corrupted."""
    entry = MockConfigEntry(
        domain=DOMAIN,
        data={
            CONF_PHONE_ID: "phone-id",
            CONF_PHONE: "13800000000",
        },
        options={CONF_SCAN_INTERVAL: 30},
    )

    hass.data[DOMAIN] = "not-a-dict"
    store_entry_options_snapshot(hass, entry)
    remove_entry_options_snapshot(hass, entry.entry_id)


@pytest.mark.asyncio
async def test_update_listener_initializes_snapshot_store_without_reload(hass) -> None:
    """Missing snapshot store should be initialized without reloading."""
    entry = MockConfigEntry(
        domain=DOMAIN,
        data={
            CONF_PHONE_ID: "phone-id",
            CONF_PHONE: "13800000000",
        },
        options={CONF_SCAN_INTERVAL: 30},
    )
    hass.data[DOMAIN] = {}

    mock_reload = AsyncMock()
    with patch.object(hass.config_entries, "async_reload", mock_reload):
        await async_reload_entry_if_options_changed(hass, entry)

    assert "options_snapshots" in hass.data[DOMAIN]
    mock_reload.assert_not_awaited()


@pytest.mark.asyncio
async def test_update_listener_stores_snapshot_when_previous_missing(hass) -> None:
    """Unknown entries should store a snapshot and skip reloading once."""
    entry = MockConfigEntry(
        domain=DOMAIN,
        data={
            CONF_PHONE_ID: "phone-id",
            CONF_PHONE: "13800000000",
        },
        options={CONF_SCAN_INTERVAL: 30},
    )
    hass.data[DOMAIN] = {"options_snapshots": {}}

    mock_reload = AsyncMock()
    with patch.object(hass.config_entries, "async_reload", mock_reload):
        await async_reload_entry_if_options_changed(hass, entry)

    snapshots = hass.data[DOMAIN]["options_snapshots"]
    assert isinstance(snapshots, dict)
    assert entry.entry_id in snapshots
    mock_reload.assert_not_awaited()
