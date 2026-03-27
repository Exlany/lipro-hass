"""Topicized MqttRuntime initialization and dependency-injection tests."""

from __future__ import annotations

from unittest.mock import AsyncMock, Mock

import pytest

from custom_components.lipro.core.coordinator.runtime.mqtt_runtime import MqttRuntime
from custom_components.lipro.core.protocol.contracts import MqttTransportFacade


@pytest.fixture
def mock_hass():
    hass = Mock()
    hass.loop = Mock()
    hass.loop.is_running = Mock(return_value=True)
    return hass


@pytest.fixture
def mock_mqtt_transport():
    transport = Mock(spec=MqttTransportFacade)
    transport.start = AsyncMock()
    transport.stop = AsyncMock()
    transport.sync_subscriptions = AsyncMock()
    transport.wait_until_connected = AsyncMock(return_value=True)
    return transport


def create_mqtt_runtime(
    mock_hass,
    mock_mqtt_transport,
    *,
    background_task_manager=None,
    polling_multiplier=2,
    dedup_window=0.5,
    reconnect_base_delay=1.0,
    reconnect_max_delay=60.0,
):
    device_resolver = Mock()
    device_resolver.get_device_by_id = Mock(return_value=None)

    property_applier = AsyncMock(return_value=True)

    listener_notifier = Mock()
    listener_notifier.schedule_listener_update = Mock()

    connect_state_tracker = Mock()
    connect_state_tracker.record_connect_state = Mock()

    group_reconciler = Mock()
    group_reconciler.schedule_group_reconciliation = Mock()

    runtime_kwargs = {}
    if background_task_manager is not None:
        runtime_kwargs["background_task_manager"] = background_task_manager

    polling_updater = Mock()
    return MqttRuntime(
        hass=mock_hass,
        mqtt_transport=mock_mqtt_transport,
        base_scan_interval=30,
        polling_updater=polling_updater,
        device_resolver=device_resolver,
        property_applier=property_applier,
        listener_notifier=listener_notifier,
        connect_state_tracker=connect_state_tracker,
        group_reconciler=group_reconciler,
        polling_multiplier=polling_multiplier,
        dedup_window=dedup_window,
        reconnect_base_delay=reconnect_base_delay,
        reconnect_max_delay=reconnect_max_delay,
        **runtime_kwargs,
    )


@pytest.fixture
def mqtt_runtime(mock_hass, mock_mqtt_transport):
    return create_mqtt_runtime(mock_hass, mock_mqtt_transport)


def get_polling_updater(runtime):
    return runtime._connection_manager._polling_updater


def get_failure_summary(runtime):
    return runtime.get_runtime_metrics()["failure_summary"]


def build_property_dict(**properties):
    return properties


class TestMqttRuntimeInitialization:
    def test_init_with_minimal_args(self, mock_hass):
        runtime = create_mqtt_runtime(mock_hass, None)

        assert runtime._hass is mock_hass
        assert runtime._mqtt_transport is None
        assert runtime._base_scan_interval == 30
        assert runtime._connection_manager is not None
        assert runtime._dedup_manager is not None
        assert runtime._reconnect_manager is not None
        assert runtime._message_handler is not None

    def test_init_with_all_args(self, mock_hass, mock_mqtt_transport):
        runtime = create_mqtt_runtime(
            mock_hass,
            mock_mqtt_transport,
            polling_multiplier=3,
            dedup_window=1.0,
            reconnect_base_delay=2.0,
            reconnect_max_delay=120.0,
        )

        assert runtime._mqtt_transport is mock_mqtt_transport
        assert runtime._base_scan_interval == 30


class TestMqttRuntimeDependencyInjection:
    def test_bind_and_detach_transport_track_runtime_presence(self, mqtt_runtime):
        transport = Mock()

        mqtt_runtime.bind_transport(transport)
        assert mqtt_runtime.has_transport is True

        mqtt_runtime.detach_transport()
        assert mqtt_runtime.has_transport is False


@pytest.mark.asyncio
async def test_setup_reports_transport_presence(mock_hass, mock_mqtt_transport):
    runtime_without_transport = create_mqtt_runtime(mock_hass, None)
    runtime_with_transport = create_mqtt_runtime(mock_hass, mock_mqtt_transport)

    assert runtime_without_transport.has_transport is False
    assert runtime_with_transport.has_transport is True
