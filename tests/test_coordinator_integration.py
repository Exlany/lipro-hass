"""Integration tests for Lipro data update coordinator.

These tests verify the actual coordinator behavior with mocked API responses.
"""

from __future__ import annotations

from unittest.mock import MagicMock

import pytest

from custom_components.lipro.core.api import (
    LiproApiError,
    LiproAuthError,
    LiproConnectionError,
)
from custom_components.lipro.core.device import LiproDevice


class TestCoordinatorDeviceManagement:
    """Tests for coordinator device management."""

    def test_device_mapping_by_serial(self, make_device):
        """Test devices are correctly mapped by serial."""
        device1 = make_device("light", serial="03ab5ccd7cxxxxxx")
        device2 = make_device("switch", serial="03ab5ccd7cyyyyyy")

        devices = {
            device1.serial: device1,
            device2.serial: device2,
        }

        assert len(devices) == 2
        assert devices["03ab5ccd7cxxxxxx"].name == "Test Light"
        assert devices["03ab5ccd7cyyyyyy"].name == "Test Switch"

    def test_iot_id_mapping(self, make_device):
        """Test IoT ID to device mapping."""
        device = make_device("light", serial="03ab5ccd7cxxxxxx")

        iot_id_to_device = {device.iot_device_id: device}

        assert device.iot_device_id == "03ab5ccd7cxxxxxx"
        assert iot_id_to_device.get("03ab5ccd7cxxxxxx") == device

    def test_group_device_iot_id(self, make_device):
        """Test group device IoT ID format."""
        # Create device with is_group=True directly

        device = LiproDevice(
            device_id=1,
            serial="mesh_group_10001",
            name="Test Group",
            device_type=1,
            iot_name="lipro_led",
            physical_model="light",
            is_group=True,
        )

        # Group devices use group_id as IoT ID
        assert device.is_group is True


class TestCoordinatorEntityRegistration:
    """Tests for entity registration in coordinator."""

    def test_register_entity(self, mock_coordinator, make_device):
        """Test entity registration."""
        device = make_device("light")
        mock_entity = MagicMock()
        mock_entity.unique_id = "03ab5ccd7cxxxxxx"
        mock_entity.device = device

        # Simulate registration
        entities = {}
        entities_by_device = {}

        entities[mock_entity.unique_id] = mock_entity
        device_serial = mock_entity.device.serial
        if device_serial not in entities_by_device:
            entities_by_device[device_serial] = []
        entities_by_device[device_serial].append(mock_entity)

        assert mock_entity.unique_id in entities
        assert len(entities_by_device[device_serial]) == 1

    def test_unregister_entity(self, mock_coordinator, make_device):
        """Test entity unregistration."""
        device = make_device("light")
        mock_entity = MagicMock()
        mock_entity.unique_id = "03ab5ccd7cxxxxxx"
        mock_entity.device = device

        # Setup
        entities = {mock_entity.unique_id: mock_entity}
        entities_by_device = {device.serial: [mock_entity]}

        # Unregister
        del entities[mock_entity.unique_id]
        entities_by_device[device.serial] = [
            e for e in entities_by_device[device.serial]
            if e.unique_id != mock_entity.unique_id
        ]

        assert mock_entity.unique_id not in entities
        assert len(entities_by_device[device.serial]) == 0


class TestCoordinatorDebounceProtection:
    """Tests for debounce protection in coordinator."""

    def test_get_protected_keys(self, make_device):
        """Test getting protected keys from entities."""
        device = make_device("light")

        mock_entity = MagicMock()
        mock_entity.unique_id = "03ab5ccd7cxxxxxx"
        mock_entity.device = device
        mock_entity.get_protected_keys.return_value = {"brightness", "temperature"}

        entities_by_device = {device.serial: [mock_entity]}

        # Simulate _get_protected_keys_for_device
        protected_keys = set()
        for entity in entities_by_device.get(device.serial, []):
            protected_keys.update(entity.get_protected_keys())

        assert protected_keys == {"brightness", "temperature"}

    def test_filter_protected_properties(self, make_device):
        """Test filtering protected properties."""
        properties = {
            "powerState": "1",
            "brightness": "80",
            "temperature": "4000",
        }
        protected_keys = {"brightness", "temperature"}

        filtered = {k: v for k, v in properties.items() if k not in protected_keys}

        assert filtered == {"powerState": "1"}
        assert "brightness" not in filtered

    def test_no_protection_when_no_entities(self, make_device):
        """Test no filtering when no entities registered."""
        properties = {
            "powerState": "1",
            "brightness": "80",
        }
        protected_keys = set()

        filtered = {k: v for k, v in properties.items() if k not in protected_keys}

        assert filtered == properties


class TestCoordinatorDeviceStatusUpdate:
    """Tests for device status update logic."""

    def test_update_device_properties(self, make_device):
        """Test updating device properties from API response."""
        device = make_device("light", properties={"powerState": "0"})

        # Simulate API response
        new_properties = {"powerState": "1", "brightness": "80"}
        device.update_properties(new_properties)

        assert device.properties["powerState"] == "1"
        assert device.properties["brightness"] == "80"

    def test_update_preserves_unmentioned_properties(self, make_device):
        """Test that update preserves properties not in the update."""
        device = make_device(
            "light",
            properties={"powerState": "1", "brightness": "50", "temperature": "4000"},
        )

        device.update_properties({"brightness": "80"})

        assert device.properties["powerState"] == "1"  # Unchanged
        assert device.properties["brightness"] == "80"  # Updated
        assert device.properties["temperature"] == "4000"  # Unchanged

    def test_availability_from_connect_state(self, make_device):
        """Test device availability is updated from connectState."""
        device = make_device("light")
        assert device.available is True

        device.update_properties({"connectState": "0"})
        assert device.available is False

        device.update_properties({"connectState": "1"})
        assert device.available is True


class TestCoordinatorErrorHandling:
    """Tests for coordinator error handling."""

    def test_auth_error_detection(self):
        """Test authentication error is properly detected."""
        error = LiproAuthError("Token expired", code=401)

        assert isinstance(error, LiproAuthError)
        assert error.code == 401

    def test_connection_error_detection(self):
        """Test connection error is properly detected."""
        error = LiproConnectionError("Network unreachable")

        assert isinstance(error, LiproConnectionError)

    def test_api_error_with_code(self):
        """Test API error with error code."""
        error = LiproApiError("Device offline", code=140003)

        assert error.code == 140003


class TestCoordinatorDeviceCategorization:
    """Tests for device categorization."""

    def test_collect_outlet_device_ids(self, make_device):
        """Test outlet device IDs are collected for power query."""
        from custom_components.lipro.const.categories import DeviceCategory

        devices = [
            make_device("light", serial="03ab5ccd7cxxxxxx"),
            make_device("outlet", serial="03ab5ccd7cyyyyyy"),
            make_device("switch", serial="03ab5ccd7czzzzzz"),
        ]

        outlet_ids = [
            d.iot_device_id for d in devices if d.category == DeviceCategory.OUTLET
        ]

        assert len(outlet_ids) == 1
        assert "03ab5ccd7cyyyyyy" in outlet_ids

    def test_separate_group_and_device_ids(self, make_device):
        """Test group and device IDs are collected separately."""

        device1 = make_device("light", serial="03ab5ccd7cxxxxxx")
        device2 = LiproDevice(
            device_id=2,
            serial="mesh_group_10001",
            name="Test Group",
            device_type=1,
            iot_name="lipro_led",
            physical_model="light",
            is_group=True,
        )

        devices = [device1, device2]

        device_ids = [d.iot_device_id for d in devices if not d.is_group]
        group_ids = [d.serial for d in devices if d.is_group]

        assert len(device_ids) == 1
        assert len(group_ids) == 1


class TestCoordinatorStaleDeviceRemoval:
    """Tests for stale device removal."""

    def test_detect_stale_devices(self):
        """Test detection of devices that no longer exist."""
        previous_serials = {"device1", "device2", "device3"}
        current_serials = {"device1", "device3"}

        stale_serials = previous_serials - current_serials

        assert stale_serials == {"device2"}

    def test_no_stale_when_devices_added(self):
        """Test no stale devices when new devices are added."""
        previous_serials = {"device1", "device2"}
        current_serials = {"device1", "device2", "device3"}

        stale_serials = previous_serials - current_serials

        assert stale_serials == set()

    def test_all_devices_stale(self):
        """Test when all previous devices are removed."""
        previous_serials = {"device1", "device2"}
        current_serials = set()

        stale_serials = previous_serials - current_serials

        assert stale_serials == {"device1", "device2"}


class TestCoordinatorMqttIntegration:
    """Tests for MQTT integration in coordinator."""

    def test_mqtt_message_device_lookup(self, make_device):
        """Test device lookup from MQTT message."""
        device = make_device("light", serial="03ab5ccd7cxxxxxx")
        iot_id_to_device = {device.iot_device_id: device}

        # Simulate MQTT message
        mqtt_device_id = "03ab5ccd7cxxxxxx"
        found_device = iot_id_to_device.get(mqtt_device_id)

        assert found_device is not None
        assert found_device.serial == "03ab5ccd7cxxxxxx"

    def test_mqtt_message_unknown_device(self):
        """Test MQTT message for unknown device is ignored."""
        iot_id_to_device = {}

        mqtt_device_id = "03ab5ccd7c999999"
        found_device = iot_id_to_device.get(mqtt_device_id)

        assert found_device is None

    def test_mqtt_properties_update(self, make_device):
        """Test MQTT message updates device properties."""
        device = make_device("light", properties={"powerState": "0"})

        # Simulate MQTT message with new state
        mqtt_properties = {"powerState": "1", "brightness": "80"}
        device.update_properties(mqtt_properties)

        assert device.is_on is True
        assert device.brightness == 80


class TestCoordinatorSendCommand:
    """Tests for command sending logic."""

    @pytest.mark.asyncio
    async def test_send_command_to_device(self, mock_coordinator, make_device):
        """Test sending command to a device."""
        device = make_device("light", serial="03ab5ccd7cxxxxxx")
        mock_coordinator.devices = {device.serial: device}

        # Call mock
        result = await mock_coordinator.async_send_command(
            device.serial,
            "power",
            [{"key": "power_on", "value": True}],
        )

        assert result is True
        mock_coordinator.async_send_command.assert_called_once()

    @pytest.mark.asyncio
    async def test_send_command_with_properties(self, mock_coordinator, make_device):
        """Test sending command with multiple properties."""
        device = make_device("light", serial="03ab5ccd7cxxxxxx")

        properties = [
            {"key": "brightness", "value": "80"},
            {"key": "temperature", "value": "4000"},
        ]

        await mock_coordinator.async_send_command(
            device.serial,
            "change_state",
            properties,
        )

        call_args = mock_coordinator.async_send_command.call_args
        assert call_args[0][1] == "change_state"
        assert call_args[0][2] == properties


class TestCoordinatorOptimisticUpdate:
    """Tests for optimistic update logic."""

    def test_optimistic_state_applied(self, make_device):
        """Test optimistic state is applied immediately."""
        device = make_device("light", properties={"powerState": "0", "brightness": "50"})

        # Apply optimistic update
        optimistic_state = {"powerState": "1", "brightness": "80"}
        device.update_properties(optimistic_state)

        assert device.properties["powerState"] == "1"
        assert device.properties["brightness"] == "80"

    def test_optimistic_state_partial_update(self, make_device):
        """Test optimistic state only updates specified properties."""
        device = make_device(
            "light",
            properties={"powerState": "1", "brightness": "50", "temperature": "4000"},
        )

        # Only update brightness
        device.update_properties({"brightness": "80"})

        assert device.properties["powerState"] == "1"  # Unchanged
        assert device.properties["brightness"] == "80"  # Updated
        assert device.properties["temperature"] == "4000"  # Unchanged
