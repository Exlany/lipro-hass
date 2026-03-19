"""Tests for the extracted MQTT connection manager."""

from __future__ import annotations

import asyncio
import logging
from unittest.mock import AsyncMock, MagicMock

import aiomqtt
import pytest

from custom_components.lipro.const.api import MQTT_RECONNECT_MIN_DELAY
from custom_components.lipro.core.mqtt.connection_manager import MqttConnectionManager


def test_connection_manager_invoke_callback_captures_callback_failure(caplog) -> None:
    manager = MqttConnectionManager()
    set_last_error = MagicMock()

    with caplog.at_level(logging.ERROR):
        ok = manager.invoke_callback(
            MagicMock(side_effect=RuntimeError("boom")),
            "on_connect",
            set_last_error,
        )

    assert ok is False
    err = set_last_error.call_args.args[0]
    assert isinstance(err, RuntimeError)
    assert str(err) == "boom"
    assert "MQTT on_connect callback failed (RuntimeError)" in caplog.text


def test_connection_manager_set_last_error_notifies_error_hook(caplog) -> None:
    assigned: list[Exception | None] = []
    manager = MqttConnectionManager(
        on_error=MagicMock(side_effect=RuntimeError("hook boom"))
    )
    err = ValueError("bad payload")

    with caplog.at_level(logging.ERROR):
        manager.set_last_error(
            err,
            assign_last_error=assigned.append,
        )

    assert assigned == [err]
    assert "MQTT error callback failed (RuntimeError)" in caplog.text


def test_connection_manager_handle_disconnect_clears_state_and_reports_callback_error() -> None:
    assign_connected = MagicMock()
    clear_client = MagicMock()
    set_last_error = MagicMock()
    manager = MqttConnectionManager(
        on_disconnect=MagicMock(side_effect=RuntimeError("disconnect boom"))
    )

    manager.handle_disconnect(
        "MQTT error: boom",
        assign_connected=assign_connected,
        clear_client=clear_client,
        set_last_error=set_last_error,
    )

    assign_connected.assert_called_once_with(False)
    clear_client.assert_called_once_with()
    err = set_last_error.call_args.args[0]
    assert isinstance(err, RuntimeError)
    assert str(err) == "disconnect boom"


@pytest.mark.asyncio
async def test_connection_manager_finalize_connection_task_sets_last_error() -> None:
    manager = MqttConnectionManager()
    clear_task_ref = MagicMock()
    set_last_error = MagicMock()

    async def _boom() -> None:
        raise RuntimeError("loop boom")

    task = asyncio.create_task(_boom())
    await asyncio.gather(task, return_exceptions=True)

    manager.finalize_connection_task(
        task,
        clear_task_ref=clear_task_ref,
        set_last_error=set_last_error,
    )

    clear_task_ref.assert_called_once_with(task)
    err = set_last_error.call_args.args[0]
    assert isinstance(err, RuntimeError)
    assert str(err) == "loop boom"


@pytest.mark.asyncio
async def test_connection_manager_consume_task_exception_returns_none_for_cancelled() -> None:
    async def _sleep() -> None:
        await asyncio.sleep(0)

    task = asyncio.create_task(_sleep())
    task.cancel()
    await asyncio.gather(task, return_exceptions=True)

    assert MqttConnectionManager.consume_task_exception(task) is None


@pytest.mark.asyncio
async def test_connection_manager_run_connection_loop_retries_after_mqtt_error() -> None:
    manager = MqttConnectionManager()
    set_last_error = MagicMock()
    handle_disconnect = MagicMock()
    sleep_calls: list[float] = []
    state = {"running": True}

    async def _sleep(wait_time: float) -> None:
        sleep_calls.append(wait_time)
        state["running"] = False

    connect_and_listen = AsyncMock(side_effect=aiomqtt.MqttError("boom"))

    await manager.run_connection_loop(
        is_running=lambda: state["running"],
        connect_and_listen=connect_and_listen,
        set_last_error=set_last_error,
        handle_disconnect=handle_disconnect,
        sleep=_sleep,
        jitter_source=lambda _low, _high: 0.0,
    )

    connect_and_listen.assert_awaited_once_with()
    err = set_last_error.call_args.args[0]
    assert isinstance(err, aiomqtt.MqttError)
    assert str(err) == "boom"
    handle_disconnect.assert_called_once_with("MQTT error: boom")
    assert sleep_calls == [MQTT_RECONNECT_MIN_DELAY]


@pytest.mark.asyncio
async def test_connection_manager_run_connection_loop_stops_on_cancelled_error() -> None:
    manager = MqttConnectionManager()
    set_last_error = MagicMock()
    handle_disconnect = MagicMock()
    sleep = AsyncMock()

    await manager.run_connection_loop(
        is_running=lambda: True,
        connect_and_listen=AsyncMock(side_effect=asyncio.CancelledError()),
        set_last_error=set_last_error,
        handle_disconnect=handle_disconnect,
        sleep=sleep,
        jitter_source=lambda _low, _high: 0.0,
    )

    set_last_error.assert_not_called()
    handle_disconnect.assert_not_called()
    sleep.assert_not_awaited()


@pytest.mark.asyncio
async def test_connection_manager_run_connection_loop_reraises_programming_error() -> None:
    manager = MqttConnectionManager()
    set_last_error = MagicMock()
    handle_disconnect = MagicMock()
    sleep = AsyncMock()

    with pytest.raises(TypeError, match="bad callback"):
        await manager.run_connection_loop(
            is_running=lambda: True,
            connect_and_listen=AsyncMock(side_effect=TypeError("bad callback")),
            set_last_error=set_last_error,
            handle_disconnect=handle_disconnect,
            sleep=sleep,
            jitter_source=lambda _low, _high: 0.0,
        )

    set_last_error.assert_not_called()
    handle_disconnect.assert_not_called()
    sleep.assert_not_awaited()


@pytest.mark.asyncio
async def test_connection_manager_run_connection_loop_resets_backoff_after_success() -> None:
    manager = MqttConnectionManager()
    set_last_error = MagicMock()
    handle_disconnect = MagicMock()
    sleep_calls: list[float] = []
    state = {"running": True}

    async def _sleep(wait_time: float) -> None:
        sleep_calls.append(wait_time)
        if len(sleep_calls) >= 2:
            state["running"] = False

    connect_and_listen = AsyncMock(side_effect=[None, aiomqtt.MqttError("boom")])

    await manager.run_connection_loop(
        is_running=lambda: state["running"],
        connect_and_listen=connect_and_listen,
        set_last_error=set_last_error,
        handle_disconnect=handle_disconnect,
        sleep=_sleep,
        jitter_source=lambda _low, _high: 0.0,
    )

    assert sleep_calls == [MQTT_RECONNECT_MIN_DELAY, MQTT_RECONNECT_MIN_DELAY]
    handle_disconnect.assert_called_once_with("MQTT error: boom")
