"""Unit tests for MqttRuntime component."""

from __future__ import annotations

import asyncio
from datetime import timedelta
from time import monotonic
from typing import cast
from unittest.mock import AsyncMock, Mock, patch

import pytest

from custom_components.lipro.core.coordinator.runtime.mqtt_runtime import MqttRuntime
from custom_components.lipro.core.device import LiproDevice
from custom_components.lipro.core.mqtt.mqtt_client import LiproMqttClient


@pytest.fixture
def mock_hass() -> Mock:
    """Create mock Home Assistant instance."""
    hass = Mock()
    hass.loop = Mock()
    hass.loop.is_running = Mock(return_value=True)
    return hass


@pytest.fixture
def mock_mqtt_client() -> Mock:
    """Create mock MQTT client."""
    client = Mock(spec=LiproMqttClient)
    client.start = AsyncMock()
    client.stop = AsyncMock()
    client.sync_subscriptions = AsyncMock()
    return client


@pytest.fixture
def mock_device() -> Mock:
    """Create mock device."""
    device = Mock(spec=LiproDevice)
    device.serial = "test_serial"
    device.name = "Test Device"
    device.is_group = False
    return device


@pytest.fixture
def mqtt_runtime(mock_hass: Mock, mock_mqtt_client: Mock) -> MqttRuntime:
    """Create MqttRuntime instance."""
    runtime = MqttRuntime(
        hass=mock_hass,
        mqtt_client=mock_mqtt_client,
        base_scan_interval=30,
        polling_multiplier=2,
        dedup_window=0.5,
        reconnect_base_delay=1.0,
        reconnect_max_delay=60.0,
    )

    device_resolver = Mock()
    device_resolver.get_device_by_id = Mock(return_value=None)

    listener_notifier = Mock()
    listener_notifier.schedule_listener_update = Mock()

    connect_state_tracker = Mock()
    connect_state_tracker.record_connect_state = Mock()

    group_reconciler = Mock()
    group_reconciler.schedule_group_reconciliation = Mock()

    runtime.set_device_resolver(device_resolver)
    runtime.set_property_applier(AsyncMock(return_value=True))
    runtime.set_listener_notifier(listener_notifier)
    runtime.set_connect_state_tracker(connect_state_tracker)
    runtime.set_group_reconciler(group_reconciler)

    return runtime


class TestMqttRuntimeInitialization:
    """Test MqttRuntime initialization."""

    def test_init_with_minimal_args(self, mock_hass: Mock) -> None:
        """Test initialization with minimal arguments."""
        runtime = MqttRuntime(
            hass=mock_hass,
            mqtt_client=None,
            base_scan_interval=30,
        )

        assert runtime._hass is mock_hass
        assert runtime._mqtt_client is None
        assert runtime._base_scan_interval == 30
        assert runtime._connection_manager is not None
        assert runtime._dedup_manager is not None
        assert runtime._reconnect_manager is not None

    def test_init_with_all_args(
        self, mock_hass: Mock, mock_mqtt_client: Mock
    ) -> None:
        """Test initialization with all arguments."""
        runtime = MqttRuntime(
            hass=mock_hass,
            mqtt_client=mock_mqtt_client,
            base_scan_interval=30,
            polling_multiplier=3,
            dedup_window=1.0,
            reconnect_base_delay=2.0,
            reconnect_max_delay=120.0,
        )

        assert runtime._mqtt_client is mock_mqtt_client
        assert runtime._base_scan_interval == 30


class TestMqttRuntimeConnection:
    """Test MQTT connection management."""

    async def test_connect_success(
        self, mqtt_runtime: MqttRuntime, mock_mqtt_client: Mock
    ) -> None:
        """Test successful MQTT connection."""
        device_ids = ["device1", "device2"]

        result = await mqtt_runtime.connect(device_ids=device_ids, biz_id="test_biz")

        assert result is True
        cast(AsyncMock, mock_mqtt_client.start).assert_awaited_once_with(device_ids)
        cast(AsyncMock, mock_mqtt_client.sync_subscriptions).assert_awaited_once_with(
            set(device_ids)
        )
        assert mqtt_runtime.is_connected is True

    async def test_connect_failure(
        self, mqtt_runtime: MqttRuntime, mock_mqtt_client: Mock
    ) -> None:
        """Test MQTT connection failure."""
        cast(AsyncMock, mock_mqtt_client.start).side_effect = Exception("Connection failed")

        result = await mqtt_runtime.connect(device_ids=["device1"], biz_id="test_biz")

        assert result is False
        assert mqtt_runtime.is_connected is False

    async def test_connect_without_client(self, mock_hass: Mock) -> None:
        """Test connection attempt without MQTT client."""
        runtime = MqttRuntime(
            hass=mock_hass,
            mqtt_client=None,
            base_scan_interval=30,
        )

        result = await runtime.connect(device_ids=["device1"], biz_id="test_biz")

        assert result is False

    async def test_connect_reraises_cancelled_error(
        self, mqtt_runtime: MqttRuntime, mock_mqtt_client: Mock
    ) -> None:
        """Cancelled connection attempts should bubble up."""
        cast(AsyncMock, mock_mqtt_client.start).side_effect = asyncio.CancelledError()

        with pytest.raises(asyncio.CancelledError):
            await mqtt_runtime.connect(device_ids=["device1"], biz_id="test_biz")

    async def test_disconnect(
        self, mqtt_runtime: MqttRuntime, mock_mqtt_client: Mock
    ) -> None:
        """Test MQTT disconnection."""
        await mqtt_runtime.connect(device_ids=["device1"], biz_id="test_biz")
        assert mqtt_runtime.is_connected is True

        await mqtt_runtime.disconnect()

        cast(AsyncMock, mock_mqtt_client.stop).assert_awaited_once()
        assert mqtt_runtime.is_connected is False

    async def test_disconnect_handles_exception(
        self, mqtt_runtime: MqttRuntime, mock_mqtt_client: Mock
    ) -> None:
        """Test disconnect handles exceptions gracefully."""
        cast(AsyncMock, mock_mqtt_client.stop).side_effect = Exception("Disconnect failed")

        await mqtt_runtime.disconnect()

        assert mqtt_runtime.is_connected is False

    async def test_disconnect_without_client(self, mock_hass: Mock) -> None:
        """Disconnect should no-op when MQTT client is absent."""
        runtime = MqttRuntime(
            hass=mock_hass,
            mqtt_client=None,
            base_scan_interval=30,
        )

        await runtime.disconnect()

    async def test_disconnect_reraises_cancelled_error(
        self, mqtt_runtime: MqttRuntime, mock_mqtt_client: Mock
    ) -> None:
        """Cancelled disconnects should not be swallowed."""
        cast(AsyncMock, mock_mqtt_client.stop).side_effect = asyncio.CancelledError()

        with pytest.raises(asyncio.CancelledError):
            await mqtt_runtime.disconnect()


class TestMqttRuntimeMessageHandling:
    """Test MQTT message handling."""

    async def test_handle_message_success(self, mqtt_runtime: MqttRuntime) -> None:
        """Test successful message handling."""
        device_id = "device1"
        properties = {"brightness": 100, "power": True}

        resolver = cast(Mock, mqtt_runtime._device_resolver)
        resolver.get_device_by_id.return_value = Mock(
            serial=device_id, name="Device 1", is_group=False
        )

        await mqtt_runtime.handle_message(device_id, properties)

        listener_notifier = cast(Mock, mqtt_runtime._listener_notifier)
        listener_notifier.schedule_listener_update.assert_called_once()

    async def test_handle_message_duplicate(self, mqtt_runtime: MqttRuntime) -> None:
        """Test duplicate message is ignored."""
        device_id = "device1"
        properties = {"brightness": 100}

        resolver = cast(Mock, mqtt_runtime._device_resolver)
        resolver.get_device_by_id.return_value = Mock(
            serial=device_id, name="Device 1", is_group=False
        )

        await mqtt_runtime.handle_message(device_id, properties)
        await mqtt_runtime.handle_message(device_id, properties)

        listener_notifier = cast(Mock, mqtt_runtime._listener_notifier)
        assert listener_notifier.schedule_listener_update.call_count == 1

    async def test_handle_message_device_not_found(self, mqtt_runtime: MqttRuntime) -> None:
        """Test message for unknown device is ignored."""
        resolver = cast(Mock, mqtt_runtime._device_resolver)
        resolver.get_device_by_id.return_value = None

        await mqtt_runtime.handle_message("unknown_device", {"test": "value"})

        property_applier = cast(AsyncMock, mqtt_runtime._property_applier)
        property_applier.assert_not_called()

    async def test_handle_message_with_connect_state(self, mqtt_runtime: MqttRuntime) -> None:
        """Test message with connectState triggers tracking."""
        device_id = "device1"
        properties = {"connectState": True}

        resolver = cast(Mock, mqtt_runtime._device_resolver)
        resolver.get_device_by_id.return_value = Mock(
            serial=device_id, name="Device 1", is_group=False
        )

        await mqtt_runtime.handle_message(device_id, properties)

        connect_state_tracker = cast(Mock, mqtt_runtime._connect_state_tracker)
        connect_state_tracker.record_connect_state.assert_called_once()

    async def test_handle_message_group_online(self, mqtt_runtime: MqttRuntime) -> None:
        """Test group device coming online triggers reconciliation."""
        device_id = "group1"
        properties = {"connectState": True}

        resolver = cast(Mock, mqtt_runtime._device_resolver)
        resolver.get_device_by_id.return_value = Mock(
            serial=device_id, name="Group 1", is_group=True
        )

        await mqtt_runtime.handle_message(device_id, properties)

        group_reconciler = cast(Mock, mqtt_runtime._group_reconciler)
        group_reconciler.schedule_group_reconciliation.assert_called_once()


class TestMqttRuntimeReconnection:
    """Test MQTT reconnection logic."""

    def test_should_attempt_reconnect_initially(self, mqtt_runtime: MqttRuntime) -> None:
        """Test reconnection should be attempted initially."""
        assert mqtt_runtime.should_attempt_reconnect() is True

    def test_should_attempt_reconnect_after_failure(
        self, mqtt_runtime: MqttRuntime, mock_mqtt_client: Mock
    ) -> None:
        """Test reconnection backoff after failure."""
        cast(AsyncMock, mock_mqtt_client.start).side_effect = Exception("Connection failed")

        assert mqtt_runtime.should_attempt_reconnect() is True

        asyncio.run(mqtt_runtime.connect(device_ids=["device1"], biz_id="test_biz"))

        assert mqtt_runtime._reconnect_manager._backoff._failure_count > 0


class TestMqttRuntimeDisconnectNotification:
    """Test disconnect notification logic."""

    @patch("custom_components.lipro.core.coordinator.runtime.mqtt_runtime.asyncio.create_task")
    def test_check_disconnect_notification_triggers(
        self, mock_create_task: Mock, mqtt_runtime: MqttRuntime
    ) -> None:
        """Test disconnect notification triggers after threshold."""

        def _close_coroutine(coro):
            coro.close()
            task = Mock()
            task.add_done_callback = Mock()
            task.cancelled = Mock(return_value=False)
            task.exception = Mock(return_value=None)
            return task

        mock_create_task.side_effect = _close_coroutine
        mqtt_runtime._connection_manager._connected = False
        mqtt_runtime._connection_manager._disconnect_time = monotonic() - 400

        mqtt_runtime.check_disconnect_notification()

        mock_create_task.assert_called_once()

    def test_check_disconnect_notification_not_triggered_when_connected(
        self, mqtt_runtime: MqttRuntime
    ) -> None:
        """Test notification not triggered when connected."""
        mqtt_runtime._connection_manager._connected = True

        with patch(
            "custom_components.lipro.core.coordinator.runtime.mqtt_runtime.asyncio.create_task"
        ) as mock_create_task:
            mqtt_runtime.check_disconnect_notification()
            mock_create_task.assert_not_called()

    def test_check_disconnect_notification_not_triggered_before_threshold(
        self, mqtt_runtime: MqttRuntime
    ) -> None:
        """Test notification not triggered before threshold."""
        mqtt_runtime._connection_manager._connected = False
        mqtt_runtime._connection_manager._disconnect_time = monotonic() - 60

        with patch(
            "custom_components.lipro.core.coordinator.runtime.mqtt_runtime.asyncio.create_task"
        ) as mock_create_task:
            mqtt_runtime.check_disconnect_notification()
            mock_create_task.assert_not_called()

    def test_check_disconnect_notification_returns_when_disconnect_time_missing(
        self, mqtt_runtime: MqttRuntime
    ) -> None:
        """Missing disconnect timestamps should short-circuit notifications."""
        mqtt_runtime._connection_manager._connected = False
        mqtt_runtime._connection_manager._disconnect_time = None

        with patch(
            "custom_components.lipro.core.coordinator.runtime.mqtt_runtime.asyncio.create_task"
        ) as mock_create_task:
            mqtt_runtime.check_disconnect_notification()
            mock_create_task.assert_not_called()

    def test_check_disconnect_notification_uses_background_task_manager(
        self, mock_hass: Mock, mock_mqtt_client: Mock
    ) -> None:
        """Background task manager should own disconnect notification tasks."""
        background_task_manager = Mock()

        def _consume(coro):
            coro.close()

        background_task_manager.create.side_effect = _consume
        runtime = MqttRuntime(
            hass=mock_hass,
            mqtt_client=mock_mqtt_client,
            base_scan_interval=30,
            background_task_manager=background_task_manager,
        )
        runtime._connection_manager._connected = False
        runtime._connection_manager._disconnect_time = monotonic() - 400

        runtime.check_disconnect_notification()

        background_task_manager.create.assert_called_once()


class TestMqttRuntimeReset:
    """Test runtime reset functionality."""

    async def test_reset_clears_all_state(
        self, mqtt_runtime: MqttRuntime, mock_mqtt_client: Mock
    ) -> None:
        """Test reset clears all runtime state."""
        await mqtt_runtime.connect(device_ids=["device1"], biz_id="test_biz")

        resolver = cast(Mock, mqtt_runtime._device_resolver)
        resolver.get_device_by_id.return_value = Mock(
            serial="device1", name="Device 1", is_group=False
        )
        await mqtt_runtime.handle_message("device1", {"test": "value"})

        mqtt_runtime.reset()

        assert mqtt_runtime.is_connected is False
        assert mqtt_runtime._connection_manager.disconnect_time is None
        assert len(mqtt_runtime._dedup_manager._message_cache) == 0


class TestMqttRuntimeDependencyInjection:
    """Test dependency injection."""

    def test_set_polling_updater(self, mqtt_runtime: MqttRuntime) -> None:
        """Test setting polling updater."""
        updater = Mock()
        mqtt_runtime.set_polling_updater(updater)
        assert mqtt_runtime._polling_updater is updater

    def test_update_polling_interval_sets_interval_on_injected_updater(
        self, mqtt_runtime: MqttRuntime
    ) -> None:
        """Polling updater should receive the new interval."""
        updater = Mock()
        mqtt_runtime.set_polling_updater(updater)

        mqtt_runtime.update_polling_interval(timedelta(seconds=45))

        assert updater.update_interval == timedelta(seconds=45)

    def test_update_polling_interval_is_noop_without_injected_updater(
        self, mock_hass: Mock, mock_mqtt_client: Mock
    ) -> None:
        """Missing updater should not raise."""
        runtime = MqttRuntime(
            hass=mock_hass,
            mqtt_client=mock_mqtt_client,
            base_scan_interval=30,
        )

        runtime.update_polling_interval(timedelta(seconds=15))

    def test_set_device_resolver(self, mqtt_runtime: MqttRuntime) -> None:
        """Test setting device resolver."""
        resolver = Mock()
        resolver.get_device_by_id = Mock(return_value=None)
        mqtt_runtime.set_device_resolver(resolver)
        assert mqtt_runtime._device_resolver is resolver

    async def test_message_handler_requires_dependencies(self, mock_hass: Mock) -> None:
        """Test message handler initialization requires all dependencies."""
        runtime = MqttRuntime(
            hass=mock_hass,
            mqtt_client=None,
            base_scan_interval=30,
        )

        with pytest.raises(RuntimeError, match="dependencies not fully injected"):
            await runtime.handle_message("device1", {"test": "value"})


@pytest.mark.asyncio
async def test_setup_reports_client_presence(mock_hass: Mock, mock_mqtt_client: Mock) -> (
    None
):
    runtime_without_client = MqttRuntime(
        hass=mock_hass,
        mqtt_client=None,
        base_scan_interval=30,
    )
    runtime_with_client = MqttRuntime(
        hass=mock_hass,
        mqtt_client=mock_mqtt_client,
        base_scan_interval=30,
    )

    assert await runtime_without_client.setup() is False
    assert await runtime_with_client.setup() is True


@pytest.mark.asyncio
async def test_disconnect_notification_helpers_call_issue_registry(
    mock_hass: Mock, mock_mqtt_client: Mock
) -> None:
    runtime = MqttRuntime(
        hass=mock_hass,
        mqtt_client=mock_mqtt_client,
        base_scan_interval=30,
    )

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


def test_reconnect_manager_tracks_backoff_gate_flag() -> None:
    from custom_components.lipro.core.coordinator.runtime.mqtt.reconnect import (
        MqttReconnectManager,
    )

    manager = MqttReconnectManager()

    flag = manager.backoff_gate_logged
    assert flag is False

    manager.mark_backoff_gate_logged()

    flag = manager.backoff_gate_logged
    assert flag is True

    manager.on_reconnect_success()

    flag = manager.backoff_gate_logged
    assert flag is False
