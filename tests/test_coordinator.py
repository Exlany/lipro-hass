"""Tests for Lipro data update coordinator.

These tests instantiate a real LiproDataUpdateCoordinator with mocked
dependencies and exercise its public and internal methods directly.
"""

from __future__ import annotations

from datetime import timedelta
from time import monotonic
from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from pytest_homeassistant_custom_component.common import MockConfigEntry

from custom_components.lipro.const import (
    DEFAULT_SCAN_INTERVAL,
    DOMAIN,
    MAX_MQTT_CACHE_SIZE,
    MQTT_DISCONNECT_NOTIFY_THRESHOLD,
)
from custom_components.lipro.core.api import LiproAuthError
from custom_components.lipro.core.device import LiproDevice

# ---------------------------------------------------------------------------
# Fixture: real coordinator with mocked deps
# ---------------------------------------------------------------------------


@pytest.fixture
def coordinator(hass, mock_lipro_api_client, mock_auth_manager):
    """Create a real LiproDataUpdateCoordinator with mocked deps."""
    entry = MockConfigEntry(
        domain=DOMAIN,
        data={
            "phone": "13800000000",
            "password_hash": "e10adc3949ba59abbe56e057f20f883e",
            "phone_id": "test-phone-id",
            "access_token": "test_token",
            "refresh_token": "test_refresh",
            "user_id": 10001,
        },
        options={},
        unique_id="lipro_10001",
    )
    entry.add_to_hass(hass)

    with patch(
        "custom_components.lipro.core.coordinator.get_anonymous_share_manager"
    ) as mock_share:
        mock_share.return_value = MagicMock(is_enabled=False, set_enabled=MagicMock())
        from custom_components.lipro.core.coordinator import LiproDataUpdateCoordinator

        return LiproDataUpdateCoordinator(
            hass, mock_lipro_api_client, mock_auth_manager, entry
        )


def _make_device(
    serial: str = "03ab5ccd7cxxxxxx",
    name: str = "Test Light",
    is_group: bool = False,
    properties: dict | None = None,
) -> LiproDevice:
    """Helper to create a LiproDevice for tests."""
    return LiproDevice(
        device_number=1,
        serial=serial,
        name=name,
        device_type=1,
        iot_name="lipro_led",
        physical_model="light",
        is_group=is_group,
        properties=properties or {},
    )


def _make_mock_entity(
    unique_id: str,
    device: LiproDevice,
    protected_keys: set[str] | None = None,
) -> MagicMock:
    """Helper to create a mock LiproEntity."""
    entity = MagicMock()
    entity.unique_id = unique_id
    entity.device = device
    entity.get_protected_keys = MagicMock(return_value=protected_keys or set())
    return entity


# ===========================================================================
# 1. Device management
# ===========================================================================


class TestCoordinatorDeviceManagement:
    """Test get_device(), get_device_by_id(), devices property."""

    def test_devices_property_returns_internal_dict(self, coordinator):
        dev = _make_device()
        coordinator._devices["03ab5ccd7cxxxxxx"] = dev
        assert coordinator.devices is coordinator._devices
        assert coordinator.devices["03ab5ccd7cxxxxxx"] is dev

    def test_get_device_found(self, coordinator):
        dev = _make_device(serial="aaa")
        coordinator._devices["aaa"] = dev
        assert coordinator.get_device("aaa") is dev

    def test_get_device_not_found(self, coordinator):
        assert coordinator.get_device("nonexistent") is None

    def test_get_device_by_id_found(self, coordinator):
        dev = _make_device(serial="bbb")
        coordinator._device_by_id["bbb"] = dev
        assert coordinator.get_device_by_id("bbb") is dev

    def test_get_device_by_id_not_found(self, coordinator):
        assert coordinator.get_device_by_id("missing") is None

    def test_get_device_by_id_gateway_mapping(self, coordinator):
        """Gateway ID mapped to a group device."""
        dev = _make_device(serial="mesh_group_10001", is_group=True)
        coordinator._device_by_id["gateway_abc"] = dev
        assert coordinator.get_device_by_id("gateway_abc") is dev


# ===========================================================================
# 2. Entity registration
# ===========================================================================


class TestCoordinatorEntityRegistration:
    """Test register_entity() and unregister_entity()."""

    def test_register_entity(self, coordinator):
        dev = _make_device()
        entity = _make_mock_entity("light_1", dev)
        coordinator.register_entity(entity)

        assert "light_1" in coordinator._entities
        assert coordinator._entities["light_1"] is entity
        assert entity in coordinator._entities_by_device[dev.serial]

    def test_register_duplicate_entity_no_double_add(self, coordinator):
        dev = _make_device()
        entity = _make_mock_entity("light_1", dev)
        coordinator.register_entity(entity)
        coordinator.register_entity(entity)

        assert coordinator._entities_by_device[dev.serial].count(entity) == 1

    def test_register_multiple_entities_same_device(self, coordinator):
        dev = _make_device()
        e1 = _make_mock_entity("light_1", dev)
        e2 = _make_mock_entity("brightness_1", dev)
        coordinator.register_entity(e1)
        coordinator.register_entity(e2)

        assert len(coordinator._entities_by_device[dev.serial]) == 2

    def test_unregister_entity(self, coordinator):
        dev = _make_device()
        entity = _make_mock_entity("light_1", dev)
        coordinator.register_entity(entity)
        coordinator.unregister_entity(entity)

        assert "light_1" not in coordinator._entities
        assert dev.serial not in coordinator._entities_by_device

    def test_unregister_one_of_two(self, coordinator):
        dev = _make_device()
        e1 = _make_mock_entity("light_1", dev)
        e2 = _make_mock_entity("brightness_1", dev)
        coordinator.register_entity(e1)
        coordinator.register_entity(e2)
        coordinator.unregister_entity(e1)

        assert "light_1" not in coordinator._entities
        assert "brightness_1" in coordinator._entities
        assert len(coordinator._entities_by_device[dev.serial]) == 1

    def test_unregister_nonexistent_is_noop(self, coordinator):
        dev = _make_device()
        entity = _make_mock_entity("ghost", dev)
        coordinator.unregister_entity(entity)  # should not raise

    def test_entity_with_no_unique_id_skipped(self, coordinator):
        dev = _make_device()
        entity = _make_mock_entity(None, dev)
        entity.unique_id = None
        coordinator.register_entity(entity)
        assert len(coordinator._entities) == 0


# ===========================================================================
# 3. Debounce filtering
# ===========================================================================


class TestCoordinatorDebounceFiltering:
    """Test _filter_protected_properties() and _get_protected_keys_for_device()."""

    def test_no_entities_returns_all_properties(self, coordinator):
        props = {"powerState": "1", "brightness": "80"}
        result = coordinator._filter_protected_properties("serial_x", props)
        assert result == props

    def test_protected_keys_filtered_out(self, coordinator):
        dev = _make_device(serial="dev1")
        entity = _make_mock_entity(
            "e1", dev, protected_keys={"brightness", "temperature"}
        )
        coordinator.register_entity(entity)

        props = {"powerState": "1", "brightness": "80", "temperature": "4000"}
        result = coordinator._filter_protected_properties("dev1", props)
        assert result == {"powerState": "1"}

    def test_get_protected_keys_aggregates_multiple_entities(self, coordinator):
        dev = _make_device(serial="dev1")
        e1 = _make_mock_entity("e1", dev, protected_keys={"brightness"})
        e2 = _make_mock_entity("e2", dev, protected_keys={"temperature"})
        coordinator.register_entity(e1)
        coordinator.register_entity(e2)

        keys = coordinator._get_protected_keys_for_device("dev1")
        assert keys == {"brightness", "temperature"}

    def test_get_protected_keys_empty_when_no_entities(self, coordinator):
        keys = coordinator._get_protected_keys_for_device("no_such_device")
        assert keys == set()


# ===========================================================================
# 4. Apply properties update
# ===========================================================================


class TestCoordinatorApplyPropertiesUpdate:
    """Test _apply_properties_update() with and without protection."""

    def test_apply_without_protection(self, coordinator):
        dev = _make_device(properties={"powerState": "0"})
        coordinator._apply_properties_update(
            dev, {"powerState": "1", "brightness": "50"}, apply_protection=False
        )
        assert dev.properties["powerState"] == "1"
        assert dev.properties["brightness"] == "50"

    def test_apply_with_protection_filters_keys(self, coordinator):
        dev = _make_device(
            serial="dev1", properties={"powerState": "0", "brightness": "30"}
        )
        entity = _make_mock_entity("e1", dev, protected_keys={"brightness"})
        coordinator.register_entity(entity)

        coordinator._apply_properties_update(
            dev, {"powerState": "1", "brightness": "99"}, apply_protection=True
        )
        assert dev.properties["powerState"] == "1"
        # brightness should NOT be overwritten because it's protected
        assert dev.properties["brightness"] == "30"

    def test_apply_empty_properties_is_noop(self, coordinator):
        dev = _make_device(properties={"powerState": "0"})
        coordinator._apply_properties_update(dev, {}, apply_protection=False)
        assert dev.properties == {"powerState": "0"}


# ===========================================================================
# 5. MQTT message handling
# ===========================================================================


class TestCoordinatorMqttMessageHandling:
    """Test _on_mqtt_message(): device lookup, property update, dedup."""

    def test_known_device_updates_properties(self, coordinator):
        dev = _make_device(serial="dev1", properties={"powerState": "0"})
        coordinator._devices["dev1"] = dev
        coordinator._device_by_id["dev1"] = dev

        coordinator._on_mqtt_message("dev1", {"powerState": "1"})
        assert dev.properties["powerState"] == "1"

    def test_unknown_device_ignored(self, coordinator):
        # Should not raise
        coordinator._on_mqtt_message("unknown_id", {"powerState": "1"})

    def test_dedup_within_window_skips_second_message(self, coordinator):
        dev = _make_device(serial="dev1", properties={"brightness": "0"})
        coordinator._devices["dev1"] = dev
        coordinator._device_by_id["dev1"] = dev

        coordinator._on_mqtt_message("dev1", {"brightness": "50"})
        assert dev.properties["brightness"] == "50"

        # Manually set brightness back to verify dedup blocks the second call
        dev.properties["brightness"] = "0"
        coordinator._on_mqtt_message("dev1", {"brightness": "50"})
        # Dedup should have skipped the second identical message
        assert dev.properties["brightness"] == "0"

    def test_dedup_expired_allows_through(self, coordinator):
        dev = _make_device(serial="dev1", properties={"brightness": "0"})
        coordinator._devices["dev1"] = dev
        coordinator._device_by_id["dev1"] = dev

        coordinator._on_mqtt_message("dev1", {"brightness": "50"})
        assert dev.properties["brightness"] == "50"

        # Expire the cache entry by backdating its timestamp
        for key in list(coordinator._mqtt_message_cache):
            coordinator._mqtt_message_cache[key] = monotonic() - 10.0

        dev.properties["brightness"] = "0"
        coordinator._on_mqtt_message("dev1", {"brightness": "50"})
        assert dev.properties["brightness"] == "50"

    def test_different_properties_not_deduped(self, coordinator):
        dev = _make_device(serial="dev1", properties={})
        coordinator._devices["dev1"] = dev
        coordinator._device_by_id["dev1"] = dev

        coordinator._on_mqtt_message("dev1", {"brightness": "50"})
        coordinator._on_mqtt_message("dev1", {"brightness": "80"})
        assert dev.properties["brightness"] == "80"


# ===========================================================================
# 6. MQTT polling interval
# ===========================================================================


class TestCoordinatorMqttPollingInterval:
    """Test _on_mqtt_connect() doubles interval, _on_mqtt_disconnect() restores."""

    def test_on_mqtt_connect_doubles_interval(self, coordinator):
        base = coordinator._base_scan_interval
        coordinator._on_mqtt_connect()

        assert coordinator._mqtt_connected is True
        assert coordinator.update_interval == timedelta(seconds=base * 2)

    def test_on_mqtt_disconnect_restores_interval(self, coordinator):
        base = coordinator._base_scan_interval
        # First connect to double it
        coordinator._on_mqtt_connect()
        assert coordinator.update_interval == timedelta(seconds=base * 2)

        # Then disconnect to restore
        coordinator._on_mqtt_disconnect()
        assert coordinator._mqtt_connected is False
        assert coordinator.update_interval == timedelta(seconds=base)

    def test_on_mqtt_connect_resets_disconnect_tracking(self, coordinator):
        coordinator._mqtt_disconnect_time = 123.0
        coordinator._mqtt_disconnect_notified = True

        coordinator._on_mqtt_connect()

        assert coordinator._mqtt_disconnect_time is None
        assert coordinator._mqtt_disconnect_notified is False

    def test_on_mqtt_disconnect_records_time_once(self, coordinator):
        coordinator._mqtt_disconnect_time = None
        coordinator._on_mqtt_disconnect()
        first_time = coordinator._mqtt_disconnect_time

        coordinator._on_mqtt_disconnect()
        assert coordinator._mqtt_disconnect_time == first_time

    def test_default_base_scan_interval(self, coordinator):
        assert coordinator._base_scan_interval == DEFAULT_SCAN_INTERVAL


# ===========================================================================
# 7. MQTT cache cleanup
# ===========================================================================


class TestCoordinatorMqttCacheCleanup:
    """Test _cleanup_mqtt_cache() removes stale entries."""

    def test_stale_entries_removed(self, coordinator):
        now = monotonic()
        coordinator._mqtt_message_cache = {
            "old_key": now - 100.0,
            "fresh_key": now - 1.0,
        }
        coordinator._cleanup_mqtt_cache(now)

        assert "old_key" not in coordinator._mqtt_message_cache
        assert "fresh_key" in coordinator._mqtt_message_cache

    def test_hard_cap_keeps_newest_half(self, coordinator):
        now = monotonic()
        # All entries are "fresh" (within 5s) but exceed MAX_MQTT_CACHE_SIZE
        coordinator._mqtt_message_cache = {
            f"key_{i}": now - (0.001 * i) for i in range(MAX_MQTT_CACHE_SIZE + 200)
        }
        coordinator._cleanup_mqtt_cache(now)

        assert len(coordinator._mqtt_message_cache) <= MAX_MQTT_CACHE_SIZE

    def test_empty_cache_is_noop(self, coordinator):
        coordinator._mqtt_message_cache = {}
        coordinator._cleanup_mqtt_cache(monotonic())
        assert coordinator._mqtt_message_cache == {}


# ===========================================================================
# 8. Send command
# ===========================================================================


class TestCoordinatorSendCommand:
    """Test async_send_command() dispatches to correct client method."""

    @pytest.mark.asyncio
    async def test_send_command_non_group(self, coordinator, mock_lipro_api_client):
        dev = _make_device(serial="dev1", is_group=False)
        result = await coordinator.async_send_command(dev, "turnOn")

        assert result is True
        mock_lipro_api_client.send_command.assert_awaited_once_with(
            "dev1", "turnOn", dev.device_type, None, dev.iot_name
        )
        mock_lipro_api_client.send_group_command.assert_not_awaited()

    @pytest.mark.asyncio
    async def test_send_command_group(self, coordinator, mock_lipro_api_client):
        dev = _make_device(serial="mesh_group_10001", is_group=True)
        props = [{"key": "brightness", "value": "80"}]
        result = await coordinator.async_send_command(dev, "setBrightness", props)

        assert result is True
        mock_lipro_api_client.send_group_command.assert_awaited_once_with(
            "mesh_group_10001", "setBrightness", dev.device_type, props, dev.iot_name
        )
        mock_lipro_api_client.send_command.assert_not_awaited()

    @pytest.mark.asyncio
    async def test_send_command_auth_error_returns_false(
        self, coordinator, mock_auth_manager
    ):
        mock_auth_manager.ensure_valid_token.side_effect = LiproAuthError("expired")
        dev = _make_device()
        result = await coordinator.async_send_command(dev, "turnOn")

        assert result is False


# ===========================================================================
# 9. Missing coordinator behaviors
# ===========================================================================


class TestCoordinatorMqttSetupAndSync:
    """Test real MQTT setup/teardown/sync methods."""

    @pytest.mark.asyncio
    async def test_async_setup_mqtt_success(self, coordinator, mock_lipro_api_client):
        coordinator._devices = {
            "dev1": _make_device(serial="dev1"),
            "mesh_group_1": _make_device(serial="mesh_group_1", is_group=True),
        }
        mock_lipro_api_client.get_mqtt_config.return_value = {
            "accessKey": "enc-ak",
            "secretKey": "enc-sk",
        }

        mock_mqtt = AsyncMock()
        with (
            patch(
                "custom_components.lipro.core.coordinator.decrypt_mqtt_credential",
                side_effect=["ak", "sk"],
            ),
            patch(
                "custom_components.lipro.core.coordinator.LiproMqttClient"
            ) as mqtt_cls,
        ):
            mqtt_cls.return_value = mock_mqtt
            ok = await coordinator.async_setup_mqtt()

        assert ok is True
        assert coordinator._biz_id == "10001"
        mock_mqtt.start.assert_awaited_once_with(["dev1", "mesh_group_1"])

    @pytest.mark.asyncio
    async def test_async_setup_mqtt_missing_credential_returns_false(
        self, coordinator, mock_lipro_api_client
    ):
        mock_lipro_api_client.get_mqtt_config.return_value = {"accessKey": "x"}
        ok = await coordinator.async_setup_mqtt()
        assert ok is False

    @pytest.mark.asyncio
    async def test_async_setup_mqtt_without_config_entry_returns_false(
        self, coordinator
    ):
        coordinator.config_entry = None
        assert await coordinator.async_setup_mqtt() is False

    @pytest.mark.asyncio
    async def test_async_stop_mqtt(self, coordinator):
        mqtt_client = AsyncMock()
        coordinator._mqtt_client = mqtt_client
        coordinator._mqtt_connected = True

        await coordinator.async_stop_mqtt()

        mqtt_client.stop.assert_awaited_once()
        assert coordinator._mqtt_client is None
        assert coordinator._mqtt_connected is False

    @pytest.mark.asyncio
    async def test_sync_mqtt_subscriptions_uses_current_devices(self, coordinator):
        mqtt_client = AsyncMock()
        coordinator._mqtt_client = mqtt_client
        coordinator._devices = {
            "dev_a": _make_device(serial="dev_a"),
            "mesh_group_1": _make_device(serial="mesh_group_1", is_group=True),
        }

        await coordinator._sync_mqtt_subscriptions()

        mqtt_client.sync_subscriptions.assert_awaited_once_with(
            {"dev_a", "mesh_group_1"}
        )


class TestCoordinatorStatusQueriesAndNotifications:
    """Test status query methods and notification/re-auth paths."""

    @pytest.mark.asyncio
    async def test_query_group_status_maps_gateway_and_updates_properties(
        self, coordinator, mock_lipro_api_client
    ):
        group = _make_device(serial="mesh_group_10001", is_group=True)
        coordinator._devices[group.serial] = group
        coordinator._group_ids_to_query = [group.serial]
        mock_lipro_api_client.query_mesh_group_status.return_value = [
            {
                "groupId": "mesh_group_10001",
                "gatewayDeviceId": "03ab5ccd7cgw",
                "properties": [{"key": "powerState", "value": "1"}],
            }
        ]

        await coordinator._query_group_status()

        assert group.properties["powerState"] == "1"
        assert coordinator._device_by_id["03ab5ccd7cgw"] is group

    @pytest.mark.asyncio
    async def test_query_outlet_power_writes_extra_data(
        self, coordinator, mock_lipro_api_client
    ):
        outlet = _make_device(serial="out1", properties={"powerState": "1"})
        coordinator._devices[outlet.serial] = outlet
        coordinator._device_by_id[outlet.serial] = outlet
        coordinator._outlet_ids_to_query = [outlet.serial]
        mock_lipro_api_client.fetch_outlet_power_info.return_value = {
            "nowPower": 33.5,
            "energyList": [{"t": "20240101", "v": 2.2}],
        }

        await coordinator._query_outlet_power()

        assert outlet.extra_data["power_info"]["nowPower"] == 33.5

    @pytest.mark.asyncio
    async def test_query_connect_status_updates_connect_state(
        self, coordinator, mock_lipro_api_client
    ):
        dev = _make_device(serial="dev1", properties={"connectState": "1"})
        coordinator._devices[dev.serial] = dev
        coordinator._device_by_id[dev.serial] = dev
        coordinator._iot_ids_to_query = [dev.serial]
        mock_lipro_api_client.query_connect_status.return_value = {dev.serial: False}

        await coordinator._query_connect_status()

        assert dev.properties["connectState"] == "0"

    @pytest.mark.asyncio
    async def test_async_remove_stale_devices(self, coordinator):
        device_entry = MagicMock(id="reg-id", name="Stale Device")
        registry = MagicMock()
        registry.async_get_device.return_value = device_entry

        with patch("custom_components.lipro.core.coordinator.dr.async_get") as dr_get:
            dr_get.return_value = registry
            await coordinator._async_remove_stale_devices({"03ab5ccd7cdead"})

        registry.async_remove_device.assert_called_once_with("reg-id")

    @pytest.mark.asyncio
    async def test_trigger_reauth_creates_notification_and_starts_reauth(
        self, coordinator
    ):
        with (
            patch.object(
                coordinator, "_async_show_auth_notification", new_callable=AsyncMock
            ) as show_auth,
            patch.object(
                coordinator.config_entry, "async_start_reauth"
            ) as start_reauth,
        ):
            await coordinator._trigger_reauth("auth_error", error="401")

        show_auth.assert_awaited_once_with("auth_error", error="401")
        start_reauth.assert_called_once_with(coordinator.hass)

    def test_check_mqtt_disconnect_notification_schedules_task(self, coordinator):
        coordinator._mqtt_enabled = True
        coordinator._mqtt_connected = False
        coordinator._mqtt_disconnect_notified = False
        coordinator._mqtt_disconnect_time = monotonic() - (
            MQTT_DISCONNECT_NOTIFY_THRESHOLD + 10
        )
        coordinator.hass.async_create_task = MagicMock()

        coordinator._check_mqtt_disconnect_notification()

        assert coordinator._mqtt_disconnect_notified is True
        coordinator.hass.async_create_task.assert_called_once()
