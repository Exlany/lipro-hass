"""Topicized MqttRuntime connection and reconnection tests."""

from __future__ import annotations

import asyncio
from datetime import timedelta

import pytest

from .test_mqtt_runtime_support import (
    create_mqtt_runtime,
    get_failure_summary,
    get_polling_updater,
)

pytest_plugins = ("tests.core.coordinator.runtime.test_mqtt_runtime_support",)


class TestMqttRuntimeConnection:
    @pytest.mark.asyncio
    async def test_connect_success(self, mqtt_runtime, mock_mqtt_transport):
        device_ids = ["device1", "device2"]

        async def wait_until_connected():
            mqtt_runtime.on_transport_connected()
            return True

        mock_mqtt_transport.wait_until_connected.side_effect = wait_until_connected

        result = await mqtt_runtime.connect(device_ids=device_ids)

        assert result is True
        mock_mqtt_transport.start.assert_awaited_once_with(device_ids)
        mock_mqtt_transport.sync_subscriptions.assert_awaited_once_with(set(device_ids))
        mock_mqtt_transport.wait_until_connected.assert_awaited_once_with()
        assert mqtt_runtime.is_connected is True

    @pytest.mark.asyncio
    async def test_connect_failure(self, mqtt_runtime, mock_mqtt_transport):
        mock_mqtt_transport.start.side_effect = RuntimeError("Connection failed")

        result = await mqtt_runtime.connect(device_ids=["device1"])

        assert result is False
        assert mqtt_runtime.is_connected is False
        assert mqtt_runtime.get_runtime_metrics()["last_transport_error_stage"] == "connect"
        assert get_failure_summary(mqtt_runtime)["error_type"] == "RuntimeError"

    @pytest.mark.asyncio
    async def test_connect_without_client(self, mock_hass):
        runtime = create_mqtt_runtime(mock_hass, None)

        result = await runtime.connect(device_ids=["device1"])

        assert result is False

    @pytest.mark.asyncio
    async def test_connect_reraises_cancelled_error(self, mqtt_runtime, mock_mqtt_transport):
        mock_mqtt_transport.start.side_effect = asyncio.CancelledError()

        with pytest.raises(asyncio.CancelledError):
            await mqtt_runtime.connect(device_ids=["device1"])

    @pytest.mark.asyncio
    async def test_disconnect(self, mqtt_runtime, mock_mqtt_transport):
        async def wait_until_connected():
            mqtt_runtime.on_transport_connected()
            return True

        mock_mqtt_transport.wait_until_connected.side_effect = wait_until_connected

        await mqtt_runtime.connect(device_ids=["device1"])
        assert mqtt_runtime.is_connected is True

        await mqtt_runtime.disconnect()

        mock_mqtt_transport.stop.assert_awaited_once()
        assert mqtt_runtime.is_connected is False

    @pytest.mark.asyncio
    async def test_disconnect_handles_exception(self, mqtt_runtime, mock_mqtt_transport):
        mqtt_runtime.on_transport_connected()
        mock_mqtt_transport.stop.side_effect = RuntimeError("Disconnect failed")

        await mqtt_runtime.disconnect()

        assert mqtt_runtime.is_connected is False
        assert mqtt_runtime._connection_manager.disconnect_time is not None
        assert mqtt_runtime.get_runtime_metrics()["last_transport_error_stage"] == "disconnect"
        assert get_failure_summary(mqtt_runtime)["error_type"] == "RuntimeError"

    @pytest.mark.asyncio
    async def test_disconnect_without_client(self, mock_hass):
        runtime = create_mqtt_runtime(mock_hass, None)

        await runtime.disconnect()

    @pytest.mark.asyncio
    async def test_disconnect_reraises_cancelled_error(self, mqtt_runtime, mock_mqtt_transport):
        mock_mqtt_transport.stop.side_effect = asyncio.CancelledError()

        with pytest.raises(asyncio.CancelledError):
            await mqtt_runtime.disconnect()

    @pytest.mark.asyncio
    async def test_sync_subscriptions_failure_returns_false(
        self, mqtt_runtime, mock_mqtt_transport
    ):
        mock_mqtt_transport.sync_subscriptions.side_effect = RuntimeError("boom")

        result = await mqtt_runtime.connect(device_ids=["device1"])

        assert result is False
        assert mqtt_runtime.is_connected is False
        assert mqtt_runtime._reconnect_manager._backoff._failure_count > 0
        assert mqtt_runtime.get_runtime_metrics()["last_transport_error_stage"] == "connect"
        assert get_failure_summary(mqtt_runtime)["error_type"] == "RuntimeError"

    def test_transport_error_does_not_mark_runtime_disconnected(self, mqtt_runtime):
        mqtt_runtime.on_transport_connected()

        mqtt_runtime.handle_transport_error(RuntimeError("decode failed"))

        assert mqtt_runtime.is_connected is True
        assert isinstance(mqtt_runtime._last_transport_error, RuntimeError)

    def test_transport_callbacks_update_polling_interval(self, mqtt_runtime):
        polling_updater = get_polling_updater(mqtt_runtime)

        mqtt_runtime.on_transport_connected()
        polling_updater.update_polling_interval.assert_called_with(timedelta(seconds=60))

        mqtt_runtime.on_transport_disconnected()
        polling_updater.update_polling_interval.assert_called_with(timedelta(seconds=30))


class TestMqttRuntimeReconnection:
    def test_should_attempt_reconnect_initially(self, mqtt_runtime):
        assert mqtt_runtime.should_attempt_reconnect() is True

    def test_should_attempt_reconnect_after_failure(self, mqtt_runtime, mock_mqtt_transport):
        mock_mqtt_transport.start.side_effect = RuntimeError("Connection failed")

        assert mqtt_runtime.should_attempt_reconnect() is True

        asyncio.run(mqtt_runtime.connect(device_ids=["device1"]))

        assert mqtt_runtime._reconnect_manager._backoff._failure_count > 0


def test_reconnect_manager_tracks_backoff_gate_flag():
    from custom_components.lipro.core.coordinator.runtime.mqtt.reconnect import (
        MqttReconnectManager,
    )

    manager = MqttReconnectManager()

    assert not manager.backoff_gate_logged

    manager.mark_backoff_gate_logged()
    assert bool(manager.backoff_gate_logged)

    manager.on_reconnect_success()
    assert not manager.backoff_gate_logged
