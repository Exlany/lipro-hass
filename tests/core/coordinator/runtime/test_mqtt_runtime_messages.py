"""Topicized MqttRuntime message-handling tests."""

from __future__ import annotations

from unittest.mock import Mock

import pytest

from .test_mqtt_runtime_support import build_property_dict

pytest_plugins = ("tests.core.coordinator.runtime.test_mqtt_runtime_support",)


class TestMqttRuntimeMessageHandling:
    @pytest.mark.asyncio
    async def test_handle_message_success(self, mqtt_runtime):
        device_id = "device1"
        properties = build_property_dict(brightness=100, power=True)

        mqtt_runtime._device_resolver.get_device_by_id.return_value = Mock(
            serial=device_id, name="Device 1", is_group=False
        )

        outcome = await mqtt_runtime.handle_message(device_id, properties)

        mqtt_runtime._listener_notifier.schedule_listener_update.assert_called_once()
        assert outcome.kind == "success"
        assert outcome.reason_code == "applied"

    @pytest.mark.asyncio
    async def test_handle_message_duplicate(self, mqtt_runtime):
        device_id = "device1"
        properties = build_property_dict(brightness=100)

        mqtt_runtime._device_resolver.get_device_by_id.return_value = Mock(
            serial=device_id, name="Device 1", is_group=False
        )

        first = await mqtt_runtime.handle_message(device_id, properties)
        second = await mqtt_runtime.handle_message(device_id, properties)

        assert mqtt_runtime._listener_notifier.schedule_listener_update.call_count == 1
        assert first.kind == "success"
        assert first.reason_code == "applied"
        assert second.kind == "skipped"
        assert second.reason_code == "duplicate_message"

    @pytest.mark.asyncio
    async def test_handle_message_device_not_found(self, mqtt_runtime):
        mqtt_runtime._device_resolver.get_device_by_id.return_value = None

        outcome = await mqtt_runtime.handle_message(
            "unknown_device", build_property_dict(test="value")
        )

        mqtt_runtime._property_applier.assert_not_called()
        assert outcome.kind == "skipped"
        assert outcome.reason_code == "unknown_device"

    @pytest.mark.asyncio
    async def test_handle_message_with_connect_state(self, mqtt_runtime):
        device_id = "device1"
        properties = build_property_dict(connectState=True)

        mqtt_runtime._device_resolver.get_device_by_id.return_value = Mock(
            serial=device_id, name="Device 1", is_group=False
        )

        outcome = await mqtt_runtime.handle_message(device_id, properties)

        mqtt_runtime._connect_state_tracker.record_connect_state.assert_called_once()
        assert outcome.kind == "success"
        assert outcome.reason_code == "applied"

    @pytest.mark.asyncio
    async def test_handle_message_group_online(self, mqtt_runtime):
        device_id = "group1"
        properties = build_property_dict(connectState=True)

        mqtt_runtime._device_resolver.get_device_by_id.return_value = Mock(
            serial=device_id, name="Group 1", is_group=True
        )

        outcome = await mqtt_runtime.handle_message(device_id, properties)

        mqtt_runtime._group_reconciler.schedule_group_reconciliation.assert_called_once()
        assert outcome.kind == "success"
        assert outcome.reason_code == "applied"

    @pytest.mark.asyncio
    async def test_handle_message_without_applied_properties_returns_typed_skip(
        self, mqtt_runtime
    ):
        device_id = "device1"
        mqtt_runtime._device_resolver.get_device_by_id.return_value = Mock(
            serial=device_id, name="Device 1", is_group=False
        )
        mqtt_runtime._property_applier.return_value = False

        outcome = await mqtt_runtime.handle_message(
            device_id, build_property_dict(power=True)
        )

        assert outcome.kind == "skipped"
        assert outcome.reason_code == "no_applied_properties"
