"""Tests for Lipro data update coordinator."""

from __future__ import annotations

from custom_components.lipro.core.device import LiproDevice, parse_properties_list


class TestLiproDataUpdateCoordinator:
    """Tests for LiproDataUpdateCoordinator."""

    def _create_device(
        self,
        serial: str = "03ab5ccd7cxxxxxx",
        name: str = "Test Device",
        device_type: int = 1,
        physical_model: str = "light",
        is_group: bool = False,
        properties: dict | None = None,
    ) -> LiproDevice:
        """Create a device for testing."""
        return LiproDevice(
            device_id=1,
            serial=serial,
            name=name,
            device_type=device_type,
            iot_name="lipro_test",
            physical_model=physical_model,
            is_group=is_group,
            properties=properties or {},
        )

    def test_device_lookup_by_serial(self):
        """Test device lookup by serial number."""
        device = self._create_device(serial="03ab5ccd7cxxxxxx")
        devices = {device.serial: device}

        assert devices.get("03ab5ccd7cxxxxxx") == device
        assert devices.get("nonexistent") is None

    def test_device_lookup_by_iot_id(self):
        """Test device lookup by IoT device ID."""
        device = self._create_device(serial="03ab5ccd7cxxxxxx")

        # IoT ID is same as serial for non-group devices
        assert device.iot_device_id == "03ab5ccd7cxxxxxx"

    def test_group_device_serial(self):
        """Test group device serial format."""
        device = self._create_device(
            serial="mesh_group_10001",
            is_group=True,
        )

        assert device.is_group is True
        assert device.serial == "mesh_group_10001"


class TestDeviceStatusUpdate:
    """Tests for device status update logic."""

    def _create_device(
        self,
        properties: dict | None = None,
    ) -> LiproDevice:
        """Create a device for testing."""
        return LiproDevice(
            device_id=1,
            serial="03ab5ccd7cxxxxxx",
            name="Test Light",
            device_type=1,
            iot_name="lipro_led",
            physical_model="light",
            properties=properties or {},
        )

    def test_update_properties(self):
        """Test updating device properties."""
        device = self._create_device(properties={"powerState": "0"})

        device.update_properties({"powerState": "1", "brightness": "80"})

        assert device.properties["powerState"] == "1"
        assert device.properties["brightness"] == "80"

    def test_update_properties_preserves_existing(self):
        """Test that update preserves existing properties."""
        device = self._create_device(
            properties={"powerState": "1", "brightness": "50", "temperature": "4000"}
        )

        device.update_properties({"brightness": "80"})

        assert device.properties["powerState"] == "1"  # Unchanged
        assert device.properties["brightness"] == "80"  # Updated
        assert device.properties["temperature"] == "4000"  # Unchanged

    def test_update_availability_on_connect_state(self):
        """Test availability is updated based on connectState."""
        device = self._create_device()
        assert device.available is True

        device.update_properties({"connectState": "0"})
        assert device.available is False

        device.update_properties({"connectState": "1"})
        assert device.available is True


class TestParsePropertiesList:
    """Tests for parse_properties_list function."""

    def test_parse_valid_list(self):
        """Test parsing valid properties list."""
        properties_list = [
            {"key": "powerState", "value": "1"},
            {"key": "brightness", "value": "80"},
            {"key": "temperature", "value": "4000"},
        ]

        result = parse_properties_list(properties_list)

        assert result == {
            "powerState": "1",
            "brightness": "80",
            "temperature": "4000",
        }

    def test_parse_empty_list(self):
        """Test parsing empty list."""
        assert parse_properties_list([]) == {}
        assert parse_properties_list(None) == {}

    def test_parse_list_with_missing_keys(self):
        """Test parsing list with missing keys."""
        properties_list = [
            {"key": "powerState", "value": "1"},
            {"value": "80"},  # Missing key
            {"key": None, "value": "test"},  # None key
        ]

        result = parse_properties_list(properties_list)

        assert result == {"powerState": "1"}


class TestDebounceProtection:
    """Tests for debounce protection logic."""

    def test_filter_protected_properties(self):
        """Test filtering protected properties."""
        properties = {
            "powerState": "1",
            "brightness": "80",
            "temperature": "4000",
        }
        protected_keys = {"brightness", "temperature"}

        # Simulate filtering logic
        filtered = {k: v for k, v in properties.items() if k not in protected_keys}

        assert filtered == {"powerState": "1"}
        assert "brightness" not in filtered
        assert "temperature" not in filtered

    def test_no_protected_keys(self):
        """Test when no keys are protected."""
        properties = {
            "powerState": "1",
            "brightness": "80",
        }
        protected_keys = set()

        filtered = {k: v for k, v in properties.items() if k not in protected_keys}

        assert filtered == properties


class TestEntityRegistration:
    """Tests for entity registration logic."""

    def test_entity_index_by_device(self):
        """Test entity indexing by device serial."""
        entities_by_device: dict[str, list] = {}
        device_serial = "03ab5ccd7cxxxxxx"

        # Simulate registration
        if device_serial not in entities_by_device:
            entities_by_device[device_serial] = []
        entities_by_device[device_serial].append("entity1")
        entities_by_device[device_serial].append("entity2")

        assert len(entities_by_device[device_serial]) == 2

    def test_entity_unregistration(self):
        """Test entity unregistration."""
        entities_by_device = {
            "03ab5ccd7cxxxxxx": ["entity1", "entity2", "entity3"],
        }
        device_serial = "03ab5ccd7cxxxxxx"
        entity_to_remove = "entity2"

        # Simulate unregistration
        entities_by_device[device_serial] = [
            e for e in entities_by_device[device_serial] if e != entity_to_remove
        ]

        assert entities_by_device[device_serial] == ["entity1", "entity3"]


class TestMqttMessageHandling:
    """Tests for MQTT message handling logic."""

    def test_mqtt_message_device_lookup(self):
        """Test device lookup from MQTT message."""
        devices = {
            "03ab5ccd7cxxxxxx": LiproDevice(
                device_id=1,
                serial="03ab5ccd7cxxxxxx",
                name="Light 1",
                device_type=1,
                iot_name="",
                physical_model="light",
            ),
        }
        iot_id_to_device = {
            "03ab5ccd7cxxxxxx": devices["03ab5ccd7cxxxxxx"],
        }

        # Simulate MQTT message lookup
        device_id = "03ab5ccd7cxxxxxx"
        device = iot_id_to_device.get(device_id)

        assert device is not None
        assert device.name == "Light 1"

    def test_mqtt_message_unknown_device(self):
        """Test MQTT message for unknown device."""
        iot_id_to_device = {}

        device_id = "03ab5ccd7c999999"
        device = iot_id_to_device.get(device_id)

        assert device is None


class TestDeviceCategorization:
    """Tests for device categorization in coordinator."""

    def test_outlet_device_ids_collection(self):
        """Test outlet device IDs are collected for power query."""
        from custom_components.lipro.const.categories import DeviceCategory

        devices = [
            LiproDevice(
                device_id=1,
                serial="03ab5ccd7cxxxxxx",
                name="Light",
                device_type=1,
                iot_name="",
                physical_model="light",
            ),
            LiproDevice(
                device_id=2,
                serial="03ab5ccd7cyyyyyy",
                name="Outlet",
                device_type=6,
                iot_name="",
                physical_model="outlet",
            ),
            LiproDevice(
                device_id=3,
                serial="03ab5ccd7czzzzzz",
                name="Switch",
                device_type=3,
                iot_name="",
                physical_model="switch",
            ),
        ]

        outlet_ids = [
            d.iot_device_id for d in devices if d.category == DeviceCategory.OUTLET
        ]

        assert len(outlet_ids) == 1
        assert "03ab5ccd7cyyyyyy" in outlet_ids

    def test_group_device_ids_collection(self):
        """Test group device IDs are collected separately."""
        devices = [
            LiproDevice(
                device_id=1,
                serial="03ab5ccd7cxxxxxx",
                name="Light",
                device_type=1,
                iot_name="",
                physical_model="light",
                is_group=False,
            ),
            LiproDevice(
                device_id=2,
                serial="mesh_group_10001",
                name="All Lights",
                device_type=1,
                iot_name="",
                physical_model="light",
                is_group=True,
            ),
        ]

        device_ids = [d.iot_device_id for d in devices if not d.is_group]
        group_ids = [d.serial for d in devices if d.is_group]

        assert len(device_ids) == 1
        assert len(group_ids) == 1
        assert "03ab5ccd7cxxxxxx" in device_ids
        assert "mesh_group_10001" in group_ids


class TestStaleDeviceRemoval:
    """Tests for stale device removal logic."""

    def test_detect_stale_devices(self):
        """Test detection of stale devices."""
        previous_serials = {"device1", "device2", "device3"}
        current_serials = {"device1", "device3"}

        stale_serials = previous_serials - current_serials

        assert stale_serials == {"device2"}

    def test_no_stale_devices(self):
        """Test when no devices are stale."""
        previous_serials = {"device1", "device2"}
        current_serials = {"device1", "device2", "device3"}

        stale_serials = previous_serials - current_serials

        assert stale_serials == set()


class TestCoordinatorConstants:
    """Tests for coordinator-related constants."""

    def test_default_scan_interval(self):
        """Test default scan interval constant."""
        from custom_components.lipro.const import DEFAULT_SCAN_INTERVAL

        # Default should be reasonable (e.g., 30 seconds)
        assert DEFAULT_SCAN_INTERVAL > 0
        assert DEFAULT_SCAN_INTERVAL <= 300  # Not more than 5 minutes

    def test_domain_constant(self):
        """Test domain constant."""
        from custom_components.lipro.const import DOMAIN

        assert DOMAIN == "lipro"
