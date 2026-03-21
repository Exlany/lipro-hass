"""Tests for Lipro MQTT transport."""

from __future__ import annotations

import asyncio
import logging
from typing import TYPE_CHECKING, cast
from unittest.mock import AsyncMock, MagicMock, patch

import aiomqtt
import pytest

from custom_components.lipro.core.mqtt.transport import MqttTransport


class TestConnectAndListen:
    """Tests for connect/listen and payload decoding paths."""

    @pytest.mark.asyncio
    async def test_connect_and_listen_subscribes_and_processes_messages(self, caplog):
        """Connect/listen should subscribe valid IDs, skip invalid ones, and process stream.

        Also verifies TLS context is cached across reconnects to avoid rebuilding it.
        """
        on_connect = MagicMock()
        client = MqttTransport(
            access_key="access",
            secret_key="secret",
            biz_id="biz001",
            phone_id="550e8400-e29b-41d4-a716-446655440000",
            on_connect=on_connect,
        )
        client._subscribed_devices = {"valid_dev", "bad/dev"}

        async def _messages():
            yield MagicMock(topic="Topic_Device_State/biz001/valid_dev")

        mqtt_client_1 = AsyncMock()
        mqtt_client_1.messages = _messages()
        mqtt_client_2 = AsyncMock()
        mqtt_client_2.messages = _messages()

        with (
            patch(
                "custom_components.lipro.core.mqtt.transport_runtime.ssl.create_default_context"
            ) as mock_tls,
            patch(
                "custom_components.lipro.core.mqtt.transport_runtime.aiomqtt.Client"
            ) as mock_client_cls,
            patch.object(client, "_process_message") as mock_process,
        ):
            context_manager_1 = AsyncMock()
            context_manager_1.__aenter__.return_value = mqtt_client_1
            context_manager_1.__aexit__.return_value = False
            context_manager_2 = AsyncMock()
            context_manager_2.__aenter__.return_value = mqtt_client_2
            context_manager_2.__aexit__.return_value = False
            mock_client_cls.side_effect = [context_manager_1, context_manager_2]

            # Connect twice to simulate reconnects: TLS context should be reused.
            with caplog.at_level(logging.WARNING):
                await client._connect_and_listen()
                await client._connect_and_listen()

        mock_tls.assert_called_once()
        assert mock_client_cls.call_count == 2
        assert (
            mock_client_cls.call_args_list[0].kwargs["tls_context"]
            is mock_client_cls.call_args_list[1].kwargs["tls_context"]
        )
        assert (
            mock_tls.return_value
            is mock_client_cls.call_args_list[0].kwargs["tls_context"]
        )
        assert on_connect.call_count == 2
        mqtt_client_1.subscribe.assert_called_once()
        mqtt_client_2.subscribe.assert_called_once()
        assert mock_process.call_count == 2
        assert "bad/dev" not in client._subscribed_devices
        # Message stream ends after one yielded message; client should no longer
        # report itself connected once _connect_and_listen returns.
        assert client.is_connected is False
        assert "bad/dev" not in caplog.text
        assert "invalid characters" in caplog.text

    @pytest.mark.asyncio
    async def test_connect_and_listen_batches_pending_and_current_topics(self):
        """Connect/listen should batch queued unsubscribes and subscriptions."""
        client = MqttTransport(
            access_key="access",
            secret_key="secret",
            biz_id="biz001",
            phone_id="550e8400-e29b-41d4-a716-446655440000",
        )
        client._pending_unsubscribe = {f"old_{idx}" for idx in range(55)}
        client._subscribed_devices = {f"new_{idx}" for idx in range(55)}

        async def _messages():
            if TYPE_CHECKING:
                yield None

        mqtt_client = AsyncMock()
        mqtt_client.messages = _messages()

        with patch(
            "custom_components.lipro.core.mqtt.transport_runtime.aiomqtt.Client"
        ) as mock_client_cls:
            context_manager = AsyncMock()
            context_manager.__aenter__.return_value = mqtt_client
            context_manager.__aexit__.return_value = False
            mock_client_cls.return_value = context_manager

            await client._connect_and_listen()

        assert mqtt_client.unsubscribe.await_count == 2
        assert mqtt_client.subscribe.await_count == 2
        assert client._pending_unsubscribe == set()
        assert client._subscribed_devices == {f"new_{idx}" for idx in range(55)}

    @pytest.mark.asyncio
    async def test_connect_and_listen_keeps_last_error_when_on_connect_fails(self):
        """on_connect callback failures should remain observable via last_error."""
        on_connect = MagicMock(side_effect=RuntimeError("callback boom"))
        client = MqttTransport(
            access_key="access",
            secret_key="secret",
            biz_id="biz001",
            phone_id="550e8400-e29b-41d4-a716-446655440000",
            on_connect=on_connect,
        )

        async def _messages():
            if TYPE_CHECKING:
                yield None

        mqtt_client = AsyncMock()
        mqtt_client.messages = _messages()

        with patch(
            "custom_components.lipro.core.mqtt.transport_runtime.aiomqtt.Client"
        ) as mock_client_cls:
            context_manager = AsyncMock()
            context_manager.__aenter__.return_value = mqtt_client
            context_manager.__aexit__.return_value = False
            mock_client_cls.return_value = context_manager

            await client._connect_and_listen()

        assert isinstance(client.last_error, RuntimeError)
        assert str(client.last_error) == "callback boom"


class TestConnectionLoop:
    """Tests for reconnection loop with backoff/jitter."""

    @pytest.mark.asyncio
    async def test_connection_loop_retries_after_mqtt_error(self):
        client = MqttTransport(
            access_key="access",
            secret_key="secret",
            biz_id="biz001",
            phone_id="550e8400-e29b-41d4-a716-446655440000",
        )
        client._running = True
        client._connected = True
        client._broker_client = MagicMock()

        with (
            patch.object(
                client,
                "_connect_and_listen",
                side_effect=[aiomqtt.MqttError("boom"), asyncio.CancelledError()],
            ),
            patch(
                "custom_components.lipro.core.mqtt.transport_runtime.random.uniform",
                return_value=0.0,
            ),
            patch(
                "custom_components.lipro.core.mqtt.transport_runtime.asyncio.sleep",
                new_callable=AsyncMock,
            ) as sleep,
        ):
            await client._connection_loop()

        sleep.assert_awaited_once()
        assert client._connected is False
        assert client._broker_client is None

    @pytest.mark.asyncio
    async def test_connection_loop_handles_oserror(self):
        client = MqttTransport(
            access_key="access",
            secret_key="secret",
            biz_id="biz001",
            phone_id="550e8400-e29b-41d4-a716-446655440000",
        )
        client._running = True

        async def _sleep_and_stop(_: float) -> None:
            client._running = False

        with (
            patch.object(
                client,
                "_connect_and_listen",
                side_effect=OSError("network down"),
            ),
            patch(
                "custom_components.lipro.core.mqtt.transport_runtime.random.uniform",
                return_value=0.0,
            ),
            patch(
                "custom_components.lipro.core.mqtt.transport_runtime.asyncio.sleep",
                side_effect=_sleep_and_stop,
            ) as sleep,
        ):
            await client._connection_loop()

        sleep.assert_called_once()
        assert client._connected is False

    @pytest.mark.asyncio
    async def test_connection_loop_handles_value_error(self):
        client = MqttTransport(
            access_key="access",
            secret_key="secret",
            biz_id="biz001",
            phone_id="550e8400-e29b-41d4-a716-446655440000",
        )
        client._running = True

        async def _sleep_and_stop(_: float) -> None:
            client._running = False

        with (
            patch.object(
                client,
                "_connect_and_listen",
                side_effect=ValueError("invalid topic"),
            ),
            patch(
                "custom_components.lipro.core.mqtt.transport_runtime.random.uniform",
                return_value=0.0,
            ),
            patch(
                "custom_components.lipro.core.mqtt.transport_runtime.asyncio.sleep",
                side_effect=_sleep_and_stop,
            ) as sleep,
        ):
            await client._connection_loop()

        sleep.assert_called_once()
        assert client._connected is False

    @pytest.mark.asyncio
    async def test_connection_loop_handles_unexpected_exception(self):
        client = MqttTransport(
            access_key="access",
            secret_key="secret",
            biz_id="biz001",
            phone_id="550e8400-e29b-41d4-a716-446655440000",
        )
        client._running = True

        async def _sleep_and_stop(_: float) -> None:
            client._running = False

        with (
            patch.object(
                client,
                "_connect_and_listen",
                side_effect=RuntimeError("unexpected"),
            ),
            patch(
                "custom_components.lipro.core.mqtt.transport_runtime.random.uniform",
                return_value=0.0,
            ),
            patch(
                "custom_components.lipro.core.mqtt.transport_runtime.asyncio.sleep",
                side_effect=_sleep_and_stop,
            ) as sleep,
        ):
            await client._connection_loop()

        sleep.assert_called_once()
        assert client._connected is False

    @pytest.mark.asyncio
    async def test_finalize_connection_task_sets_last_error_and_calls_error_hook(self):
        """Background connection task failures should be observable."""
        on_error = MagicMock()
        client = MqttTransport(
            access_key="access",
            secret_key="secret",
            biz_id="biz001",
            phone_id="550e8400-e29b-41d4-a716-446655440000",
            on_error=on_error,
        )

        async def _boom() -> None:
            raise RuntimeError("loop boom")

        task = asyncio.create_task(_boom())
        await asyncio.gather(task, return_exceptions=True)
        client._task = cast(asyncio.Task[None] | None, task)

        client._async_finalize_connection_task(task)

        assert client._task is None
        assert isinstance(client.last_error, RuntimeError)
        on_error.assert_called_once()
