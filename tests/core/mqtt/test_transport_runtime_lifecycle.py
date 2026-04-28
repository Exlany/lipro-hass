"""Tests for Lipro MQTT transport."""

from __future__ import annotations

import asyncio
import logging
from typing import cast
from unittest.mock import AsyncMock, MagicMock, patch

import aiomqtt
import pytest

from custom_components.lipro.core.mqtt.transport import MqttTransport


class TestMqttTransport:
    """Tests for MqttTransport class."""

    def test_init(self):
        """Test client initialization."""
        client = MqttTransport(
            access_key="access",
            secret_key="secret",
            biz_id="biz001",
            phone_id="550e8400-e29b-41d4-a716-446655440000",
        )

        assert client.is_connected is False
        assert client.subscribed_count == 0

    def test_init_with_callbacks(self):
        """Test client initialization with callbacks."""
        on_message = MagicMock()
        on_connect = MagicMock()
        on_disconnect = MagicMock()

        client = MqttTransport(
            access_key="access",
            secret_key="secret",
            biz_id="biz001",
            phone_id="550e8400-e29b-41d4-a716-446655440000",
            on_message=on_message,
            on_connect=on_connect,
            on_disconnect=on_disconnect,
        )

        assert client._on_message is on_message
        assert client._on_connect is on_connect
        assert client._on_disconnect is on_disconnect

    @pytest.mark.asyncio
    async def test_start(self):
        """Test starting MQTT transport."""
        client = MqttTransport(
            access_key="access",
            secret_key="secret",
            biz_id="biz001",
            phone_id="550e8400-e29b-41d4-a716-446655440000",
        )

        device_ids = ["03ab5ccd7cxxxxxx", "03ab5ccd7cyyyyyy"]

        with patch.object(client, "_connection_loop", new_callable=AsyncMock):
            await client.start(device_ids)

            assert client._running is True
            assert client._subscribed_devices == set(device_ids)
            assert client.subscribed_count == 2

    @pytest.mark.asyncio
    async def test_start_already_running(self):
        """Test starting already running client."""
        client = MqttTransport(
            access_key="access",
            secret_key="secret",
            biz_id="biz001",
            phone_id="550e8400-e29b-41d4-a716-446655440000",
        )
        client._running = True

        with patch.object(
            client, "_connection_loop", new_callable=AsyncMock
        ) as mock_loop:
            await client.start(["device1"])

            # Should not start again
            mock_loop.assert_not_called()

    @pytest.mark.asyncio
    async def test_stop(self):
        """Test stopping MQTT transport."""
        client = MqttTransport(
            access_key="access",
            secret_key="secret",
            biz_id="biz001",
            phone_id="550e8400-e29b-41d4-a716-446655440000",
        )
        client._running = True
        client._connected = True

        # Create a proper async task mock
        async def dummy_task():
            pass

        import asyncio

        client._task = asyncio.create_task(dummy_task())
        # Wait for dummy task to complete
        await asyncio.sleep(0)

        await client.stop()

        assert client._running is False
        assert client._connected is False
        assert client._task is None

    def test_handle_disconnect(self):
        """Test disconnect handling."""
        on_disconnect = MagicMock()
        client = MqttTransport(
            access_key="access",
            secret_key="secret",
            biz_id="biz001",
            phone_id="550e8400-e29b-41d4-a716-446655440000",
            on_disconnect=on_disconnect,
        )
        client._connected = True
        client._broker_client = cast(aiomqtt.Client | None, MagicMock())

        client._handle_disconnect("Test reason")

        assert client._connected is False
        assert client._broker_client is None
        on_disconnect.assert_called_once()

    def test_handle_disconnect_callback_failure_sets_last_error(self, caplog):
        """Disconnect callback exceptions should be captured as last_error."""
        on_disconnect = MagicMock(side_effect=RuntimeError("boom"))
        client = MqttTransport(
            access_key="access",
            secret_key="secret",
            biz_id="biz001",
            phone_id="550e8400-e29b-41d4-a716-446655440000",
            on_disconnect=on_disconnect,
        )
        client._connected = True
        client._broker_client = MagicMock()

        with caplog.at_level(logging.ERROR):
            client._handle_disconnect("Test reason")

        assert isinstance(client.last_error, RuntimeError)
        assert str(client.last_error) == "boom"

    @pytest.mark.asyncio
    async def test_consume_task_exception_cancelled_returns_none(self):
        """Cancelled background tasks should not be treated as errors."""

        async def _long_task() -> None:
            await asyncio.sleep(10)

        task = asyncio.create_task(_long_task())
        await asyncio.sleep(0)
        task.cancel()
        with pytest.raises(asyncio.CancelledError):
            await task

        assert MqttTransport._consume_task_exception(task) is None


class TestMqttTransportProperties:
    """Tests for MQTT transport properties."""

    def test_is_connected(self):
        """Test is_connected property."""
        client = MqttTransport(
            access_key="access",
            secret_key="secret",
            biz_id="biz001",
            phone_id="550e8400-e29b-41d4-a716-446655440000",
        )

        assert client.is_connected is False

        client._connected = True
        assert client.is_connected is True

    def test_subscribed_count(self):
        """Test subscribed_count property."""
        client = MqttTransport(
            access_key="access",
            secret_key="secret",
            biz_id="biz001",
            phone_id="550e8400-e29b-41d4-a716-446655440000",
        )

        assert client.subscribed_count == 0

        client._subscribed_devices = {"device1", "device2", "device3"}
        assert client.subscribed_count == 3

    def test_subscribed_devices_returns_copy(self):
        """Test subscribed_devices returns a copy, not the internal set."""
        client = MqttTransport(
            access_key="access",
            secret_key="secret",
            biz_id="biz001",
            phone_id="550e8400-e29b-41d4-a716-446655440000",
        )
        client._subscribed_devices = {"device1", "device2"}

        snapshot = client.subscribed_devices
        snapshot.add("injected")

        # Internal set must not be affected
        assert "injected" not in client._subscribed_devices
        assert len(client._subscribed_devices) == 2
