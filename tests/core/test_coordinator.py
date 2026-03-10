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

from tests.conftest_shared import make_api_device, mock_anonymous_share_manager, refresh_and_sync_devices


_CONFIG_ENTRY_DATA = {
    "phone": "13800000000",
    "password_hash": "e10adc3949ba59abbe56e057f20f883e",
    "phone_id": "test-phone-id",
    "access_token": "test_token",
    "refresh_token": "test_refresh",
    "user_id": 10001,
}


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
