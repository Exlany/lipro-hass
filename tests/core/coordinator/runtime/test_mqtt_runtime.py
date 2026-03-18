"""Unit tests for MqttRuntime component."""

from __future__ import annotations

import asyncio
from datetime import timedelta
from time import monotonic
from typing import cast
from unittest.mock import AsyncMock, Mock, patch

import pytest

from custom_components.lipro.core.coordinator.runtime.mqtt_runtime import MqttRuntime
from custom_components.lipro.core.coordinator.types import PropertyDict
from custom_components.lipro.core.device import LiproDevice
from custom_components.lipro.core.protocol.contracts import MqttTransportFacade
from custom_components.lipro.core.telemetry.models import FailureSummary


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
    client = Mock(spec=MqttTransportFacade)
    client.start = AsyncMock()
    client.stop = AsyncMock()
    client.sync_subscriptions = AsyncMock()
    client.wait_until_connected = AsyncMock(return_value=True)
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
    """Create MqttRuntime instance with all required dependencies."""
    device_resolver = Mock()
    device_resolver.get_device_by_id = Mock(return_value=None)

    property_applier = AsyncMock(return_value=True)

    listener_notifier = Mock()
    listener_notifier.schedule_listener_update = Mock()

    connect_state_tracker = Mock()
    connect_state_tracker.record_connect_state = Mock()

    group_reconciler = Mock()
    group_reconciler.schedule_group_reconciliation = Mock()

    polling_updater = Mock()
    return MqttRuntime(
        hass=mock_hass,
        mqtt_client=mock_mqtt_client,
        base_scan_interval=30,
        polling_updater=polling_updater,
        device_resolver=device_resolver,
        property_applier=property_applier,
        listener_notifier=listener_notifier,
        connect_state_tracker=connect_state_tracker,
        group_reconciler=group_reconciler,
        polling_multiplier=2,
        dedup_window=0.5,
        reconnect_base_delay=1.0,
        reconnect_max_delay=60.0,
    )


def _get_polling_updater(runtime: MqttRuntime) -> Mock:
    """Return the injected polling updater mock."""
    return cast(Mock, runtime._connection_manager._polling_updater)


def _get_failure_summary(runtime: MqttRuntime) -> FailureSummary:
    """Return the typed failure-summary view from runtime metrics."""
    return cast(FailureSummary, runtime.get_runtime_metrics()["failure_summary"])


def _property_dict(**properties: object) -> PropertyDict:
    """Build one typed MQTT property payload for tests."""
    return cast(PropertyDict, properties)


class TestMqttRuntimeInitialization:
    """Test MqttRuntime initialization (constructor-based DI)."""

    def test_init_with_minimal_args(self, mock_hass: Mock) -> None:
        """Test initialization with minimal arguments."""
        runtime = _create_mqtt_runtime_with_deps(mock_hass, None)

        assert runtime._hass is mock_hass
        assert runtime._mqtt_client is None
        assert runtime._base_scan_interval == 30
        assert runtime._connection_manager is not None
        assert runtime._dedup_manager is not None
        assert runtime._reconnect_manager is not None
        assert runtime._message_handler is not None

    def test_init_with_all_args(
        self, mock_hass: Mock, mock_mqtt_client: Mock
    ) -> None:
        """Test initialization with all arguments."""
        device_resolver = Mock()
        device_resolver.get_device_by_id = Mock(return_value=None)
        property_applier = AsyncMock(return_value=True)
        listener_notifier = Mock()
        listener_notifier.schedule_listener_update = Mock()
        connect_state_tracker = Mock()
        connect_state_tracker.record_connect_state = Mock()
        group_reconciler = Mock()
        group_reconciler.schedule_group_reconciliation = Mock()

        polling_updater = Mock()
        runtime = MqttRuntime(
            hass=mock_hass,
            mqtt_client=mock_mqtt_client,
            base_scan_interval=30,
            polling_updater=polling_updater,
            device_resolver=device_resolver,
            property_applier=property_applier,
            listener_notifier=listener_notifier,
            connect_state_tracker=connect_state_tracker,
            group_reconciler=group_reconciler,
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
        """Test successful MQTT connection after real transport callback."""
        device_ids = ["device1", "device2"]

        async def _wait_until_connected() -> bool:
            mqtt_runtime.on_transport_connected()
            return True

        cast(AsyncMock, mock_mqtt_client.wait_until_connected).side_effect = (
            _wait_until_connected
        )

        result = await mqtt_runtime.connect(device_ids=device_ids)

        assert result is True
        cast(AsyncMock, mock_mqtt_client.start).assert_awaited_once_with(device_ids)
        cast(AsyncMock, mock_mqtt_client.sync_subscriptions).assert_awaited_once_with(
            set(device_ids)
        )
        cast(AsyncMock, mock_mqtt_client.wait_until_connected).assert_awaited_once_with()
        assert mqtt_runtime.is_connected is True

    async def test_connect_failure(
        self, mqtt_runtime: MqttRuntime, mock_mqtt_client: Mock
    ) -> None:
        """Test MQTT connection failure."""
        cast(AsyncMock, mock_mqtt_client.start).side_effect = RuntimeError("Connection failed")

        result = await mqtt_runtime.connect(device_ids=["device1"])

        assert result is False
        assert mqtt_runtime.is_connected is False
        assert mqtt_runtime.get_runtime_metrics()["last_transport_error_stage"] == "connect"
        assert _get_failure_summary(mqtt_runtime)["error_type"] == "RuntimeError"

    async def test_connect_without_client(self, mock_hass: Mock) -> None:
        """Test connection attempt without MQTT client."""
        runtime = _create_mqtt_runtime_with_deps(mock_hass, None)

        result = await runtime.connect(device_ids=["device1"])

        assert result is False

    async def test_connect_reraises_cancelled_error(
        self, mqtt_runtime: MqttRuntime, mock_mqtt_client: Mock
    ) -> None:
        """Cancelled connection attempts should bubble up."""
        cast(AsyncMock, mock_mqtt_client.start).side_effect = asyncio.CancelledError()

        with pytest.raises(asyncio.CancelledError):
            await mqtt_runtime.connect(device_ids=["device1"])

    async def test_disconnect(
        self, mqtt_runtime: MqttRuntime, mock_mqtt_client: Mock
    ) -> None:
        """Test MQTT disconnection."""

        async def _wait_until_connected() -> bool:
            mqtt_runtime.on_transport_connected()
            return True

        cast(AsyncMock, mock_mqtt_client.wait_until_connected).side_effect = (
            _wait_until_connected
        )

        await mqtt_runtime.connect(device_ids=["device1"])
        assert mqtt_runtime.is_connected is True

        await mqtt_runtime.disconnect()

        cast(AsyncMock, mock_mqtt_client.stop).assert_awaited_once()
        assert mqtt_runtime.is_connected is False

    async def test_disconnect_handles_exception(
        self, mqtt_runtime: MqttRuntime, mock_mqtt_client: Mock
    ) -> None:
        """Test disconnect handles exceptions gracefully."""
        mqtt_runtime.on_transport_connected()
        cast(AsyncMock, mock_mqtt_client.stop).side_effect = RuntimeError("Disconnect failed")

        await mqtt_runtime.disconnect()

        assert mqtt_runtime.is_connected is False
        assert mqtt_runtime._connection_manager.disconnect_time is not None
        assert mqtt_runtime.get_runtime_metrics()["last_transport_error_stage"] == "disconnect"
        assert _get_failure_summary(mqtt_runtime)["error_type"] == "RuntimeError"

    async def test_disconnect_without_client(self, mock_hass: Mock) -> None:
        """Disconnect should no-op when MQTT client is absent."""
        runtime = _create_mqtt_runtime_with_deps(mock_hass, None)

        await runtime.disconnect()

    async def test_disconnect_reraises_cancelled_error(
        self, mqtt_runtime: MqttRuntime, mock_mqtt_client: Mock
    ) -> None:
        """Cancelled disconnects should not be swallowed."""
        cast(AsyncMock, mock_mqtt_client.stop).side_effect = asyncio.CancelledError()

        with pytest.raises(asyncio.CancelledError):
            await mqtt_runtime.disconnect()

    async def test_sync_subscriptions_failure_returns_false(
        self, mqtt_runtime: MqttRuntime, mock_mqtt_client: Mock
    ) -> None:
        """Subscription sync failures should not fake a successful connection."""
        cast(AsyncMock, mock_mqtt_client.sync_subscriptions).side_effect = RuntimeError(
            "boom"
        )

        result = await mqtt_runtime.connect(device_ids=["device1"])

        assert result is False
        assert mqtt_runtime.is_connected is False
        assert mqtt_runtime._reconnect_manager._backoff._failure_count > 0
        assert mqtt_runtime.get_runtime_metrics()["last_transport_error_stage"] == "connect"
        assert _get_failure_summary(mqtt_runtime)["error_type"] == "RuntimeError"

    async def test_transport_error_does_not_mark_runtime_disconnected(
        self, mqtt_runtime: MqttRuntime
    ) -> None:
        """Transport errors alone should not mutate connection state."""
        mqtt_runtime.on_transport_connected()

        mqtt_runtime.handle_transport_error(RuntimeError("decode failed"))

        assert mqtt_runtime.is_connected is True
        assert isinstance(mqtt_runtime._last_transport_error, RuntimeError)

    def test_transport_callbacks_update_polling_interval(
        self, mqtt_runtime: MqttRuntime
    ) -> None:
        """Real transport callbacks should drive coordinator polling interval."""
        polling_updater = _get_polling_updater(mqtt_runtime)

        mqtt_runtime.on_transport_connected()
        polling_updater.update_polling_interval.assert_called_with(timedelta(seconds=60))

        mqtt_runtime.on_transport_disconnected()
        polling_updater.update_polling_interval.assert_called_with(timedelta(seconds=30))


class TestMqttRuntimeMessageHandling:
    """Test MQTT message handling."""

    async def test_handle_message_success(self, mqtt_runtime: MqttRuntime) -> None:
        """Test successful message handling."""
        device_id = "device1"
        properties = _property_dict(brightness=100, power=True)

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
        properties = _property_dict(brightness=100)

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

        await mqtt_runtime.handle_message("unknown_device", _property_dict(test="value"))

        property_applier = cast(AsyncMock, mqtt_runtime._property_applier)
        property_applier.assert_not_called()

    async def test_handle_message_with_connect_state(self, mqtt_runtime: MqttRuntime) -> None:
        """Test message with connectState triggers tracking."""
        device_id = "device1"
        properties = _property_dict(connectState=True)

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
        properties = _property_dict(connectState=True)

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
        cast(AsyncMock, mock_mqtt_client.start).side_effect = RuntimeError("Connection failed")

        assert mqtt_runtime.should_attempt_reconnect() is True

        asyncio.run(mqtt_runtime.connect(device_ids=["device1"]))

        assert mqtt_runtime._reconnect_manager._backoff._failure_count > 0


class TestMqttRuntimeDisconnectNotification:
    """Test disconnect notification logic."""

    @patch("custom_components.lipro.core.coordinator.runtime.mqtt_runtime.asyncio.create_task")
    def test_check_disconnect_notification_triggers(
        self, mock_create_task: Mock, mqtt_runtime: MqttRuntime
    ) -> None:
        """Test disconnect notification triggers after threshold."""

        def _close_coroutine(coro, **kwargs):
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

        def _consume(coro, **kwargs):
            coro.close()

        background_task_manager.create.side_effect = _consume

        device_resolver = Mock()
        device_resolver.get_device_by_id = Mock(return_value=None)
        property_applier = AsyncMock(return_value=True)
        listener_notifier = Mock()
        listener_notifier.schedule_listener_update = Mock()
        connect_state_tracker = Mock()
        connect_state_tracker.record_connect_state = Mock()
        group_reconciler = Mock()
        group_reconciler.schedule_group_reconciliation = Mock()

        polling_updater = Mock()
        runtime = MqttRuntime(
            hass=mock_hass,
            mqtt_client=mock_mqtt_client,
            base_scan_interval=30,
            polling_updater=polling_updater,
            device_resolver=device_resolver,
            property_applier=property_applier,
            listener_notifier=listener_notifier,
            connect_state_tracker=connect_state_tracker,
            group_reconciler=group_reconciler,
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
        await mqtt_runtime.connect(device_ids=["device1"])

        resolver = cast(Mock, mqtt_runtime._device_resolver)
        resolver.get_device_by_id.return_value = Mock(
            serial="device1", name="Device 1", is_group=False
        )
        await mqtt_runtime.handle_message("device1", _property_dict(test="value"))

        mqtt_runtime.reset()

        assert mqtt_runtime.is_connected is False
        assert mqtt_runtime._connection_manager.disconnect_time is None
        assert len(mqtt_runtime._dedup_manager._message_cache) == 0


class TestMqttRuntimeDependencyInjection:
    """Test dependency injection (constructor-based)."""

    def test_bind_and_detach_transport_track_runtime_presence(
        self, mqtt_runtime: MqttRuntime
    ) -> None:
        """Transport binding should be explicit and observable."""
        transport = Mock()

        mqtt_runtime.bind_transport(transport)
        assert mqtt_runtime.has_transport is True

        mqtt_runtime.detach_transport()
        assert mqtt_runtime.has_transport is False


def _create_mqtt_runtime_with_deps(
    mock_hass: Mock, mock_mqtt_client: Mock | None
) -> MqttRuntime:
    """Helper to create MqttRuntime with all required dependencies."""
    device_resolver = Mock()
    device_resolver.get_device_by_id = Mock(return_value=None)
    property_applier = AsyncMock(return_value=True)
    listener_notifier = Mock()
    listener_notifier.schedule_listener_update = Mock()
    connect_state_tracker = Mock()
    connect_state_tracker.record_connect_state = Mock()
    group_reconciler = Mock()
    group_reconciler.schedule_group_reconciliation = Mock()

    polling_updater = Mock()
    return MqttRuntime(
        hass=mock_hass,
        mqtt_client=mock_mqtt_client,
        base_scan_interval=30,
        polling_updater=polling_updater,
        device_resolver=device_resolver,
        property_applier=property_applier,
        listener_notifier=listener_notifier,
        connect_state_tracker=connect_state_tracker,
        group_reconciler=group_reconciler,
    )


@pytest.mark.asyncio
async def test_setup_reports_client_presence(mock_hass: Mock, mock_mqtt_client: Mock) -> (
    None
):
    runtime_without_client = _create_mqtt_runtime_with_deps(mock_hass, None)
    runtime_with_client = _create_mqtt_runtime_with_deps(mock_hass, mock_mqtt_client)

    assert runtime_without_client.has_transport is False
    assert runtime_with_client.has_transport is True


@pytest.mark.asyncio
async def test_disconnect_notification_helpers_call_issue_registry(
    mock_hass: Mock, mock_mqtt_client: Mock
) -> None:
    runtime = _create_mqtt_runtime_with_deps(mock_hass, mock_mqtt_client)

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
