"""Thin smoke tests for the Lipro firmware update platform."""

from __future__ import annotations

from unittest.mock import AsyncMock, MagicMock, patch

import pytest


def _entry_with_runtime(coordinator: MagicMock) -> MagicMock:
    """Build a lightweight config entry stub for async_setup_entry tests."""
    entry = MagicMock()
    entry.runtime_data = coordinator
    return entry


@pytest.mark.asyncio
async def test_update_async_setup_entry_filters_groups(
    hass, mock_coordinator, make_device
):
    """Update platform should only create entities for real devices."""
    from custom_components.lipro.entities.firmware_update import (
        LiproFirmwareUpdateEntity,
    )
    from custom_components.lipro.update import async_setup_entry

    real_device = make_device("light", serial="03ab5ccd7c111111")
    mesh_group = make_device("light", serial="mesh_group_10001", is_group=True)
    invalid_device = make_device("light", serial="invalid_serial")

    mock_coordinator.devices = {
        real_device.serial: real_device,
        mesh_group.serial: mesh_group,
        invalid_device.serial: invalid_device,
    }

    async_add_entities = MagicMock()
    await async_setup_entry(
        hass, _entry_with_runtime(mock_coordinator), async_add_entities
    )

    entities = async_add_entities.call_args[0][0]
    assert len(entities) == 1
    assert isinstance(entities[0], LiproFirmwareUpdateEntity)
    assert entities[0].device.serial == real_device.serial


@pytest.mark.asyncio
async def test_update_entity_parses_latest_and_certified(mock_coordinator, make_device):
    """Entity should match OTA row and expose latest/certified state."""
    from custom_components.lipro.entities.firmware_update import (
        LiproFirmwareUpdateEntity,
    )

    device = make_device(
        "light",
        serial="03ab5ccd7c111111",
        properties={"version": "1.0.0"},
    )
    mock_coordinator.devices = {device.serial: device}
    mock_coordinator.get_device = MagicMock(return_value=device)
    mock_coordinator.protocol = MagicMock()
    mock_coordinator.protocol.query_ota_info = AsyncMock(
        return_value=[
            {
                "deviceType": "ff000006",
                "latestVersion": "9.9.9",
                "certified": False,
            },
            {
                "deviceType": device.device_type_hex,
                "latestVersion": "1.1.0",
                "certifiedVersions": ["1.1.0"],
                "upgradeCommand": {
                    "command": "CHANGE_STATE",
                    "properties": {"version": "1.1.0"},
                },
            },
        ]
    )

    entity = LiproFirmwareUpdateEntity(mock_coordinator, device)
    with patch.object(entity, "async_write_ha_state"):
        await entity.async_update()

    assert entity.installed_version == "1.0.0"
    assert entity.latest_version == "1.1.0"
    assert entity.extra_state_attributes["certified"] is True
    mock_coordinator.protocol.query_ota_info.assert_awaited_once_with(
        device_id=device.serial,
        device_type=device.device_type_hex,
        iot_name=device.iot_name,
        allow_rich_v2_fallback=True,
    )
