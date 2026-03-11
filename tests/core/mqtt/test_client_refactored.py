"""Tests for the refactored MQTT client composition."""

from __future__ import annotations

import asyncio
from collections.abc import Callable
from typing import cast
from unittest.mock import AsyncMock, MagicMock

import pytest

from custom_components.lipro.core.mqtt.connection_manager import MqttConnectionManager
from custom_components.lipro.core.mqtt.message_processor import MqttMessageProcessor
from custom_components.lipro.core.mqtt.mqtt_client import LiproMqttClient
from custom_components.lipro.core.mqtt.payload import parse_mqtt_payload
from custom_components.lipro.core.mqtt.topic_builder import MqttTopicBuilder


def _make_client(**kwargs) -> LiproMqttClient:
    return LiproMqttClient(
        access_key="access",
        secret_key="secret",
        biz_id="biz001",
        phone_id="550e8400-e29b-41d4-a716-446655440000",
        **kwargs,
    )


def test_client_initializes_refactored_helpers() -> None:
    client = _make_client()

    assert isinstance(client._message_processor, MqttMessageProcessor)
    assert isinstance(client._topic_builder, MqttTopicBuilder)
    assert isinstance(client._connection_manager, MqttConnectionManager)


def test_client_build_topic_pairs_delegates_to_topic_builder() -> None:
    client = _make_client()
    topic_builder = MagicMock(spec=MqttTopicBuilder)
    topic_builder.build_topic_pairs.return_value = [("dev1", "topic/1")]
    client._topic_builder = topic_builder

    topic_pairs = client._build_topic_pairs(
        ["dev1"],
        invalid_log_message="Skipping invalid MQTT device ID %s",
    )

    assert topic_pairs == [("dev1", "topic/1")]
    topic_builder.build_topic_pairs.assert_called_once_with(
        ["dev1"],
        invalid_log_message="Skipping invalid MQTT device ID %s",
        on_invalid=None,
    )


def test_client_batched_topic_pairs_delegates_to_topic_builder() -> None:
    client = _make_client()
    topic_builder = MagicMock(spec=MqttTopicBuilder)
    topic_builder.batch_topic_pairs.return_value = [[("dev1", "topic/1")]]
    client._topic_builder = topic_builder

    batches = client._batched_topic_pairs([("dev1", "topic/1")])

    assert batches == [[("dev1", "topic/1")]]
    topic_builder.batch_topic_pairs.assert_called_once_with([("dev1", "topic/1")])


def test_client_process_message_delegates_to_message_processor() -> None:
    on_message = MagicMock()
    client = _make_client(on_message=on_message)
    processor = MagicMock(spec=MqttMessageProcessor)
    message = MagicMock()
    client._message_processor = processor

    client._process_message(message)

    processor.process_message.assert_called_once()
    args = processor.process_message.call_args.args
    kwargs = processor.process_message.call_args.kwargs
    assert args == (message,)
    assert kwargs["parse_payload"] is parse_mqtt_payload
    assert kwargs["on_message"] is on_message
    assert kwargs["invoke_callback"] == client._invoke_callback
    assert kwargs["set_last_error"] == client._set_last_error
    assert kwargs["clear_last_error"] == client._clear_last_error


@pytest.mark.asyncio
async def test_client_connection_loop_delegates_to_connection_manager() -> None:
    client = _make_client()
    connection_manager = MagicMock(spec=MqttConnectionManager)
    connection_manager.run_connection_loop = AsyncMock()
    client._connection_manager = connection_manager
    client._connected = True
    client._client = MagicMock()

    await client._connection_loop()

    connection_manager.run_connection_loop.assert_awaited_once()
    kwargs = connection_manager.run_connection_loop.call_args.kwargs
    assert callable(kwargs["is_running"])
    assert kwargs["connect_and_listen"] == client._connect_and_listen
    assert kwargs["set_last_error"] == client._set_last_error
    assert kwargs["handle_disconnect"] == client._handle_disconnect
    assert client.is_connected is False
    assert client._client is None


def test_client_handle_disconnect_delegates_to_connection_manager() -> None:
    client = _make_client()
    connection_manager = MagicMock(spec=MqttConnectionManager)
    client._connection_manager = connection_manager
    client._connected = True
    client._client = MagicMock()

    client._handle_disconnect("MQTT error: boom")

    call_args = connection_manager.handle_disconnect.call_args
    assert call_args is not None
    args = call_args.args
    kwargs: dict[str, object] = call_args.kwargs
    assign_connected = cast(Callable[[bool], None], kwargs["assign_connected"])
    clear_client = cast(Callable[[], None], kwargs["clear_client"])
    assert args == ("MQTT error: boom",)
    assign_connected(False)
    clear_client()
    assert client.is_connected is False
    assert client._client is None


def test_client_error_helpers_delegate_to_connection_manager() -> None:
    client = _make_client()
    connection_manager = MagicMock(spec=MqttConnectionManager)
    connection_manager.invoke_callback.return_value = False

    def _assign_error(err: Exception, *, assign_last_error) -> None:
        assign_last_error(err)

    def _clear_error(*, assign_last_error) -> None:
        assign_last_error(None)

    connection_manager.set_last_error.side_effect = _assign_error
    connection_manager.clear_last_error.side_effect = _clear_error
    client._connection_manager = connection_manager

    callback = MagicMock()
    err = RuntimeError("boom")

    assert client._invoke_callback(callback, "on_message", "dev1", {}) is False
    client._set_last_error(err)
    assert client.last_error is err
    client._clear_last_error()
    assert client.last_error is None



@pytest.mark.asyncio
async def test_client_finalize_connection_task_delegates_to_connection_manager() -> None:
    client = _make_client()
    connection_manager = MagicMock(spec=MqttConnectionManager)
    client._connection_manager = connection_manager

    async def _done() -> None:
        return None

    task = asyncio.create_task(_done())
    await asyncio.gather(task)
    client._task = task

    def _finalize(current_task: asyncio.Task[None], *, clear_task_ref, set_last_error) -> None:
        clear_task_ref(current_task)

    connection_manager.finalize_connection_task.side_effect = _finalize

    client._async_finalize_connection_task(task)

    connection_manager.finalize_connection_task.assert_called_once()
    assert client._task is None
