"""Coordinator polling service - stable refresh and polling surface."""

from __future__ import annotations

import asyncio
from collections.abc import Callable
from dataclasses import dataclass
import logging
from typing import TYPE_CHECKING

from ..outlet_power import apply_outlet_power_info, should_reraise_outlet_power_error
from ..runtime.outlet_power_runtime import query_outlet_power

if TYPE_CHECKING:
    from ...device import LiproDevice
    from ..runtime.device_runtime import DeviceRuntime
    from ..runtime.status_runtime import StatusRuntime
    from ..runtime.tuning_runtime import TuningRuntime
    from ..types import StatusQueryMetrics
    from .mqtt_service import CoordinatorMqttService
    from .protocol_service import CoordinatorProtocolService


@dataclass(slots=True)
class CoordinatorPollingService:
    """Expose coordinator-managed refresh and polling flows through one seam."""

    device_runtime: DeviceRuntime
    status_runtime: StatusRuntime
    tuning_runtime: TuningRuntime
    protocol_service: CoordinatorProtocolService
    mqtt_service: CoordinatorMqttService
    devices_getter: Callable[[], dict[str, LiproDevice]]
    replace_devices: Callable[[dict[str, LiproDevice]], None]
    publish_updated_data: Callable[[dict[str, LiproDevice]], None]
    get_device_by_id: Callable[[str], LiproDevice | None]
    has_mqtt_transport_getter: Callable[[], bool]
    logger: logging.Logger

    async def async_refresh_devices(self) -> dict[str, LiproDevice]:
        """Force a full device snapshot refresh and publish the latest state."""
        await self.async_refresh_device_snapshot(force=True, mqtt_timeout_seconds=5)
        refreshed_devices = dict(self.devices_getter())
        self.publish_updated_data(refreshed_devices)
        return refreshed_devices

    def get_outlet_ids_for_power_polling(self) -> list[str]:
        """Resolve the current outlet IDs participating in power polling."""
        snapshot = self.device_runtime.get_last_snapshot()
        if snapshot is not None and snapshot.outlet_ids:
            return list(snapshot.outlet_ids)
        return [
            device.iot_device_id
            for device in self.devices_getter().values()
            if device.capabilities.is_outlet and device.iot_device_id
        ]

    async def async_run_outlet_power_polling(self) -> None:
        """Refresh outlet power info on the canonical coordinator polling path."""
        if not self.status_runtime.should_query_power():
            return

        outlet_ids = self.get_outlet_ids_for_power_polling()
        if not outlet_ids:
            return

        outlet_ids_to_query = self.status_runtime.get_outlet_power_query_slice(
            outlet_ids
        )
        if not outlet_ids_to_query:
            return

        await query_outlet_power(
            outlet_ids_to_query=outlet_ids_to_query,
            round_robin_index=0,
            resolve_cycle_size=lambda total_devices: total_devices,
            fetch_outlet_power_info=self.protocol_service.async_fetch_outlet_power_info,
            get_device_by_id=lambda device_id: (
                self.get_device_by_id(device_id) if isinstance(device_id, str) else None
            ),
            apply_outlet_power_info=apply_outlet_power_info,
            should_reraise_outlet_power_error=should_reraise_outlet_power_error,
            logger=self.logger,
            concurrency=max(1, min(3, len(outlet_ids_to_query))),
        )
        self.status_runtime.mark_power_query_complete()
        self.status_runtime.advance_outlet_power_cycle(outlet_ids)

    async def async_refresh_device_snapshot(
        self,
        *,
        force: bool,
        mqtt_timeout_seconds: float | None = None,
    ) -> None:
        """Refresh device snapshot, synchronize state, and sync MQTT."""
        snapshot = await self.device_runtime.refresh_devices(force=force)
        self.replace_devices(snapshot.devices)

        if not self.has_mqtt_transport_getter():
            return

        if mqtt_timeout_seconds is None:
            await self.mqtt_service.async_sync_subscriptions()
            return

        async with asyncio.timeout(mqtt_timeout_seconds):
            await self.mqtt_service.async_sync_subscriptions()

    async def async_run_status_polling(self) -> None:
        """Run adaptive REST status polling and follow-up outlet power refresh."""
        devices = self.devices_getter()
        candidates = self.status_runtime.filter_query_candidates(
            devices,
            list(devices.keys()),
            mqtt_connected=self.mqtt_service.connected,
        )

        results: list[StatusQueryMetrics] = []
        if candidates:
            batches = self.status_runtime.compute_query_batches(candidates)
            if batches:
                results = await self.status_runtime.execute_parallel_queries(batches)

        for metrics in results:
            device_count = metrics.get("device_count", 0)
            duration = metrics.get("duration", 0.0)
            if device_count > 0 and duration > 0:
                self.tuning_runtime.record_batch_metric(
                    batch_size=device_count,
                    duration=duration,
                    device_count=device_count,
                )

        new_batch_size = self.tuning_runtime.compute_adaptive_batch_size()
        if new_batch_size is not None:
            self.status_runtime.update_batch_size(new_batch_size)

        await self.async_run_outlet_power_polling()


__all__ = ["CoordinatorPollingService"]
