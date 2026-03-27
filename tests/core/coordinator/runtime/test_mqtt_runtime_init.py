"""Topicized MqttRuntime initialization and dependency-injection tests."""

from __future__ import annotations

from unittest.mock import Mock

import pytest

from .test_mqtt_runtime_support import create_mqtt_runtime

pytest_plugins = ("tests.core.coordinator.runtime.test_mqtt_runtime_support",)


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
