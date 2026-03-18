"""Integration tests for Lipro data update coordinator.

These tests exercise the real coordinator methods (_async_update_data,
device_runtime.refresh_devices, etc.) with mocked API responses,
verifying the coordinator's actual behavior.
"""

from __future__ import annotations

from unittest.mock import MagicMock, patch

import pytest
from pytest_homeassistant_custom_component.common import MockConfigEntry

from custom_components.lipro.const.api import MAX_DEVICES_PER_QUERY
from custom_components.lipro.core.api import (
    LiproApiError,
    LiproAuthError,
    LiproConnectionError,
    LiproRefreshTokenExpiredError,
)
from homeassistant.exceptions import ConfigEntryAuthFailed
from homeassistant.helpers.update_coordinator import UpdateFailed
from tests.conftest_shared import (
    make_api_device,
    make_device_page,
    refresh_and_sync_devices,
)

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

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
    """Create a real Coordinator wired to mock API/auth."""
    entry = MockConfigEntry(
        domain="lipro",
        data=_CONFIG_ENTRY_DATA,
        options={},
        unique_id="lipro_10001",
    )
    entry.add_to_hass(hass)
    with patch(
        "custom_components.lipro.core.anonymous_share.get_anonymous_share_manager"
    ) as mock_share:
        mock_share.return_value = MagicMock(is_enabled=False, set_enabled=MagicMock())
        from custom_components.lipro.core.coordinator import Coordinator

        return Coordinator(
            hass, mock_lipro_api_client, mock_auth_manager, entry
        )


# =========================================================================
# 1. _async_update_data happy-path flow
# =========================================================================


class TestCoordinatorUpdateFlow:
    """Test _async_update_data fetches devices on first call."""

    @pytest.mark.asyncio
    async def test_first_update_fetches_devices(
        self, coordinator, mock_lipro_api_client
    ):
        """First call should fetch devices from API."""
        mock_lipro_api_client.get_devices.return_value = make_device_page([
                make_api_device(serial="03ab5ccd7c000001", name="Light 1"),
            ])

        with patch(
            "custom_components.lipro.core.anonymous_share.get_anonymous_share_manager"
        ) as mock_share:
            mock_share.return_value = MagicMock(is_enabled=False)
            result = await coordinator._async_update_data()

        assert "03ab5ccd7c000001" in result
        mock_lipro_api_client.get_devices.assert_awaited_once_with(
            offset=0,
            limit=MAX_DEVICES_PER_QUERY,
        )

    @pytest.mark.asyncio
    async def test_second_update_skips_device_fetch(
        self, coordinator, mock_lipro_api_client
    ):
        """Subsequent calls should NOT re-fetch devices."""
        mock_lipro_api_client.get_devices.return_value = make_device_page([make_api_device(serial="03ab5ccd7c000001")])

        with patch(
            "custom_components.lipro.core.anonymous_share.get_anonymous_share_manager"
        ) as mock_share:
            mock_share.return_value = MagicMock(is_enabled=False)
            await coordinator._async_update_data()
            mock_lipro_api_client.get_devices.reset_mock()
            await coordinator._async_update_data()

        mock_lipro_api_client.get_devices.assert_not_awaited()

    @pytest.mark.asyncio
    async def test_periodic_update_refetches_device_list(
        self, coordinator, mock_lipro_api_client
    ):
        """Periodic refresh should re-fetch devices."""
        mock_lipro_api_client.get_devices.return_value = make_device_page([make_api_device(serial="03ab5ccd7c000001")])

        with patch(
            "custom_components.lipro.core.anonymous_share.get_anonymous_share_manager"
        ) as mock_share:
            mock_share.return_value = MagicMock(is_enabled=False)
            await coordinator._async_update_data()
            mock_lipro_api_client.get_devices.reset_mock()

            # Request force refresh
            coordinator.device_refresh_service.request_force_refresh()
            await coordinator._async_update_data()

        mock_lipro_api_client.get_devices.assert_awaited_once_with(
            offset=0,
            limit=MAX_DEVICES_PER_QUERY,
        )

    @pytest.mark.asyncio
    async def test_ensure_valid_token_called(
        self, coordinator, mock_lipro_api_client, mock_auth_manager
    ):
        """_async_update_data must call async_ensure_authenticated before anything else."""
        mock_lipro_api_client.get_devices.return_value = make_device_page([make_api_device()])

        with patch(
            "custom_components.lipro.core.anonymous_share.get_anonymous_share_manager"
        ) as mock_share:
            mock_share.return_value = MagicMock(is_enabled=False)
            await coordinator._async_update_data()

        mock_auth_manager.async_ensure_authenticated.assert_awaited()


# =========================================================================
# 2. device_runtime.refresh_devices — pagination, gateway filtering
# =========================================================================


class TestCoordinatorFetchDevices:
    """Test device_runtime.refresh_devices pagination and gateway filtering."""

    @pytest.mark.asyncio
    async def test_single_page(self, coordinator, mock_lipro_api_client):
        """Fewer than MAX_DEVICES_PER_QUERY devices should require one page."""
        devices = [make_api_device(serial=f"03ab5ccd7c{i:06x}") for i in range(3)]
        mock_lipro_api_client.get_devices.return_value = make_device_page(devices)

        with patch(
            "custom_components.lipro.core.anonymous_share.get_anonymous_share_manager"
        ) as mock_share:
            mock_share.return_value = MagicMock(is_enabled=False)
            await refresh_and_sync_devices(coordinator)

        assert len(coordinator.devices) == 3
        mock_lipro_api_client.get_devices.assert_awaited_once_with(
            offset=0,
            limit=MAX_DEVICES_PER_QUERY,
        )

    @pytest.mark.asyncio
    async def test_pagination_multiple_pages(self, coordinator, mock_lipro_api_client):
        """When first page is full, coordinator should request a second page."""
        page1 = [
            make_api_device(serial=f"03ab5ccd7c{i:06x}")
            for i in range(MAX_DEVICES_PER_QUERY)
        ]
        page2 = [make_api_device(serial=f"03ab5ccd7d{i:06x}") for i in range(5)]
        mock_lipro_api_client.get_devices.side_effect = [
            make_device_page(page1, total=len(page1) + len(page2)),
            make_device_page(page2, total=len(page1) + len(page2)),
        ]

        with patch(
            "custom_components.lipro.core.anonymous_share.get_anonymous_share_manager"
        ) as mock_share:
            mock_share.return_value = MagicMock(is_enabled=False)
            await refresh_and_sync_devices(coordinator)

        assert len(coordinator.devices) == MAX_DEVICES_PER_QUERY + 5
        assert mock_lipro_api_client.get_devices.call_count == 2

    @pytest.mark.asyncio
    async def test_fetch_devices_rejects_malformed_devices_payload(
        self, coordinator, mock_lipro_api_client
    ):
        """Malformed devices payload must reject the refresh atomically."""
        mock_lipro_api_client.get_devices.return_value = make_device_page("invalid")

        with pytest.raises(Exception, match="stage=page_payload"):
            await refresh_and_sync_devices(coordinator)

        assert len(coordinator.devices) == 0

    @pytest.mark.asyncio
    async def test_fetch_devices_rejects_non_dict_rows_atomically(
        self, coordinator, mock_lipro_api_client
    ):
        """Non-dict rows must reject the full refresh atomically."""
        mock_lipro_api_client.get_devices.return_value = make_device_page([
                make_api_device(serial="03ab5ccd7c000001"),
                "bad-row",
                123,
            ])

        with pytest.raises(Exception, match="stage=page_row"):
            await refresh_and_sync_devices(coordinator)

        assert coordinator.devices == {}

    @pytest.mark.asyncio
    async def test_gateway_devices_filtered_out(
        self, coordinator, mock_lipro_api_client
    ):
        """Gateway devices must be excluded from the device dict."""
        devices = [
            make_api_device(serial="03ab5ccd7c000001", physical_model="light"),
            make_api_device(
                serial="03ab5ccd7c000002",
                physical_model="gateway",
                device_type=11,
            ),
        ]
        mock_lipro_api_client.get_devices.return_value = make_device_page(devices)

        with patch(
            "custom_components.lipro.core.anonymous_share.get_anonymous_share_manager"
        ) as mock_share:
            mock_share.return_value = MagicMock(is_enabled=False)
            await refresh_and_sync_devices(coordinator)

        assert len(coordinator.devices) == 1
        assert "03ab5ccd7c000001" in coordinator.devices
        assert "03ab5ccd7c000002" not in coordinator.devices


# =========================================================================
# 3. Error handling
# =========================================================================


class TestCoordinatorErrorHandling:
    """Test error handling in _async_update_data."""

    @pytest.mark.asyncio
    async def test_refresh_token_expired_raises_config_entry_auth_failed(
        self, coordinator, mock_auth_manager
    ):
        """LiproRefreshTokenExpiredError -> ConfigEntryAuthFailed."""
        mock_auth_manager.async_ensure_authenticated.side_effect = (
            LiproRefreshTokenExpiredError("expired")
        )
        with pytest.raises(ConfigEntryAuthFailed):
            await coordinator._async_update_data()

    @pytest.mark.asyncio
    async def test_auth_error_raises_config_entry_auth_failed(
        self, coordinator, mock_auth_manager
    ):
        """LiproAuthError -> ConfigEntryAuthFailed."""
        mock_auth_manager.async_ensure_authenticated.side_effect = LiproAuthError(
            "unauthorized"
        )
        with pytest.raises(ConfigEntryAuthFailed):
            await coordinator._async_update_data()

    @pytest.mark.asyncio
    async def test_connection_error_raises_update_failed(
        self, coordinator, mock_auth_manager
    ):
        """LiproConnectionError -> UpdateFailed."""
        mock_auth_manager.async_ensure_authenticated.side_effect = (
            LiproConnectionError("timeout")
        )
        with pytest.raises(UpdateFailed):
            await coordinator._async_update_data()

    @pytest.mark.asyncio
    async def test_api_error_raises_update_failed(
        self, coordinator, mock_lipro_api_client
    ):
        """LiproApiError during device fetch -> UpdateFailed."""
        mock_lipro_api_client.get_devices.side_effect = LiproApiError(
            "server error"
        )

        with patch(
            "custom_components.lipro.core.anonymous_share.get_anonymous_share_manager"
        ) as mock_share:
            mock_share.return_value = MagicMock(is_enabled=False)
            with pytest.raises(UpdateFailed, match="server error"):
                await coordinator._async_update_data()

    @pytest.mark.asyncio
    async def test_auth_error_during_fetch_raises_config_entry_auth_failed(
        self, coordinator, mock_lipro_api_client
    ):
        """LiproAuthError during get_devices -> ConfigEntryAuthFailed."""
        mock_lipro_api_client.get_devices.side_effect = LiproAuthError(
            "unauthorized"
        )

        with patch(
            "custom_components.lipro.core.anonymous_share.get_anonymous_share_manager"
        ) as mock_share:
            mock_share.return_value = MagicMock(is_enabled=False)
            with pytest.raises(ConfigEntryAuthFailed):
                await coordinator._async_update_data()


    @pytest.mark.asyncio
    async def test_rejected_refresh_keeps_last_known_good_state(
        self, coordinator, mock_lipro_api_client
    ):
        """Rejected page-2 refresh must preserve current coordinator state."""
        serial = "03ab5ccd7c000001"
        mock_lipro_api_client.get_devices.return_value = make_device_page(
            [make_api_device(serial=serial)]
        )

        with patch(
            "custom_components.lipro.core.anonymous_share.get_anonymous_share_manager"
        ) as mock_share:
            mock_share.return_value = MagicMock(is_enabled=False)
            await coordinator._async_update_data()

            coordinator.device_refresh_service.request_force_refresh()
            mock_lipro_api_client.get_devices.side_effect = [
                make_device_page([make_api_device(serial=serial)], total=2),
                Exception("Network error"),
            ]

            with pytest.raises(UpdateFailed, match="page=2"):
                await coordinator._async_update_data()

        assert set(coordinator.devices) == {serial}
        telemetry = coordinator.telemetry_service.build_snapshot()
        assert telemetry["last_runtime_failure_stage"] == "runtime"
        assert telemetry["failure_summary"]["error_type"] == (
            "RuntimeSnapshotRefreshRejectedError"
        )


# =========================================================================
# 4. Device refresh service
# =========================================================================


class TestCoordinatorRefreshDevices:
    """Test device refresh public API."""

    @pytest.mark.asyncio
    async def test_refresh_devices_requests_force_refresh(
        self, coordinator, mock_lipro_api_client
    ):
        """Requesting force refresh should cause next update to re-fetch devices."""
        mock_lipro_api_client.get_devices.return_value = make_device_page([make_api_device(serial="03ab5ccd7c000001")])

        with patch(
            "custom_components.lipro.core.anonymous_share.get_anonymous_share_manager"
        ) as mock_share:
            mock_share.return_value = MagicMock(is_enabled=False)
            # First update
            await coordinator._async_update_data()
            mock_lipro_api_client.get_devices.reset_mock()

            # Request force refresh via device runtime
            coordinator.device_refresh_service.request_force_refresh()

            # Next update should force refresh
            await coordinator._async_update_data()

        mock_lipro_api_client.get_devices.assert_awaited_once_with(
            offset=0,
            limit=MAX_DEVICES_PER_QUERY,
        )
