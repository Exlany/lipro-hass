"""Tests for update-entity refresh and OTA row selection concerns."""

from __future__ import annotations

from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from custom_components.lipro.core.ota import rows_cache


@pytest.fixture(autouse=True)
def _clear_shared_ota_rows_cache():
    rows_cache.clear_shared_ota_rows_cache()
    yield
    rows_cache.clear_shared_ota_rows_cache()


def _patch_write_state(entity: object) -> None:
    """Patch instance-level state writer to avoid Home Assistant side effects."""
    patch.object(entity, "async_write_ha_state", new=MagicMock()).start()


@pytest.mark.asyncio
async def test_update_entity_reuses_shared_ota_rows_cache_for_same_model(
    mock_coordinator, make_device
):
    """Entities with same model key should share one OTA cloud query."""
    from custom_components.lipro.entities.firmware_update import (
        LiproFirmwareUpdateEntity,
    )

    dev_a = make_device(
        "light",
        serial="03ab5ccd7c111111",
        properties={"version": "1.0.0"},
    )
    dev_b = make_device(
        "light",
        serial="03ab5ccd7c222222",
        properties={"version": "1.0.0"},
    )
    mock_coordinator.devices = {dev_a.serial: dev_a, dev_b.serial: dev_b}
    mock_coordinator.get_device = MagicMock(
        side_effect=lambda serial: mock_coordinator.devices.get(serial)
    )
    mock_coordinator.protocol = MagicMock()
    mock_coordinator.protocol.query_ota_info = AsyncMock(
        return_value=[
            {
                "deviceType": dev_a.device_type_hex,
                "latestVersion": "1.1.0",
                "certified": True,
            }
        ]
    )

    ent_a = LiproFirmwareUpdateEntity(mock_coordinator, dev_a)
    ent_b = LiproFirmwareUpdateEntity(mock_coordinator, dev_b)

    with (
        patch.object(ent_a, "async_write_ha_state"),
        patch.object(ent_b, "async_write_ha_state"),
    ):
        await ent_a.async_update()
        await ent_b.async_update()

    assert ent_a.latest_version == "1.1.0"
    assert ent_b.latest_version == "1.1.0"
    assert mock_coordinator.protocol.query_ota_info.await_count == 1


@pytest.mark.asyncio
async def test_update_entity_cache_row_for_other_device_falls_back_to_direct_query(
    mock_coordinator, make_device
):
    """Cached serial-specific row should trigger direct query for another device."""
    from custom_components.lipro.entities.firmware_update import (
        LiproFirmwareUpdateEntity,
    )

    dev_a = make_device(
        "light",
        serial="03ab5ccd7c111111",
        properties={"version": "1.0.0"},
    )
    dev_b = make_device(
        "light",
        serial="03ab5ccd7c222222",
        properties={"version": "1.0.0"},
    )
    mock_coordinator.devices = {dev_a.serial: dev_a, dev_b.serial: dev_b}
    mock_coordinator.get_device = MagicMock(
        side_effect=lambda serial: mock_coordinator.devices.get(serial)
    )
    mock_coordinator.protocol = MagicMock()
    mock_coordinator.protocol.query_ota_info = AsyncMock(
        side_effect=[
            [
                {
                    "deviceId": dev_a.serial,
                    "deviceType": dev_a.device_type_hex,
                    "latestVersion": "1.1.0",
                    "certified": True,
                }
            ],
            [
                {
                    "deviceId": dev_b.serial,
                    "deviceType": dev_b.device_type_hex,
                    "latestVersion": "1.2.0",
                    "certified": True,
                }
            ],
        ]
    )

    ent_a = LiproFirmwareUpdateEntity(mock_coordinator, dev_a)
    ent_b = LiproFirmwareUpdateEntity(mock_coordinator, dev_b)
    _patch_write_state(ent_a)
    _patch_write_state(ent_b)

    await ent_a.async_update()
    await ent_b.async_update()

    assert ent_a.latest_version == "1.1.0"
    assert ent_b.latest_version == "1.2.0"
    assert mock_coordinator.protocol.query_ota_info.await_count == 2


@pytest.mark.asyncio
async def test_update_entity_prefers_controller_row_matching_device_iot_name(
    mock_coordinator, make_device
):
    """Controller OTA row selection should prefer row whose bleName matches device iot_name."""
    from custom_components.lipro.entities.firmware_update import (
        LiproFirmwareUpdateEntity,
    )

    device = make_device(
        "switch",
        serial="03ab5ccd7c222222",
        iot_name="T21JE",
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
    _patch_write_state(entity)
    await entity.async_update()

    assert entity.latest_version == "2.6.44"


@pytest.mark.asyncio
async def test_update_entity_version_compare_error_is_conservative(
    mock_coordinator, make_device
):
    """Version parse errors should not infer update availability."""
    from custom_components.lipro.entities.firmware_update import (
        LiproFirmwareUpdateEntity,
    )

    device = make_device(
        "light",
        serial="03ab5ccd7c444444",
        properties={"version": "1.0.0"},
    )
    mock_coordinator.devices = {device.serial: device}
    mock_coordinator.get_device = MagicMock(return_value=device)
    mock_coordinator.protocol = MagicMock()
    mock_coordinator.protocol.query_ota_info = AsyncMock(
        return_value=[
            {
                "deviceType": device.device_type_hex,
                "latestVersion": "1.0.0+build.bad",
            }
        ]
    )

    entity = LiproFirmwareUpdateEntity(mock_coordinator, device)
    _patch_write_state(entity)

    with patch.object(entity, "version_is_newer", side_effect=ValueError("invalid")):
        await entity.async_update()

    assert entity._ota_candidate is not None
    assert entity._ota_candidate.update_available is False
