"""Tests for Lipro firmware update platform."""

from __future__ import annotations

from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from homeassistant.exceptions import HomeAssistantError


def _entry_with_runtime(coordinator: MagicMock) -> MagicMock:
    """Build a lightweight config entry stub for async_setup_entry tests."""
    entry = MagicMock()
    entry.runtime_data = coordinator
    return entry


def test_parse_remote_manifest_payload_ignores_summary_wrapper():
    """Remote payload should ignore stale summary and use firmware_list only."""
    from custom_components.lipro.core.ota_utils import (
        parse_verified_firmware_manifest_payload,
    )

    versions, versions_by_type = parse_verified_firmware_manifest_payload(
        {
            "updated_at": "2026-02-27T00:00:00Z",
            "summary": {
                "verified_versions": ["7.10.9"],
                "verified_versions_by_type": {"ff000001": ["7.10.9"]},
            },
            "firmware_list": [
                {
                    "firmwareVersion": "7.10.8",
                    "certified": True,
                    "deviceType": "ff000001",
                    "iotName": "21P3",
                    "physicalModel": "light",
                }
            ],
        }
    )

    assert versions == frozenset({"7.10.8"})
    assert versions_by_type["21p3"] == frozenset({"7.10.8"})


def test_parse_remote_manifest_payload_derives_from_firmware_list():
    """Remote payload should fallback to firmware_list when summary is missing."""
    from custom_components.lipro.core.ota_utils import (
        parse_verified_firmware_manifest_payload,
    )

    versions, versions_by_type = parse_verified_firmware_manifest_payload(
        {
            "firmware_list": [
                {
                    "firmwareVersion": "7.10.9",
                    "certified": True,
                    "deviceType": "ff000001",
                    "iotName": "21P3",
                    "physicalModel": "light",
                },
                {
                    "version": "9.9.9",
                    "certified": True,
                },
                {
                    "version": "7.10.8",
                    "certified": False,
                },
                {
                    "version": "7.10.7",
                },
            ]
        }
    )

    assert versions == frozenset({"7.10.9", "9.9.9"})
    assert versions_by_type["21p3"] == frozenset({"7.10.9"})


def test_parse_remote_manifest_payload_derives_type_keys_without_certification_key():
    """Rows without certification_key/source should still derive type keys from metadata."""
    from custom_components.lipro.core.ota_utils import (
        parse_verified_firmware_manifest_payload,
    )

    versions, versions_by_type = parse_verified_firmware_manifest_payload(
        {
            "firmware_list": [
                {
                    "version": "7.10.9",
                    "certified": True,
                    "deviceType": "ff000001",
                    "iotName": "21P3",
                    "physicalModel": "light",
                }
            ]
        }
    )

    assert versions == frozenset({"7.10.9"})
    assert versions_by_type["21p3"] == frozenset({"7.10.9"})


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


@pytest.mark.asyncio
async def test_update_entity_uses_remote_manifest_certification_fallback(
    mock_coordinator, make_device
):
    """Remote manifest certification should take precedence when available."""
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
                "latestVersion": "8.0.0",
                "needUpgrade": True,
                "upgradeCommand": {
                    "command": "CHANGE_STATE",
                    "properties": [{"key": "version", "value": "8.0.0"}],
                },
            }
        ]
    )

    entity = LiproFirmwareUpdateEntity(mock_coordinator, device)
    entity.hass = MagicMock()
    entity.async_write_ha_state = MagicMock()

    with patch(
        "custom_components.lipro.update._load_remote_firmware_manifest",
        AsyncMock(return_value=(frozenset({"8.0.0"}), {})),
    ):
        await entity.async_update()

    assert entity.latest_version == "8.0.0"
    assert entity.extra_state_attributes["certified"] is True


@pytest.mark.asyncio
async def test_update_entity_accepts_newer_certified_version_than_installed(
    mock_coordinator, make_device
):
    """Any certified version newer than current firmware should be treated as certified."""
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
    entity.hass = MagicMock()
    entity.async_write_ha_state = MagicMock()

    with patch(
        "custom_components.lipro.update._load_remote_firmware_manifest",
        AsyncMock(return_value=(frozenset({"8.0.0"}), {})),
    ):
        await entity.async_update()

    assert entity.latest_version == "7.10.9"
    assert entity.extra_state_attributes["certified"] is True


@pytest.mark.asyncio
async def test_update_entity_type_manifest_blocks_global_fallback(
    mock_coordinator, make_device
):
    """If type-specific certification exists, global list should not override it."""
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
    entity.hass = MagicMock()
    entity.async_write_ha_state = MagicMock()

    with (
        patch(
            "custom_components.lipro.update._load_remote_firmware_manifest",
            AsyncMock(
                return_value=(
                    frozenset({"8.0.0"}),
                    {str(device.iot_name).lower(): frozenset({"7.10.7"})},
                )
            ),
        ),
        patch(
            "custom_components.lipro.update._load_verified_firmware_manifest",
            return_value=(frozenset(), {}),
        ),
    ):
        await entity.async_update()

    assert entity.latest_version == "7.10.9"
    assert entity.extra_state_attributes["certified"] is False


@pytest.mark.asyncio
async def test_update_entity_uses_ble_name_for_type_certification(
    mock_coordinator, make_device
):
    """Controller OTA rows should support type match via bleName."""
    from custom_components.lipro.update import LiproFirmwareUpdateEntity

    device = make_device(
        "switch",
        serial="03ab5ccd7c222222",
        properties={"version": "2.6.40"},
    )
    mock_coordinator.devices = {device.serial: device}
    mock_coordinator.get_device = MagicMock(return_value=device)
    mock_coordinator.client = MagicMock()
    mock_coordinator.client.query_ota_info = AsyncMock(
        return_value=[
            {
                "bleName": "T21JC",
                "version": "2.6.43",
                "needUpgrade": True,
                "upgradeCommand": {
                    "command": "CHANGE_STATE",
                    "properties": [{"key": "version", "value": "2.6.43"}],
                },
            }
        ]
    )

    entity = LiproFirmwareUpdateEntity(mock_coordinator, device)
    entity.hass = MagicMock()
    entity.async_write_ha_state = MagicMock()

    with (
        patch(
            "custom_components.lipro.update._load_remote_firmware_manifest",
            AsyncMock(
                return_value=(
                    frozenset(),
                    {"t21jc": frozenset({"2.6.43"})},
                )
            ),
        ),
        patch(
            "custom_components.lipro.update._load_verified_firmware_manifest",
            return_value=(frozenset(), {}),
        ),
    ):
        await entity.async_update()

    assert entity.latest_version == "2.6.43"
    assert entity.extra_state_attributes["certified"] is True


@pytest.mark.asyncio
async def test_update_entity_prefers_controller_row_matching_device_iot_name(
    mock_coordinator, make_device
):
    """Controller OTA row selection should prefer row whose bleName matches device iot_name."""
    from custom_components.lipro.update import LiproFirmwareUpdateEntity

    device = make_device(
        "switch",
        serial="03ab5ccd7c222222",
        iot_name="T21JE",
        properties={"version": "2.6.40"},
    )
    mock_coordinator.devices = {device.serial: device}
    mock_coordinator.get_device = MagicMock(return_value=device)
    mock_coordinator.client = MagicMock()
    mock_coordinator.client.query_ota_info = AsyncMock(
        return_value=[
            {
                "bleName": "T21JC",
                "version": "2.6.43",
                "needUpgrade": True,
                "upgradeCommand": {
                    "command": "CHANGE_STATE",
                    "properties": [{"key": "version", "value": "2.6.43"}],
                },
            },
            {
                "bleName": "T21JE",
                "version": "2.6.44",
                "needUpgrade": True,
                "upgradeCommand": {
                    "command": "CHANGE_STATE",
                    "properties": [{"key": "version", "value": "2.6.44"}],
                },
            },
        ]
    )

    entity = LiproFirmwareUpdateEntity(mock_coordinator, device)
    entity.async_write_ha_state = MagicMock()
    await entity.async_update()

    assert entity.latest_version == "2.6.44"


@pytest.mark.asyncio
async def test_update_entity_uses_iot_name_for_type_certification(
    mock_coordinator, make_device
):
    """Type certification should match iotName key only."""
    from custom_components.lipro.update import LiproFirmwareUpdateEntity

    device = make_device(
        "light",
        serial="03ab5ccd7c333333",
        iot_name="21P3",
        product_id=11,
        properties={"version": "7.10.8"},
    )
    mock_coordinator.devices = {device.serial: device}
    mock_coordinator.get_device = MagicMock(return_value=device)
    mock_coordinator.client = MagicMock()
    mock_coordinator.client.query_ota_info = AsyncMock(
        return_value=[
            {
                "deviceType": "ff000001",
                "latestVersion": "7.10.9",
                "needUpgrade": True,
            }
        ]
    )

    entity = LiproFirmwareUpdateEntity(mock_coordinator, device)
    entity.hass = MagicMock()
    entity.async_write_ha_state = MagicMock()

    with (
        patch(
            "custom_components.lipro.update._load_remote_firmware_manifest",
            AsyncMock(
                return_value=(
                    frozenset(),
                    {"21p3": frozenset({"7.10.9"})},
                )
            ),
        ),
        patch(
            "custom_components.lipro.update._load_verified_firmware_manifest",
            return_value=(frozenset(), {}),
        ),
    ):
        await entity.async_update()

    assert entity.latest_version == "7.10.9"
    assert entity.extra_state_attributes["certified"] is True
