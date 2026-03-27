"""Topicized MqttRuntime notification and reset tests."""

from __future__ import annotations

from time import monotonic
from unittest.mock import Mock, patch

import pytest

from .test_mqtt_runtime_init import build_property_dict, create_mqtt_runtime

pytest_plugins = ("tests.core.coordinator.runtime.test_mqtt_runtime_init",)


class TestMqttRuntimeDisconnectNotification:
    @patch("custom_components.lipro.core.coordinator.runtime.mqtt_runtime.asyncio.create_task")
    def test_check_disconnect_notification_triggers(self, mock_create_task, mqtt_runtime):
        def close_coroutine(coro, **kwargs):
            coro.close()
            task = Mock()
            task.add_done_callback = Mock()
            task.cancelled = Mock(return_value=False)
            task.exception = Mock(return_value=None)
            return task

        mock_create_task.side_effect = close_coroutine
        mqtt_runtime._connection_manager._connected = False
        mqtt_runtime._connection_manager._disconnect_time = monotonic() - 400

        mqtt_runtime.check_disconnect_notification()

        mock_create_task.assert_called_once()

    def test_check_disconnect_notification_not_triggered_when_connected(self, mqtt_runtime):
        mqtt_runtime._connection_manager._connected = True

        with patch(
            "custom_components.lipro.core.coordinator.runtime.mqtt_runtime.asyncio.create_task"
        ) as mock_create_task:
            mqtt_runtime.check_disconnect_notification()
            mock_create_task.assert_not_called()

    def test_check_disconnect_notification_not_triggered_before_threshold(self, mqtt_runtime):
        mqtt_runtime._connection_manager._connected = False
        mqtt_runtime._connection_manager._disconnect_time = monotonic() - 60

        with patch(
            "custom_components.lipro.core.coordinator.runtime.mqtt_runtime.asyncio.create_task"
        ) as mock_create_task:
            mqtt_runtime.check_disconnect_notification()
            mock_create_task.assert_not_called()

    def test_check_disconnect_notification_returns_when_disconnect_time_missing(
        self, mqtt_runtime
    ):
        mqtt_runtime._connection_manager._connected = False
        mqtt_runtime._connection_manager._disconnect_time = None

        with patch(
            "custom_components.lipro.core.coordinator.runtime.mqtt_runtime.asyncio.create_task"
        ) as mock_create_task:
            mqtt_runtime.check_disconnect_notification()
            mock_create_task.assert_not_called()

    def test_check_disconnect_notification_uses_background_task_manager(
        self, mock_hass, mock_mqtt_transport
    ):
        background_task_manager = Mock()

        def consume(coro, **kwargs):
            coro.close()

        background_task_manager.create.side_effect = consume
        runtime = create_mqtt_runtime(
            mock_hass,
            mock_mqtt_transport,
            background_task_manager=background_task_manager,
        )
        runtime._connection_manager._connected = False
        runtime._connection_manager._disconnect_time = monotonic() - 400

        runtime.check_disconnect_notification()

        background_task_manager.create.assert_called_once()


class TestMqttRuntimeReset:
    @pytest.mark.asyncio
    async def test_reset_clears_all_state(self, mqtt_runtime):
        await mqtt_runtime.connect(device_ids=["device1"])

        mqtt_runtime._device_resolver.get_device_by_id.return_value = Mock(
            serial="device1", name="Device 1", is_group=False
        )
        await mqtt_runtime.handle_message("device1", build_property_dict(test="value"))

        mqtt_runtime.reset()

        assert mqtt_runtime.is_connected is False
        assert mqtt_runtime._connection_manager.disconnect_time is None
        assert len(mqtt_runtime._dedup_manager._message_cache) == 0


@pytest.mark.asyncio
async def test_disconnect_notification_helpers_call_issue_registry(
    mock_hass, mock_mqtt_transport
):
    runtime = create_mqtt_runtime(mock_hass, mock_mqtt_transport)

    with patch(
        "custom_components.lipro.core.coordinator.runtime.mqtt_runtime.async_create_issue"
    ) as create_issue, patch(
        "custom_components.lipro.core.coordinator.runtime.mqtt_runtime.async_delete_issue"
    ) as delete_issue:
        await runtime._async_show_mqtt_disconnect_notification(6)
        await runtime.clear_disconnect_notification()

    create_issue.assert_called_once()
    delete_issue.assert_called_once_with(
        mock_hass,
        domain="lipro",
        issue_id="mqtt_disconnected",
    )
