"""Tests for Lipro data update coordinator.

These tests instantiate a real LiproDataUpdateCoordinator with mocked
dependencies and exercise its public and internal methods directly.
"""

from __future__ import annotations

import asyncio
from collections import deque
from collections.abc import Callable, Coroutine
from datetime import timedelta
import logging
from time import monotonic
from types import SimpleNamespace
from typing import Any
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
from custom_components.lipro.core.command.expectation import (
    PendingCommandExpectation as _PendingCommandExpectation,
)
from custom_components.lipro.core.coordinator.tuning import (
    _CONNECT_STATUS_MQTT_STALE_SECONDS,
)
from custom_components.lipro.core.device import LiproDevice
from custom_components.lipro.core.utils.redaction import redact_identifier
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
        "custom_components.lipro.core.coordinator.state.get_anonymous_share_manager"
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
    properties: dict[str, Any] | None = None,
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
    unique_id: str | None,
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
        coordinator._device_identity_index.register("bbb", dev)
        assert coordinator.get_device_by_id("bbb") is dev

    def test_get_device_by_id_not_found(self, coordinator):
        assert coordinator.get_device_by_id("missing") is None

    def test_get_device_by_id_gateway_mapping(self, coordinator):
        """Gateway ID mapped to a group device."""
        dev = _make_device(serial="mesh_group_10001", is_group=True)
        coordinator._device_identity_index.register("gateway_abc", dev)
        assert coordinator.get_device_by_id("gateway_abc") is dev

    def test_get_device_by_id_register_supports_case_and_strip(self, coordinator):
        """Registered lookup IDs should support strip/lower lookups."""
        dev = _make_device(serial="mesh_group_10002", is_group=True)
        coordinator._device_identity_index.register("GW_MixedCase_001", dev)
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

    def test_unregister_old_entity_does_not_remove_new_instance_with_same_unique_id(
        self, coordinator
    ):
        dev = _make_device()
        old = _make_mock_entity("light_1", dev)
        new = _make_mock_entity("light_1", dev)

        coordinator.register_entity(old)
        coordinator.register_entity(new)
        coordinator.unregister_entity(old)

        assert coordinator._entities["light_1"] is new
        assert coordinator._entities_by_device[dev.serial] == [new]

    def test_entity_with_no_unique_id_skipped(self, coordinator):
        dev = _make_device()
        entity = _make_mock_entity(None, dev)
        entity.unique_id = None
        coordinator.register_entity(entity)
        assert len(coordinator._entities) == 0

    def test_unregister_entity_with_no_unique_id_is_noop(self, coordinator):
        dev = _make_device()
        coordinator._entities = {"existing": _make_mock_entity("existing", dev)}
        coordinator._entities_by_device = {
            dev.serial: [coordinator._entities["existing"]]
        }

        entity = _make_mock_entity(None, dev)
        entity.unique_id = None
        coordinator.unregister_entity(entity)

        assert set(coordinator._entities) == {"existing"}
        assert coordinator._entities_by_device[dev.serial] == [
            coordinator._entities["existing"]
        ]


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

    def test_protected_keys_no_overlap_returns_original_properties(self, coordinator):
        dev = _make_device(serial="dev1")
        entity = _make_mock_entity("e1", dev, protected_keys={"brightness"})
        coordinator.register_entity(entity)

        props = {"powerState": "1"}
        result = coordinator._filter_protected_properties("dev1", props)

        assert result is props


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

    def test_apply_ignores_non_positive_fan_gear_values(self, coordinator):
        """fanGear<=0 should not alter inferred fan gear upper-bound."""
        fan = LiproDevice(
            device_number=1,
            serial="mesh_group_10001",
            name="Fan Light",
            device_type=4,
            iot_name="unknown_model",
            physical_model="fanLight",
            properties={"fanGear": "3"},
        )

        coordinator._apply_properties_update(
            fan,
            {"fanGear": "0"},
            apply_protection=False,
        )

        assert fan.max_fan_gear == 6
        assert fan.fan_gear == 1

    def test_apply_skips_fan_gear_adaptation_when_key_missing(self, coordinator):
        """Missing fanGear should leave capability bounds unchanged."""
        fan = LiproDevice(
            device_number=1,
            serial="mesh_group_10001",
            name="Fan Light",
            device_type=4,
            iot_name="unknown_model",
            physical_model="fanLight",
            properties={"fanGear": "3"},
        )

        coordinator._apply_properties_update(
            fan,
            {"powerState": "1"},
            apply_protection=False,
        )

        assert fan.max_fan_gear == 6
        assert fan.properties["powerState"] == "1"

    def test_apply_filters_stale_values_while_command_pending(self, coordinator):
        """Pending command keys should ignore stale mismatched values."""
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
        coordinator._device_identity_index.register("dev1", dev)

        coordinator._on_mqtt_message("dev1", {"powerState": "1"})
        assert dev.properties["powerState"] == "1"

    def test_unknown_device_ignored(self, coordinator, caplog):
        unknown_id = "03ab5ccd7c123456"

        with caplog.at_level(
            logging.DEBUG,
            logger="custom_components.lipro.core.coordinator",
        ):
            coordinator._on_mqtt_message(unknown_id, {"powerState": "1"})

        redacted = redact_identifier(unknown_id)
        assert redacted is not None
        assert redacted in caplog.text
        assert unknown_id not in caplog.text

    def test_dedup_within_window_skips_second_message(self, coordinator):
        dev = _make_device(serial="dev1", properties={"brightness": "0"})
        coordinator._devices["dev1"] = dev
        coordinator._device_identity_index.register("dev1", dev)

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
        coordinator._device_identity_index.register("dev1", dev)

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
        coordinator._device_identity_index.register("dev1", dev)

        coordinator._on_mqtt_message("dev1", {"brightness": "50"})
        coordinator._on_mqtt_message("dev1", {"brightness": "80"})
        assert dev.properties["brightness"] == "80"

    def test_flush_mqtt_listener_update_clears_handle_and_notifies(self, coordinator):
        coordinator._mqtt_listener_update_handle = object()

        with patch.object(coordinator, "async_update_listeners") as notify:
            coordinator._flush_mqtt_listener_update()

        assert coordinator._mqtt_listener_update_handle is None
        notify.assert_called_once()

    def test_is_duplicate_mqtt_payload_hash_none_skips_dedup(self, coordinator, caplog):
        with (
            caplog.at_level(
                logging.DEBUG,
                logger="custom_components.lipro.core.coordinator.mqtt.messages",
            ),
            patch(
                "custom_components.lipro.core.coordinator.mqtt.messages.compute_properties_hash",
                return_value=None,
            ),
        ):
            duplicated = coordinator._is_duplicate_mqtt_payload(
                device_id="dev1",
                device_name="Device 1",
                properties={"brightness": "50"},
                current_time=10.0,
            )

        assert duplicated is False
        assert coordinator._mqtt_message_cache == {}
        assert "cannot hash properties" in caplog.text

    def test_is_duplicate_mqtt_payload_debug_logs_elapsed_on_duplicate(
        self, coordinator, caplog
    ):
        coordinator._debug_mode = True

        first = coordinator._is_duplicate_mqtt_payload(
            device_id="dev1",
            device_name="Device 1",
            properties={"brightness": "50"},
            current_time=100.0,
        )
        with caplog.at_level(
            logging.DEBUG,
            logger="custom_components.lipro.core.coordinator.mqtt.messages",
        ):
            second = coordinator._is_duplicate_mqtt_payload(
                device_id="dev1",
                device_name="Device 1",
                properties={"brightness": "50"},
                current_time=100.2,
            )

        assert first is False
        assert second is True
        assert "skipping duplicate message for Device 1" in caplog.text

    def test_is_duplicate_mqtt_payload_over_capacity_triggers_cleanup(
        self, coordinator
    ):
        coordinator._mqtt_message_cache = {
            f"key_{idx}": float(idx) for idx in range(MAX_MQTT_CACHE_SIZE)
        }

        with patch.object(coordinator, "_cleanup_mqtt_cache") as cleanup:
            duplicated = coordinator._is_duplicate_mqtt_payload(
                device_id="dev-new",
                device_name="Device New",
                properties={"brightness": "50"},
                current_time=123.0,
            )

        assert duplicated is False
        cleanup.assert_called_once_with(123.0)

    def test_schedule_mqtt_group_online_reconciliation_respects_cooldown(
        self, coordinator
    ):
        coordinator._mqtt_group_online_reconcile_task = None
        coordinator._mqtt_group_online_reconcile_last_at = 100.0

        with patch.object(coordinator, "_track_background_task") as track:
            coordinator._schedule_mqtt_group_online_reconciliation(
                device_name="Group 1", now=103.0
            )

        track.assert_not_called()
        assert coordinator._mqtt_group_online_reconcile_last_at == 100.0
        assert coordinator._mqtt_group_online_reconcile_task is None

    def test_after_mqtt_properties_applied_empty_properties_is_noop(self, coordinator):
        dev = _make_device(serial="dev1", properties={})
        coordinator._devices["dev1"] = dev
        coordinator._device_identity_index.register("dev1", dev)
        coordinator._last_mqtt_connect_state_at.clear()
        coordinator._connect_status_priority_ids = {"dev1"}

        with (
            patch.object(coordinator, "_schedule_mqtt_listener_update") as schedule,
            patch.object(
                coordinator, "_schedule_mqtt_group_online_reconciliation"
            ) as reconcile,
        ):
            coordinator._after_mqtt_properties_applied(dev, {}, current_time=200.0)

        schedule.assert_not_called()
        reconcile.assert_not_called()
        assert coordinator._last_mqtt_connect_state_at == {}
        assert coordinator._connect_status_priority_ids == {"dev1"}


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
            "custom_components.lipro.core.coordinator.mqtt.lifecycle.async_delete_issue"
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

    def test_on_mqtt_disconnect_resets_connect_status_runtime_state(self, coordinator):
        coordinator._connect_status_skip_history.extend([True, False, True])
        coordinator._connect_status_mqtt_stale_seconds = 123.0
        coordinator._force_connect_status_refresh = False

        coordinator._on_mqtt_disconnect()

        assert list(coordinator._connect_status_skip_history) == []
        assert (
            coordinator._connect_status_mqtt_stale_seconds
            == _CONNECT_STATUS_MQTT_STALE_SECONDS
        )
        assert coordinator._force_connect_status_refresh is True

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
            "custom_components.lipro.core.coordinator.device_refresh.monotonic",
            return_value=150.0,
        ):
            assert coordinator._should_refresh_device_list() is False

    def test_should_refresh_after_interval(self, coordinator):
        coordinator._devices = {"dev1": _make_device(serial="dev1")}
        coordinator._force_device_refresh = False
        coordinator._last_device_refresh_at = 100.0

        with patch(
            "custom_components.lipro.core.coordinator.device_refresh.monotonic",
            return_value=1000.0,
        ):
            assert coordinator._should_refresh_device_list() is True

    def test_schedule_reload_for_added_devices(self, coordinator):
        coordinator._devices = {
            "dev1": _make_device(serial="dev1"),
            "dev2": _make_device(serial="dev2"),
        }
        coordinator.hass.config_entries.async_schedule_reload = MagicMock()

        with (
            patch(
                "custom_components.lipro.core.coordinator.device_refresh._ENTRY_RELOAD_DEBOUNCE_SECONDS",
                0.0,
            ),
            patch(
                "custom_components.lipro.core.coordinator.device_refresh.collect_registry_serials_for_entry",
                return_value={"dev1"},
            ),
        ):
            coordinator._schedule_reload_for_added_devices({"dev1"})

        coordinator.hass.config_entries.async_schedule_reload.assert_called_once_with(
            coordinator.config_entry.entry_id
        )

    def test_schedule_reload_ignores_first_baseline_fetch(self, coordinator):
        coordinator._devices = {"dev1": _make_device(serial="dev1")}
        coordinator.hass.config_entries.async_schedule_reload = MagicMock()

        coordinator._schedule_reload_for_added_devices(
            set(),
        )

        coordinator.hass.config_entries.async_schedule_reload.assert_not_called()

    def test_schedule_reload_ignores_removals_only(self, coordinator):
        coordinator._devices = {"dev1": _make_device(serial="dev1")}
        coordinator.hass.config_entries.async_schedule_reload = MagicMock()

        coordinator._schedule_reload_for_added_devices(
            {"dev1", "dev2"},
        )

        coordinator.hass.config_entries.async_schedule_reload.assert_not_called()

    def test_schedule_reload_ignores_returning_devices_seen_in_cloud(self, coordinator):
        """Devices that reappear after a transient cloud omission should not reload."""
        coordinator._devices = {
            "dev1": _make_device(serial="dev1"),
            "dev2": _make_device(serial="dev2"),
        }
        coordinator.hass.config_entries.async_schedule_reload = MagicMock()

        with (
            patch(
                "custom_components.lipro.core.coordinator.device_refresh._ENTRY_RELOAD_DEBOUNCE_SECONDS",
                0.0,
            ),
            patch(
                "custom_components.lipro.core.coordinator.device_refresh.collect_registry_serials_for_entry",
                return_value={"dev1", "dev2"},
            ),
        ):
            coordinator._schedule_reload_for_added_devices({"dev1"})

        coordinator.hass.config_entries.async_schedule_reload.assert_not_called()

    def test_schedule_reload_is_rate_limited(self, coordinator):
        coordinator._devices = {
            "dev1": _make_device(serial="dev1"),
            "dev2": _make_device(serial="dev2"),
        }
        coordinator.hass.config_entries.async_schedule_reload = MagicMock()
        coordinator._last_entry_reload_at = 100.0
        delayed_handle = MagicMock()

        with (
            patch(
                "custom_components.lipro.core.coordinator.device_refresh._ENTRY_RELOAD_DEBOUNCE_SECONDS",
                0.0,
            ),
            patch(
                "custom_components.lipro.core.coordinator.device_refresh.collect_registry_serials_for_entry",
                return_value={"dev1"},
            ),
            patch(
                "custom_components.lipro.core.coordinator.device_refresh.monotonic",
                return_value=150.0,
            ),
            patch.object(coordinator.hass.loop, "is_running", return_value=True),
            patch.object(
                coordinator.hass.loop,
                "call_later",
                return_value=delayed_handle,
            ) as call_later,
        ):
            coordinator._schedule_reload_for_added_devices({"dev1"})

        coordinator.hass.config_entries.async_schedule_reload.assert_not_called()
        call_later.assert_called_once_with(10.0, coordinator._flush_entry_reload)
        assert coordinator._entry_reload_handle is delayed_handle

    def test_schedule_reload_debounces_multiple_triggers(self, coordinator):
        coordinator._devices = {
            "dev1": _make_device(serial="dev1"),
            "dev2": _make_device(serial="dev2"),
        }
        coordinator.hass.config_entries.async_schedule_reload = MagicMock()
        scheduled_callback: list[Callable[[], None]] = []
        delayed_handle = MagicMock()

        def _call_later(delay: float, callback: Callable[[], None]) -> MagicMock:
            scheduled_callback.append(callback)
            return delayed_handle

        with (
            patch(
                "custom_components.lipro.core.coordinator.device_refresh._ENTRY_RELOAD_DEBOUNCE_SECONDS",
                5.0,
            ),
            patch(
                "custom_components.lipro.core.coordinator.device_refresh._ENTRY_RELOAD_MIN_INTERVAL_SECONDS",
                0.0,
            ),
            patch(
                "custom_components.lipro.core.coordinator.device_refresh.collect_registry_serials_for_entry",
                return_value={"dev1"},
            ),
            patch.object(coordinator.hass.loop, "is_running", return_value=True),
            patch.object(
                coordinator.hass.loop,
                "call_later",
                side_effect=_call_later,
            ) as call_later,
        ):
            coordinator._schedule_reload_for_added_devices({"dev1"})
            coordinator._schedule_reload_for_added_devices({"dev1"})

            call_later.assert_called_once()
            coordinator.hass.config_entries.async_schedule_reload.assert_not_called()
            assert len(scheduled_callback) == 1

            scheduled_callback[0]()

        coordinator.hass.config_entries.async_schedule_reload.assert_called_once_with(
            coordinator.config_entry.entry_id
        )


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
            "custom_components.lipro.core.command.result.asyncio.sleep",
            new=AsyncMock(),
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

    def test_last_command_failure_returns_none_when_unset(self, coordinator):
        coordinator._last_command_failure = None

        assert coordinator.last_command_failure is None

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
            coordinator.hass.config_entries.async_schedule_reload = MagicMock()
            stale_entity = _make_mock_entity(
                unique_id="lipro_03ab5ccd7cdead",
                device=_make_device(serial="03ab5ccd7cdead"),
            )
            coordinator._entities_by_device["03ab5ccd7cdead"] = [stale_entity]
            coordinator._entities[stale_entity.unique_id] = stale_entity

            for _ in range(3):
                with patch(
                    "custom_components.lipro.core.coordinator.device_refresh._ENTRY_RELOAD_DEBOUNCE_SECONDS",
                    0.0,
                ):
                    await coordinator._reconcile_stale_devices(
                        {dev.serial, "03ab5ccd7cdead"},
                    )

        remove_stale.assert_awaited_once_with({"03ab5ccd7cdead"})
        assert "03ab5ccd7cdead" not in coordinator._missing_device_cycles
        assert "03ab5ccd7cdead" not in coordinator._pending_command_expectations
        assert "03ab5ccd7cdead" not in coordinator._entities_by_device
        assert stale_entity.unique_id not in coordinator._entities
        coordinator.hass.config_entries.async_schedule_reload.assert_called_once()

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
            "custom_components.lipro.core.coordinator.auth_issues.async_delete_issue"
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

    def test_schedule_post_command_refresh_with_mqtt_immediate_and_delayed_when_pending_expectation(
        self, coordinator
    ):
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
            skip_immediate=False,
            device_serial="dev1",
        )

        assert len(scheduled) == 2

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
        coordinator._last_mqtt_connect_state_at = {"active": 1.0, "stale": 2.0}
        coordinator._connect_status_priority_ids = {"active", "stale"}

        coordinator._prune_runtime_state_for_devices({"active"})

        assert set(coordinator._pending_command_expectations) == {"active"}
        assert set(coordinator._device_state_latency_seconds) == {"active"}
        assert set(coordinator._last_mqtt_connect_state_at) == {"active"}
        assert coordinator._connect_status_priority_ids == {"active"}

    def test_adapt_state_batch_size_down_on_high_latency(self, coordinator):
        coordinator._state_status_batch_size = 64
        coordinator._state_batch_metrics = deque(
            [(64, 4.5, 0)] * 6,
            maxlen=24,
        )

        coordinator._adapt_state_batch_size()

        assert coordinator._state_status_batch_size == 56

    def test_adapt_state_batch_size_up_on_low_latency_and_no_fallback(
        self, coordinator
    ):
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
        from custom_components.lipro.core.coordinator.tuning import (
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

    @pytest.mark.parametrize(
        (
            "mqtt_enabled",
            "mqtt_connected",
            "disconnect_time",
            "backoff_allows_attempt",
            "expected",
        ),
        [
            (False, False, None, True, 60.0),
            (True, True, None, True, 60.0),
            (True, False, 123.0, True, 20.0),
            (True, False, None, False, 20.0),
            (True, False, None, True, 60.0),
        ],
    )
    def test_resolve_connect_status_query_interval_seconds_degraded_mode(
        self,
        coordinator,
        mqtt_enabled,
        mqtt_connected,
        disconnect_time,
        backoff_allows_attempt,
        expected,
    ):
        coordinator._mqtt_enabled = mqtt_enabled
        coordinator._mqtt_connected = mqtt_connected
        coordinator._mqtt_disconnect_time = disconnect_time

        with patch.object(
            type(coordinator._mqtt_setup_backoff),
            "should_attempt",
            return_value=backoff_allows_attempt,
        ):
            interval = coordinator._resolve_connect_status_query_interval_seconds(
                1000.0
            )

        assert interval == expected

    def test_resolve_connect_status_query_ids_records_skip_when_mqtt_is_fresh(
        self, coordinator
    ):
        coordinator._iot_ids_to_query = ["dev1"]
        coordinator._mqtt_enabled = True
        coordinator._mqtt_connected = True
        coordinator._force_connect_status_refresh = False
        coordinator._last_connect_status_query_time = 0.0
        coordinator._last_mqtt_connect_state_at["dev1"] = 1000.0

        with patch(
            "custom_components.lipro.core.coordinator.tuning.monotonic",
            return_value=1000.0,
        ):
            ids = coordinator._resolve_connect_status_query_ids()

        assert ids == []
        assert coordinator._connect_status_skip_history[-1] is True
        assert coordinator._last_connect_status_query_time == 1000.0

    def test_resolve_connect_status_query_ids_interval_not_reached_is_noop(
        self, coordinator
    ):
        coordinator._iot_ids_to_query = ["dev1"]
        coordinator._mqtt_enabled = True
        coordinator._mqtt_connected = False
        coordinator._force_connect_status_refresh = False
        coordinator._last_connect_status_query_time = 1000.0

        with patch(
            "custom_components.lipro.core.coordinator.tuning.monotonic",
            return_value=1000.5,
        ):
            ids = coordinator._resolve_connect_status_query_ids()

        assert ids == []
        assert list(coordinator._connect_status_skip_history) == []
        assert coordinator._last_connect_status_query_time == 1000.0

    def test_resolve_connect_status_query_ids_force_refresh_consumes_flag(
        self, coordinator
    ):
        coordinator._iot_ids_to_query = ["dev1", "dev2"]
        coordinator._mqtt_enabled = True
        coordinator._mqtt_connected = True
        coordinator._force_connect_status_refresh = True
        coordinator._last_connect_status_query_time = 0.0

        with patch(
            "custom_components.lipro.core.coordinator.tuning.monotonic",
            return_value=1000.0,
        ):
            ids = coordinator._resolve_connect_status_query_ids()

        assert set(ids) == {"dev1", "dev2"}
        assert coordinator._force_connect_status_refresh is False
        assert list(coordinator._connect_status_skip_history) == []
        assert coordinator._last_connect_status_query_time == 1000.0

    def test_build_developer_report_disabled_mode_has_note(self, coordinator):
        with patch(
            "custom_components.lipro.core.coordinator.state.get_anonymous_share_manager"
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

    def test_load_options_debug_mode_has_no_global_logger_side_effect(
        self, coordinator
    ):
        coordinator.hass.config_entries.async_update_entry(
            coordinator.config_entry,
            options={"debug_mode": True},
        )
        with patch(
            "custom_components.lipro.core.coordinator.state.logging.getLogger"
        ) as get_logger:
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
    async def test_async_setup_mqtt_success(
        self, coordinator, mock_lipro_api_client, caplog
    ):
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
                "custom_components.lipro.core.mqtt.credentials.decrypt_mqtt_credential",
                side_effect=["ak", "sk"],
            ),
            patch(
                "custom_components.lipro.core.mqtt.client.LiproMqttClient"
            ) as mqtt_cls,
        ):
            mqtt_cls.return_value = mock_mqtt
            with caplog.at_level(
                logging.DEBUG,
                logger="custom_components.lipro.core.coordinator",
            ):
                ok = await coordinator.async_setup_mqtt()

        assert ok is True
        assert coordinator._biz_id == "10001"
        mock_mqtt.start.assert_awaited_once_with(["dev1", "mesh_group_1"])
        redacted = redact_identifier("mesh_group_1")
        assert redacted is not None
        assert redacted in caplog.text
        assert "MQTT: subscribing to mesh group mesh_group_1" not in caplog.text

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
                "custom_components.lipro.core.coordinator.mqtt.lifecycle.resolve_mqtt_biz_id",
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

    def test_ensure_mqtt_runtime_recreates_when_missing(self, coordinator):
        coordinator._mqtt_runtime = None

        runtime = coordinator._ensure_mqtt_runtime()

        assert coordinator._mqtt_runtime is runtime

    def test_mqtt_connected_property_reflects_internal_flag(self, coordinator):
        coordinator._mqtt_connected = True
        assert coordinator.mqtt_connected is True

        coordinator._mqtt_connected = False
        assert coordinator.mqtt_connected is False

    @pytest.mark.asyncio
    async def test_mqtt_setup_failure_blocks_reschedule_inside_backoff_window(
        self, coordinator
    ):
        coordinator._mqtt_enabled = True
        coordinator._mqtt_client = None
        coordinator._devices = {"dev1": _make_device(serial="dev1")}
        coordinator.async_setup_mqtt = AsyncMock(return_value=False)
        coordinator._mqtt_setup_in_progress = True

        with patch(
            "custom_components.lipro.core.coordinator.mqtt.lifecycle.monotonic",
            return_value=100.0,
        ):
            await coordinator._async_setup_mqtt_safe()

        scheduled: list[object] = []

        def _track(coro):
            scheduled.append(coro)
            coro.close()
            return MagicMock()

        coordinator._track_background_task = MagicMock(side_effect=_track)
        with patch(
            "custom_components.lipro.core.coordinator.mqtt.lifecycle.monotonic",
            return_value=100.5,
        ):
            coordinator._schedule_mqtt_setup_if_needed()

        assert coordinator._mqtt_setup_in_progress is False
        assert scheduled == []

    @pytest.mark.asyncio
    async def test_async_setup_mqtt_safe_propagates_cancelled_error(self, coordinator):
        coordinator.async_setup_mqtt = AsyncMock(side_effect=asyncio.CancelledError())
        coordinator._mqtt_setup_in_progress = True

        with pytest.raises(asyncio.CancelledError):
            await coordinator._async_setup_mqtt_safe()

        assert coordinator._mqtt_setup_in_progress is False

    @pytest.mark.asyncio
    async def test_mqtt_setup_success_resets_backoff_and_allows_immediate_retry(
        self, coordinator
    ):
        coordinator._mqtt_enabled = True
        coordinator._mqtt_client = None
        coordinator._devices = {"dev1": _make_device(serial="dev1")}

        coordinator.async_setup_mqtt = AsyncMock(return_value=False)
        coordinator._mqtt_setup_in_progress = True
        with patch(
            "custom_components.lipro.core.coordinator.mqtt.lifecycle.monotonic",
            return_value=200.0,
        ):
            await coordinator._async_setup_mqtt_safe()

        coordinator.async_setup_mqtt = AsyncMock(return_value=True)
        coordinator._mqtt_setup_in_progress = True
        with patch(
            "custom_components.lipro.core.coordinator.mqtt.lifecycle.monotonic",
            return_value=201.0,
        ):
            await coordinator._async_setup_mqtt_safe()

        scheduled: list[object] = []

        def _track(coro):
            scheduled.append(coro)
            coro.close()
            return MagicMock()

        coordinator._track_background_task = MagicMock(side_effect=_track)
        with patch(
            "custom_components.lipro.core.coordinator.mqtt.lifecycle.monotonic",
            return_value=201.0,
        ):
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
        assert coordinator.get_device_by_id("03ab5ccd7cgw") is group
        assert coordinator.get_device_by_id("03ab5ccd7c111111") is group
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

    def test_apply_group_lookup_mappings_clears_gateway_extra_data_when_gateway_missing(
        self, coordinator
    ):
        group = _make_device(serial="mesh_group_10001", is_group=True)
        group.extra_data["gateway_device_id"] = "03ab5ccd7cgw"
        coordinator._device_identity_index.register("03ab5ccd7cgw", group)

        coordinator._apply_group_lookup_mappings(group, {"devices": []})

        assert "gateway_device_id" not in group.extra_data
        assert coordinator.get_device_by_id("03ab5ccd7cgw") is None

    @pytest.mark.asyncio
    async def test_query_outlet_power_writes_extra_data(
        self, coordinator, mock_lipro_api_client
    ):
        outlet = _make_device(serial="out1", properties={"powerState": "1"})
        coordinator._devices[outlet.serial] = outlet
        coordinator._device_identity_index.register(outlet.serial, outlet)
        coordinator._outlet_ids_to_query = [outlet.serial]
        mock_lipro_api_client.fetch_outlet_power_info.return_value = {
            "nowPower": 33.5,
            "energyList": [{"t": "20240101", "v": 2.2}],
        }

        await coordinator._query_outlet_power()

        assert outlet.extra_data["power_info"]["nowPower"] == 33.5

    @pytest.mark.asyncio
    async def test_query_outlet_power_batch_unparseable_falls_back_to_per_device(
        self, coordinator, mock_lipro_api_client
    ):
        out1 = _make_device(serial="out1", properties={"powerState": "1"})
        out2 = _make_device(serial="out2", properties={"powerState": "1"})
        coordinator._devices[out1.serial] = out1
        coordinator._devices[out2.serial] = out2
        coordinator._device_identity_index.register(out1.serial, out1)
        coordinator._device_identity_index.register(out2.serial, out2)
        coordinator._outlet_ids_to_query = [out1.serial, out2.serial]

        def _fetch(device_ids):
            if device_ids == ["out1", "out2"]:
                return {"nowPower": 9.9}
            if device_ids == ["out1"]:
                return {"nowPower": 1.1}
            if device_ids == ["out2"]:
                return {"nowPower": 2.2}
            return {}

        mock_lipro_api_client.fetch_outlet_power_info.side_effect = _fetch

        await coordinator._query_outlet_power()

        assert out1.extra_data["power_info"]["nowPower"] == 1.1
        assert out2.extra_data["power_info"]["nowPower"] == 2.2
        assert mock_lipro_api_client.fetch_outlet_power_info.await_count == 3

    @pytest.mark.asyncio
    async def test_query_outlet_power_raises_auth_error(
        self, coordinator, mock_lipro_api_client
    ):
        outlet = _make_device(serial="out1", properties={"powerState": "1"})
        coordinator._devices[outlet.serial] = outlet
        coordinator._device_identity_index.register(outlet.serial, outlet)
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
        coordinator._device_identity_index.register(outlet.serial, outlet)
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
        coordinator._device_identity_index.register(outlet.serial, outlet)
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
        coordinator._device_identity_index.register(dev.serial, dev)
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
    async def test_update_device_status_schedules_group_status_query(self, coordinator):
        coordinator._iot_ids_to_query = []
        coordinator._group_ids_to_query = ["mesh_group_1"]
        coordinator._outlet_ids_to_query = []
        coordinator._power_monitoring_enabled = False

        coordinator._query_group_status = AsyncMock()
        coordinator._track_background_task = lambda coro: asyncio.create_task(coro)

        await coordinator._update_device_status()

        coordinator._query_group_status.assert_awaited_once()

    def test_apply_device_status_row_ignores_missing_device_id(self, coordinator):
        coordinator._apply_device_status_row({})

    def test_apply_device_status_row_ignores_unknown_device_id(self, coordinator):
        coordinator._apply_device_status_row({"deviceId": "unknown"})

    @pytest.mark.asyncio
    async def test_update_device_status_queries_only_stale_connect_ids_with_mqtt(
        self, coordinator, mock_lipro_api_client
    ):
        dev_a = _make_device(serial="dev_a", properties={"connectState": "1"})
        dev_b = _make_device(serial="dev_b", properties={"connectState": "1"})
        coordinator._devices[dev_a.serial] = dev_a
        coordinator._devices[dev_b.serial] = dev_b
        coordinator._device_identity_index.register(dev_a.serial, dev_a)
        coordinator._device_identity_index.register(dev_b.serial, dev_b)
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
        coordinator._device_identity_index.register(dev.serial, dev)
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
        coordinator._device_identity_index.register(dev.serial, dev)
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
        coordinator._device_identity_index.register(dev_a.serial, dev_a)
        coordinator._device_identity_index.register(dev_b.serial, dev_b)
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
        coordinator._device_identity_index.register(dev_a.serial, dev_a)
        coordinator._device_identity_index.register(dev_b.serial, dev_b)
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
        coordinator._device_identity_index.register(dev.serial, dev)
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
        coordinator._device_identity_index.register(dev.serial, dev)
        coordinator._iot_ids_to_query = [dev.serial]
        mock_lipro_api_client.query_device_status.return_value = []
        mock_lipro_api_client.query_connect_status.return_value = {dev.serial: True}

        await coordinator._update_device_status()
        await coordinator._update_device_status()

        assert mock_lipro_api_client.query_connect_status.await_count == 1

    @pytest.mark.asyncio
    async def test_query_outlet_power_limits_single_cycle_burst_for_large_fleet(
        self, coordinator, mock_lipro_api_client
    ):
        coordinator._outlet_ids_to_query = [f"out{i}" for i in range(100)]
        mock_lipro_api_client.fetch_outlet_power_info.return_value = {
            f"out{i}": {"nowPower": float(i)} for i in range(10)
        }

        await coordinator._query_outlet_power()

        # 100 devices should be capped to prevent large one-cycle bursts.
        assert mock_lipro_api_client.fetch_outlet_power_info.await_count == 1
        assert (
            len(mock_lipro_api_client.fetch_outlet_power_info.await_args.args[0]) == 10
        )
        assert coordinator._outlet_power_round_robin_index == 10

    def test_resolve_outlet_power_cycle_size_scales_with_device_count(
        self, coordinator
    ):
        assert coordinator._resolve_outlet_power_cycle_size(0) == 0
        assert coordinator._resolve_outlet_power_cycle_size(8) == 8
        assert coordinator._resolve_outlet_power_cycle_size(10) == 10
        assert coordinator._resolve_outlet_power_cycle_size(20) == 5
        assert coordinator._resolve_outlet_power_cycle_size(100) == 10

    @pytest.mark.asyncio
    async def test_group_mqtt_online_variants_schedule_reconciliation(
        self, coordinator
    ):
        """Numeric/boolean connectState payloads should trigger group reconciliation."""
        group = _make_device(serial="mesh_group_10001", is_group=True, properties={})
        coordinator._devices[group.serial] = group
        coordinator._device_identity_index.register(group.serial, group)
        coordinator.async_request_refresh = AsyncMock()

        created_tasks: list[asyncio.Task[None]] = []

        def _capture_task(coro: Coroutine[Any, Any, None]) -> asyncio.Task[None]:
            task = asyncio.create_task(coro)
            created_tasks.append(task)
            return task

        with patch.object(
            coordinator.hass, "async_create_task", side_effect=_capture_task
        ):
            coordinator._on_mqtt_message(group.serial, {"connectState": 1})

        await asyncio.gather(*created_tasks)
        coordinator.async_request_refresh.assert_awaited_once()

    @pytest.mark.asyncio
    async def test_group_mqtt_online_reconciliation_cooldown_skips_bursts(
        self, coordinator
    ):
        """Group online reconnect bursts should schedule at most one refresh."""
        group = _make_device(serial="mesh_group_10001", is_group=True, properties={})
        coordinator._devices[group.serial] = group
        coordinator._device_identity_index.register(group.serial, group)
        coordinator.async_request_refresh = AsyncMock()

        created_tasks: list[asyncio.Task[None]] = []

        def _capture_task(coro: Coroutine[Any, Any, None]) -> asyncio.Task[None]:
            task = asyncio.create_task(coro)
            created_tasks.append(task)
            return task

        with (
            patch.object(
                coordinator.hass, "async_create_task", side_effect=_capture_task
            ),
            patch(
                "custom_components.lipro.core.coordinator.mqtt.messages.monotonic",
                side_effect=[100.0, 101.0],
            ),
        ):
            coordinator._on_mqtt_message(group.serial, {"connectState": 1})
            coordinator._on_mqtt_message(group.serial, {"connectState": 1})

        await asyncio.gather(*created_tasks)
        coordinator.async_request_refresh.assert_awaited_once()
        assert len(created_tasks) == 1

    def test_apply_group_status_row_missing_group_id_is_ignored(self, coordinator):
        coordinator._apply_group_status_row({"properties": []})

    def test_apply_group_status_row_unknown_group_is_ignored(self, coordinator):
        coordinator._apply_group_status_row(
            {"groupId": "mesh_group_404", "properties": []}
        )

    @pytest.mark.asyncio
    async def test_fetch_devices_syncs_mqtt_subscriptions_when_connected(
        self, coordinator
    ):
        coordinator._devices = {}
        coordinator._mqtt_client = object()
        coordinator._mqtt_connected = True
        coordinator._fetch_all_device_pages = AsyncMock(return_value=[])
        coordinator._record_devices_for_anonymous_share = AsyncMock()
        coordinator._reconcile_stale_devices = AsyncMock()
        coordinator._sync_mqtt_subscriptions = AsyncMock()

        await coordinator._fetch_devices()

        coordinator._sync_mqtt_subscriptions.assert_awaited_once()

    @pytest.mark.asyncio
    async def test_async_remove_stale_devices(self, coordinator):
        device_entry = MagicMock(id="reg-id", name="Stale Device")
        registry = MagicMock()
        registry.async_get_device.return_value = device_entry

        with patch(
            "custom_components.lipro.core.coordinator.device_refresh.dr.async_get"
        ) as dr_get:
            dr_get.return_value = registry
            await coordinator._async_remove_stale_devices({"03ab5ccd7cdead"})

        registry.async_remove_device.assert_called_once_with("reg-id")

    @pytest.mark.asyncio
    async def test_async_remove_stale_devices_swallows_registry_errors(
        self, coordinator
    ):
        with (
            patch(
                "custom_components.lipro.core.coordinator.device_refresh.remove_stale_registry_devices",
                side_effect=RuntimeError("registry failure"),
            ),
            patch(
                "custom_components.lipro.core.coordinator.device_refresh.dr.async_get",
                return_value=MagicMock(),
            ),
        ):
            await coordinator._async_remove_stale_devices({"03ab5ccd7cdead"})

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
                "custom_components.lipro.core.coordinator.device_refresh.dr.async_get",
                return_value=device_registry,
            ),
            patch(
                "custom_components.lipro.core.coordinator.device_refresh.ar.async_get",
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
                "custom_components.lipro.core.coordinator.device_refresh.dr.async_get",
                return_value=device_registry,
            ),
            patch(
                "custom_components.lipro.core.coordinator.device_refresh.ar.async_get",
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
                "custom_components.lipro.core.coordinator.device_refresh.dr.async_get",
                return_value=device_registry,
            ),
            patch(
                "custom_components.lipro.core.coordinator.device_refresh.ar.async_get",
                return_value=area_registry,
            ),
        ):
            coordinator._sync_device_room_assignments(previous)

        device_registry.async_update_device.assert_called_once_with(
            "dev-entry-1",
            suggested_area="儿童房",
            area_id="area-kids",
        )

    def test_sync_device_room_assignments_force_sync_when_room_unchanged(
        self, coordinator
    ):
        previous = {
            "03ab5ccd7c111111": _make_device(serial="03ab5ccd7c111111", name="Lamp A")
        }
        previous["03ab5ccd7c111111"].room_name = "主卧"

        current = _make_device(serial="03ab5ccd7c111111", name="Lamp A")
        current.room_name = "主卧"
        coordinator._devices = {"03ab5ccd7c111111": current}
        coordinator._room_area_sync_force = True

        device_entry = MagicMock(id="dev-entry-1", area_id="custom-area")
        device_registry = MagicMock()
        device_registry.async_get_device.return_value = device_entry

        area_registry = MagicMock()
        area_registry.async_get_area.return_value = SimpleNamespace(name="手动区域")
        area_registry.async_get_or_create.return_value = SimpleNamespace(
            id="area-bedroom"
        )

        with (
            patch(
                "custom_components.lipro.core.coordinator.device_refresh.dr.async_get",
                return_value=device_registry,
            ),
            patch(
                "custom_components.lipro.core.coordinator.device_refresh.ar.async_get",
                return_value=area_registry,
            ),
        ):
            coordinator._sync_device_room_assignments(previous)

        device_registry.async_update_device.assert_called_once_with(
            "dev-entry-1",
            suggested_area="主卧",
            area_id="area-bedroom",
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
                "custom_components.lipro.core.coordinator.device_refresh.dr.async_get",
                return_value=device_registry,
            ),
            patch(
                "custom_components.lipro.core.coordinator.device_refresh.ar.async_get",
                return_value=area_registry,
            ),
        ):
            coordinator._sync_device_room_assignments(previous)

        device_registry.async_update_device.assert_called_once_with(
            "dev-entry-1",
            suggested_area=None,
            area_id=None,
        )

    def test_sync_device_room_assignments_swallows_registry_sync_errors(
        self, coordinator
    ):
        previous = {
            "03ab5ccd7c111111": _make_device(serial="03ab5ccd7c111111", name="Lamp A")
        }
        coordinator._devices = {
            "03ab5ccd7c111111": _make_device(serial="03ab5ccd7c111111", name="Lamp A")
        }

        with (
            patch(
                "custom_components.lipro.core.coordinator.device_refresh.sync_device_room_assignments",
                side_effect=RuntimeError("sync failed"),
            ),
            patch(
                "custom_components.lipro.core.coordinator.device_refresh.dr.async_get",
                return_value=MagicMock(),
            ),
            patch(
                "custom_components.lipro.core.coordinator.device_refresh.ar.async_get",
                return_value=MagicMock(),
            ),
        ):
            coordinator._sync_device_room_assignments(previous)

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
        assert show_auth.await_args is not None
        await_args = show_auth.await_args
        assert await_args.args == ("auth_error",)
        placeholder_values = " ".join(
            str(value) for value in await_args.kwargs.values()
        )
        assert raw_error not in placeholder_values
        assert await_args.kwargs.get("error") == "AuthError"
        start_reauth.assert_called_once_with(coordinator.hass)

    @pytest.mark.parametrize(
        "marker",
        [
            "   ",
            "1AuthError(code=401)",
            "Auth-Error(code=401)",
            "AuthError(code=123456789012345678901234567890123)",
        ],
    )
    def test_is_safe_error_marker_rejects_invalid_shapes(self, coordinator, marker):
        assert coordinator._is_safe_error_marker(marker) is False

    @pytest.mark.asyncio
    async def test_raise_update_data_error_auth_path_hides_raw_error(self, coordinator):
        raw_error = "AUTH_RAW_SECRET_123"
        with (
            patch.object(coordinator, "_trigger_reauth", new=AsyncMock()) as reauth,
            pytest.raises(ConfigEntryAuthFailed) as err_info,
        ):
            await coordinator._raise_update_data_error(LiproAuthError(raw_error))

        reauth.assert_awaited_once()
        assert reauth.await_args is not None
        await_args = reauth.await_args
        assert await_args.args == ("auth_error",)
        placeholder_values = " ".join(
            str(value) for value in await_args.kwargs.values()
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
    async def test_raise_update_data_error_reraises_unknown_exception(
        self, coordinator
    ):
        err = RuntimeError("unexpected-runtime-error")
        with (
            patch.object(coordinator, "_trigger_reauth", new=AsyncMock()) as reauth,
            pytest.raises(RuntimeError) as err_info,
        ):
            await coordinator._raise_update_data_error(err)

        reauth.assert_not_awaited()
        assert err_info.value is err

    @pytest.mark.asyncio
    async def test_async_update_data_clears_auth_issues_after_success(
        self, coordinator
    ):
        with patch(
            "custom_components.lipro.core.coordinator.auth_issues.async_delete_issue"
        ) as delete_issue:
            await coordinator._async_update_data()

        delete_issue.assert_any_call(coordinator.hass, DOMAIN, "auth_expired")
        delete_issue.assert_any_call(coordinator.hass, DOMAIN, "auth_error")

    @pytest.mark.asyncio
    async def test_async_update_data_raises_unexpected_update_failure_when_handler_returns(
        self, coordinator
    ):
        coordinator._async_ensure_authenticated = AsyncMock(
            side_effect=LiproApiError("boom")
        )
        coordinator._raise_update_data_error = AsyncMock(return_value=None)

        with pytest.raises(UpdateFailed, match="Unexpected update failure"):
            await coordinator._async_update_data()

    @pytest.mark.asyncio
    async def test_show_mqtt_disconnect_notification_creates_issue(self, coordinator):
        with patch(
            "custom_components.lipro.core.coordinator.mqtt.lifecycle.async_create_issue"
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
            "custom_components.lipro.core.coordinator.auth_issues.async_create_issue"
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

    def test_parse_device_list_page_filters_malformed_rows_and_preserves_has_more(
        self, coordinator
    ):
        limit = MAX_DEVICES_PER_QUERY
        raw_page: list[object] = [{}] + ["bad"] + [123] + ([{}] * (limit - 3))
        logger = MagicMock()

        page, has_more = coordinator._parse_device_list_page(
            {"devices": raw_page},
            limit=limit,
            logger=logger,
        )

        assert len(page) == limit - 2
        assert has_more is True
        logger.debug.assert_called_once_with(
            "Skipping %d malformed device rows from API payload",
            2,
        )

    def test_parse_device_list_page_rejects_non_list_devices_payload(self, coordinator):
        with pytest.raises(LiproApiError, match="expected devices list"):
            coordinator._parse_device_list_page(
                {"devices": {}},
                limit=MAX_DEVICES_PER_QUERY,
            )

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
        full_page: list[dict[str, object]] = [{} for _ in range(MAX_DEVICES_PER_QUERY)]
        mock_lipro_api_client.get_devices.return_value = {"devices": full_page}

        with (
            patch(
                "custom_components.lipro.core.coordinator.device_refresh._MAX_DEVICE_LIST_PAGES",
                2,
            ),
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
            "custom_components.lipro.core.coordinator.state.get_anonymous_share_manager",
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

        with patch(
            "custom_components.lipro.core.coordinator.device_refresh.dr.async_get"
        ) as dr_get:
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
            "custom_components.lipro.core.coordinator.state.get_anonymous_share_manager",
            return_value=share_manager,
        ):
            await coordinator.async_shutdown()

        pending_refresh_task.cancel.assert_called_once()
        assert coordinator._post_command_refresh_tasks == {}
        share_manager.submit_report.assert_awaited_once()
        mqtt_client.stop.assert_awaited_once()
        mock_lipro_api_client.close.assert_awaited_once()

    @pytest.mark.asyncio
    async def test_shutdown_cancels_mqtt_listener_update_handle(self, coordinator):
        listener_handle = MagicMock()
        coordinator._mqtt_listener_update_handle = listener_handle

        share_manager = MagicMock(is_enabled=False)
        share_manager.submit_report = AsyncMock()

        with patch(
            "custom_components.lipro.core.coordinator.state.get_anonymous_share_manager",
            return_value=share_manager,
        ):
            await coordinator.async_shutdown()

        listener_handle.cancel.assert_called_once()
        assert coordinator._mqtt_listener_update_handle is None

    @pytest.mark.asyncio
    async def test_shutdown_propagates_cancelled_error_from_share_report(
        self, coordinator, mock_lipro_api_client
    ):
        share_manager = MagicMock(is_enabled=True)
        share_manager.submit_report = AsyncMock(side_effect=asyncio.CancelledError())

        coordinator.async_stop_mqtt = AsyncMock()

        with (
            patch(
                "custom_components.lipro.core.coordinator.state.get_anonymous_share_manager",
                return_value=share_manager,
            ),
            pytest.raises(asyncio.CancelledError),
        ):
            await coordinator.async_shutdown()

        coordinator.async_stop_mqtt.assert_not_awaited()
        mock_lipro_api_client.close.assert_not_awaited()

    @pytest.mark.asyncio
    async def test_shutdown_propagates_cancelled_error_from_stop_mqtt(
        self, coordinator, mock_lipro_api_client
    ):
        share_manager = MagicMock(is_enabled=False)
        share_manager.submit_report = AsyncMock()

        coordinator.async_stop_mqtt = AsyncMock(side_effect=asyncio.CancelledError())

        with (
            patch(
                "custom_components.lipro.core.coordinator.state.get_anonymous_share_manager",
                return_value=share_manager,
            ),
            pytest.raises(asyncio.CancelledError),
        ):
            await coordinator.async_shutdown()

        mock_lipro_api_client.close.assert_not_awaited()

    @pytest.mark.asyncio
    async def test_shutdown_propagates_cancelled_error_from_client_close(
        self, coordinator, mock_lipro_api_client
    ):
        share_manager = MagicMock(is_enabled=False)
        share_manager.submit_report = AsyncMock()

        coordinator.async_stop_mqtt = AsyncMock()
        mock_lipro_api_client.close.side_effect = asyncio.CancelledError()

        with (
            patch(
                "custom_components.lipro.core.coordinator.state.get_anonymous_share_manager",
                return_value=share_manager,
            ),
            pytest.raises(asyncio.CancelledError),
        ):
            await coordinator.async_shutdown()

    @pytest.mark.asyncio
    async def test_delayed_command_refresh_executes_refresh(self, coordinator):
        coordinator.async_request_refresh = AsyncMock()

        with patch(
            "custom_components.lipro.core.command.result.asyncio.sleep",
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


class TestCoordinatorAdaptiveTuning:
    """Test adaptive tuning and status metrics snapshot paths."""

    def test_build_status_metrics_snapshot_with_samples(self, coordinator):
        coordinator._state_batch_metrics.append((32, 1.5, 0))
        coordinator._state_batch_metrics.append((24, 2.0, 1))

        snapshot = coordinator._build_status_metrics_snapshot()

        assert snapshot["state_batch_size_avg"] == 28.0
        assert snapshot["state_batch_duration_avg_seconds"] == 1.75
        assert snapshot["state_metrics_samples"] == 2

    def test_adapt_state_batch_size_noop_when_unchanged(self, coordinator):
        coordinator._state_batch_metrics.append((32, 2.0, 0))
        original = coordinator._state_status_batch_size
        coordinator._adapt_state_batch_size()
        assert coordinator._state_status_batch_size == original


class TestRedactIdentifier:
    """Edge-case coverage for redact_identifier."""

    def test_whitespace_only_returns_none(self):
        assert redact_identifier("   ") is None
