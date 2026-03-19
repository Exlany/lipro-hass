"""Tests for the refactored MQTT transport composition."""

from __future__ import annotations

import asyncio
from collections.abc import Callable
import importlib
from typing import cast
from unittest.mock import AsyncMock, MagicMock

import pytest

from custom_components.lipro.core.mqtt.connection_manager import MqttConnectionManager
from custom_components.lipro.core.mqtt.message_processor import MqttMessageProcessor
from custom_components.lipro.core.mqtt.payload import parse_mqtt_payload
from custom_components.lipro.core.mqtt.topic_builder import MqttTopicBuilder
from custom_components.lipro.core.mqtt.transport import MqttTransport


def _make_transport(**kwargs) -> MqttTransport:
    return MqttTransport(
        access_key="access",
        secret_key="secret",
        biz_id="biz001",
        phone_id="550e8400-e29b-41d4-a716-446655440000",
        **kwargs,
    )


def test_mqtt_package_keeps_transport_out_of_package_exports() -> None:
    mqtt_package_module = importlib.import_module(
        "custom_components.lipro.core.mqtt"
    )
    transport_module = importlib.import_module(
        "custom_components.lipro.core.mqtt.transport"
    )

    assert not hasattr(mqtt_package_module, "MqttTransport")
    assert hasattr(transport_module, "MqttTransport")


def test_transport_initializes_refactored_helpers() -> None:
    transport = _make_transport()

    assert isinstance(transport._message_processor, MqttMessageProcessor)
    assert isinstance(transport._topic_builder, MqttTopicBuilder)
    assert isinstance(transport._connection_manager, MqttConnectionManager)


def test_transport_build_topic_pairs_delegates_to_topic_builder() -> None:
    transport = _make_transport()
    topic_builder = MagicMock(spec=MqttTopicBuilder)
    topic_builder.build_topic_pairs.return_value = [("dev1", "topic/1")]
    transport._topic_builder = topic_builder

    topic_pairs = transport._build_topic_pairs(
        ["dev1"],
        invalid_log_message="Skipping invalid MQTT device ID %s",
    )

    assert topic_pairs == [("dev1", "topic/1")]
    topic_builder.build_topic_pairs.assert_called_once_with(
        ["dev1"],
        invalid_log_message="Skipping invalid MQTT device ID %s",
        on_invalid=None,
    )


def test_transport_batched_topic_pairs_delegates_to_topic_builder() -> None:
    transport = _make_transport()
    topic_builder = MagicMock(spec=MqttTopicBuilder)
    topic_builder.batch_topic_pairs.return_value = [[("dev1", "topic/1")]]
    transport._topic_builder = topic_builder

    batches = transport._batched_topic_pairs([("dev1", "topic/1")])

    assert batches == [[("dev1", "topic/1")]]
    topic_builder.batch_topic_pairs.assert_called_once_with([("dev1", "topic/1")])


def test_transport_process_message_delegates_to_message_processor() -> None:
    on_message = MagicMock()
    transport = _make_transport(on_message=on_message)
    processor = MagicMock(spec=MqttMessageProcessor)
    message = MagicMock()
    transport._message_processor = processor

    transport._process_message(message)

    processor.process_message.assert_called_once()
    args = processor.process_message.call_args.args
    kwargs = processor.process_message.call_args.kwargs
    assert args == (message,)
    assert kwargs["parse_payload"] is parse_mqtt_payload
    assert kwargs["on_message"] is on_message
    assert kwargs["invoke_callback"] == transport._invoke_callback
    assert kwargs["set_last_error"] == transport._set_last_error
    assert kwargs["clear_last_error"] == transport._clear_last_error


@pytest.mark.asyncio
async def test_transport_connection_loop_delegates_to_connection_manager() -> None:
    transport = _make_transport()
    connection_manager = MagicMock(spec=MqttConnectionManager)
    connection_manager.run_connection_loop = AsyncMock()
    transport._connection_manager = connection_manager
    transport._connected = True
    transport._broker_client = MagicMock()

    await transport._connection_loop()

    connection_manager.run_connection_loop.assert_awaited_once()
    kwargs = connection_manager.run_connection_loop.call_args.kwargs
    assert callable(kwargs["is_running"])
    assert kwargs["connect_and_listen"] == transport._connect_and_listen
    assert kwargs["set_last_error"] == transport._set_last_error
    assert kwargs["handle_disconnect"] == transport._handle_disconnect
    assert transport.is_connected is False
    assert transport._broker_client is None


def test_transport_handle_disconnect_delegates_to_connection_manager() -> None:
    transport = _make_transport()
    connection_manager = MagicMock(spec=MqttConnectionManager)
    transport._connection_manager = connection_manager
    transport._connected = True
    transport._broker_client = MagicMock()

    transport._handle_disconnect("MQTT error: boom")

    call_args = connection_manager.handle_disconnect.call_args
    assert call_args is not None
    args = call_args.args
    kwargs: dict[str, object] = call_args.kwargs
    assign_connected = cast(Callable[[bool], None], kwargs["assign_connected"])
    clear_client = cast(Callable[[], None], kwargs["clear_client"])
    assert args == ("MQTT error: boom",)
    assign_connected(False)
    clear_client()
    assert transport.is_connected is False
    assert transport._broker_client is None


def test_transport_error_helpers_delegate_to_connection_manager() -> None:
    transport = _make_transport()
    connection_manager = MagicMock(spec=MqttConnectionManager)
    connection_manager.invoke_callback.return_value = False

    def _assign_error(err: Exception, *, assign_last_error) -> None:
        assign_last_error(err)

    def _clear_error(*, assign_last_error) -> None:
        assign_last_error(None)

    connection_manager.set_last_error.side_effect = _assign_error
    connection_manager.clear_last_error.side_effect = _clear_error
    transport._connection_manager = connection_manager

    callback = MagicMock()
    err = RuntimeError("boom")

    assert (
        transport._invoke_callback(callback, "on_message", "dev1", {})
        is False
    )
    transport._set_last_error(err)
    assert transport.last_error is err
    transport._clear_last_error()
    assert transport.last_error is None


@pytest.mark.asyncio
async def test_transport_finalize_connection_task_delegates_to_connection_manager() -> None:
    transport = _make_transport()
    connection_manager = MagicMock(spec=MqttConnectionManager)
    transport._connection_manager = connection_manager

    async def _done() -> None:
        return None

    task = asyncio.create_task(_done())
    await asyncio.gather(task)
    transport._task = task

    def _finalize(
        current_task: asyncio.Task[None], *, clear_task_ref, set_last_error
    ) -> None:
        clear_task_ref(current_task)

    connection_manager.finalize_connection_task.side_effect = _finalize

    transport._async_finalize_connection_task(task)

    connection_manager.finalize_connection_task.assert_called_once()
    assert transport._task is None


@pytest.mark.asyncio
async def test_wait_until_connected_uses_real_transport_event() -> None:
    transport = _make_transport()
    transport._running = True

    async def _mark_connected() -> None:
        await asyncio.sleep(0)
        transport._connected = True
        transport._connected_event.set()

    task = asyncio.create_task(_mark_connected())
    assert await transport.wait_until_connected(timeout=1) is True
    await task
