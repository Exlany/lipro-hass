"""Coordinator tests for new runtime architecture.

Tests focus on public API behavior through service layer.
"""

from __future__ import annotations

from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from pytest_homeassistant_custom_component.common import MockConfigEntry

from custom_components.lipro.const.base import DOMAIN
from custom_components.lipro.core.api import LiproAuthError, LiproConnectionError
from homeassistant.exceptions import ConfigEntryAuthFailed
from homeassistant.helpers.update_coordinator import UpdateFailed
from tests.conftest_shared import (
    make_api_device,
    mock_anonymous_share_manager,
    refresh_and_sync_devices,
)

_CONFIG_ENTRY_DATA = {
    "phone": "13800000000",
    "password_hash": "e10adc3949ba59abbe56e057f20f883e",
    "phone_id": "test-phone-id",
    "access_token": "test_token",
    "refresh_token": "test_refresh",
    "user_id": 10001,
}


class _Entity:
    """Simple entity stub with identity-based equality semantics."""

    def __init__(self, entity_id: str, device) -> None:
        self.entity_id = entity_id
        self.device = device


@pytest.fixture
def coordinator(hass, mock_lipro_api_client, mock_auth_manager):
    """Create coordinator with mocked dependencies."""
    entry = MockConfigEntry(
        domain=DOMAIN,
        data=_CONFIG_ENTRY_DATA,
        options={},
        unique_id="lipro_10001",
    )
    entry.add_to_hass(hass)
    with patch(
        "custom_components.lipro.core.anonymous_share.get_anonymous_share_manager"
    ) as mock_share:
        mock_share.return_value = mock_anonymous_share_manager()
        from custom_components.lipro.core.coordinator import Coordinator

        return Coordinator(hass, mock_lipro_api_client, mock_auth_manager, entry)


# =========================================================================
# Service Layer Tests
# =========================================================================


class TestCoordinatorServices:
    """Test coordinator service layer."""

    @pytest.mark.asyncio
    async def test_device_refresh_service_provides_devices(
        self, coordinator, mock_lipro_api_client
    ):
        """Test device refresh service provides device access."""
        mock_lipro_api_client.get_device_list.return_value = {
            "data": [make_api_device(serial="03ab5ccd7c000001")],
            "hasMore": False,
        }

        with patch(
            "custom_components.lipro.core.anonymous_share.get_anonymous_share_manager"
        ) as mock_share:
            mock_share.return_value = mock_anonymous_share_manager()
            await refresh_and_sync_devices(coordinator)

        devices = coordinator.device_refresh_service.devices
        assert len(devices) == 1
        assert "03ab5ccd7c000001" in devices

    @pytest.mark.asyncio
    async def test_device_refresh_service_get_device_by_id(
        self, coordinator, mock_lipro_api_client
    ):
        """Test device lookup by ID through service layer."""
        mock_lipro_api_client.get_device_list.return_value = {
            "data": [make_api_device(serial="03ab5ccd7c000001")],
            "hasMore": False,
        }

        with patch(
            "custom_components.lipro.core.anonymous_share.get_anonymous_share_manager"
        ) as mock_share:
            mock_share.return_value = mock_anonymous_share_manager()
            await refresh_and_sync_devices(coordinator)

        device = coordinator.device_refresh_service.get_device_by_id("03ab5ccd7c000001")
        assert device is not None
        assert device.serial == "03ab5ccd7c000001"

    @pytest.mark.asyncio
    async def test_state_service_provides_device_access(
        self, coordinator, mock_lipro_api_client
    ):
        """Test state service provides device access."""
        mock_lipro_api_client.get_device_list.return_value = {
            "data": [make_api_device(serial="03ab5ccd7c000001")],
            "hasMore": False,
        }

        with patch(
            "custom_components.lipro.core.anonymous_share.get_anonymous_share_manager"
        ) as mock_share:
            mock_share.return_value = mock_anonymous_share_manager()
            await refresh_and_sync_devices(coordinator)

        devices = coordinator.state_service.devices
        assert len(devices) == 1
        assert "03ab5ccd7c000001" in devices


# =========================================================================
# Runtime Component Tests
# =========================================================================


class TestCoordinatorRuntimeComponents:
    """Test coordinator runtime components."""

    def test_coordinator_keeps_internal_runtime_registry(self, coordinator):
        """Coordinator should keep runtimes internal behind one registry."""
        assert hasattr(coordinator, "_runtimes")
        assert hasattr(coordinator._runtimes, "device")
        assert hasattr(coordinator._runtimes, "status")
        assert hasattr(coordinator._runtimes, "state")
        assert hasattr(coordinator._runtimes, "command")
        assert hasattr(coordinator._runtimes, "mqtt")

    def test_coordinator_has_service_layer(self, coordinator):
        """Test coordinator exposes formal service layer."""
        assert hasattr(coordinator, "auth_service")
        assert hasattr(coordinator, "device_refresh_service")
        assert hasattr(coordinator, "state_service")
        assert hasattr(coordinator, "command_service")
        assert hasattr(coordinator, "mqtt_service")
        assert hasattr(coordinator, "telemetry_service")
        assert hasattr(coordinator, "signal_service")

    def test_group_reconciliation_callback_records_signal_and_requests_refresh(
        self, coordinator
    ) -> None:
        coordinator._runtimes.device.request_force_refresh = MagicMock()

        coordinator.signal_service.schedule_group_reconciliation("Group 1", 2.0)

        assert coordinator.telemetry_service.build_snapshot()["signals"] == {
            "connect_state_event_count": 0,
            "group_reconciliation_request_count": 1,
            "recent_connect_state_events": [],
            "recent_group_reconciliation_requests": [
                {"device_name": "Group 1", "timestamp": 2.0}
            ],
        }
        coordinator._runtimes.device.request_force_refresh.assert_called_once_with()

    def test_connect_state_callback_records_signal(self, coordinator) -> None:
        coordinator.signal_service.record_connect_state("dev1", 1.5, True)

        assert coordinator.telemetry_service.build_snapshot()["signals"] == {
            "connect_state_event_count": 1,
            "group_reconciliation_request_count": 0,
            "recent_connect_state_events": [
                {"device_serial": "dev1", "timestamp": 1.5, "is_online": True}
            ],
            "recent_group_reconciliation_requests": [],
        }

    @pytest.mark.asyncio
    async def test_async_shutdown_releases_runtime_resources(self, coordinator) -> None:
        """Coordinator shutdown should stop MQTT and clear owned resources."""
        coordinator._runtimes.mqtt.clear_disconnect_notification = AsyncMock()
        coordinator._runtimes.mqtt.disconnect = AsyncMock()
        coordinator._runtimes.mqtt.reset = MagicMock()
        coordinator._runtimes.device.reset = MagicMock()
        coordinator._state.background_task_manager.cancel_all = AsyncMock()
        coordinator.client.attach_mqtt_facade = MagicMock()
        coordinator._runtimes.mqtt.detach_transport = MagicMock()

        with (
            patch(
                "custom_components.lipro.core.coordinator.coordinator.CoordinatorCommandService.async_shutdown",
                new_callable=AsyncMock,
            ) as command_shutdown,
            patch(
                "custom_components.lipro.core.coordinator.coordinator.DataUpdateCoordinator.async_shutdown",
                new_callable=AsyncMock,
            ) as base_shutdown,
        ):
            await coordinator.async_shutdown()

        coordinator._runtimes.mqtt.clear_disconnect_notification.assert_awaited_once()
        command_shutdown.assert_awaited_once()
        coordinator._runtimes.mqtt.disconnect.assert_awaited_once()
        coordinator._state.background_task_manager.cancel_all.assert_awaited_once()
        coordinator._runtimes.mqtt.reset.assert_called_once()
        coordinator._runtimes.device.reset.assert_called_once()
        coordinator.client.attach_mqtt_facade.assert_called_once_with(None)
        coordinator._runtimes.mqtt.detach_transport.assert_called_once()
        base_shutdown.assert_awaited_once()

    @pytest.mark.asyncio
    async def test_public_entrypoints_follow_current_device_state(
        self, coordinator, mock_lipro_api_client
    ):
        """Test public coordinator entrypoints expose the current device state."""
        serial = "03ab5ccd7c000001"
        mock_lipro_api_client.get_device_list.return_value = {
            "data": [make_api_device(serial=serial)],
            "hasMore": False,
        }

        with patch(
            "custom_components.lipro.core.anonymous_share.get_anonymous_share_manager"
        ) as mock_share:
            mock_share.return_value = mock_anonymous_share_manager()
            await refresh_and_sync_devices(coordinator)

        device = coordinator.get_device(serial)

        assert device is not None
        assert coordinator.get_device_by_id(serial) is device
        assert coordinator.get_device_lock(serial) is coordinator.get_device_lock(serial)

    @pytest.mark.asyncio
    async def test_apply_properties_update_skips_stale_pending_values(
        self, coordinator
    ):
        """Stale MQTT payloads should be filtered before hitting the state runtime."""
        device = MagicMock(serial="dev1")
        coordinator._runtimes.command.filter_pending_state_properties = MagicMock(return_value={})
        coordinator._runtimes.command.observe_state_confirmation = MagicMock()
        coordinator._runtimes.state.apply_properties_update = AsyncMock(return_value=True)

        changed = await coordinator._apply_properties_update(
            device,
            {"powerState": "0"},
            "mqtt",
        )

        assert changed is False
        coordinator._runtimes.command.filter_pending_state_properties.assert_called_once_with(
            device_serial="dev1",
            properties={"powerState": "0"},
        )
        coordinator._runtimes.command.observe_state_confirmation.assert_not_called()
        coordinator._runtimes.state.apply_properties_update.assert_not_awaited()

    @pytest.mark.asyncio
    async def test_apply_properties_update_observes_confirmation_before_state_write(
        self, coordinator
    ):
        """Confirmed state updates should feed command-latency learning before write-through."""
        device = MagicMock(serial="dev1")
        coordinator._runtimes.command.filter_pending_state_properties = MagicMock(
            return_value={"powerState": "1"}
        )
        coordinator._runtimes.command.observe_state_confirmation = MagicMock(return_value=0.5)
        coordinator._runtimes.state.apply_properties_update = AsyncMock(return_value=True)

        changed = await coordinator._apply_properties_update(
            device,
            {"powerState": "1"},
            "mqtt",
        )

        assert changed is True
        coordinator._runtimes.command.observe_state_confirmation.assert_called_once_with(
            device_serial="dev1",
            properties={"powerState": "1"},
        )
        coordinator._runtimes.state.apply_properties_update.assert_awaited_once_with(
            device,
            {"powerState": "1"},
            source="mqtt",
        )

    @pytest.mark.asyncio
    async def test_async_refresh_devices_syncs_snapshot_and_notifies_listeners(
        self, coordinator
    ):
        """Force refresh should sync the snapshot, MQTT subscriptions, and listeners."""
        device = MagicMock()
        snapshot = MagicMock(devices={"dev1": device})
        coordinator._runtimes.device.refresh_devices = AsyncMock(return_value=snapshot)
        coordinator._runtimes.mqtt.bind_transport(MagicMock())
        coordinator.async_set_updated_data = MagicMock()

        with patch.object(
            type(coordinator.mqtt_service),
            "async_sync_subscriptions",
            new_callable=AsyncMock,
        ) as sync_subscriptions:
            result = await coordinator.async_refresh_devices()

        coordinator._runtimes.device.refresh_devices.assert_awaited_once_with(force=True)
        sync_subscriptions.assert_awaited_once()
        coordinator.async_set_updated_data.assert_called_once_with(coordinator.devices)
        assert result == {"dev1": device}
        assert coordinator.devices == {"dev1": device}

    @pytest.mark.asyncio
    async def test_status_runtime_updates_device_through_coordinator_callbacks(
        self, coordinator, mock_lipro_api_client
    ):
        """Test status polling updates coordinator-managed device state."""
        serial = "03ab5ccd7c000001"
        mock_lipro_api_client.get_device_list.return_value = {
            "data": [make_api_device(serial=serial)],
            "hasMore": False,
        }
        coordinator.client.query_device_status = MagicMock(return_value=None)

        with patch(
            "custom_components.lipro.core.anonymous_share.get_anonymous_share_manager"
        ) as mock_share:
            mock_share.return_value = mock_anonymous_share_manager()
            await refresh_and_sync_devices(coordinator)

        device = coordinator.get_device(serial)
        assert device is not None
        coordinator.client.query_device_status = AsyncMock(
            return_value=[
                {"iotId": serial, "powerState": "1"},
                {"ignored": True},
            ]
        )

        result = await coordinator._runtimes.status.execute_status_query([serial, "skip"])

        assert result["updated_count"] == 1
        assert result["error"] is None
        assert device.properties["powerState"] == "1"

    @pytest.mark.asyncio
    async def test_status_runtime_respects_pending_state_filter(
        self, coordinator, mock_lipro_api_client
    ) -> None:
        """REST status polling should still pass through coordinator confirmation filtering."""
        serial = "03ab5ccd7c000001"
        mock_lipro_api_client.get_device_list.return_value = {
            "data": [make_api_device(serial=serial)],
            "hasMore": False,
        }
        coordinator.client.query_device_status = MagicMock(return_value=None)

        with patch(
            "custom_components.lipro.core.anonymous_share.get_anonymous_share_manager"
        ) as mock_share:
            mock_share.return_value = mock_anonymous_share_manager()
            await refresh_and_sync_devices(coordinator)

        device = coordinator.get_device(serial)
        assert device is not None
        coordinator.client.query_device_status = AsyncMock(
            return_value=[{"iotId": serial, "powerState": "1"}]
        )
        coordinator._runtimes.command.filter_pending_state_properties = MagicMock(
            return_value={}
        )
        coordinator._runtimes.command.observe_state_confirmation = MagicMock()

        result = await coordinator._runtimes.status.execute_status_query([serial])

        assert result["updated_count"] == 0
        assert result["error"] is None
        assert device.properties.get("powerState") != "1"
        coordinator._runtimes.command.filter_pending_state_properties.assert_called_once_with(
            device_serial=serial,
            properties={"powerState": "1"},
        )
        coordinator._runtimes.command.observe_state_confirmation.assert_not_called()

    @pytest.mark.asyncio
    async def test_async_run_status_polling_refreshes_due_outlet_power(
        self, coordinator, mock_lipro_api_client
    ) -> None:
        """Outlet power polling should run on the coordinator main status path."""
        serial = "03ab5ccd7c000006"
        mock_lipro_api_client.get_device_list.return_value = {
            "data": [
                make_api_device(
                    serial=serial,
                    device_type=6,
                    iot_name="lipro_outlet",
                    physical_model="outlet",
                )
            ],
            "hasMore": False,
        }
        mock_lipro_api_client.fetch_outlet_power_info = AsyncMock(
            return_value={"nowPower": 12.5}
        )

        with patch(
            "custom_components.lipro.core.anonymous_share.get_anonymous_share_manager"
        ) as mock_share:
            mock_share.return_value = mock_anonymous_share_manager()
            await refresh_and_sync_devices(coordinator)

        device = coordinator.get_device(serial)
        assert device is not None
        coordinator._runtimes.status.filter_query_candidates = MagicMock(return_value=[])
        coordinator._runtimes.status.should_query_power = MagicMock(return_value=True)
        coordinator._runtimes.status.get_outlet_power_query_slice = MagicMock(
            return_value=[serial]
        )
        coordinator._runtimes.status.mark_power_query_complete = MagicMock()
        coordinator._runtimes.status.advance_outlet_power_cycle = MagicMock()

        await coordinator._async_run_status_polling()

        assert device.outlet_power_info is not None
        assert device.outlet_power_info["nowPower"] == 12.5
        assert "power_info" not in device.extra_data
        mock_lipro_api_client.fetch_outlet_power_info.assert_awaited_once_with(serial)
        coordinator._runtimes.status.mark_power_query_complete.assert_called_once_with()
        coordinator._runtimes.status.advance_outlet_power_cycle.assert_called_once_with(
            [serial]
        )

    @pytest.mark.asyncio
    async def test_async_send_command_surfaces_reauth_when_auth_expires(
        self, coordinator, mock_lipro_api_client
    ):
        """Test public command dispatch triggers reauth on auth failures."""
        serial = "03ab5ccd7c000001"
        mock_lipro_api_client.get_device_list.return_value = {
            "data": [make_api_device(serial=serial)],
            "hasMore": False,
        }
        mock_lipro_api_client.send_command.side_effect = LiproAuthError("Auth failed")

        with patch(
            "custom_components.lipro.core.anonymous_share.get_anonymous_share_manager"
        ) as mock_share:
            mock_share.return_value = mock_anonymous_share_manager()
            await refresh_and_sync_devices(coordinator)

        device = coordinator.get_device(serial)
        assert device is not None

        with pytest.raises(ConfigEntryAuthFailed, match="auth_error"):
            await coordinator.async_send_command(device, "POWER_ON")


class TestCoordinatorEntityLifecycle:
    """Test public entity lifecycle behavior exposed by the coordinator."""

    @pytest.mark.asyncio
    async def test_register_entity_tracks_device_subscription_once(
        self, coordinator, mock_lipro_api_client
    ):
        """Test registering an entity exposes it once for later state updates."""
        serial = "03ab5ccd7c000001"
        mock_lipro_api_client.get_device_list.return_value = {
            "data": [make_api_device(serial=serial)],
            "hasMore": False,
        }

        with patch(
            "custom_components.lipro.core.anonymous_share.get_anonymous_share_manager"
        ) as mock_share:
            mock_share.return_value = mock_anonymous_share_manager()
            await refresh_and_sync_devices(coordinator)

        device = coordinator.get_device(serial)
        assert device is not None
        entity = _Entity("light.test_device", device)

        coordinator.register_entity(entity)
        coordinator.register_entity(entity)

        assert coordinator._runtimes.state.get_entities_for_device(serial) == [entity]

    @pytest.mark.asyncio
    async def test_register_entity_accepts_non_canonical_device_identifier(
        self, coordinator, mock_lipro_api_client
    ):
        """Test entity registration still works when the entity reports a formatted serial."""
        serial = "03ab5ccd7c000001"
        mock_lipro_api_client.get_device_list.return_value = {
            "data": [make_api_device(serial=serial)],
            "hasMore": False,
        }

        with patch(
            "custom_components.lipro.core.anonymous_share.get_anonymous_share_manager"
        ) as mock_share:
            mock_share.return_value = mock_anonymous_share_manager()
            await refresh_and_sync_devices(coordinator)

        entity = _Entity(
            "light.test_device_alias",
            MagicMock(serial=f" {serial.upper()} "),
        )

        coordinator.register_entity(entity)

        assert coordinator._runtimes.state.get_entities_for_device(serial) == [entity]

        coordinator.unregister_entity(entity)

        assert coordinator._runtimes.state.get_entities_for_device(serial) == []

    def test_register_entity_ignores_missing_entity_id(self, coordinator):
        """Test registering an anonymous entity is a no-op."""
        coordinator.register_entity(_Entity("", MagicMock(serial="03ab5ccd7c000001")))

        assert coordinator._runtimes.state.get_entity_count() == 0

    @pytest.mark.asyncio
    async def test_unregister_entity_keeps_active_entity_until_matching_instance_removed(
        self, coordinator, mock_lipro_api_client
    ):
        """Test unregistering a stale entity instance does not drop the live one."""
        serial = "03ab5ccd7c000001"
        mock_lipro_api_client.get_device_list.return_value = {
            "data": [make_api_device(serial=serial)],
            "hasMore": False,
        }

        with patch(
            "custom_components.lipro.core.anonymous_share.get_anonymous_share_manager"
        ) as mock_share:
            mock_share.return_value = mock_anonymous_share_manager()
            await refresh_and_sync_devices(coordinator)

        device = coordinator.get_device(serial)
        assert device is not None
        active_entity = _Entity("light.test_device", device)
        stale_entity = _Entity("light.test_device", device)

        coordinator.register_entity(active_entity)
        coordinator.unregister_entity(stale_entity)

        assert coordinator._runtimes.state.get_entities_for_device(serial) == [active_entity]

        coordinator.unregister_entity(active_entity)

        assert coordinator._runtimes.state.get_entities_for_device(serial) == []

    def test_unregister_entity_ignores_missing_entity_id(self, coordinator):
        """Test unregistering an anonymous entity is a no-op."""
        coordinator.unregister_entity(_Entity("", MagicMock(serial="03ab5ccd7c000001")))

        assert coordinator._runtimes.state.get_entity_count() == 0


# =========================================================================
# Update Flow Tests
# =========================================================================


class TestCoordinatorUpdateFlow:
    """Test coordinator update flow."""

    @pytest.mark.asyncio
    async def test_update_calls_auth_check(
        self, coordinator, mock_lipro_api_client, mock_auth_manager
    ):
        """Test update flow calls authentication check."""
        mock_lipro_api_client.get_device_list.return_value = {
            "data": [make_api_device()],
            "hasMore": False,
        }

        with patch(
            "custom_components.lipro.core.anonymous_share.get_anonymous_share_manager"
        ) as mock_share:
            mock_share.return_value = mock_anonymous_share_manager()
            await coordinator._async_update_data()

        mock_auth_manager.async_ensure_authenticated.assert_awaited()

    @pytest.mark.asyncio
    async def test_auth_error_raises_config_entry_auth_failed(
        self, coordinator, mock_auth_manager
    ):
        """Test auth error raises ConfigEntryAuthFailed."""
        mock_auth_manager.async_ensure_authenticated.side_effect = LiproAuthError(
            "Auth failed"
        )

        with pytest.raises(ConfigEntryAuthFailed):
            await coordinator._async_update_data()

    @pytest.mark.asyncio
    async def test_connection_error_raises_update_failed(
        self, coordinator, mock_auth_manager
    ):
        """Test connection error raises UpdateFailed."""
        mock_auth_manager.async_ensure_authenticated.side_effect = (
            LiproConnectionError("Connection failed")
        )

        with pytest.raises(UpdateFailed):
            await coordinator._async_update_data()

    @pytest.mark.asyncio
    async def test_timeout_error_raises_timeout_update_failed(
        self, coordinator, mock_auth_manager
    ):
        """Test update timeout is surfaced as a timeout-specific failure."""
        mock_auth_manager.async_ensure_authenticated.side_effect = TimeoutError()

        with pytest.raises(UpdateFailed, match="Update timeout"):
            await coordinator._async_update_data()

    @pytest.mark.asyncio
    async def test_unexpected_error_raises_generic_update_failed(
        self, coordinator, mock_auth_manager
    ):
        """Test unexpected update errors are mapped to a stable failure."""
        mock_auth_manager.async_ensure_authenticated.side_effect = RuntimeError("boom")

        with pytest.raises(UpdateFailed, match="Unexpected update failure"):
            await coordinator._async_update_data()
