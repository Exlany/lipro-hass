"""Tests for update-entity install flow concerns."""

from __future__ import annotations

from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from custom_components.lipro.core.ota.candidate import _InstallCommand, _OtaCandidate
from homeassistant.exceptions import HomeAssistantError


def _candidate(
    *,
    update_available: bool,
    latest_version: str | None,
    certified: bool = True,
    command: str = "CHANGE_STATE",
    properties: list[dict[str, str]] | None = None,
) -> _OtaCandidate:
    install_command = _InstallCommand(command=command, properties=properties)
    return _OtaCandidate(
        installed_version=None,
        latest_version=latest_version,
        update_available=update_available,
        certified=certified,
        release_summary=None,
        release_url=None,
        install_command=install_command,
    )


def _patch_write_state(entity: object) -> None:
    """Patch instance-level state writer to avoid Home Assistant side effects."""
    patch.object(entity, "async_write_ha_state", new=MagicMock()).start()


@pytest.mark.asyncio
async def test_update_entity_installs_certified_firmware(mock_coordinator, make_device):
    """Certified firmware should install directly."""
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
    _patch_write_state(entity)
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
    _patch_write_state(entity)
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
                "deviceType": device.device_type_hex,
                "latestVersion": "1.1.0",
                "needUpgrade": True,
                "certified": True,
            }
        ]
    )

    entity = LiproFirmwareUpdateEntity(mock_coordinator, device)
    _patch_write_state(entity)
    await entity.async_update()

    with pytest.raises(HomeAssistantError) as err:
        await entity.async_install(version=None, backup=False)
    assert err.value.translation_key == "firmware_install_unsupported"


@pytest.mark.asyncio
async def test_async_install_raises_when_no_update_available(
    mock_coordinator, make_device
) -> None:
    from custom_components.lipro.entities.firmware_update import (
        LiproFirmwareUpdateEntity,
    )

    device = make_device("light", serial="03ab5ccd7c404040")
    entity = LiproFirmwareUpdateEntity(mock_coordinator, device)
    entity._ota_candidate = None

    with (
        patch.object(entity, "async_write_ha_state"),
        patch.object(entity, "_async_refresh_ota", new=AsyncMock(return_value=None)),
        pytest.raises(HomeAssistantError) as err,
    ):
        await entity.async_install(version=None, backup=False)

    assert err.value.translation_key == "firmware_no_update"


@pytest.mark.asyncio
async def test_async_install_raises_when_requested_version_mismatch(
    mock_coordinator, make_device
) -> None:
    from custom_components.lipro.entities.firmware_update import (
        LiproFirmwareUpdateEntity,
    )

    device = make_device("light", serial="03ab5ccd7c505050")
    entity = LiproFirmwareUpdateEntity(mock_coordinator, device)
    entity._ota_candidate = _candidate(update_available=True, latest_version="1.1.0")

    with (
        patch.object(entity, "async_write_ha_state"),
        patch.object(entity, "_async_refresh_ota", new=AsyncMock(return_value=None)),
        pytest.raises(HomeAssistantError) as err,
    ):
        await entity.async_install(version="2.0.0", backup=False)

    assert err.value.translation_key == "firmware_version_mismatch"
    assert err.value.translation_placeholders == {"version": "2.0.0"}


@pytest.mark.asyncio
async def test_async_install_raises_when_send_command_returns_false(
    mock_coordinator, make_device
) -> None:
    from custom_components.lipro.entities.firmware_update import (
        LiproFirmwareUpdateEntity,
    )

    device = make_device("light", serial="03ab5ccd7c606060")
    mock_coordinator.async_send_command = AsyncMock(return_value=False)
    entity = LiproFirmwareUpdateEntity(mock_coordinator, device)
    entity._ota_candidate = _candidate(
        update_available=True,
        latest_version="1.1.0",
        certified=True,
    )

    with (
        patch.object(entity, "async_write_ha_state"),
        patch.object(entity, "_async_refresh_ota", new=AsyncMock(return_value=None)),
        pytest.raises(HomeAssistantError) as err,
    ):
        await entity.async_install(version=None, backup=False)

    assert err.value.translation_key == "firmware_install_failed"
    assert entity.in_progress is False
