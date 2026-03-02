"""Tests for Lipro data update coordinator.

These tests instantiate a real LiproDataUpdateCoordinator with mocked
dependencies and exercise its public and internal methods directly.
"""

from __future__ import annotations

import asyncio
from collections import deque
from datetime import timedelta
import logging
from time import monotonic
from types import SimpleNamespace
from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from pytest_homeassistant_custom_component.common import MockConfigEntry

from custom_components.lipro.const import (
    CONF_DEBUG_MODE,
    CONF_ENABLE_POWER_MONITORING,
    CONF_MQTT_ENABLED,
    CONF_POWER_QUERY_INTERVAL,
    CONF_ROOM_AREA_SYNC_FORCE,
    CONF_SCAN_INTERVAL,
    DEFAULT_SCAN_INTERVAL,
    DOMAIN,
    MAX_MQTT_CACHE_SIZE,
    MQTT_DISCONNECT_NOTIFY_THRESHOLD,
)
from custom_components.lipro.const.api import MAX_DEVICES_PER_QUERY
from custom_components.lipro.const.config import CONF_COMMAND_RESULT_VERIFY
from custom_components.lipro.core.api import (
    LiproApiError,
    LiproAuthError,
    LiproConnectionError,
    LiproRefreshTokenExpiredError,
)
from custom_components.lipro.core.device import LiproDevice
from homeassistant.exceptions import ConfigEntryAuthFailed
from homeassistant.helpers.issue_registry import IssueSeverity
from homeassistant.helpers.update_coordinator import UpdateFailed

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

    def test_get_device_by_id_legacy_direct_write_supports_case_and_strip(
        self, coordinator
    ):
        """Legacy direct writes to _device_by_id remain compatible."""
        dev = _make_device(serial="mesh_group_10002", is_group=True)
        coordinator._device_by_id["GW_MixedCase_001"] = dev
        assert coordinator.get_device_by_id("  gw_mixedcase_001  ") is dev


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

    def test_apply_adapts_fan_gear_upper_bound(self, coordinator):
        """Observed fanGear should raise unknown max_fan_gear bounds."""
        fan = LiproDevice(
            device_number=1,
            serial="mesh_group_10001",
            name="Fan Light",
            device_type=4,
            iot_name="unknown_model",
            physical_model="fanLight",
            properties={"fanGear": "1"},
        )
        assert fan.max_fan_gear == 6

        coordinator._apply_properties_update(
            fan,
            {"fanGear": "10"},
            apply_protection=False,
        )

        assert fan.max_fan_gear == 10
        assert fan.fan_speed_range == (1, 10)
        assert fan.fan_gear == 10

    def test_apply_does_not_shrink_fan_gear_upper_bound(self, coordinator):
        """Lower runtime fanGear values must not reduce learned upper-bound."""
        fan = LiproDevice(
            device_number=1,
            serial="mesh_group_10001",
            name="Fan Light",
            device_type=4,
            iot_name="21F1",
            physical_model="fanLight",
            properties={"fanGear": "10"},
            max_fan_gear=10,
        )

        coordinator._apply_properties_update(
            fan,
            {"fanGear": "5"},
            apply_protection=False,
        )

        assert fan.max_fan_gear == 10
        assert fan.fan_gear == 5

    def test_apply_ignores_invalid_fan_gear_values(self, coordinator):
        """Malformed fanGear values should not mutate capability bounds."""
        fan = LiproDevice(
            device_number=1,
            serial="mesh_group_10001",
            name="Fan Light",
            device_type=4,
            iot_name="unknown_model",
            physical_model="fanLight",
            properties={"fanGear": "1"},
        )

        coordinator._apply_properties_update(
            fan,
            {"fanGear": "not-a-number"},
            apply_protection=False,
        )
        assert fan.max_fan_gear == 6

    def test_apply_filters_stale_values_while_command_pending(self, coordinator):
        """Pending command keys should ignore stale mismatched values."""
        from custom_components.lipro.core.coordinator import _PendingCommandExpectation

        dev = _make_device(serial="dev1", properties={"brightness": "10"})
        coordinator._pending_command_expectations["dev1"] = _PendingCommandExpectation(
            sent_at=monotonic(),
            expected={"brightness": "60"},
        )

        coordinator._apply_properties_update(
            dev,
            {"brightness": "30", "powerState": "1"},
            apply_protection=True,
        )

        # stale brightness is filtered, unrelated key still updates
        assert dev.properties["brightness"] == "10"
        assert dev.properties["powerState"] == "1"

    def test_apply_confirms_pending_command_and_learns_latency(self, coordinator):
        """Matching update confirms expectation and updates adaptive latency."""
        from custom_components.lipro.core.coordinator import _PendingCommandExpectation

        dev = _make_device(serial="dev1", properties={"brightness": "10"})
        coordinator._pending_command_expectations["dev1"] = _PendingCommandExpectation(
            sent_at=monotonic() - 2.0,
            expected={"brightness": "60"},
        )

        coordinator._apply_properties_update(
            dev,
            {"brightness": "60"},
            apply_protection=True,
        )

        assert "dev1" not in coordinator._pending_command_expectations
        assert 1.5 <= coordinator._device_state_latency_seconds["dev1"] <= 8.0

    def test_apply_prunes_expired_pending_expectation(self, coordinator):
        """Expired pending expectation should be dropped before filtering."""
        from custom_components.lipro.core.coordinator import _PendingCommandExpectation

        dev = _make_device(serial="dev1", properties={"brightness": "10"})
        coordinator._pending_command_expectations["dev1"] = _PendingCommandExpectation(
            sent_at=monotonic() - 30.0,
            expected={"brightness": "60"},
        )

        coordinator._apply_properties_update(
            dev,
            {"brightness": "30"},
            apply_protection=True,
        )

        assert "dev1" not in coordinator._pending_command_expectations
        assert dev.properties["brightness"] == "30"

    def test_apply_properties_update_logs_do_not_leak_property_values(
        self, coordinator, caplog
    ):
        dev = _make_device(serial="dev1", name="Safe Device", properties={})
        secret_value = "raw-secret-value-123"

        with caplog.at_level(
            logging.DEBUG,
            logger="custom_components.lipro.core.coordinator",
        ):
            coordinator._apply_properties_update(
                dev,
                {"apiToken": secret_value},
                apply_protection=False,
            )

        assert any("Updated" in rec.getMessage() for rec in caplog.records)
        assert secret_value not in caplog.text

    def test_track_command_expectation_drops_empty_expected(self, coordinator):
        coordinator._track_command_expectation(
            "dev1",
            "CHANGE_STATE",
            [{"value": "1"}],
        )

        assert "dev1" not in coordinator._pending_command_expectations

    def test_observe_command_confirmation_prunes_expired(self, coordinator):
        from custom_components.lipro.core.coordinator import _PendingCommandExpectation

        coordinator._pending_command_expectations["dev1"] = _PendingCommandExpectation(
            sent_at=monotonic() - 30.0,
            expected={"brightness": "60"},
        )

        coordinator._observe_command_confirmation("dev1", {"brightness": "60"})

        assert "dev1" not in coordinator._pending_command_expectations

    def test_update_state_latency_uses_ewma_for_existing_device(self, coordinator):
        coordinator._device_state_latency_seconds["dev1"] = 4.0

        coordinator._update_state_latency("dev1", observed_latency=6.0)

        assert coordinator._device_state_latency_seconds["dev1"] == pytest.approx(4.7)


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

    def test_on_mqtt_connect_dismisses_disconnect_issue(self, coordinator):
        with patch(
            "custom_components.lipro.core.coordinator.async_delete_issue"
        ) as delete_issue:
            coordinator._on_mqtt_connect()

        delete_issue.assert_called_once_with(
            coordinator.hass, DOMAIN, "mqtt_disconnected"
        )

    def test_on_mqtt_disconnect_records_time_once(self, coordinator):
        coordinator._mqtt_disconnect_time = None
        coordinator._on_mqtt_disconnect()
        first_time = coordinator._mqtt_disconnect_time

        coordinator._on_mqtt_disconnect()
        assert coordinator._mqtt_disconnect_time == first_time

    def test_default_base_scan_interval(self, coordinator):
        assert coordinator._base_scan_interval == DEFAULT_SCAN_INTERVAL

    def test_base_scan_interval_invalid_option_falls_back_to_default(self, coordinator):
        """Corrupted persisted scan_interval should not raise."""
        coordinator.config_entry = SimpleNamespace(
            options={CONF_SCAN_INTERVAL: "not-a-number"}
        )
        assert coordinator._base_scan_interval == DEFAULT_SCAN_INTERVAL

    def test_base_scan_interval_without_config_entry_returns_default(self, coordinator):
        coordinator.config_entry = None
        assert coordinator._base_scan_interval == DEFAULT_SCAN_INTERVAL


class TestCoordinatorOptionsHardening:
    """Test defensive option coercion for malformed persisted values."""

    def test_load_options_coerces_string_booleans(self, coordinator):
        coordinator.config_entry = SimpleNamespace(
            options={
                CONF_MQTT_ENABLED: "false",
                CONF_ENABLE_POWER_MONITORING: "0",
                CONF_DEBUG_MODE: "true",
                CONF_ROOM_AREA_SYNC_FORCE: "1",
                CONF_COMMAND_RESULT_VERIFY: "true",
            }
        )

        coordinator._load_options()

        assert coordinator._mqtt_enabled is False
        assert coordinator._power_monitoring_enabled is False
        assert coordinator._debug_mode is True
        assert coordinator._room_area_sync_force is True
        assert coordinator._command_result_verify is True

    def test_should_query_power_handles_invalid_interval_option(self, coordinator):
        coordinator.config_entry = SimpleNamespace(
            options={CONF_POWER_QUERY_INTERVAL: "oops"}
        )
        coordinator._load_options()
        coordinator._last_power_query_time = monotonic()

        # Should not raise TypeError when interval option is malformed.
        assert coordinator._should_query_power() is False


# ===========================================================================
# 7. Device-list refresh policy
# ===========================================================================


class TestCoordinatorDeviceListRefreshPolicy:
    """Test periodic full device-list refresh decisions."""

    def test_should_refresh_when_no_devices(self, coordinator):
        coordinator._devices = {}
        coordinator._force_device_refresh = False

        assert coordinator._should_refresh_device_list() is True

    def test_should_refresh_when_force_flag_is_set(self, coordinator):
        coordinator._devices = {"dev1": _make_device(serial="dev1")}
        coordinator._force_device_refresh = True

        assert coordinator._should_refresh_device_list() is True

    def test_should_not_refresh_within_interval(self, coordinator):
        coordinator._devices = {"dev1": _make_device(serial="dev1")}
        coordinator._force_device_refresh = False
        coordinator._last_device_refresh_at = 100.0

        with patch(
            "custom_components.lipro.core.coordinator.monotonic", return_value=150.0
        ):
            assert coordinator._should_refresh_device_list() is False

    def test_should_refresh_after_interval(self, coordinator):
        coordinator._devices = {"dev1": _make_device(serial="dev1")}
        coordinator._force_device_refresh = False
        coordinator._last_device_refresh_at = 100.0

        with patch(
            "custom_components.lipro.core.coordinator.monotonic", return_value=1000.0
        ):
            assert coordinator._should_refresh_device_list() is True

    def test_schedule_reload_for_added_devices(self, coordinator):
        coordinator._devices = {
            "dev1": _make_device(serial="dev1"),
            "dev2": _make_device(serial="dev2"),
        }
        scheduled = []

        def _create_task(coro):
            scheduled.append(coro)
            coro.close()
            task = MagicMock()
            task.done.return_value = True
            return task

        coordinator.hass.async_create_task = _create_task
        coordinator._schedule_reload_for_added_devices({"dev1"})

        assert len(scheduled) == 1

    def test_schedule_reload_ignores_first_baseline_fetch(self, coordinator):
        coordinator._devices = {"dev1": _make_device(serial="dev1")}
        coordinator.hass.async_create_task = MagicMock()

        coordinator._schedule_reload_for_added_devices(set())

        coordinator.hass.async_create_task.assert_not_called()

    def test_schedule_reload_ignores_removals_only(self, coordinator):
        coordinator._devices = {"dev1": _make_device(serial="dev1")}
        coordinator.hass.async_create_task = MagicMock()

        coordinator._schedule_reload_for_added_devices({"dev1", "dev2"})

        coordinator.hass.async_create_task.assert_not_called()


# ===========================================================================
# 8. MQTT cache cleanup
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
# 9. Send command
# ===========================================================================


class TestCoordinatorSendCommand:
    """Test async_send_command() dispatches to correct client method."""

    @pytest.mark.asyncio
    async def test_send_command_non_group(self, coordinator, mock_lipro_api_client):
        dev = _make_device(serial="dev1", is_group=False)
        result = await coordinator.async_send_command(dev, "turnOn")

        assert result is True
        mock_lipro_api_client.send_command.assert_awaited_once_with(
            "dev1", "turnOn", dev.device_type_hex, None, dev.iot_name
        )
        mock_lipro_api_client.send_group_command.assert_not_awaited()

    @pytest.mark.asyncio
    async def test_send_command_verify_enabled_queries_command_result(
        self, coordinator, mock_lipro_api_client
    ):
        dev = _make_device(serial="dev1", is_group=False)
        coordinator._command_result_verify = True
        mock_lipro_api_client.send_command.return_value = {
            "pushSuccess": True,
            "msgSn": "682550445474476112",
        }
        mock_lipro_api_client.query_command_result = AsyncMock(
            return_value={"success": True}
        )

        result = await coordinator.async_send_command(dev, "turnOn")

        assert result is True
        mock_lipro_api_client.query_command_result.assert_awaited_once_with(
            msg_sn="682550445474476112",
            device_id="dev1",
            device_type=dev.device_type_hex,
        )

    @pytest.mark.asyncio
    async def test_send_command_verify_enabled_missing_msgsn_returns_false(
        self, coordinator, mock_lipro_api_client
    ):
        dev = _make_device(serial="dev1", is_group=False)
        coordinator._command_result_verify = True
        mock_lipro_api_client.send_command.return_value = {"pushSuccess": True}
        mock_lipro_api_client.query_command_result = AsyncMock()

        result = await coordinator.async_send_command(dev, "turnOn")

        assert result is False
        failure = coordinator.last_command_failure
        assert isinstance(failure, dict)
        assert failure["reason"] == "command_result_unconfirmed"
        assert failure["code"] == "command_result_missing_msgsn"
        assert failure["route"] == "device_direct"
        assert failure["device_id"] == "dev1"
        assert failure["command"] == "turnOn"
        mock_lipro_api_client.query_command_result.assert_not_awaited()

    @pytest.mark.asyncio
    async def test_send_command_verify_enabled_unconfirmed_returns_false(
        self, coordinator, mock_lipro_api_client
    ):
        dev = _make_device(serial="dev1", is_group=False)
        coordinator._command_result_verify = True
        mock_lipro_api_client.send_command.return_value = {
            "pushSuccess": True,
            "msgSn": "682550445474476112",
        }
        mock_lipro_api_client.query_command_result = AsyncMock(
            return_value={"status": "pending"}
        )

        with patch(
            "custom_components.lipro.core.coordinator.asyncio.sleep", new=AsyncMock()
        ):
            result = await coordinator.async_send_command(dev, "turnOn")

        assert result is False
        failure = coordinator.last_command_failure
        assert isinstance(failure, dict)
        assert failure["reason"] == "command_result_unconfirmed"
        assert failure["code"] == "command_result_unconfirmed"
        assert failure["route"] == "device_direct"
        assert failure["msg_sn"] == "682550445474476112"
        assert failure["device_id"] == "dev1"
        assert mock_lipro_api_client.query_command_result.await_count == 3

    @pytest.mark.asyncio
    async def test_send_command_group(self, coordinator, mock_lipro_api_client):
        dev = _make_device(serial="mesh_group_10001", is_group=True)
        props = [{"key": "brightness", "value": "80"}]
        result = await coordinator.async_send_command(dev, "setBrightness", props)

        assert result is True
        mock_lipro_api_client.send_group_command.assert_awaited_once_with(
            "mesh_group_10001",
            "setBrightness",
            dev.device_type_hex,
            props,
            dev.iot_name,
        )
        mock_lipro_api_client.send_command.assert_not_awaited()

    @pytest.mark.asyncio
    async def test_send_command_group_change_state_power_on_normalized(
        self, coordinator, mock_lipro_api_client
    ):
        dev = _make_device(serial="mesh_group_10001", is_group=True)
        result = await coordinator.async_send_command(
            dev,
            "CHANGE_STATE",
            [{"key": "powerState", "value": "1"}],
        )

        assert result is True
        mock_lipro_api_client.send_group_command.assert_awaited_once_with(
            "mesh_group_10001",
            "POWER_ON",
            dev.device_type_hex,
            None,
            dev.iot_name,
        )

    @pytest.mark.asyncio
    async def test_send_command_group_change_state_power_off_normalized(
        self, coordinator, mock_lipro_api_client
    ):
        dev = _make_device(serial="mesh_group_10001", is_group=True)
        result = await coordinator.async_send_command(
            dev,
            "CHANGE_STATE",
            [{"key": "powerState", "value": "0"}],
        )

        assert result is True
        mock_lipro_api_client.send_group_command.assert_awaited_once_with(
            "mesh_group_10001",
            "POWER_OFF",
            dev.device_type_hex,
            None,
            dev.iot_name,
        )

    @pytest.mark.asyncio
    async def test_send_command_group_change_state_without_power_keeps_original(
        self, coordinator, mock_lipro_api_client
    ):
        dev = _make_device(serial="mesh_group_10001", is_group=True)
        props = [{"key": "brightness", "value": "80"}]
        result = await coordinator.async_send_command(
            dev,
            "CHANGE_STATE",
            props,
        )

        assert result is True
        mock_lipro_api_client.send_group_command.assert_awaited_once_with(
            "mesh_group_10001",
            "CHANGE_STATE",
            dev.device_type_hex,
            props,
            dev.iot_name,
        )

    @pytest.mark.asyncio
    async def test_send_command_group_change_state_power_and_brightness_keeps_original(
        self, coordinator, mock_lipro_api_client
    ):
        """Mixed property updates must not be collapsed to POWER_ON/OFF."""
        dev = _make_device(serial="mesh_group_10001", is_group=True)
        props = [
            {"key": "powerState", "value": "1"},
            {"key": "brightness", "value": "80"},
        ]
        result = await coordinator.async_send_command(
            dev,
            "CHANGE_STATE",
            props,
        )

        assert result is True
        mock_lipro_api_client.send_group_command.assert_awaited_once_with(
            "mesh_group_10001",
            "CHANGE_STATE",
            dev.device_type_hex,
            props,
            dev.iot_name,
        )

    @pytest.mark.asyncio
    async def test_send_command_group_error_non_gateway_fallback_returns_false(
        self, coordinator, mock_lipro_api_client
    ):
        dev = _make_device(serial="mesh_group_10001", is_group=True)
        dev.extra_data["group_member_ids"] = ["03ab5ccd7c654321"]
        dev.extra_data["group_member_count"] = 1
        fallback_id = "03ab5ccd7c123456"
        mock_lipro_api_client.send_group_command.side_effect = LiproApiError(
            "group failed", code=140003
        )

        result = await coordinator.async_send_command(
            dev,
            "POWER_ON",
            fallback_device_id=fallback_id,
        )

        assert result is False
        mock_lipro_api_client.send_group_command.assert_awaited_once_with(
            "mesh_group_10001",
            "POWER_ON",
            dev.device_type_hex,
            None,
            dev.iot_name,
        )
        mock_lipro_api_client.send_command.assert_not_awaited()

    @pytest.mark.asyncio
    async def test_send_command_group_error_single_member_fallback_succeeds(
        self, coordinator, mock_lipro_api_client
    ):
        dev = _make_device(serial="mesh_group_10001", is_group=True)
        member_id = "03ab5ccd7c123456"
        dev.extra_data["group_member_ids"] = [member_id]
        dev.extra_data["group_member_count"] = 1
        mock_lipro_api_client.send_group_command.side_effect = LiproApiError(
            "group failed", code=140003
        )
        mock_lipro_api_client.send_command.return_value = {"pushSuccess": True}

        result = await coordinator.async_send_command(
            dev,
            "POWER_ON",
            fallback_device_id=member_id,
        )

        assert result is True
        mock_lipro_api_client.send_group_command.assert_awaited_once_with(
            "mesh_group_10001",
            "POWER_ON",
            dev.device_type_hex,
            None,
            dev.iot_name,
        )
        mock_lipro_api_client.send_command.assert_awaited_once_with(
            member_id,
            "POWER_ON",
            dev.device_type_hex,
            None,
            dev.iot_name,
        )

    @pytest.mark.asyncio
    async def test_send_command_group_push_fail_multi_member_fallback_ignored(
        self, coordinator, mock_lipro_api_client
    ):
        dev = _make_device(serial="mesh_group_10001", is_group=True)
        dev.extra_data["group_member_ids"] = [
            "03ab5ccd7c123456",
            "03ab5ccd7c999999",
        ]
        dev.extra_data["group_member_count"] = 2
        mock_lipro_api_client.send_group_command.return_value = {"pushSuccess": False}

        result = await coordinator.async_send_command(
            dev,
            "POWER_ON",
            fallback_device_id="03AB5CCD7C123456",
        )

        assert result is False
        mock_lipro_api_client.send_group_command.assert_awaited_once()
        mock_lipro_api_client.send_command.assert_not_awaited()

    @pytest.mark.asyncio
    async def test_send_command_group_push_fail_single_member_fallback_succeeds(
        self, coordinator, mock_lipro_api_client
    ):
        dev = _make_device(serial="mesh_group_10001", is_group=True)
        dev.extra_data["group_member_ids"] = ["03ab5ccd7c123456"]
        dev.extra_data["group_member_count"] = 1
        mock_lipro_api_client.send_group_command.return_value = {"pushSuccess": False}
        mock_lipro_api_client.send_command.return_value = {"pushSuccess": True}

        result = await coordinator.async_send_command(
            dev,
            "POWER_ON",
            fallback_device_id="03AB5CCD7C123456",
        )

        assert result is True
        mock_lipro_api_client.send_group_command.assert_awaited_once()
        mock_lipro_api_client.send_command.assert_awaited_once_with(
            "03ab5ccd7c123456",
            "POWER_ON",
            dev.device_type_hex,
            None,
            dev.iot_name,
        )

    @pytest.mark.asyncio
    async def test_send_command_group_error_without_valid_member_fallback_returns_false(
        self, coordinator, mock_lipro_api_client
    ):
        dev = _make_device(serial="mesh_group_10001", is_group=True)
        mock_lipro_api_client.send_group_command.side_effect = LiproApiError(
            "group failed", code=140003
        )

        result = await coordinator.async_send_command(
            dev,
            "POWER_ON",
            fallback_device_id="mesh_group_10001",
        )

        assert result is False
        mock_lipro_api_client.send_group_command.assert_awaited_once()
        mock_lipro_api_client.send_command.assert_not_awaited()

    @pytest.mark.asyncio
    async def test_send_command_group_fallback_under_mqtt_disconnect_and_stale_reconcile(
        self, coordinator, mock_lipro_api_client
    ):
        """MQTT disconnect + fallback send + stale cleanup should work together."""
        from custom_components.lipro.core.coordinator import _PendingCommandExpectation

        member_id = "03ab5ccd7c123456"
        dev = _make_device(serial="mesh_group_10001", is_group=True)
        dev.extra_data["group_member_ids"] = [member_id]
        dev.extra_data["group_member_count"] = 1
        coordinator._devices = {dev.serial: dev}

        coordinator._debug_mode = True
        coordinator._mqtt_connected = True
        coordinator._on_mqtt_disconnect()
        coordinator._pending_command_expectations["03ab5ccd7cdead"] = (
            _PendingCommandExpectation(
                sent_at=monotonic(),
                expected={"powerState": "1"},
            )
        )

        mock_lipro_api_client.send_group_command.side_effect = LiproApiError(
            "group failed", code=140003
        )
        mock_lipro_api_client.send_command.return_value = {"pushSuccess": True}

        scheduled: list[object] = []

        def _create_task(coro):
            scheduled.append(coro)
            coro.close()
            task = MagicMock()
            task.done.return_value = True
            return task

        with patch.object(
            coordinator.hass, "async_create_task", side_effect=_create_task
        ):
            result = await coordinator.async_send_command(
                dev,
                "POWER_ON",
                fallback_device_id=member_id,
            )

        assert result is True
        assert len(scheduled) == 2
        assert len(coordinator._command_traces) == 1
        assert coordinator._command_traces[0]["route"] == "group_error_fallback_member"
        mock_lipro_api_client.send_group_command.assert_awaited_once()
        mock_lipro_api_client.send_command.assert_awaited_once_with(
            member_id,
            "POWER_ON",
            dev.device_type_hex,
            None,
            dev.iot_name,
        )

        with patch.object(
            coordinator,
            "_async_remove_stale_devices",
            new=AsyncMock(),
        ) as remove_stale:
            for _ in range(3):
                await coordinator._reconcile_stale_devices(
                    {dev.serial, "03ab5ccd7cdead"},
                )

        remove_stale.assert_awaited_once_with({"03ab5ccd7cdead"})
        assert "03ab5ccd7cdead" not in coordinator._missing_device_cycles
        assert "03ab5ccd7cdead" not in coordinator._pending_command_expectations

    @pytest.mark.asyncio
    async def test_send_command_non_group_push_fail_returns_false(
        self, coordinator, mock_lipro_api_client
    ):
        dev = _make_device(serial="03ab5ccd7c123456", is_group=False)
        mock_lipro_api_client.send_command.return_value = {"pushSuccess": False}

        result = await coordinator.async_send_command(dev, "POWER_ON")

        assert result is False
        mock_lipro_api_client.send_command.assert_awaited_once()

    @pytest.mark.asyncio
    async def test_send_command_auth_error_returns_false(
        self, coordinator, mock_auth_manager
    ):
        mock_auth_manager.ensure_valid_token.side_effect = LiproAuthError("expired")
        dev = _make_device()
        with patch.object(coordinator, "_trigger_reauth", new=AsyncMock()) as reauth:
            result = await coordinator.async_send_command(dev, "turnOn")

        assert result is False
        reauth.assert_awaited_once_with("auth_error")

    @pytest.mark.asyncio
    async def test_send_command_refresh_token_expired_triggers_auth_expired(
        self, coordinator, mock_auth_manager
    ):
        mock_auth_manager.ensure_valid_token.side_effect = (
            LiproRefreshTokenExpiredError("refresh expired")
        )
        dev = _make_device()
        with patch.object(coordinator, "_trigger_reauth", new=AsyncMock()) as reauth:
            result = await coordinator.async_send_command(dev, "turnOn")

        assert result is False
        reauth.assert_awaited_once_with("auth_expired")

    @pytest.mark.asyncio
    async def test_send_command_generic_api_error_does_not_trigger_reauth(
        self, coordinator, mock_lipro_api_client
    ):
        dev = _make_device(serial="03ab5ccd7c123456", is_group=False)
        mock_lipro_api_client.send_command.side_effect = LiproApiError("api down")
        with patch.object(coordinator, "_trigger_reauth", new=AsyncMock()) as reauth:
            result = await coordinator.async_send_command(dev, "POWER_ON")

        assert result is False
        reauth.assert_not_awaited()

    @pytest.mark.asyncio
    async def test_send_command_clears_auth_issues_on_success(
        self, coordinator, mock_lipro_api_client
    ):
        dev = _make_device(serial="dev1", is_group=False)

        with patch(
            "custom_components.lipro.core.coordinator.async_delete_issue"
        ) as delete_issue:
            result = await coordinator.async_send_command(dev, "turnOn")

        assert result is True
        delete_issue.assert_any_call(coordinator.hass, DOMAIN, "auth_expired")
        delete_issue.assert_any_call(coordinator.hass, DOMAIN, "auth_error")
        mock_lipro_api_client.send_command.assert_awaited_once_with(
            "dev1", "turnOn", dev.device_type_hex, None, dev.iot_name
        )

    @pytest.mark.asyncio
    async def test_send_command_schedules_post_refresh(
        self, coordinator, mock_lipro_api_client
    ):
        dev = _make_device(serial="dev1", is_group=False)
        with patch.object(coordinator, "_schedule_post_command_refresh") as schedule:
            result = await coordinator.async_send_command(dev, "turnOn")

        assert result is True
        schedule.assert_called_once_with(skip_immediate=False, device_serial="dev1")

    @pytest.mark.asyncio
    async def test_send_command_brightness_change_schedules_delayed_only_refresh(
        self, coordinator, mock_lipro_api_client
    ):
        """Brightness-only CHANGE_STATE should skip immediate refresh."""
        dev = _make_device(serial="dev1", is_group=False)
        with patch.object(coordinator, "_schedule_post_command_refresh") as schedule:
            result = await coordinator.async_send_command(
                dev,
                "CHANGE_STATE",
                [{"key": "brightness", "value": "60"}],
            )

        assert result is True
        schedule.assert_called_once_with(skip_immediate=True, device_serial="dev1")

    @pytest.mark.asyncio
    async def test_send_command_fan_gear_change_schedules_delayed_only_refresh(
        self, coordinator, mock_lipro_api_client
    ):
        """fanGear-only CHANGE_STATE should skip immediate refresh."""
        dev = _make_device(serial="dev1", is_group=False)
        with patch.object(coordinator, "_schedule_post_command_refresh") as schedule:
            result = await coordinator.async_send_command(
                dev,
                "CHANGE_STATE",
                [{"key": "fanGear", "value": "3"}],
            )

        assert result is True
        schedule.assert_called_once_with(skip_immediate=True, device_serial="dev1")

    @pytest.mark.asyncio
    async def test_send_command_position_change_schedules_delayed_only_refresh(
        self, coordinator, mock_lipro_api_client
    ):
        """position-only CHANGE_STATE should skip immediate refresh."""
        dev = _make_device(serial="dev1", is_group=False)
        with patch.object(coordinator, "_schedule_post_command_refresh") as schedule:
            result = await coordinator.async_send_command(
                dev,
                "CHANGE_STATE",
                [{"key": "position", "value": "20"}],
            )

        assert result is True
        schedule.assert_called_once_with(skip_immediate=True, device_serial="dev1")

    def test_schedule_post_command_refresh_without_mqtt(self, coordinator):
        coordinator._mqtt_connected = False
        scheduled = []

        def _create_task(coro):
            scheduled.append(coro)
            coro.close()
            task = MagicMock()
            task.done.return_value = True
            return task

        coordinator.hass.async_create_task = _create_task
        coordinator._schedule_post_command_refresh()

        assert len(scheduled) == 2

    def test_schedule_post_command_refresh_skip_immediate_without_mqtt(
        self, coordinator
    ):
        coordinator._mqtt_connected = False
        scheduled = []

        def _create_task(coro):
            scheduled.append(coro)
            coro.close()
            task = MagicMock()
            task.done.return_value = True
            return task

        coordinator.hass.async_create_task = _create_task
        coordinator._schedule_post_command_refresh(skip_immediate=True)

        assert len(scheduled) == 1

    def test_schedule_post_command_refresh_with_mqtt(self, coordinator):
        coordinator._mqtt_connected = True
        scheduled = []

        def _create_task(coro):
            scheduled.append(coro)
            coro.close()
            task = MagicMock()
            task.done.return_value = True
            return task

        coordinator.hass.async_create_task = _create_task
        coordinator._schedule_post_command_refresh()

        assert len(scheduled) == 1

    def test_schedule_post_command_refresh_skip_immediate_with_mqtt(self, coordinator):
        coordinator._mqtt_connected = True
        scheduled = []

        def _create_task(coro):
            scheduled.append(coro)
            coro.close()
            task = MagicMock()
            task.done.return_value = True
            return task

        coordinator.hass.async_create_task = _create_task
        coordinator._schedule_post_command_refresh(skip_immediate=True)

        assert len(scheduled) == 0

    def test_schedule_post_command_refresh_with_mqtt_and_pending_expectation(
        self, coordinator
    ):
        from custom_components.lipro.core.coordinator import _PendingCommandExpectation

        coordinator._mqtt_connected = True
        coordinator._pending_command_expectations["dev1"] = _PendingCommandExpectation(
            sent_at=monotonic(),
            expected={"brightness": "50"},
        )
        scheduled = []

        def _create_task(coro):
            scheduled.append(coro)
            coro.close()
            task = MagicMock()
            task.done.return_value = True
            return task

        coordinator.hass.async_create_task = _create_task
        coordinator._schedule_post_command_refresh(
            skip_immediate=True,
            device_serial="dev1",
        )

        # MQTT connected, but pending command keeps one delayed fallback refresh.
        assert len(scheduled) == 1

    def test_schedule_post_command_refresh_same_device_cancels_previous_task(
        self, coordinator
    ):
        coordinator._mqtt_connected = False
        previous = MagicMock()
        previous.done.return_value = False
        coordinator._post_command_refresh_tasks["dev1"] = previous

        def _create_task(coro):
            coro.close()
            task = MagicMock()
            task.done.return_value = True
            return task

        coordinator.hass.async_create_task = _create_task
        coordinator._schedule_post_command_refresh(
            skip_immediate=True,
            device_serial="dev1",
        )

        previous.cancel.assert_called_once()

    def test_schedule_post_command_refresh_different_devices_do_not_cancel(
        self, coordinator
    ):
        coordinator._mqtt_connected = False
        previous = MagicMock()
        previous.done.return_value = False
        coordinator._post_command_refresh_tasks["dev1"] = previous

        def _create_task(coro):
            coro.close()
            task = MagicMock()
            task.done.return_value = True
            return task

        coordinator.hass.async_create_task = _create_task
        coordinator._schedule_post_command_refresh(
            skip_immediate=True,
            device_serial="dev2",
        )

        previous.cancel.assert_not_called()

    def test_get_adaptive_post_refresh_delay_uses_learned_latency(self, coordinator):
        coordinator._device_state_latency_seconds["dev1"] = 4.0
        assert coordinator._get_adaptive_post_refresh_delay("dev1") == pytest.approx(
            4.6
        )

    def test_prune_runtime_state_for_devices(self, coordinator):
        from custom_components.lipro.core.coordinator import _PendingCommandExpectation

        coordinator._pending_command_expectations = {
            "active": _PendingCommandExpectation(
                sent_at=monotonic(),
                expected={"brightness": "50"},
            ),
            "stale": _PendingCommandExpectation(
                sent_at=monotonic(),
                expected={"brightness": "10"},
            ),
        }
        coordinator._device_state_latency_seconds = {"active": 2.0, "stale": 5.0}

        coordinator._prune_runtime_state_for_devices({"active"})

        assert set(coordinator._pending_command_expectations) == {"active"}
        assert set(coordinator._device_state_latency_seconds) == {"active"}

    def test_adapt_state_batch_size_down_on_high_latency(self, coordinator):
        coordinator._state_status_batch_size = 64
        coordinator._state_batch_metrics = deque(
            [(64, 4.5, 0)] * 6,
            maxlen=24,
        )

        coordinator._adapt_state_batch_size()

        assert coordinator._state_status_batch_size == 56

    def test_adapt_state_batch_size_up_on_low_latency_and_no_fallback(self, coordinator):
        coordinator._state_status_batch_size = 32
        coordinator._state_batch_metrics = deque(
            [(32, 0.6, 0)] * 6,
            maxlen=24,
        )

        coordinator._adapt_state_batch_size()

        assert coordinator._state_status_batch_size == 40

    @pytest.mark.asyncio
    async def test_query_device_status_wires_batch_metric_and_adaptation(
        self, coordinator, mock_lipro_api_client
    ):
        coordinator._iot_ids_to_query = ["dev1"]

        async def _query_device_status(_ids, **kwargs):
            kwargs["on_batch_metric"](24, 0.25, 0)
            return []

        mock_lipro_api_client.query_device_status.side_effect = _query_device_status
        with patch.object(coordinator, "_adapt_state_batch_size") as adapt:
            await coordinator._query_device_status()

        adapt.assert_called_once()
        assert coordinator._state_batch_metrics[-1] == (24, 0.25, 0)

    def test_adapt_connect_status_stale_window_by_skip_ratio(self, coordinator):
        from custom_components.lipro.core.coordinator import (
            _CONNECT_STATUS_SKIP_RATIO_WINDOW,
        )

        coordinator._connect_status_mqtt_stale_seconds = 180.0
        coordinator._connect_status_skip_history = deque(
            [False] * _CONNECT_STATUS_SKIP_RATIO_WINDOW,
            maxlen=_CONNECT_STATUS_SKIP_RATIO_WINDOW,
        )
        coordinator._adapt_connect_status_stale_window()
        assert coordinator._connect_status_mqtt_stale_seconds == 195.0

        coordinator._connect_status_skip_history = deque(
            [True] * _CONNECT_STATUS_SKIP_RATIO_WINDOW,
            maxlen=_CONNECT_STATUS_SKIP_RATIO_WINDOW,
        )
        coordinator._adapt_connect_status_stale_window()
        assert coordinator._connect_status_mqtt_stale_seconds == 180.0

    def test_resolve_connect_status_query_ids_records_skip_when_mqtt_is_fresh(
        self, coordinator
    ):
        coordinator._iot_ids_to_query = ["dev1"]
        coordinator._mqtt_enabled = True
        coordinator._mqtt_connected = True
        coordinator._force_connect_status_refresh = False
        coordinator._last_connect_status_query_time = 0.0
        coordinator._last_mqtt_connect_state_at["dev1"] = 1000.0

        with patch("custom_components.lipro.core.coordinator.monotonic", return_value=1000.0):
            ids = coordinator._resolve_connect_status_query_ids()

        assert ids == []
        assert coordinator._connect_status_skip_history[-1] is True

    def test_build_developer_report_disabled_mode_has_note(self, coordinator):
        with patch(
            "custom_components.lipro.core.coordinator.get_anonymous_share_manager"
        ) as mock_share:
            mock_share.return_value = MagicMock(pending_count=(0, 0))
            report = coordinator.build_developer_report()

        assert report["debug_mode_enabled"] is False
        assert report["recent_commands"] == []
        assert "note" in report
        assert report["entry_id"] != coordinator.config_entry.entry_id
        assert report["unique_id"] != coordinator.config_entry.unique_id
        assert "***" in report["entry_id"]
        assert "***" in report["unique_id"]
        assert "status_metrics" in report["runtime"]

    def test_load_options_debug_mode_has_no_global_logger_side_effect(self, coordinator):
        coordinator.hass.config_entries.async_update_entry(
            coordinator.config_entry,
            options={"debug_mode": True},
        )
        with patch("custom_components.lipro.core.coordinator.logging.getLogger") as get_logger:
            coordinator._load_options()

        assert coordinator._debug_mode is True
        get_logger.assert_not_called()

    @pytest.mark.asyncio
    async def test_send_command_records_trace_when_debug_mode_enabled(
        self, coordinator, mock_lipro_api_client
    ):
        coordinator._debug_mode = True
        dev = _make_device(serial="dev1", is_group=False)
        mock_lipro_api_client.send_command.return_value = {
            "pushSuccess": True,
            "msgSn": "trace-msg-sn",
            "pushTimestamp": 1739942400,
        }

        result = await coordinator.async_send_command(
            dev,
            "POWER_ON",
            [{"key": "powerState", "value": "1"}],
        )

        assert result is True
        assert len(coordinator._command_traces) == 1
        trace = coordinator._command_traces[0]
        assert trace["success"] is True
        assert trace["route"] == "device_direct"
        assert trace["requested_command"] == "POWER_ON"
        assert trace["push_success"] is True
        assert trace["response_msg_sn"] == "trace-msg-sn"
        assert trace["response_push_timestamp"] == 1739942400


# ===========================================================================
# 10. Missing coordinator behaviors
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
    async def test_async_setup_mqtt_missing_biz_id_returns_false(self, coordinator):
        with (
            patch.object(
                coordinator,
                "_resolve_mqtt_decrypted_credentials",
                new_callable=AsyncMock,
                return_value=("ak", "sk"),
            ),
            patch(
                "custom_components.lipro.core.coordinator.resolve_mqtt_biz_id",
                return_value=None,
            ),
        ):
            assert await coordinator.async_setup_mqtt() is False

    @pytest.mark.asyncio
    @pytest.mark.parametrize(
        "err",
        [LiproApiError("api boom"), ValueError("bad decrypt payload")],
    )
    async def test_async_setup_mqtt_setup_error_returns_false(self, coordinator, err):
        with patch.object(
            coordinator,
            "_resolve_mqtt_decrypted_credentials",
            new_callable=AsyncMock,
        ) as resolve:
            resolve.side_effect = err
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

    @pytest.mark.asyncio
    async def test_sync_mqtt_subscriptions_without_client_is_noop(self, coordinator):
        coordinator._mqtt_client = None
        coordinator._devices = {"dev_a": _make_device(serial="dev_a")}

        await coordinator._sync_mqtt_subscriptions()

    @pytest.mark.asyncio
    async def test_mqtt_setup_failure_blocks_reschedule_inside_backoff_window(
        self, coordinator
    ):
        coordinator._mqtt_enabled = True
        coordinator._mqtt_client = None
        coordinator._devices = {"dev1": _make_device(serial="dev1")}
        coordinator.async_setup_mqtt = AsyncMock(return_value=False)
        coordinator._mqtt_setup_in_progress = True

        with patch("custom_components.lipro.core.coordinator.monotonic", return_value=100.0):
            await coordinator._async_setup_mqtt_safe()

        scheduled: list[object] = []

        def _track(coro):
            scheduled.append(coro)
            coro.close()
            return MagicMock()

        coordinator._track_background_task = MagicMock(side_effect=_track)
        with patch("custom_components.lipro.core.coordinator.monotonic", return_value=100.5):
            coordinator._schedule_mqtt_setup_if_needed()

        assert coordinator._mqtt_setup_in_progress is False
        assert scheduled == []

    @pytest.mark.asyncio
    async def test_mqtt_setup_success_resets_backoff_and_allows_immediate_retry(
        self, coordinator
    ):
        coordinator._mqtt_enabled = True
        coordinator._mqtt_client = None
        coordinator._devices = {"dev1": _make_device(serial="dev1")}

        coordinator.async_setup_mqtt = AsyncMock(return_value=False)
        coordinator._mqtt_setup_in_progress = True
        with patch("custom_components.lipro.core.coordinator.monotonic", return_value=200.0):
            await coordinator._async_setup_mqtt_safe()

        coordinator.async_setup_mqtt = AsyncMock(return_value=True)
        coordinator._mqtt_setup_in_progress = True
        with patch("custom_components.lipro.core.coordinator.monotonic", return_value=201.0):
            await coordinator._async_setup_mqtt_safe()

        scheduled: list[object] = []

        def _track(coro):
            scheduled.append(coro)
            coro.close()
            return MagicMock()

        coordinator._track_background_task = MagicMock(side_effect=_track)
        with patch("custom_components.lipro.core.coordinator.monotonic", return_value=201.0):
            coordinator._schedule_mqtt_setup_if_needed()

        assert len(scheduled) == 1
        assert coordinator._mqtt_setup_in_progress is True


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
                "devices": [
                    {"deviceId": "03ab5ccd7c111111"},
                    {"deviceId": "03AB5CCD7C222222"},
                ],
                "properties": [{"key": "powerState", "value": "1"}],
            }
        ]

        await coordinator._query_group_status()

        assert group.properties["powerState"] == "1"
        assert coordinator._device_by_id["03ab5ccd7cgw"] is group
        assert coordinator._device_by_id["03ab5ccd7c111111"] is group
        assert coordinator.get_device_by_id("03AB5CCD7C222222") is group
        assert coordinator.get_device_by_id("03ab5ccd7c222222") is group
        assert group.extra_data["group_member_count"] == 2
        assert group.extra_data["group_member_ids"] == [
            "03ab5ccd7c111111",
            "03AB5CCD7C222222",
        ]

    @pytest.mark.asyncio
    async def test_query_group_status_replaces_stale_member_and_gateway_lookup_ids(
        self, coordinator, mock_lipro_api_client
    ):
        group = _make_device(serial="mesh_group_10001", is_group=True)
        coordinator._devices[group.serial] = group
        coordinator._group_ids_to_query = [group.serial]
        mock_lipro_api_client.query_mesh_group_status.side_effect = [
            [
                {
                    "groupId": "mesh_group_10001",
                    "gatewayDeviceId": "03ab5ccd7cgw_old",
                    "devices": [
                        {"deviceId": "03ab5ccd7cold111"},
                        {"deviceId": "03ab5ccd7cstay222"},
                    ],
                    "properties": [],
                }
            ],
            [
                {
                    "groupId": "mesh_group_10001",
                    "gatewayDeviceId": "03ab5ccd7cgw_new",
                    "devices": [
                        {"deviceId": "03ab5ccd7cstay222"},
                        {"deviceId": "03ab5ccd7cnew333"},
                    ],
                    "properties": [],
                }
            ],
        ]

        await coordinator._query_group_status()
        await coordinator._query_group_status()

        assert coordinator.get_device_by_id("03ab5ccd7cgw_old") is None
        assert coordinator.get_device_by_id("03ab5ccd7cold111") is None
        assert coordinator.get_device_by_id("03ab5ccd7cgw_new") is group
        assert coordinator.get_device_by_id("03ab5ccd7cstay222") is group
        assert coordinator.get_device_by_id("03ab5ccd7cnew333") is group
        assert group.extra_data["group_member_lookup_ids"] == [
            "03ab5ccd7cstay222",
            "03ab5ccd7cnew333",
        ]

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
    async def test_query_outlet_power_raises_auth_error(
        self, coordinator, mock_lipro_api_client
    ):
        outlet = _make_device(serial="out1", properties={"powerState": "1"})
        coordinator._devices[outlet.serial] = outlet
        coordinator._device_by_id[outlet.serial] = outlet
        coordinator._outlet_ids_to_query = [outlet.serial]
        mock_lipro_api_client.fetch_outlet_power_info.side_effect = LiproAuthError(
            "unauthorized"
        )

        with pytest.raises(LiproAuthError):
            await coordinator._query_outlet_power()

    @pytest.mark.asyncio
    async def test_query_outlet_power_raises_connection_error(
        self, coordinator, mock_lipro_api_client
    ):
        outlet = _make_device(serial="out1", properties={"powerState": "1"})
        coordinator._devices[outlet.serial] = outlet
        coordinator._device_by_id[outlet.serial] = outlet
        coordinator._outlet_ids_to_query = [outlet.serial]
        mock_lipro_api_client.fetch_outlet_power_info.side_effect = (
            LiproConnectionError("timeout")
        )

        with pytest.raises(LiproConnectionError):
            await coordinator._query_outlet_power()

    @pytest.mark.asyncio
    async def test_query_single_outlet_power_empty_payload_is_noop(
        self, coordinator, mock_lipro_api_client
    ):
        outlet = _make_device(serial="out1", properties={"powerState": "1"})
        coordinator._devices[outlet.serial] = outlet
        coordinator._device_by_id[outlet.serial] = outlet
        mock_lipro_api_client.fetch_outlet_power_info.return_value = {}

        await coordinator._query_single_outlet_power(outlet.serial)

        assert "power_info" not in outlet.extra_data

    @pytest.mark.asyncio
    async def test_query_single_outlet_power_non_reraise_api_error_is_swallowed(
        self, coordinator, mock_lipro_api_client
    ):
        mock_lipro_api_client.fetch_outlet_power_info.side_effect = LiproApiError(
            "payload invalid",
            100000,
        )

        await coordinator._query_single_outlet_power("out1")

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
    async def test_query_connect_status_without_iot_ids_is_noop(
        self, coordinator, mock_lipro_api_client
    ):
        coordinator._iot_ids_to_query = []

        await coordinator._query_connect_status()

        mock_lipro_api_client.query_connect_status.assert_not_awaited()

    @pytest.mark.asyncio
    async def test_update_device_status_queries_only_stale_connect_ids_with_mqtt(
        self, coordinator, mock_lipro_api_client
    ):
        dev_a = _make_device(serial="dev_a", properties={"connectState": "1"})
        dev_b = _make_device(serial="dev_b", properties={"connectState": "1"})
        coordinator._devices[dev_a.serial] = dev_a
        coordinator._devices[dev_b.serial] = dev_b
        coordinator._device_by_id[dev_a.serial] = dev_a
        coordinator._device_by_id[dev_b.serial] = dev_b
        coordinator._iot_ids_to_query = [dev_a.serial, dev_b.serial]
        coordinator._mqtt_enabled = True
        coordinator._mqtt_connected = True
        coordinator._force_connect_status_refresh = False
        coordinator._last_connect_status_query_time = monotonic() - 120
        coordinator._last_mqtt_connect_state_at[dev_a.serial] = monotonic()
        coordinator._last_mqtt_connect_state_at[dev_b.serial] = 0.0

        mock_lipro_api_client.query_device_status.return_value = []
        mock_lipro_api_client.query_connect_status.return_value = {dev_b.serial: False}

        await coordinator._update_device_status()

        mock_lipro_api_client.query_connect_status.assert_awaited_once_with(
            [dev_b.serial]
        )

    @pytest.mark.asyncio
    async def test_update_device_status_skips_connect_query_when_mqtt_is_fresh(
        self, coordinator, mock_lipro_api_client
    ):
        dev = _make_device(serial="dev1", properties={"connectState": "1"})
        coordinator._devices[dev.serial] = dev
        coordinator._device_by_id[dev.serial] = dev
        coordinator._iot_ids_to_query = [dev.serial]
        coordinator._mqtt_enabled = True
        coordinator._mqtt_connected = True
        coordinator._force_connect_status_refresh = False
        coordinator._last_connect_status_query_time = monotonic() - 120
        coordinator._last_mqtt_connect_state_at[dev.serial] = monotonic()

        mock_lipro_api_client.query_device_status.return_value = []

        await coordinator._update_device_status()

        mock_lipro_api_client.query_connect_status.assert_not_awaited()

    @pytest.mark.asyncio
    async def test_update_device_status_uses_degraded_connect_interval_when_mqtt_unstable(
        self, coordinator, mock_lipro_api_client
    ):
        dev = _make_device(serial="dev1", properties={"connectState": "1"})
        coordinator._devices[dev.serial] = dev
        coordinator._device_by_id[dev.serial] = dev
        coordinator._iot_ids_to_query = [dev.serial]
        coordinator._mqtt_enabled = True
        coordinator._mqtt_connected = False
        coordinator._mqtt_disconnect_time = monotonic() - 5.0
        coordinator._force_connect_status_refresh = False
        coordinator._last_connect_status_query_time = monotonic() - 30.0

        mock_lipro_api_client.query_device_status.return_value = []
        mock_lipro_api_client.query_connect_status.return_value = {dev.serial: True}

        await coordinator._update_device_status()

        mock_lipro_api_client.query_connect_status.assert_awaited_once_with(
            [dev.serial]
        )

    @pytest.mark.asyncio
    async def test_update_device_status_force_refresh_uses_priority_connect_id(
        self, coordinator, mock_lipro_api_client
    ):
        dev_a = _make_device(serial="dev_a", properties={"connectState": "1"})
        dev_b = _make_device(serial="dev_b", properties={"connectState": "1"})
        coordinator._devices[dev_a.serial] = dev_a
        coordinator._devices[dev_b.serial] = dev_b
        coordinator._device_by_id[dev_a.serial] = dev_a
        coordinator._device_by_id[dev_b.serial] = dev_b
        coordinator._iot_ids_to_query = [dev_a.serial, dev_b.serial]
        coordinator._mqtt_enabled = True
        coordinator._mqtt_connected = True
        coordinator._force_connect_status_refresh = True
        coordinator._connect_status_priority_ids = {dev_b.serial}

        mock_lipro_api_client.query_device_status.return_value = []
        mock_lipro_api_client.query_connect_status.return_value = {dev_b.serial: True}

        await coordinator._update_device_status()

        mock_lipro_api_client.query_connect_status.assert_awaited_once_with(
            [dev_b.serial]
        )
        assert dev_b.serial not in coordinator._connect_status_priority_ids

    @pytest.mark.asyncio
    async def test_update_device_status_force_refresh_keeps_priority_on_empty_connect_result(
        self, coordinator, mock_lipro_api_client
    ):
        dev_a = _make_device(serial="dev_a", properties={"connectState": "1"})
        dev_b = _make_device(serial="dev_b", properties={"connectState": "1"})
        coordinator._devices[dev_a.serial] = dev_a
        coordinator._devices[dev_b.serial] = dev_b
        coordinator._device_by_id[dev_a.serial] = dev_a
        coordinator._device_by_id[dev_b.serial] = dev_b
        coordinator._iot_ids_to_query = [dev_a.serial, dev_b.serial]
        coordinator._mqtt_enabled = True
        coordinator._mqtt_connected = True
        coordinator._force_connect_status_refresh = True
        coordinator._connect_status_priority_ids = {dev_b.serial}

        mock_lipro_api_client.query_device_status.return_value = []
        mock_lipro_api_client.query_connect_status.return_value = {}

        await coordinator._update_device_status()

        mock_lipro_api_client.query_connect_status.assert_awaited_once_with(
            [dev_b.serial]
        )
        assert dev_b.serial in coordinator._connect_status_priority_ids

    @pytest.mark.asyncio
    async def test_update_device_status_applies_connect_status_last(
        self, coordinator, mock_lipro_api_client
    ):
        """connectState should converge to realtime connect-status result."""
        dev = _make_device(serial="dev1", properties={"connectState": "1"})
        coordinator._devices[dev.serial] = dev
        coordinator._device_by_id[dev.serial] = dev
        coordinator._iot_ids_to_query = [dev.serial]

        async def delayed_device_status(_device_ids, **_kwargs):
            await asyncio.sleep(0.01)
            return [
                {
                    "deviceId": dev.serial,
                    "properties": [{"key": "connectState", "value": "0"}],
                }
            ]

        async def fast_connect_status(_device_ids):
            await asyncio.sleep(0)
            return {dev.serial: True}

        mock_lipro_api_client.query_device_status.side_effect = delayed_device_status
        mock_lipro_api_client.query_connect_status.side_effect = fast_connect_status

        await coordinator._update_device_status()

        assert dev.properties["connectState"] == "1"

    @pytest.mark.asyncio
    async def test_update_device_status_throttles_connect_status_queries(
        self, coordinator, mock_lipro_api_client
    ):
        dev = _make_device(serial="dev1", properties={"connectState": "1"})
        coordinator._devices[dev.serial] = dev
        coordinator._device_by_id[dev.serial] = dev
        coordinator._iot_ids_to_query = [dev.serial]
        mock_lipro_api_client.query_device_status.return_value = []
        mock_lipro_api_client.query_connect_status.return_value = {dev.serial: True}

        await coordinator._update_device_status()
        await coordinator._update_device_status()

        assert mock_lipro_api_client.query_connect_status.await_count == 1

    @pytest.mark.asyncio
    async def test_query_outlet_power_uses_dynamic_cycle_size_for_large_fleet(
        self, coordinator
    ):
        coordinator._outlet_ids_to_query = [f"out{i}" for i in range(100)]
        coordinator._query_single_outlet_power = AsyncMock()

        await coordinator._query_outlet_power()

        # 100 devices, target 4 cycles => ceil(100/4)=25 queries this cycle
        assert coordinator._query_single_outlet_power.await_count == 25

    def test_resolve_outlet_power_cycle_size_scales_with_device_count(self, coordinator):
        assert coordinator._resolve_outlet_power_cycle_size(0) == 0
        assert coordinator._resolve_outlet_power_cycle_size(8) == 8
        assert coordinator._resolve_outlet_power_cycle_size(10) == 10
        assert coordinator._resolve_outlet_power_cycle_size(100) == 25

    @pytest.mark.asyncio
    async def test_group_mqtt_online_variants_schedule_reconciliation(
        self, coordinator
    ):
        """Numeric/boolean connectState payloads should trigger group reconciliation."""
        group = _make_device(serial="mesh_group_10001", is_group=True, properties={})
        coordinator._devices[group.serial] = group
        coordinator._device_by_id[group.serial] = group
        coordinator.async_request_refresh = AsyncMock()

        created_tasks: list[asyncio.Task] = []

        def _capture_task(coro):
            task = asyncio.create_task(coro)
            created_tasks.append(task)
            return task

        with patch.object(
            coordinator.hass, "async_create_task", side_effect=_capture_task
        ):
            coordinator._on_mqtt_message(group.serial, {"connectState": 1})

        await asyncio.gather(*created_tasks)
        coordinator.async_request_refresh.assert_awaited_once()

    def test_apply_group_status_row_missing_group_id_is_ignored(self, coordinator):
        coordinator._apply_group_status_row({"properties": []})

    def test_apply_group_status_row_unknown_group_is_ignored(self, coordinator):
        coordinator._apply_group_status_row(
            {"groupId": "mesh_group_404", "properties": []}
        )

    @pytest.mark.asyncio
    async def test_async_remove_stale_devices(self, coordinator):
        device_entry = MagicMock(id="reg-id", name="Stale Device")
        registry = MagicMock()
        registry.async_get_device.return_value = device_entry

        with patch("custom_components.lipro.core.coordinator.dr.async_get") as dr_get:
            dr_get.return_value = registry
            await coordinator._async_remove_stale_devices({"03ab5ccd7cdead"})

        registry.async_remove_device.assert_called_once_with("reg-id")

    def test_sync_device_room_assignments_updates_area_when_cloud_room_renamed(
        self, coordinator
    ):
        previous = {
            "03ab5ccd7c111111": _make_device(serial="03ab5ccd7c111111", name="Lamp A")
        }
        previous["03ab5ccd7c111111"].room_name = "主卧"

        current = _make_device(serial="03ab5ccd7c111111", name="Lamp A")
        current.room_name = "主卧新"
        coordinator._devices = {"03ab5ccd7c111111": current}

        device_entry = MagicMock(id="dev-entry-1", area_id="area-old")
        device_registry = MagicMock()
        device_registry.async_get_device.return_value = device_entry

        area_old = SimpleNamespace(name="主卧")
        area_new = SimpleNamespace(id="area-new")
        area_registry = MagicMock()
        area_registry.async_get_area.return_value = area_old
        area_registry.async_get_or_create.return_value = area_new

        with (
            patch(
                "custom_components.lipro.core.coordinator.dr.async_get",
                return_value=device_registry,
            ),
            patch(
                "custom_components.lipro.core.coordinator.ar.async_get",
                return_value=area_registry,
            ),
        ):
            coordinator._sync_device_room_assignments(previous)

        device_registry.async_update_device.assert_called_once_with(
            "dev-entry-1",
            suggested_area="主卧新",
            area_id="area-new",
        )

    def test_sync_device_room_assignments_keeps_user_custom_area(self, coordinator):
        previous = {
            "03ab5ccd7c111111": _make_device(serial="03ab5ccd7c111111", name="Lamp A")
        }
        previous["03ab5ccd7c111111"].room_name = "主卧"

        current = _make_device(serial="03ab5ccd7c111111", name="Lamp A")
        current.room_name = "儿童房"
        coordinator._devices = {"03ab5ccd7c111111": current}

        device_entry = MagicMock(id="dev-entry-1", area_id="custom-area")
        device_registry = MagicMock()
        device_registry.async_get_device.return_value = device_entry

        area_registry = MagicMock()
        area_registry.async_get_area.return_value = SimpleNamespace(name="手动区域")

        with (
            patch(
                "custom_components.lipro.core.coordinator.dr.async_get",
                return_value=device_registry,
            ),
            patch(
                "custom_components.lipro.core.coordinator.ar.async_get",
                return_value=area_registry,
            ),
        ):
            coordinator._sync_device_room_assignments(previous)

        device_registry.async_update_device.assert_called_once_with(
            "dev-entry-1",
            suggested_area="儿童房",
        )

    def test_sync_device_room_assignments_force_sync_overrides_user_area(
        self, coordinator
    ):
        previous = {
            "03ab5ccd7c111111": _make_device(serial="03ab5ccd7c111111", name="Lamp A")
        }
        previous["03ab5ccd7c111111"].room_name = "主卧"

        current = _make_device(serial="03ab5ccd7c111111", name="Lamp A")
        current.room_name = "儿童房"
        coordinator._devices = {"03ab5ccd7c111111": current}
        coordinator._room_area_sync_force = True

        device_entry = MagicMock(id="dev-entry-1", area_id="custom-area")
        device_registry = MagicMock()
        device_registry.async_get_device.return_value = device_entry

        area_registry = MagicMock()
        area_registry.async_get_or_create.return_value = SimpleNamespace(id="area-kids")

        with (
            patch(
                "custom_components.lipro.core.coordinator.dr.async_get",
                return_value=device_registry,
            ),
            patch(
                "custom_components.lipro.core.coordinator.ar.async_get",
                return_value=area_registry,
            ),
        ):
            coordinator._sync_device_room_assignments(previous)

        device_registry.async_update_device.assert_called_once_with(
            "dev-entry-1",
            suggested_area="儿童房",
            area_id="area-kids",
        )

    def test_sync_device_room_assignments_clears_area_when_room_removed(
        self, coordinator
    ):
        previous = {
            "03ab5ccd7c111111": _make_device(serial="03ab5ccd7c111111", name="Lamp A")
        }
        previous["03ab5ccd7c111111"].room_name = "书房"

        current = _make_device(serial="03ab5ccd7c111111", name="Lamp A")
        current.room_name = " "
        coordinator._devices = {"03ab5ccd7c111111": current}

        device_entry = MagicMock(id="dev-entry-1", area_id="area-old")
        device_registry = MagicMock()
        device_registry.async_get_device.return_value = device_entry

        area_registry = MagicMock()
        area_registry.async_get_area.return_value = SimpleNamespace(name="书房")

        with (
            patch(
                "custom_components.lipro.core.coordinator.dr.async_get",
                return_value=device_registry,
            ),
            patch(
                "custom_components.lipro.core.coordinator.ar.async_get",
                return_value=area_registry,
            ),
        ):
            coordinator._sync_device_room_assignments(previous)

        device_registry.async_update_device.assert_called_once_with(
            "dev-entry-1",
            suggested_area=None,
            area_id=None,
        )

    @pytest.mark.asyncio
    async def test_trigger_reauth_sanitizes_placeholder_and_starts_reauth(
        self, coordinator
    ):
        raw_error = "raw-auth-secret-401"
        with (
            patch.object(
                coordinator, "_async_show_auth_notification", new_callable=AsyncMock
            ) as show_auth,
            patch.object(
                coordinator.config_entry, "async_start_reauth"
            ) as start_reauth,
        ):
            await coordinator._trigger_reauth("auth_error", error=raw_error)

        show_auth.assert_awaited_once()
        assert show_auth.await_args.args == ("auth_error",)
        placeholder_values = " ".join(
            str(value) for value in show_auth.await_args.kwargs.values()
        )
        assert raw_error not in placeholder_values
        assert show_auth.await_args.kwargs.get("error") == "AuthError"
        start_reauth.assert_called_once_with(coordinator.hass)

    @pytest.mark.asyncio
    async def test_raise_update_data_error_auth_path_hides_raw_error(
        self, coordinator
    ):
        raw_error = "AUTH_RAW_SECRET_123"
        with (
            patch.object(coordinator, "_trigger_reauth", new=AsyncMock()) as reauth,
            pytest.raises(ConfigEntryAuthFailed) as err_info,
        ):
            await coordinator._raise_update_data_error(LiproAuthError(raw_error))

        reauth.assert_awaited_once()
        assert reauth.await_args.args == ("auth_error",)
        placeholder_values = " ".join(
            str(value) for value in reauth.await_args.kwargs.values()
        )
        assert raw_error not in placeholder_values
        assert raw_error not in str(err_info.value)

    @pytest.mark.asyncio
    async def test_raise_update_data_error_refresh_token_path_hides_raw_error(
        self, coordinator
    ):
        raw_error = "REFRESH_RAW_SECRET_456"
        with (
            patch.object(coordinator, "_trigger_reauth", new=AsyncMock()) as reauth,
            pytest.raises(ConfigEntryAuthFailed) as err_info,
        ):
            await coordinator._raise_update_data_error(
                LiproRefreshTokenExpiredError(raw_error)
            )

        reauth.assert_awaited_once_with("auth_expired")
        assert raw_error not in str(err_info.value)

    @pytest.mark.asyncio
    @pytest.mark.parametrize(
        "err",
        [
            LiproConnectionError("CONNECTION_RAW_SECRET_789"),
            LiproApiError("API_RAW_SECRET_999"),
        ],
    )
    async def test_raise_update_data_error_non_auth_paths_hide_raw_error(
        self, coordinator, err
    ):
        with (
            patch.object(coordinator, "_trigger_reauth", new=AsyncMock()) as reauth,
            pytest.raises(UpdateFailed) as err_info,
        ):
            await coordinator._raise_update_data_error(err)

        reauth.assert_not_awaited()
        assert "RAW_SECRET" not in str(err_info.value)

    @pytest.mark.asyncio
    async def test_async_update_data_clears_auth_issues_after_success(
        self, coordinator
    ):
        with patch(
            "custom_components.lipro.core.coordinator.async_delete_issue"
        ) as delete_issue:
            await coordinator._async_update_data()

        delete_issue.assert_any_call(coordinator.hass, DOMAIN, "auth_expired")
        delete_issue.assert_any_call(coordinator.hass, DOMAIN, "auth_error")

    @pytest.mark.asyncio
    async def test_show_mqtt_disconnect_notification_creates_issue(self, coordinator):
        with patch(
            "custom_components.lipro.core.coordinator.async_create_issue"
        ) as create_issue:
            await coordinator._async_show_mqtt_disconnect_notification(minutes=12)

        create_issue.assert_called_once_with(
            coordinator.hass,
            domain=DOMAIN,
            issue_id="mqtt_disconnected",
            is_fixable=False,
            severity=IssueSeverity.WARNING,
            translation_key="mqtt_disconnected",
            translation_placeholders={"minutes": "12"},
        )

    @pytest.mark.asyncio
    async def test_show_auth_notification_creates_issue(self, coordinator):
        with patch(
            "custom_components.lipro.core.coordinator.async_create_issue"
        ) as create_issue:
            await coordinator._async_show_auth_notification("auth_error", error="401")

        create_issue.assert_called_once_with(
            coordinator.hass,
            domain=DOMAIN,
            issue_id="auth_error",
            is_fixable=True,
            severity=IssueSeverity.ERROR,
            translation_key="auth_error",
            translation_placeholders={"error": "401"},
        )

    def test_check_mqtt_disconnect_notification_schedules_task(self, coordinator):
        coordinator._mqtt_enabled = True
        coordinator._mqtt_connected = False
        coordinator._mqtt_disconnect_notified = False
        coordinator._mqtt_disconnect_time = monotonic() - (
            MQTT_DISCONNECT_NOTIFY_THRESHOLD + 10
        )
        scheduled = []

        def _create_task(coro):
            scheduled.append(coro)
            coro.close()
            task = MagicMock()
            task.done.return_value = True
            return task

        coordinator.hass.async_create_task = _create_task

        coordinator._check_mqtt_disconnect_notification()

        assert coordinator._mqtt_disconnect_notified is True
        assert len(scheduled) == 1


class TestCoordinatorDefensivePaths:
    """Test high-value defensive branches for malformed payloads and shutdown."""

    @pytest.mark.asyncio
    async def test_fetch_all_device_pages_rejects_non_object_response(
        self, coordinator, mock_lipro_api_client
    ):
        mock_lipro_api_client.get_devices.return_value = []

        with pytest.raises(LiproApiError, match="Malformed device list response"):
            await coordinator._fetch_all_device_pages()

    @pytest.mark.asyncio
    async def test_fetch_all_device_pages_treats_none_devices_as_empty_page(
        self, coordinator, mock_lipro_api_client
    ):
        mock_lipro_api_client.get_devices.return_value = {"devices": None}

        assert await coordinator._fetch_all_device_pages() == []

    @pytest.mark.asyncio
    async def test_fetch_all_device_pages_stops_on_pagination_guard(
        self, coordinator, mock_lipro_api_client
    ):
        full_page = [{} for _ in range(MAX_DEVICES_PER_QUERY)]
        mock_lipro_api_client.get_devices.return_value = {"devices": full_page}

        with (
            patch("custom_components.lipro.core.coordinator._MAX_DEVICE_LIST_PAGES", 2),
            pytest.raises(LiproApiError, match="pagination exceeded 2 pages"),
        ):
            await coordinator._fetch_all_device_pages()

        assert mock_lipro_api_client.get_devices.call_count == 2

    @pytest.mark.asyncio
    async def test_record_devices_for_anonymous_share_enabled(self, coordinator):
        coordinator._devices = {"dev1": _make_device(serial="dev1")}
        share_manager = MagicMock(is_enabled=True)
        share_manager.async_ensure_loaded = AsyncMock()
        share_manager.record_devices = MagicMock()

        with patch(
            "custom_components.lipro.core.coordinator.get_anonymous_share_manager",
            return_value=share_manager,
        ):
            await coordinator._record_devices_for_anonymous_share()

        share_manager.async_ensure_loaded.assert_awaited_once()
        share_manager.record_devices.assert_called_once()
        recorded = share_manager.record_devices.call_args.args[0]
        assert len(recorded) == 1
        assert recorded[0].serial == "dev1"

    @pytest.mark.asyncio
    async def test_async_remove_stale_devices_without_config_entry_is_noop(
        self, coordinator
    ):
        coordinator.config_entry = None

        with patch("custom_components.lipro.core.coordinator.dr.async_get") as dr_get:
            await coordinator._async_remove_stale_devices({"03ab5ccd7cdead"})

        dr_get.assert_not_called()

    @pytest.mark.asyncio
    async def test_shutdown_tolerates_report_stop_and_close_errors(
        self, coordinator, mock_lipro_api_client
    ):
        pending_refresh_task = MagicMock()
        pending_refresh_task.done.return_value = False
        coordinator._post_command_refresh_tasks["dev1"] = pending_refresh_task

        mqtt_client = AsyncMock()
        mqtt_client.stop.side_effect = OSError("mqtt stop failed")
        coordinator._mqtt_client = mqtt_client

        mock_lipro_api_client.close.side_effect = TimeoutError("close timeout")

        share_manager = MagicMock(is_enabled=True)
        share_manager.submit_report = AsyncMock(side_effect=OSError("upload failed"))

        with patch(
            "custom_components.lipro.core.coordinator.get_anonymous_share_manager",
            return_value=share_manager,
        ):
            await coordinator.async_shutdown()

        pending_refresh_task.cancel.assert_called_once()
        assert coordinator._post_command_refresh_tasks == {}
        share_manager.submit_report.assert_awaited_once()
        mqtt_client.stop.assert_awaited_once()
        mock_lipro_api_client.close.assert_awaited_once()

    @pytest.mark.asyncio
    async def test_delayed_command_refresh_executes_refresh(self, coordinator):
        coordinator.async_request_refresh = AsyncMock()

        with patch(
            "custom_components.lipro.core.coordinator.asyncio.sleep",
            new_callable=AsyncMock,
        ):
            await coordinator._async_delayed_command_refresh(0.1)

        coordinator.async_request_refresh.assert_awaited_once()

    @pytest.mark.asyncio
    async def test_track_background_task_cancelled_on_shutdown(self, coordinator):
        async def _sleep_forever():
            await asyncio.sleep(3600)

        task = coordinator._track_background_task(_sleep_forever())
        assert task in coordinator._background_tasks

        await coordinator.async_shutdown()

        assert task.cancelled()
        assert not coordinator._background_tasks

    @pytest.mark.asyncio
    async def test_track_background_task_consumes_exception(self, coordinator):
        async def _raise_later():
            await asyncio.sleep(0)
            raise RuntimeError("boom")

        task = coordinator._track_background_task(_raise_later())
        await asyncio.sleep(0.05)

        assert task.done()
        assert task not in coordinator._background_tasks
