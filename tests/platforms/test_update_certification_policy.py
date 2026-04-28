"""Tests for update-entity certification and manifest policy concerns."""

from __future__ import annotations

from unittest.mock import AsyncMock, MagicMock, patch

import pytest


def _patch_write_state(entity: object) -> None:
    """Patch instance-level state writer to avoid Home Assistant side effects."""
    patch.object(entity, "async_write_ha_state", new=MagicMock()).start()


@pytest.mark.asyncio
async def test_update_entity_uses_manifest_certification_fallback(
    mock_coordinator, make_device
):
    """Manifest certification should be used when OTA row has no cert flags."""
    from custom_components.lipro.entities.firmware_update import (
        LiproFirmwareUpdateEntity,
    )

    device = make_device(
        "light",
        serial="03ab5ccd7c111111",
        properties={"version": "7.10.8"},
    )
    mock_coordinator.devices = {device.serial: device}
    mock_coordinator.get_device = MagicMock(return_value=device)
    mock_coordinator.protocol = MagicMock()
    mock_coordinator.protocol.query_ota_info = AsyncMock(
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
    _patch_write_state(entity)
    await entity.async_update()

    assert entity.latest_version == "7.10.9"
    assert entity.extra_state_attributes["certified"] is True


@pytest.mark.asyncio
async def test_update_entity_remote_manifest_does_not_certify_on_its_own(
    mock_coordinator, make_device
):
    """Remote manifest metadata alone should not mark firmware as certified."""
    from custom_components.lipro.entities.firmware_update import (
        LiproFirmwareUpdateEntity,
    )

    device = make_device(
        "light",
        serial="03ab5ccd7c111111",
        properties={"version": "7.10.8"},
    )
    mock_coordinator.devices = {device.serial: device}
    mock_coordinator.get_device = MagicMock(return_value=device)
    mock_coordinator.protocol = MagicMock()
    mock_coordinator.protocol.query_ota_info = AsyncMock(
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
    _patch_write_state(entity)

    with (
        patch(
            "custom_components.lipro.firmware_manifest.async_load_remote_firmware_manifest",
            AsyncMock(return_value=(frozenset({"8.0.0"}), {})),
        ),
        patch(
            "custom_components.lipro.firmware_manifest.load_verified_firmware_manifest",
            return_value=(frozenset(), {}),
        ),
    ):
        await entity.async_update()

    assert entity.latest_version == "8.0.0"
    assert entity.extra_state_attributes["certified"] is False


@pytest.mark.asyncio
async def test_update_entity_accepts_newer_locally_certified_version_than_installed(
    mock_coordinator, make_device
):
    """Every certified version newer than current firmware should be treated as certified."""
    from custom_components.lipro.entities.firmware_update import (
        LiproFirmwareUpdateEntity,
    )

    device = make_device(
        "light",
        serial="03ab5ccd7c111111",
        properties={"version": "7.10.8"},
    )
    mock_coordinator.devices = {device.serial: device}
    mock_coordinator.get_device = MagicMock(return_value=device)
    mock_coordinator.protocol = MagicMock()
    mock_coordinator.protocol.query_ota_info = AsyncMock(
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
    _patch_write_state(entity)

    with (
        patch(
            "custom_components.lipro.firmware_manifest.async_load_remote_firmware_manifest",
            AsyncMock(return_value=(frozenset(), {})),
        ),
        patch(
            "custom_components.lipro.firmware_manifest.load_verified_firmware_manifest",
            return_value=(frozenset({"7.10.9"}), {}),
        ),
    ):
        await entity.async_update()

    assert entity.latest_version == "7.10.9"
    assert entity.extra_state_attributes["certified"] is True


@pytest.mark.asyncio
async def test_update_entity_type_manifest_blocks_global_fallback(
    mock_coordinator, make_device
):
    """If type-specific certification exists, global list should not override it."""
    from custom_components.lipro.entities.firmware_update import (
        LiproFirmwareUpdateEntity,
    )

    device = make_device(
        "light",
        serial="03ab5ccd7c111111",
        properties={"version": "7.10.8"},
    )
    mock_coordinator.devices = {device.serial: device}
    mock_coordinator.get_device = MagicMock(return_value=device)
    mock_coordinator.protocol = MagicMock()
    mock_coordinator.protocol.query_ota_info = AsyncMock(
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
    _patch_write_state(entity)

    with (
        patch(
            "custom_components.lipro.firmware_manifest.async_load_remote_firmware_manifest",
            AsyncMock(
                return_value=(
                    frozenset({"8.0.0"}),
                    {str(device.iot_name).lower(): frozenset({"7.10.7"})},
                )
            ),
        ),
        patch(
            "custom_components.lipro.firmware_manifest.load_verified_firmware_manifest",
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
    from custom_components.lipro.entities.firmware_update import (
        LiproFirmwareUpdateEntity,
    )

    device = make_device(
        "switch",
        serial="03ab5ccd7c222222",
        properties={"version": "2.6.40"},
    )
    mock_coordinator.devices = {device.serial: device}
    mock_coordinator.get_device = MagicMock(return_value=device)
    mock_coordinator.protocol = MagicMock()
    mock_coordinator.protocol.query_ota_info = AsyncMock(
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
    _patch_write_state(entity)

    with (
        patch(
            "custom_components.lipro.firmware_manifest.async_load_remote_firmware_manifest",
            AsyncMock(return_value=(frozenset(), {})),
        ),
        patch(
            "custom_components.lipro.firmware_manifest.load_verified_firmware_manifest",
            return_value=(frozenset(), {"t21jc": frozenset({"2.6.43"})}),
        ),
    ):
        await entity.async_update()

    assert entity.latest_version == "2.6.43"
    assert entity.extra_state_attributes["certified"] is True


@pytest.mark.asyncio
async def test_update_entity_uses_iot_name_for_type_certification(
    mock_coordinator, make_device
):
    """Type certification should match iotName key only."""
    from custom_components.lipro.entities.firmware_update import (
        LiproFirmwareUpdateEntity,
    )

    device = make_device(
        "light",
        serial="03ab5ccd7c333333",
        iot_name="21P3",
        product_id=11,
        properties={"version": "7.10.8"},
    )
    mock_coordinator.devices = {device.serial: device}
    mock_coordinator.get_device = MagicMock(return_value=device)
    mock_coordinator.protocol = MagicMock()
    mock_coordinator.protocol.query_ota_info = AsyncMock(
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
    _patch_write_state(entity)

    with (
        patch(
            "custom_components.lipro.firmware_manifest.async_load_remote_firmware_manifest",
            AsyncMock(return_value=(frozenset(), {})),
        ),
        patch(
            "custom_components.lipro.firmware_manifest.load_verified_firmware_manifest",
            return_value=(frozenset(), {"21p3": frozenset({"7.10.9"})}),
        ),
    ):
        await entity.async_update()

    assert entity.latest_version == "7.10.9"
    assert entity.extra_state_attributes["certified"] is True


def test_update_entity_is_version_newer_error_returns_false(
    mock_coordinator, make_device
):
    """Certification version comparison should not fallback to string order."""
    from custom_components.lipro.entities.firmware_update import (
        LiproFirmwareUpdateEntity,
    )

    device = make_device(
        "light",
        serial="03ab5ccd7c555555",
        properties={"version": "1.0.0"},
    )
    entity = LiproFirmwareUpdateEntity(mock_coordinator, device)

    with patch.object(entity, "version_is_newer", side_effect=ValueError("invalid")):
        assert entity._is_version_newer("2.0.0-beta", "1.0.0") is False


def test_update_entity_certified_matching_compare_error_is_conservative(
    mock_coordinator, make_device
):
    """Certification matching should stay conservative on compare errors."""
    from custom_components.lipro.core.ota.manifest import matches_certified_versions
    from custom_components.lipro.entities.firmware_update import (
        LiproFirmwareUpdateEntity,
    )

    device = make_device(
        "light",
        serial="03ab5ccd7c666666",
        properties={"version": "1.0.0"},
    )
    entity = LiproFirmwareUpdateEntity(mock_coordinator, device)

    with patch.object(entity, "version_is_newer", side_effect=ValueError("invalid")):
        assert (
            matches_certified_versions(
                {"2.0.0-beta"},
                installed="1.0.0",
                latest="2.0.0-beta",
                is_version_newer=entity._is_version_newer,
            )
            is True
        )
        assert (
            matches_certified_versions(
                {"2.0.0-beta"},
                installed="1.0.0",
                latest="2.0.0-rc",
                is_version_newer=entity._is_version_newer,
            )
            is False
        )
