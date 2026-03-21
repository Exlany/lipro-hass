"""Coordinator lifecycle helpers for MQTT setup, update cycles, and shutdown."""

from __future__ import annotations

import asyncio
from collections.abc import Awaitable, Callable
import logging

from homeassistant.config_entries import ConfigEntry
from homeassistant.exceptions import ConfigEntryAuthFailed
from homeassistant.helpers.update_coordinator import UpdateFailed

from ..api import (
    LiproApiError,
    LiproAuthError,
    LiproConnectionError,
    LiproRefreshTokenExpiredError,
)
from ..device import LiproDevice
from ..protocol import LiproProtocolFacade
from ..utils.background_task_manager import BackgroundTaskManager
from .mqtt.setup import build_mqtt_subscription_device_ids
from .mqtt_lifecycle import async_setup_mqtt as setup_mqtt_lifecycle
from .runtime.device.snapshot import RuntimeSnapshotRefreshRejectedError
from .runtime.device_runtime import DeviceRuntime
from .runtime.mqtt_runtime import MqttRuntime
from .services import CoordinatorTelemetryService

_LOGGER = logging.getLogger(__name__)


class CoordinatorUpdateCycle:
    """Own the coordinator's scheduled update orchestration without becoming a root."""

    def __init__(
        self,
        *,
        ensure_authenticated: Callable[[], Awaitable[None]],
        should_refresh_device_list: Callable[[], bool],
        refresh_device_snapshot: Callable[[], Awaitable[None]],
        has_mqtt_transport: Callable[[], bool],
        has_devices: Callable[[], bool],
        setup_mqtt: Callable[[], Awaitable[bool]],
        run_status_polling: Callable[[], Awaitable[None]],
        telemetry_service: CoordinatorTelemetryService,
        devices_getter: Callable[[], dict[str, LiproDevice]],
    ) -> None:
        """Capture the callables and state needed for one coordinator update cycle."""
        self._ensure_authenticated = ensure_authenticated
        self._should_refresh_device_list = should_refresh_device_list
        self._refresh_device_snapshot = refresh_device_snapshot
        self._has_mqtt_transport = has_mqtt_transport
        self._has_devices = has_devices
        self._setup_mqtt = setup_mqtt
        self._run_status_polling = run_status_polling
        self._telemetry_service = telemetry_service
        self._devices_getter = devices_getter

    async def _async_refresh_snapshot_if_needed(self) -> None:
        await async_refresh_snapshot_if_needed(
            should_refresh_device_list=self._should_refresh_device_list,
            refresh_device_snapshot=self._refresh_device_snapshot,
        )

    async def _async_setup_mqtt_if_needed(self) -> None:
        await async_setup_mqtt_if_needed(
            has_transport=self._has_mqtt_transport(),
            has_devices=self._has_devices(),
            setup_mqtt=self._setup_mqtt,
        )

    async def _async_run_status_polling_if_needed(self) -> None:
        await async_run_status_polling_if_needed(
            has_devices=self._has_devices(),
            run_status_polling=self._run_status_polling,
        )

    async def _async_run_update_cycle(self) -> None:
        await async_run_update_cycle(
            ensure_authenticated=self._ensure_authenticated,
            refresh_snapshot_if_needed=self._async_refresh_snapshot_if_needed,
            setup_mqtt_if_needed=self._async_setup_mqtt_if_needed,
            run_status_polling_if_needed=self._async_run_status_polling_if_needed,
        )

    async def async_update_data(self) -> dict[str, LiproDevice]:
        """Run the scheduled update cycle and return the canonical device mapping."""
        return await async_update_data(
            run_update_cycle=self._async_run_update_cycle,
            telemetry_service=self._telemetry_service,
            devices=self._devices_getter(),
        )


async def _async_run_best_effort_shutdown_step(
    *,
    label: str,
    operation: Callable[[], Awaitable[object]],
) -> None:
    """Run one shutdown step with explicit best-effort semantics."""
    try:
        await operation()
    except asyncio.CancelledError:
        raise
    except (
        LookupError,
        OSError,
        RuntimeError,
        TypeError,
        ValueError,
    ) as err:
        _LOGGER.warning(
            "%s failed during best-effort shutdown (%s)",
            label,
            type(err).__name__,
        )


async def async_setup_mqtt(
    *,
    protocol: LiproProtocolFacade,
    config_entry: ConfigEntry | None,
    devices: dict[str, LiproDevice],
    background_task_manager: BackgroundTaskManager,
    mqtt_runtime: MqttRuntime,
) -> bool:
    """Set up MQTT transport for one coordinator runtime."""
    if config_entry is None:
        _LOGGER.error("Cannot setup MQTT: config_entry is None")
        return False

    device_ids = build_mqtt_subscription_device_ids(devices)
    if not device_ids:
        return False

    if mqtt_runtime.has_transport:
        if mqtt_runtime.is_connected:
            await mqtt_runtime.sync_subscriptions(device_ids)
            return True
        return await mqtt_runtime.connect(device_ids=device_ids)

    result = await setup_mqtt_lifecycle(
        protocol=protocol,
        config_entry=config_entry,
        background_task_manager=background_task_manager,
        devices=devices,
        mqtt_runtime=mqtt_runtime,
    )
    return result is not None


async def async_shutdown(
    *,
    protocol: LiproProtocolFacade,
    mqtt_runtime: MqttRuntime,
    device_runtime: DeviceRuntime,
    background_task_manager: BackgroundTaskManager,
    shutdown_command_service: Callable[[], Awaitable[None]],
) -> None:
    """Release coordinator-owned MQTT and background resources."""
    await _async_run_best_effort_shutdown_step(
        label="MQTT disconnect notification cleanup",
        operation=mqtt_runtime.clear_disconnect_notification,
    )
    await _async_run_best_effort_shutdown_step(
        label="Command service shutdown",
        operation=shutdown_command_service,
    )
    await _async_run_best_effort_shutdown_step(
        label="MQTT runtime shutdown",
        operation=mqtt_runtime.disconnect,
    )
    await _async_run_best_effort_shutdown_step(
        label="Background task shutdown",
        operation=background_task_manager.cancel_all,
    )

    protocol.attach_mqtt_facade(None)
    mqtt_runtime.detach_transport()
    mqtt_runtime.reset()
    device_runtime.reset()


async def async_refresh_snapshot_if_needed(
    *,
    should_refresh_device_list: Callable[[], bool],
    refresh_device_snapshot: Callable[[], Awaitable[None]],
) -> None:
    """Refresh the canonical device snapshot when runtime policy requests it."""
    if not should_refresh_device_list():
        return
    async with asyncio.timeout(10):
        await refresh_device_snapshot()


async def async_setup_mqtt_if_needed(
    *,
    has_transport: bool,
    has_devices: bool,
    setup_mqtt: Callable[[], Awaitable[bool]],
) -> None:
    """Attach MQTT transport when devices exist and no transport is bound yet."""
    if has_transport or not has_devices:
        return
    async with asyncio.timeout(5):
        await setup_mqtt()


async def async_run_status_polling_if_needed(
    *,
    has_devices: bool,
    run_status_polling: Callable[[], Awaitable[None]],
) -> None:
    """Run adaptive status polling only when devices are currently tracked."""
    if not has_devices:
        return
    async with asyncio.timeout(10):
        await run_status_polling()


async def async_run_update_cycle(
    *,
    ensure_authenticated: Callable[[], Awaitable[None]],
    refresh_snapshot_if_needed: Callable[[], Awaitable[None]],
    setup_mqtt_if_needed: Callable[[], Awaitable[None]],
    run_status_polling_if_needed: Callable[[], Awaitable[None]],
) -> None:
    """Run the coordinator's scheduled update stages inside the global timeout."""
    async with asyncio.timeout(30):
        await ensure_authenticated()
        await refresh_snapshot_if_needed()
        await setup_mqtt_if_needed()
        await run_status_polling_if_needed()


async def async_update_data(
    *,
    run_update_cycle: Callable[[], Awaitable[None]],
    telemetry_service: CoordinatorTelemetryService,
    devices: dict[str, LiproDevice],
) -> dict[str, LiproDevice]:
    """Fetch data for one update-coordinator cycle."""
    try:
        await run_update_cycle()
        telemetry_service.record_update_success()
        return devices

    except asyncio.CancelledError:
        raise
    except TimeoutError:
        telemetry_service.record_update_failure(
            TimeoutError("Update timeout"),
            stage="timeout",
        )
        _LOGGER.error("Update data timeout after 30 seconds")
        raise UpdateFailed("Update timeout") from None

    except (
        LiproRefreshTokenExpiredError,
        LiproAuthError,
    ) as err:
        telemetry_service.record_update_failure(err, stage="auth")
        _LOGGER.error("Authentication failed: %s", err)
        error_message = f"Authentication failed: {err}"
        raise ConfigEntryAuthFailed(error_message) from err

    except (
        LiproConnectionError,
        LiproApiError,
    ) as err:
        telemetry_service.record_update_failure(err, stage="protocol")
        _LOGGER.error("Update failed: %s", err)
        error_message = f"Update failed: {err}"
        raise UpdateFailed(error_message) from err

    except RuntimeSnapshotRefreshRejectedError as err:
        telemetry_service.record_update_failure(err, stage="runtime")
        _LOGGER.warning("Device snapshot refresh rejected: %s", err)
        raise UpdateFailed(str(err)) from err

    except (
        AttributeError,
        LookupError,
        OSError,
        RuntimeError,
        TypeError,
        ValueError,
    ) as err:
        telemetry_service.record_update_failure(err, stage="unexpected")
        _LOGGER.exception("Unexpected update failure")
        raise UpdateFailed("Unexpected update failure") from err


__all__ = [
    "CoordinatorUpdateCycle",
    "async_refresh_snapshot_if_needed",
    "async_run_status_polling_if_needed",
    "async_run_update_cycle",
    "async_setup_mqtt",
    "async_setup_mqtt_if_needed",
    "async_shutdown",
    "async_update_data",
]
