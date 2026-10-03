"""Failure and cancellation contracts for coordinator resource cleanup."""

from __future__ import annotations

import asyncio
from unittest.mock import AsyncMock, MagicMock

import pytest

from custom_components.lipro.core.coordinator import lifecycle, mqtt_lifecycle
from custom_components.lipro.core.device import LiproDevice


@pytest.mark.parametrize(
    "failure", [RuntimeError("cleanup failed"), OSError("offline")]
)
async def test_shutdown_continues_after_cleanup_failure(failure: Exception) -> None:
    """A failed cleanup must not strand the remaining resources."""
    protocol = MagicMock()
    runtime = MagicMock()
    runtime.clear_disconnect_notification = AsyncMock(side_effect=failure)
    runtime.disconnect = AsyncMock()
    devices = MagicMock()
    tasks = MagicMock(cancel_all=AsyncMock())
    shutdown_commands = AsyncMock()

    await lifecycle.async_shutdown(
        protocol=protocol,
        mqtt_runtime=runtime,
        device_runtime=devices,
        background_task_manager=tasks,
        shutdown_command_service=shutdown_commands,
    )

    shutdown_commands.assert_awaited_once()
    runtime.disconnect.assert_awaited_once()
    tasks.cancel_all.assert_awaited_once()
    protocol.attach_mqtt_facade.assert_called_once_with(None)
    runtime.detach_transport.assert_called_once()
    runtime.reset.assert_called_once()
    devices.reset.assert_called_once()


async def test_shutdown_propagates_cancellation() -> None:
    """Cancellation must not be converted into a best-effort warning."""
    runtime = MagicMock(
        clear_disconnect_notification=AsyncMock(side_effect=asyncio.CancelledError)
    )
    shutdown_commands = AsyncMock()
    with pytest.raises(asyncio.CancelledError):
        await lifecycle.async_shutdown(
            protocol=MagicMock(),
            mqtt_runtime=runtime,
            device_runtime=MagicMock(),
            background_task_manager=MagicMock(),
            shutdown_command_service=shutdown_commands,
        )
    shutdown_commands.assert_not_awaited()
    runtime.reset.assert_not_called()


@pytest.mark.parametrize("failure", [RuntimeError("disconnect failed"), TimeoutError()])
async def test_failed_setup_detaches_even_when_disconnect_fails(
    failure: Exception,
) -> None:
    """A failed transport close must not leave a bound unusable facade."""
    protocol = MagicMock()
    runtime = MagicMock(disconnect=AsyncMock(side_effect=failure))
    await mqtt_lifecycle._teardown_failed_mqtt_setup(
        protocol=protocol, mqtt_runtime=runtime, mqtt_facade=MagicMock()
    )
    runtime.detach_transport.assert_called_once()
    protocol.attach_mqtt_facade.assert_called_once_with(None)


async def test_failed_setup_teardown_propagates_cancellation() -> None:
    """Transport close cancellation must reach its lifecycle owner."""
    protocol = MagicMock()
    runtime = MagicMock(disconnect=AsyncMock(side_effect=asyncio.CancelledError))
    with pytest.raises(asyncio.CancelledError):
        await mqtt_lifecycle._teardown_failed_mqtt_setup(
            protocol=protocol, mqtt_runtime=runtime, mqtt_facade=MagicMock()
        )
    runtime.detach_transport.assert_not_called()


@pytest.mark.parametrize("connected", [True, False])
async def test_setup_reuses_existing_transport(connected: bool) -> None:
    """Reconnect or refresh subscriptions without constructing a second transport."""
    protocol = MagicMock()
    runtime = MagicMock(
        has_transport=True,
        is_connected=connected,
        sync_subscriptions=AsyncMock(),
        connect=AsyncMock(return_value=True),
    )
    device = LiproDevice(
        device_number=1,
        serial="device1",
        name="Light",
        device_type=1,
        iot_name="lipro_light",
    )
    assert await lifecycle.async_setup_mqtt(
        protocol=protocol,
        config_entry=MagicMock(),
        devices={"device1": device},
        background_task_manager=MagicMock(),
        mqtt_runtime=runtime,
    )
    if connected:
        runtime.sync_subscriptions.assert_awaited_once_with(["device1"])
        runtime.connect.assert_not_awaited()
    else:
        runtime.connect.assert_awaited_once_with(device_ids=["device1"])
        runtime.sync_subscriptions.assert_not_awaited()
    protocol.build_mqtt_facade.assert_not_called()


async def test_config_timeout_does_not_bind_transport() -> None:
    """Timeout records a typed failure and leaves setup safe to retry."""
    protocol = MagicMock(get_mqtt_config=AsyncMock(side_effect=TimeoutError))
    runtime = MagicMock()
    result = await mqtt_lifecycle.async_setup_mqtt(
        protocol=protocol,
        config_entry=MagicMock(),
        background_task_manager=MagicMock(),
        devices={},
        mqtt_runtime=runtime,
    )
    assert result is None
    runtime.handle_transport_error.assert_called_once()
    call = runtime.handle_transport_error.call_args
    assert isinstance(call.args[0], TimeoutError)
    assert call.kwargs == {"stage": "config_fetch"}
    runtime.bind_transport.assert_not_called()
    protocol.build_mqtt_facade.assert_not_called()
