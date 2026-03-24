"""Tests for update-entity background refresh task concerns."""

from __future__ import annotations

import asyncio
from datetime import timedelta
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from custom_components.lipro import firmware_manifest
from custom_components.lipro.core import LiproApiError
from custom_components.lipro.core.ota import rows_cache
from custom_components.lipro.entities import firmware_update as firmware_update_module
from custom_components.lipro.entities.firmware_update import LiproFirmwareUpdateEntity
from homeassistant.util import dt as dt_util


@pytest.fixture(autouse=True)
def _clear_shared_ota_rows_cache():
    rows_cache.clear_shared_ota_rows_cache()
    yield
    rows_cache.clear_shared_ota_rows_cache()


def _read_ota_refresh_task(
    entity: LiproFirmwareUpdateEntity,
) -> asyncio.Task[None] | None:
    """Return the current OTA refresh task with an explicit typed read."""
    return entity._ota_refresh_task


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

    assert _read_ota_refresh_task(entity) is None
    debug.assert_called_once()
    assert debug.call_args.args[0] == "OTA refresh task failed during removal (%s)"
    assert debug.call_args.args[1] == "RuntimeError"


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

    assert _read_ota_refresh_task(entity) is None
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
async def test_async_refresh_ota_returns_early_when_not_force_and_not_stale(
    mock_coordinator, make_device
) -> None:
    entity = LiproFirmwareUpdateEntity(mock_coordinator, make_device("light"))
    query_rows = AsyncMock()

    with (
        patch.object(entity, "_should_refresh_ota", return_value=False),
        patch("custom_components.lipro.entities.firmware_update.async_select_row_with_shared_cache", new=query_rows),
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
    mock_coordinator.protocol.query_ota_info = AsyncMock(
        return_value=[{"deviceType": "ff000001"}]
    )

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
        patch("custom_components.lipro.entities.firmware_update.async_select_row_with_shared_cache", new=query_rows),
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
        patch(
            "custom_components.lipro.core.ota.rows_cache.async_get_rows_with_shared_cache",
            new=query_rows,
        ),
        patch.object(entity, "_query_ota_rows_from_cloud", new=query_cloud),
    ):
        await entity._async_refresh_ota(force=True)

    assert isinstance(entity.last_error, LiproApiError)
    write_state.assert_called_once()
