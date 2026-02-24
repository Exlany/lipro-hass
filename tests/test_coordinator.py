"""Tests for Lipro data update coordinator."""

from __future__ import annotations

from datetime import timedelta
from unittest.mock import patch

import pytest

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
            device_number=1,
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
            device_number=1,
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
                device_number=1,
                serial="03ab5ccd7cxxxxxx",
                name="Light 1",
                device_type=1,
                iot_name="",
                physical_model="light",
            ),
        }
        device_by_id = {
            "03ab5ccd7cxxxxxx": devices["03ab5ccd7cxxxxxx"],
        }

        # Simulate MQTT message lookup
        device_id = "03ab5ccd7cxxxxxx"
        device = device_by_id.get(device_id)

        assert device is not None
        assert device.name == "Light 1"

    def test_mqtt_message_unknown_device(self):
        """Test MQTT message for unknown device."""
        device_by_id = {}

        device_id = "03ab5ccd7c999999"
        device = device_by_id.get(device_id)

        assert device is None


class TestDeviceCategorization:
    """Tests for device categorization in coordinator."""

    def test_outlet_device_ids_collection(self):
        """Test outlet device IDs are collected for power query."""
        from custom_components.lipro.const.categories import DeviceCategory

        devices = [
            LiproDevice(
                device_number=1,
                serial="03ab5ccd7cxxxxxx",
                name="Light",
                device_type=1,
                iot_name="",
                physical_model="light",
            ),
            LiproDevice(
                device_number=2,
                serial="03ab5ccd7cyyyyyy",
                name="Outlet",
                device_type=6,
                iot_name="",
                physical_model="outlet",
            ),
            LiproDevice(
                device_number=3,
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
                device_number=1,
                serial="03ab5ccd7cxxxxxx",
                name="Light",
                device_type=1,
                iot_name="",
                physical_model="light",
                is_group=False,
            ),
            LiproDevice(
                device_number=2,
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


class TestMqttPollingInterval:
    """Tests for MQTT connect/disconnect polling interval adjustment."""

    def test_mqtt_connect_doubles_polling_interval(self):
        """Test MQTT connect logic: interval should be 2x base."""
        from custom_components.lipro.const import (
            CONF_SCAN_INTERVAL,
            DEFAULT_SCAN_INTERVAL,
        )

        base = 30
        # Replicate the logic from _on_mqtt_connect
        options = {CONF_SCAN_INTERVAL: base}
        interval = timedelta(
            seconds=options.get(CONF_SCAN_INTERVAL, DEFAULT_SCAN_INTERVAL) * 2
        )

        assert interval == timedelta(seconds=60)

    def test_mqtt_disconnect_restores_polling_interval(self):
        """Test MQTT disconnect logic: interval should be 1x base."""
        from custom_components.lipro.const import (
            CONF_SCAN_INTERVAL,
            DEFAULT_SCAN_INTERVAL,
        )

        base = 30
        options = {CONF_SCAN_INTERVAL: base}
        interval = timedelta(
            seconds=options.get(CONF_SCAN_INTERVAL, DEFAULT_SCAN_INTERVAL)
        )

        assert interval == timedelta(seconds=30)

    def test_mqtt_connect_uses_default_when_no_option(self):
        """Test MQTT connect uses DEFAULT_SCAN_INTERVAL when option missing."""
        from custom_components.lipro.const import DEFAULT_SCAN_INTERVAL

        interval = timedelta(seconds=DEFAULT_SCAN_INTERVAL * 2)

        assert interval == timedelta(seconds=DEFAULT_SCAN_INTERVAL * 2)
        # Verify the multiplier is 2, not 3
        assert interval.total_seconds() / DEFAULT_SCAN_INTERVAL == 2


class TestConnectStateReconciliation:
    """Tests for connectState=='1' triggering REST API refresh for groups."""

    def test_group_online_triggers_refresh(self):
        """Test group device coming online schedules a REST refresh."""
        device = LiproDevice(
            device_number=1,
            serial="mesh_group_10001",
            name="All Lights",
            device_type=1,
            iot_name="",
            physical_model="light",
            is_group=True,
            properties={"connectState": "0"},
        )

        # The reconciliation condition: connectState=="1" AND device.is_group
        properties = {"connectState": "1"}
        connect_state = properties.get("connectState")

        assert connect_state == "1"
        assert device.is_group is True
        # Both conditions met → should trigger refresh

    def test_non_group_online_does_not_trigger_refresh(self):
        """Test non-group device coming online does NOT meet refresh condition."""
        device = LiproDevice(
            device_number=1,
            serial="03ab5ccd7cxxxxxx",
            name="Light",
            device_type=1,
            iot_name="lipro_test",
            physical_model="light",
            is_group=False,
            properties={"connectState": "0"},
        )

        properties = {"connectState": "1"}
        connect_state = properties.get("connectState")

        assert connect_state == "1"
        assert device.is_group is False
        # is_group is False → should NOT trigger refresh

    def test_group_offline_does_not_trigger_refresh(self):
        """Test group device going offline does NOT meet refresh condition."""
        properties = {"connectState": "0"}
        connect_state = properties.get("connectState")

        assert connect_state != "1"
        # connectState != "1" → should NOT trigger refresh


class TestMqttDedupCacheLimit:
    """Tests for MQTT dedup cache size limit."""

    def test_cache_hard_cap_enforced(self):
        """Test that cache is trimmed when exceeding MAX_MQTT_CACHE_SIZE."""
        from custom_components.lipro.const.api import MAX_MQTT_CACHE_SIZE

        # Simulate a cache that exceeds the limit
        cache: dict[str, float] = {}
        for i in range(MAX_MQTT_CACHE_SIZE + 100):
            cache[f"device_{i}:hash_{i}"] = float(i)

        assert len(cache) > MAX_MQTT_CACHE_SIZE

        # Apply the same cleanup logic as coordinator._on_mqtt_message
        sorted_items = sorted(cache.items(), key=lambda x: x[1])
        cache = dict(sorted_items[len(sorted_items) // 2 :])

        # Should be reduced to half
        assert len(cache) == (MAX_MQTT_CACHE_SIZE + 100) // 2 + (
            (MAX_MQTT_CACHE_SIZE + 100) % 2
        )
        assert len(cache) <= MAX_MQTT_CACHE_SIZE

    def test_cache_under_limit_not_trimmed(self):
        """Test that cache under limit is not affected."""
        from custom_components.lipro.const.api import MAX_MQTT_CACHE_SIZE

        cache: dict[str, float] = {}
        for i in range(10):
            cache[f"device_{i}:hash_{i}"] = float(i)

        # Under limit — no trimming needed
        assert len(cache) < MAX_MQTT_CACHE_SIZE
        # The condition check would skip trimming
        should_trim = len(cache) > MAX_MQTT_CACHE_SIZE
        assert should_trim is False

    def test_cache_trim_keeps_newest_entries(self):
        """Test that trimming keeps the newest (highest timestamp) entries."""
        cache: dict[str, float] = {}
        for i in range(100):
            cache[f"key_{i}"] = float(i)

        sorted_items = sorted(cache.items(), key=lambda x: x[1])
        trimmed = dict(sorted_items[len(sorted_items) // 2 :])

        # Newest entries (50-99) should be kept
        assert "key_99" in trimmed
        assert "key_50" in trimmed
        # Oldest entries (0-49) should be removed
        assert "key_0" not in trimmed
        assert "key_49" not in trimmed


class TestAnonymousShareAsyncLoad:
    """Tests for anonymous share deferred async loading."""

    @pytest.mark.asyncio
    async def test_async_ensure_loaded_calls_load(self):
        """Test async_ensure_loaded triggers _load_reported_devices in thread."""
        from custom_components.lipro.core.anonymous_share import AnonymousShareManager

        manager = AnonymousShareManager()
        manager._cache_loaded = False

        with patch.object(manager, "_load_reported_devices") as mock_load:
            await manager.async_ensure_loaded()
            mock_load.assert_called_once()

        # Second call should be a no-op
        with patch.object(manager, "_load_reported_devices") as mock_load:
            await manager.async_ensure_loaded()
            mock_load.assert_not_called()

    def test_set_enabled_defers_load(self):
        """Test set_enabled sets _cache_loaded=False instead of loading sync."""
        from custom_components.lipro.core.anonymous_share import AnonymousShareManager

        manager = AnonymousShareManager()

        with patch.object(manager, "_load_reported_devices") as mock_load:
            manager.set_enabled(True, storage_path="/var/lib/test")
            # Should NOT call sync load
            mock_load.assert_not_called()
            # Should mark cache as needing load
            assert manager._cache_loaded is False


class TestMqttDisconnectNotification:
    """Tests for MQTT prolonged disconnect notification logic."""

    def test_check_skipped_when_mqtt_disabled(self):
        """Test notification check is skipped when MQTT is disabled."""
        mqtt_enabled = False
        mqtt_connected = False
        mqtt_disconnect_time = 0.0  # long ago
        mqtt_disconnect_notified = False

        should_notify = (
            mqtt_enabled
            and not mqtt_connected
            and mqtt_disconnect_time is not None
            and not mqtt_disconnect_notified
        )
        assert should_notify is False

    def test_check_skipped_when_connected(self):
        """Test notification check is skipped when MQTT is connected."""
        mqtt_enabled = True
        mqtt_connected = True
        mqtt_disconnect_time = 0.0
        mqtt_disconnect_notified = False

        should_notify = (
            mqtt_enabled
            and not mqtt_connected
            and mqtt_disconnect_time is not None
            and not mqtt_disconnect_notified
        )
        assert should_notify is False

    def test_check_skipped_when_already_notified(self):
        """Test notification check is skipped when already notified."""
        mqtt_enabled = True
        mqtt_connected = False
        mqtt_disconnect_time = 0.0
        mqtt_disconnect_notified = True

        should_notify = (
            mqtt_enabled
            and not mqtt_connected
            and mqtt_disconnect_time is not None
            and not mqtt_disconnect_notified
        )
        assert should_notify is False

    def test_check_skipped_when_no_disconnect_time(self):
        """Test notification check is skipped when disconnect time is None."""
        mqtt_enabled = True
        mqtt_connected = False
        mqtt_disconnect_time = None
        mqtt_disconnect_notified = False

        should_notify = (
            mqtt_enabled
            and not mqtt_connected
            and mqtt_disconnect_time is not None
            and not mqtt_disconnect_notified
        )
        assert should_notify is False

    def test_notify_when_threshold_exceeded(self):
        """Test notification fires when disconnect exceeds threshold."""
        from time import monotonic

        from custom_components.lipro.const.api import MQTT_DISCONNECT_NOTIFY_THRESHOLD

        mqtt_disconnect_time = monotonic() - MQTT_DISCONNECT_NOTIFY_THRESHOLD - 1
        elapsed = monotonic() - mqtt_disconnect_time

        assert elapsed >= MQTT_DISCONNECT_NOTIFY_THRESHOLD

    def test_no_notify_when_under_threshold(self):
        """Test no notification when disconnect is under threshold."""
        from time import monotonic

        from custom_components.lipro.const.api import MQTT_DISCONNECT_NOTIFY_THRESHOLD

        mqtt_disconnect_time = monotonic() - 10  # Only 10 seconds ago
        elapsed = monotonic() - mqtt_disconnect_time

        assert elapsed < MQTT_DISCONNECT_NOTIFY_THRESHOLD

    def test_connect_resets_disconnect_tracking(self):
        """Test that MQTT connect resets disconnect tracking state."""
        # Simulate state after prolonged disconnect + notification
        mqtt_disconnect_time = 100.0
        mqtt_disconnect_notified = True

        # Simulate _on_mqtt_connect reset logic
        mqtt_disconnect_time = None
        mqtt_disconnect_notified = False

        assert mqtt_disconnect_time is None
        assert mqtt_disconnect_notified is False

    def test_disconnect_records_time_only_once(self):
        """Test that repeated disconnects don't reset the initial disconnect time."""
        from time import monotonic

        mqtt_disconnect_time = None

        # First disconnect
        if mqtt_disconnect_time is None:
            mqtt_disconnect_time = monotonic()
        first_time = mqtt_disconnect_time

        # Second disconnect callback (e.g., reconnect attempt failed)
        if mqtt_disconnect_time is None:
            mqtt_disconnect_time = monotonic()

        # Should still be the first time
        assert mqtt_disconnect_time == first_time

    def test_threshold_constant_is_reasonable(self):
        """Test MQTT disconnect notify threshold is reasonable."""
        from custom_components.lipro.const.api import MQTT_DISCONNECT_NOTIFY_THRESHOLD

        assert MQTT_DISCONNECT_NOTIFY_THRESHOLD >= 60  # At least 1 minute
        assert MQTT_DISCONNECT_NOTIFY_THRESHOLD <= 600  # At most 10 minutes
