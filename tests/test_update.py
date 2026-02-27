"""Tests for Lipro firmware update platform."""

from __future__ import annotations

from unittest.mock import AsyncMock, MagicMock

import pytest

from homeassistant.exceptions import HomeAssistantError


def _entry_with_runtime(coordinator: MagicMock) -> MagicMock:
    """Build a lightweight config entry stub for async_setup_entry tests."""
    entry = MagicMock()
    entry.runtime_data = coordinator
    return entry


@pytest.mark.asyncio
async def test_update_async_setup_entry_filters_groups(mock_coordinator, make_device):
    """Update platform should only create entities for real devices."""
    from custom_components.lipro.update import (
        LiproFirmwareUpdateEntity,
        async_setup_entry,
    )

    real_device = make_device("light", serial="03ab5ccd7c111111")
    mesh_group = make_device("light", serial="mesh_group_10001", is_group=True)
    invalid_device = make_device("light", serial="invalid_serial")

    mock_coordinator.devices = {
        real_device.serial: real_device,
        mesh_group.serial: mesh_group,
        invalid_device.serial: invalid_device,
    }

    async_add_entities = MagicMock()
    await async_setup_entry(None, _entry_with_runtime(mock_coordinator), async_add_entities)

    entities = async_add_entities.call_args[0][0]
    assert len(entities) == 1
    assert isinstance(entities[0], LiproFirmwareUpdateEntity)
    assert entities[0].device.serial == real_device.serial


@pytest.mark.asyncio
async def test_update_entity_parses_latest_and_certified(mock_coordinator, make_device):
    """Entity should match OTA row and expose latest/certified state."""
    from custom_components.lipro.update import LiproFirmwareUpdateEntity

    device = make_device(
        "light",
        serial="03ab5ccd7c111111",
        properties={"version": "1.0.0"},
    )
    mock_coordinator.devices = {device.serial: device}
    mock_coordinator.get_device = MagicMock(return_value=device)
    mock_coordinator.client = MagicMock()
    mock_coordinator.client.query_ota_info = AsyncMock(
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
    entity.async_write_ha_state = MagicMock()
    await entity.async_update()

    assert entity.installed_version == "1.0.0"
    assert entity.latest_version == "1.1.0"
    assert entity.extra_state_attributes["certified"] is True
    mock_coordinator.client.query_ota_info.assert_awaited_once_with(
        device_id=device.serial,
        device_type=device.device_type_hex,
    )


@pytest.mark.asyncio
async def test_update_entity_installs_certified_firmware(mock_coordinator, make_device):
    """Certified firmware should install directly."""
    from custom_components.lipro.update import LiproFirmwareUpdateEntity

    device = make_device(
        "light",
        serial="03ab5ccd7c111111",
        properties={"version": "1.0.0"},
    )
    mock_coordinator.devices = {device.serial: device}
    mock_coordinator.get_device = MagicMock(return_value=device)
    mock_coordinator.client = MagicMock()
    mock_coordinator.client.query_ota_info = AsyncMock(
        return_value=[
            {
                "deviceType": device.device_type_hex,
                "latestVersion": "1.1.0",
                "needUpgrade": True,
                "certified": True,
                "upgradeCommand": {
                    "command": "CHANGE_STATE",
                    "properties": [{"key": "version", "value": "1.1.0"}],
                },
            }
        ]
    )
    mock_coordinator.async_send_command = AsyncMock(return_value=True)
    mock_coordinator.async_request_refresh = AsyncMock()

    entity = LiproFirmwareUpdateEntity(mock_coordinator, device)
    entity.async_write_ha_state = MagicMock()
    await entity.async_update()
    await entity.async_install(version=None, backup=False)

    mock_coordinator.async_send_command.assert_awaited_once_with(
        device,
        "CHANGE_STATE",
        [{"key": "version", "value": "1.1.0"}],
    )
    mock_coordinator.async_request_refresh.assert_awaited()


@pytest.mark.asyncio
async def test_update_entity_requires_confirmation_for_unverified(
    mock_coordinator, make_device
):
    """Unverified firmware should require a second confirmation click."""
    from custom_components.lipro.update import LiproFirmwareUpdateEntity

    device = make_device(
        "light",
        serial="03ab5ccd7c111111",
        properties={"version": "1.0.0"},
    )
    mock_coordinator.devices = {device.serial: device}
    mock_coordinator.get_device = MagicMock(return_value=device)
    mock_coordinator.client = MagicMock()
    mock_coordinator.client.query_ota_info = AsyncMock(
        return_value=[
            {
                "deviceType": device.device_type_hex,
                "latestVersion": "1.1.0",
                "needUpgrade": True,
                "certified": False,
                "upgradeCommand": {
                    "command": "CHANGE_STATE",
                    "properties": [{"key": "version", "value": "1.1.0"}],
                },
            }
        ]
    )
    mock_coordinator.async_send_command = AsyncMock(return_value=True)
    mock_coordinator.async_request_refresh = AsyncMock()

    entity = LiproFirmwareUpdateEntity(mock_coordinator, device)
    entity.async_write_ha_state = MagicMock()
    await entity.async_update()

    with pytest.raises(HomeAssistantError) as first_attempt:
        await entity.async_install(version=None, backup=False)
    assert first_attempt.value.translation_key == "firmware_unverified_confirm_required"
    assert entity.extra_state_attributes["confirmation_required"] is True
    mock_coordinator.async_send_command.assert_not_awaited()

    await entity.async_install(version=None, backup=False)
    mock_coordinator.async_send_command.assert_awaited_once()


@pytest.mark.asyncio
async def test_update_entity_raises_when_install_command_missing(
    mock_coordinator, make_device
):
    """Install should fail when OTA payload has no executable command."""
    from custom_components.lipro.update import LiproFirmwareUpdateEntity

    device = make_device(
        "light",
        serial="03ab5ccd7c111111",
        properties={"version": "1.0.0"},
    )
    mock_coordinator.devices = {device.serial: device}
    mock_coordinator.get_device = MagicMock(return_value=device)
    mock_coordinator.client = MagicMock()
    mock_coordinator.client.query_ota_info = AsyncMock(
        return_value=[
            {
                "deviceType": device.device_type_hex,
                "latestVersion": "1.1.0",
                "needUpgrade": True,
                "certified": True,
            }
        ]
    )

    entity = LiproFirmwareUpdateEntity(mock_coordinator, device)
    entity.async_write_ha_state = MagicMock()
    await entity.async_update()

    with pytest.raises(HomeAssistantError) as err:
        await entity.async_install(version=None, backup=False)
    assert err.value.translation_key == "firmware_install_unsupported"


@pytest.mark.asyncio
async def test_update_entity_uses_manifest_certification_fallback(
    mock_coordinator, make_device
):
    """Manifest certification should be used when OTA row has no cert flags."""
    from custom_components.lipro.update import LiproFirmwareUpdateEntity

    device = make_device(
        "light",
        serial="03ab5ccd7c111111",
        properties={"version": "7.10.8"},
    )
    mock_coordinator.devices = {device.serial: device}
    mock_coordinator.get_device = MagicMock(return_value=device)
    mock_coordinator.client = MagicMock()
    mock_coordinator.client.query_ota_info = AsyncMock(
        return_value=[
            {
                "deviceType": device.device_type_hex,
                "latestVersion": "7.10.9",
                "needUpgrade": True,
                "upgradeCommand": {
                    "command": "CHANGE_STATE",
                    "properties": [{"key": "version", "value": "7.10.9"}],
                },
            }
        ]
    )

    entity = LiproFirmwareUpdateEntity(mock_coordinator, device)
    entity.async_write_ha_state = MagicMock()
    await entity.async_update()

    assert entity.latest_version == "7.10.9"
    assert entity.extra_state_attributes["certified"] is True
    assert entity.extra_state_attributes["certification_source"] == "manifest"
