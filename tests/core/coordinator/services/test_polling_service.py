"""Tests for the coordinator polling/refresh service."""

from __future__ import annotations

import logging
from typing import cast
from unittest.mock import AsyncMock, MagicMock

import pytest

from custom_components.lipro.core.coordinator.services.polling_service import (
    CoordinatorPollingService,
)
from custom_components.lipro.core.device import LiproDevice


def _replace_devices(
    devices: dict[str, LiproDevice], snapshot_devices: dict[str, LiproDevice]
) -> None:
    devices.clear()
    devices.update(snapshot_devices)


@pytest.mark.asyncio
async def test_polling_service_refresh_devices_updates_state_and_notifies() -> None:
    device = cast(LiproDevice, MagicMock())
    devices: dict[str, LiproDevice] = {}
    snapshot = MagicMock(devices={"dev1": device})
    device_runtime = MagicMock(refresh_devices=AsyncMock(return_value=snapshot))
    mqtt_service = MagicMock(connected=False, async_sync_subscriptions=AsyncMock())
    publisher = MagicMock()

    service = CoordinatorPollingService(
        device_runtime=device_runtime,
        status_runtime=MagicMock(),
        tuning_runtime=MagicMock(),
        protocol_service=MagicMock(async_fetch_outlet_power_info=AsyncMock()),
        mqtt_service=mqtt_service,
        devices_getter=lambda: devices,
        replace_devices=lambda snapshot_devices: _replace_devices(
            devices, snapshot_devices
        ),
        publish_updated_data=publisher,
        get_device_by_id=lambda device_id: devices.get(device_id),
        has_mqtt_transport_getter=lambda: False,
        logger=logging.getLogger(__name__),
    )

    result = await service.async_refresh_devices()

    assert devices == {"dev1": device}
    assert result == {"dev1": device}
    publisher.assert_called_once_with({"dev1": device})
    device_runtime.refresh_devices.assert_awaited_once_with(force=True)


def test_polling_service_prefers_snapshot_outlet_ids() -> None:
    snapshot = MagicMock(outlet_ids=["outlet-a"])
    service = CoordinatorPollingService(
        device_runtime=MagicMock(get_last_snapshot=MagicMock(return_value=snapshot)),
        status_runtime=MagicMock(),
        tuning_runtime=MagicMock(),
        protocol_service=MagicMock(async_fetch_outlet_power_info=AsyncMock()),
        mqtt_service=MagicMock(connected=False, async_sync_subscriptions=AsyncMock()),
        devices_getter=dict,
        replace_devices=MagicMock(),
        publish_updated_data=MagicMock(),
        get_device_by_id=lambda _device_id: None,
        has_mqtt_transport_getter=lambda: False,
        logger=logging.getLogger(__name__),
    )

    assert service.get_outlet_ids_for_power_polling() == ["outlet-a"]


@pytest.mark.asyncio
async def test_polling_service_refresh_snapshot_syncs_mqtt_when_transport_exists() -> (
    None
):
    devices: dict[str, LiproDevice] = {}
    snapshot = MagicMock(devices={"dev1": cast(LiproDevice, MagicMock())})
    device_runtime = MagicMock(refresh_devices=AsyncMock(return_value=snapshot))
    mqtt_service = MagicMock(connected=True, async_sync_subscriptions=AsyncMock())
    service = CoordinatorPollingService(
        device_runtime=device_runtime,
        status_runtime=MagicMock(),
        tuning_runtime=MagicMock(),
        protocol_service=MagicMock(async_fetch_outlet_power_info=AsyncMock()),
        mqtt_service=mqtt_service,
        devices_getter=lambda: devices,
        replace_devices=lambda snapshot_devices: _replace_devices(
            devices, snapshot_devices
        ),
        publish_updated_data=MagicMock(),
        get_device_by_id=lambda device_id: devices.get(device_id),
        has_mqtt_transport_getter=lambda: True,
        logger=logging.getLogger(__name__),
    )

    await service.async_refresh_device_snapshot(force=True, mqtt_timeout_seconds=None)

    assert set(devices) == {"dev1"}
    mqtt_service.async_sync_subscriptions.assert_awaited_once_with()


@pytest.mark.asyncio
async def test_polling_service_status_polling_updates_tuning_and_power_cycle() -> None:
    device = cast(
        LiproDevice,
        MagicMock(
            capabilities=MagicMock(is_outlet=True),
            iot_device_id="outlet-1",
        ),
    )
    devices: dict[str, LiproDevice] = {"dev1": device}
    status_runtime = MagicMock()
    status_runtime.filter_query_candidates.return_value = ["dev1"]
    status_runtime.compute_query_batches.return_value = [["dev1"]]
    status_runtime.execute_parallel_queries = AsyncMock(
        return_value=[{"device_count": 1, "duration": 1.5}]
    )
    status_runtime.should_query_power.return_value = False
    tuning_runtime = MagicMock(compute_adaptive_batch_size=MagicMock(return_value=48))
    service = CoordinatorPollingService(
        device_runtime=MagicMock(get_last_snapshot=MagicMock(return_value=None)),
        status_runtime=status_runtime,
        tuning_runtime=tuning_runtime,
        protocol_service=MagicMock(async_fetch_outlet_power_info=AsyncMock()),
        mqtt_service=MagicMock(connected=True, async_sync_subscriptions=AsyncMock()),
        devices_getter=lambda: devices,
        replace_devices=MagicMock(),
        publish_updated_data=MagicMock(),
        get_device_by_id=lambda device_id: devices.get(device_id),
        has_mqtt_transport_getter=lambda: False,
        logger=logging.getLogger(__name__),
    )

    await service.async_run_status_polling()

    tuning_runtime.record_batch_metric.assert_called_once_with(
        batch_size=1,
        duration=1.5,
        device_count=1,
    )
    status_runtime.update_batch_size.assert_called_once_with(48)
