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

    def test_coordinator_has_runtime_components(self, coordinator):
        """Test coordinator exposes runtime components."""
        assert hasattr(coordinator, "device_runtime")
        assert hasattr(coordinator, "status_runtime")
        assert hasattr(coordinator, "state_runtime")
        assert hasattr(coordinator, "command_runtime")
        assert hasattr(coordinator, "mqtt_runtime")

    def test_coordinator_has_service_layer(self, coordinator):
        """Test coordinator exposes service layer."""
        assert hasattr(coordinator, "device_refresh_service")
        assert hasattr(coordinator, "state_service")
        assert hasattr(coordinator, "command_service")
        assert hasattr(coordinator, "mqtt_service")

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
    async def test_status_runtime_updates_device_through_coordinator_callbacks(
        self, coordinator, mock_lipro_api_client
    ):
        """Test status polling updates coordinator-managed device state."""
        serial = "03ab5ccd7c000001"
        mock_lipro_api_client.get_device_list.return_value = {
            "data": [make_api_device(serial=serial)],
            "hasMore": False,
        }
        coordinator.client.status = MagicMock()
        coordinator.client.status.query_device_status = MagicMock()
        coordinator.client.status.query_device_status.return_value = None

        with patch(
            "custom_components.lipro.core.anonymous_share.get_anonymous_share_manager"
        ) as mock_share:
            mock_share.return_value = mock_anonymous_share_manager()
            await refresh_and_sync_devices(coordinator)

        device = coordinator.get_device(serial)
        assert device is not None
        coordinator.client.status.query_device_status = AsyncMock(
            return_value=[
                {"iotId": serial, "powerState": "1"},
                {"ignored": True},
            ]
        )

        result = await coordinator.status_runtime.execute_status_query([serial, "skip"])

        assert result["updated_count"] == 1
        assert result["error"] is None
        assert device.properties["powerState"] == "1"

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

        assert coordinator.state_runtime.get_entities_for_device(serial) == [entity]

    def test_register_entity_ignores_missing_entity_id(self, coordinator):
        """Test registering an anonymous entity is a no-op."""
        coordinator.register_entity(_Entity("", MagicMock(serial="03ab5ccd7c000001")))

        assert coordinator.state_runtime.get_entity_count() == 0

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

        assert coordinator.state_runtime.get_entities_for_device(serial) == [active_entity]

        coordinator.unregister_entity(active_entity)

        assert coordinator.state_runtime.get_entities_for_device(serial) == []

    def test_unregister_entity_ignores_missing_entity_id(self, coordinator):
        """Test unregistering an anonymous entity is a no-op."""
        coordinator.unregister_entity(_Entity("", MagicMock(serial="03ab5ccd7c000001")))

        assert coordinator.state_runtime.get_entity_count() == 0


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
