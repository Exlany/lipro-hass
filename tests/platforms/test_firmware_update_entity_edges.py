"""Edge-branch tests for firmware update entity runtime paths."""

from __future__ import annotations

import asyncio
from collections.abc import Generator
from datetime import timedelta
from typing import cast
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from custom_components.lipro import firmware_manifest
from custom_components.lipro.core import LiproApiError
from custom_components.lipro.core.ota import rows_cache
from custom_components.lipro.core.ota.candidate import _InstallCommand, _OtaCandidate
from custom_components.lipro.entities import firmware_update as firmware_update_module
from custom_components.lipro.entities.firmware_update import LiproFirmwareUpdateEntity
from homeassistant.exceptions import HomeAssistantError
from homeassistant.util import dt as dt_util


@pytest.fixture(autouse=True)
def _clear_ota_rows_shared_cache() -> Generator[None]:
    rows_cache.clear_shared_ota_rows_cache()
    yield
    rows_cache.clear_shared_ota_rows_cache()


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


@pytest.mark.asyncio
async def test_async_added_to_hass_loads_manifest_and_schedules_refresh(
    mock_coordinator, make_device
) -> None:
    device = make_device("light", serial="03ab5ccd7c101010")
    entity = LiproFirmwareUpdateEntity(mock_coordinator, device)

    with (
        patch(
            "custom_components.lipro.entities.firmware_update.LiproEntity.async_added_to_hass",
            new=AsyncMock(),
        ) as super_added,
        patch(
            "custom_components.lipro.entities.firmware_update.asyncio.to_thread",
            new=AsyncMock(),
        ) as to_thread,
        patch.object(entity, "_schedule_ota_refresh") as schedule_refresh,
    ):
        await entity.async_added_to_hass()

    super_added.assert_awaited_once()
    to_thread.assert_awaited_once_with(
        firmware_manifest.load_verified_firmware_manifest
    )
    schedule_refresh.assert_called_once_with(force=True)


@pytest.mark.asyncio
async def test_async_will_remove_from_hass_logs_task_exception_from_cancel(
    mock_coordinator, make_device
) -> None:
    device = make_device("light", serial="03ab5ccd7c202020")
    entity = LiproFirmwareUpdateEntity(mock_coordinator, device)

    async def _cancel_then_boom() -> None:
        try:
            await asyncio.sleep(10)
        except asyncio.CancelledError as err:
            raise RuntimeError("cancel boom") from err

    task = asyncio.create_task(_cancel_then_boom())
    await asyncio.sleep(0)
    entity._ota_refresh_task = task

    with (
        patch(
            "custom_components.lipro.entities.firmware_update.LiproEntity.async_will_remove_from_hass",
            new=AsyncMock(),
        ),
        patch(
            "custom_components.lipro.entities.firmware_update._LOGGER.debug"
        ) as debug,
    ):
        await entity.async_will_remove_from_hass()

    assert cast(asyncio.Task[None] | None, entity._ota_refresh_task) is None
    debug.assert_called_once()
    assert debug.call_args.args[0] == "OTA refresh task failed during removal (%s)"
    assert debug.call_args.args[1] == "RuntimeError"


def test_handle_coordinator_update_refreshes_installed_version_and_schedules(
    mock_coordinator, make_device
) -> None:
    device = make_device(
        "light",
        serial="03ab5ccd7c303030",
        properties={"version": "1.0.0"},
    )
    entity = LiproFirmwareUpdateEntity(mock_coordinator, device)

    with (
        patch(
            "custom_components.lipro.entities.firmware_update.LiproEntity._handle_coordinator_update"
        ) as super_update,
        patch.object(entity, "_schedule_ota_refresh") as schedule_refresh,
    ):
        device.properties["version"] = "1.2.3"
        entity._handle_coordinator_update()

    assert entity.installed_version == "1.2.3"
    schedule_refresh.assert_called_once_with(force=False)
    super_update.assert_called_once()


@pytest.mark.asyncio
async def test_async_install_raises_when_no_update_available(
    mock_coordinator, make_device
) -> None:
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


def test_schedule_ota_refresh_skips_when_not_forced_and_not_stale(
    mock_coordinator, make_device
) -> None:
    entity = LiproFirmwareUpdateEntity(mock_coordinator, make_device("light"))
    entity.hass = MagicMock()

    with patch.object(entity, "_should_refresh_ota", return_value=False):
        entity._schedule_ota_refresh(force=False)

    entity.hass.async_create_task.assert_not_called()


def test_schedule_ota_refresh_skips_when_existing_task_is_pending(
    mock_coordinator, make_device
) -> None:
    entity = LiproFirmwareUpdateEntity(mock_coordinator, make_device("light"))
    entity.hass = MagicMock()
    pending_task = MagicMock()
    pending_task.done.return_value = False
    entity._ota_refresh_task = pending_task

    entity._schedule_ota_refresh(force=True)

    entity.hass.async_create_task.assert_not_called()


def test_schedule_ota_refresh_creates_task_and_registers_done_callback(
    mock_coordinator, make_device
) -> None:
    entity = LiproFirmwareUpdateEntity(mock_coordinator, make_device("light"))
    entity.hass = MagicMock()
    created_task = MagicMock()
    created_task.done.return_value = False
    entity.hass.async_create_task.return_value = created_task

    entity._schedule_ota_refresh(force=True)

    entity.hass.async_create_task.assert_called_once()
    scheduled_coro = entity.hass.async_create_task.call_args.args[0]
    assert asyncio.iscoroutine(scheduled_coro)
    scheduled_coro.close()
    created_task.add_done_callback.assert_called_once_with(
        entity._async_finalize_refresh_task
    )
    assert entity._ota_refresh_task is created_task


@pytest.mark.asyncio
async def test_async_finalize_refresh_task_returns_early_when_no_error(
    mock_coordinator, make_device
) -> None:
    entity = LiproFirmwareUpdateEntity(mock_coordinator, make_device("light"))
    write_state = MagicMock()

    async def _ok() -> None:
        return None

    with patch.object(entity, "async_write_ha_state", write_state):
        task = asyncio.create_task(_ok())
        await task
        entity._ota_refresh_task = task

        entity._async_finalize_refresh_task(task)

    assert cast(asyncio.Task[None] | None, entity._ota_refresh_task) is None
    write_state.assert_not_called()


@pytest.mark.asyncio
async def test_async_clear_refresh_task_returns_none_for_success() -> None:
    async def _ok() -> None:
        return None

    task = asyncio.create_task(_ok())
    await task
    assert LiproFirmwareUpdateEntity._async_clear_refresh_task(task) is None


def test_set_last_error_without_callback_only_stores_error(
    mock_coordinator, make_device
) -> None:
    entity = LiproFirmwareUpdateEntity(mock_coordinator, make_device("light"))
    err = RuntimeError("ota error")

    entity._set_last_error(err)

    assert entity.last_error is err


def test_should_refresh_ota_respects_refresh_interval(
    mock_coordinator, make_device
) -> None:
    entity = LiproFirmwareUpdateEntity(mock_coordinator, make_device("light"))
    now = dt_util.utcnow()

    with patch(
        "custom_components.lipro.entities.firmware_update.dt_util.utcnow",
        return_value=now,
    ):
        entity._last_ota_refresh = (
            now - firmware_update_module._OTA_REFRESH_INTERVAL + timedelta(seconds=1)
        )
        assert entity._should_refresh_ota() is False

        entity._last_ota_refresh = now - firmware_update_module._OTA_REFRESH_INTERVAL
        assert entity._should_refresh_ota() is True


@pytest.mark.asyncio
async def test_query_ota_rows_with_shared_cache_rechecks_cache_inside_lock(
    mock_coordinator, make_device
) -> None:
    device = make_device("light", serial="03ab5ccd7c707070")
    mock_coordinator.protocol = MagicMock()
    mock_coordinator.protocol.query_ota_info = AsyncMock(return_value=[])
    entity = LiproFirmwareUpdateEntity(mock_coordinator, device)
    cache_key = entity._ota_rows_cache_key()
    cached_rows = [{"deviceId": device.serial, "latestVersion": "1.1.0"}]

    async with rows_cache._OTA_ROWS_CACHE_LOCK:
        task = asyncio.create_task(entity._query_ota_rows_with_shared_cache())
        await asyncio.sleep(0)
        rows_cache._OTA_ROWS_CACHE[cache_key] = rows_cache.OtaRowsCacheEntry(
            time=dt_util.utcnow(),
            rows=cached_rows,
        )

    rows, from_cache = await task
    assert rows == cached_rows
    assert from_cache is True
    mock_coordinator.protocol.query_ota_info.assert_not_awaited()


@pytest.mark.asyncio
async def test_async_refresh_ota_returns_early_when_not_force_and_not_stale(
    mock_coordinator, make_device
) -> None:
    entity = LiproFirmwareUpdateEntity(mock_coordinator, make_device("light"))
    query_rows = AsyncMock()

    with (
        patch.object(entity, "_should_refresh_ota", return_value=False),
        patch.object(entity, "_query_ota_rows_with_shared_cache", new=query_rows),
    ):
        await entity._async_refresh_ota(force=False)

    query_rows.assert_not_awaited()


@pytest.mark.asyncio
async def test_query_ota_rows_from_cloud_prefers_light_v2_fallback(
    mock_coordinator, make_device
) -> None:
    device = make_device(
        "light",
        serial="mesh_group_49155",
        iot_name="21P3",
    )
    entity = LiproFirmwareUpdateEntity(mock_coordinator, device)
    mock_coordinator.protocol.query_ota_info = AsyncMock(return_value=[{"deviceType": "ff000001"}])

    result = await entity._query_ota_rows_from_cloud()

    assert result == [{"deviceType": "ff000001"}]
    mock_coordinator.protocol.query_ota_info.assert_awaited_once_with(
        device_id="mesh_group_49155",
        device_type=device.device_type_hex,
        iot_name="21P3",
        allow_rich_v2_fallback=True,
    )


@pytest.mark.asyncio
async def test_async_refresh_ota_stores_error_when_shared_query_fails(
    mock_coordinator, make_device
) -> None:
    device = make_device("light", serial="03ab5ccd7c808080")
    entity = LiproFirmwareUpdateEntity(mock_coordinator, device)
    write_state = MagicMock()
    query_rows = AsyncMock(side_effect=LiproApiError("shared fail", 500))

    with (
        patch.object(entity, "async_write_ha_state", write_state),
        patch.object(entity, "_query_ota_rows_with_shared_cache", new=query_rows),
    ):
        await entity._async_refresh_ota(force=True)

    assert isinstance(entity.last_error, LiproApiError)
    write_state.assert_called_once()


@pytest.mark.asyncio
async def test_async_refresh_ota_stores_error_when_direct_query_after_cache_mismatch_fails(
    mock_coordinator, make_device
) -> None:
    device = make_device("light", serial="03ab5ccd7c909090")
    entity = LiproFirmwareUpdateEntity(mock_coordinator, device)
    write_state = MagicMock()
    query_rows = AsyncMock(return_value=([{"deviceId": "03ab5ccd7c000000"}], True))
    query_cloud = AsyncMock(side_effect=LiproApiError("direct fail", 500))

    with (
        patch.object(entity, "async_write_ha_state", write_state),
        patch.object(entity, "_query_ota_rows_with_shared_cache", new=query_rows),
        patch.object(entity, "_query_ota_rows_from_cloud", new=query_cloud),
    ):
        await entity._async_refresh_ota(force=True)

    assert isinstance(entity.last_error, LiproApiError)
    write_state.assert_called_once()


def test_apply_ota_candidate_clears_release_attributes_when_candidate_missing(
    mock_coordinator, make_device
) -> None:
    entity = LiproFirmwareUpdateEntity(mock_coordinator, make_device("light"))
    entity._ota_candidate = None
    entity._attr_release_summary = "old summary"
    entity._attr_release_url = "https://example.com/release"

    entity._apply_ota_candidate()

    assert entity.release_summary is None
    assert entity.release_url is None


def test_resolve_local_manifest_certification_ignores_remote_advisory_truth() -> None:
    from custom_components.lipro.core.ota.candidate import (
        OtaManifestTruth,
        resolve_certification,
    )

    assert resolve_certification(
        {"latestVersion": "8.0.0"},
        installed="7.0.0",
        latest="8.0.0",
        device_iot_name="21P3",
        manifest_truth=OtaManifestTruth(
            verified_versions=frozenset(),
            versions_by_type={},
        ),
        is_version_newer=lambda candidate, current: candidate > current,
    ) is False
