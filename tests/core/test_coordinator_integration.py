"""Integration tests for coordinator update and device-refresh flows."""

from __future__ import annotations

import pytest

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

from tests.core.coordinator.conftest import (  # noqa: F401
    coordinator,
    patch_anonymous_share_manager,
)


class TestCoordinatorUpdateFlow:
    """Test real coordinator update flow with mocked collaborators."""

    @pytest.mark.asyncio
    async def test_first_update_fetches_devices(
        self,
        coordinator,
        mock_lipro_api_client,
        patch_anonymous_share_manager,
    ):
        """First call should fetch devices from API."""
        mock_lipro_api_client.get_devices.return_value = make_device_page(
            [make_api_device(serial="03ab5ccd7c000001", name="Light 1")]
        )

        result = await coordinator._async_update_data()

        assert "03ab5ccd7c000001" in result
        mock_lipro_api_client.get_devices.assert_awaited_once_with(
            offset=0,
            limit=MAX_DEVICES_PER_QUERY,
        )

    @pytest.mark.asyncio
    async def test_second_update_skips_device_fetch(
        self,
        coordinator,
        mock_lipro_api_client,
        patch_anonymous_share_manager,
    ):
        """Subsequent calls should not re-fetch devices."""
        mock_lipro_api_client.get_devices.return_value = make_device_page(
            [make_api_device(serial="03ab5ccd7c000001")]
        )

        await coordinator._async_update_data()
        mock_lipro_api_client.get_devices.reset_mock()

        await coordinator._async_update_data()

        mock_lipro_api_client.get_devices.assert_not_awaited()

    @pytest.mark.asyncio
    async def test_periodic_update_refetches_device_list(
        self,
        coordinator,
        mock_lipro_api_client,
        patch_anonymous_share_manager,
    ):
        """Periodic refresh should re-fetch devices."""
        mock_lipro_api_client.get_devices.return_value = make_device_page(
            [make_api_device(serial="03ab5ccd7c000001")]
        )

        await coordinator._async_update_data()
        mock_lipro_api_client.get_devices.reset_mock()

        coordinator.device_refresh_service.request_force_refresh()
        await coordinator._async_update_data()

        mock_lipro_api_client.get_devices.assert_awaited_once_with(
            offset=0,
            limit=MAX_DEVICES_PER_QUERY,
        )

    @pytest.mark.asyncio
    async def test_ensure_valid_token_called(
        self,
        coordinator,
        mock_lipro_api_client,
        mock_auth_manager,
        patch_anonymous_share_manager,
    ):
        """Coordinator must authenticate before updating anything else."""
        mock_lipro_api_client.get_devices.return_value = make_device_page(
            [make_api_device()]
        )

        await coordinator._async_update_data()

        mock_auth_manager.async_ensure_authenticated.assert_awaited()


class TestCoordinatorFetchDevices:
    """Test pagination, validation, and filtering in refresh_devices."""

    @pytest.mark.asyncio
    async def test_single_page(
        self,
        coordinator,
        mock_lipro_api_client,
        patch_anonymous_share_manager,
    ):
        """Fewer than MAX devices should require one page."""
        devices = [make_api_device(serial=f"03ab5ccd7c{i:06x}") for i in range(3)]
        mock_lipro_api_client.get_devices.return_value = make_device_page(devices)

        await refresh_and_sync_devices(coordinator)

        assert len(coordinator.devices) == 3
        mock_lipro_api_client.get_devices.assert_awaited_once_with(
            offset=0,
            limit=MAX_DEVICES_PER_QUERY,
        )

    @pytest.mark.asyncio
    async def test_pagination_multiple_pages(
        self,
        coordinator,
        mock_lipro_api_client,
        patch_anonymous_share_manager,
    ):
        """When the first page is full, a second page should be requested."""
        page1 = [
            make_api_device(serial=f"03ab5ccd7c{i:06x}")
            for i in range(MAX_DEVICES_PER_QUERY)
        ]
        page2 = [make_api_device(serial=f"03ab5ccd7d{i:06x}") for i in range(5)]
        mock_lipro_api_client.get_devices.side_effect = [
            make_device_page(page1, total=len(page1) + len(page2)),
            make_device_page(page2, total=len(page1) + len(page2)),
        ]

        await refresh_and_sync_devices(coordinator)

        assert len(coordinator.devices) == MAX_DEVICES_PER_QUERY + 5
        assert mock_lipro_api_client.get_devices.call_count == 2

    @pytest.mark.asyncio
    async def test_fetch_devices_rejects_malformed_devices_payload(
        self,
        coordinator,
        mock_lipro_api_client,
        patch_anonymous_share_manager,
    ):
        """Malformed devices payload must reject the refresh atomically."""
        mock_lipro_api_client.get_devices.return_value = make_device_page("invalid")

        with pytest.raises(Exception, match="stage=page_payload"):
            await refresh_and_sync_devices(coordinator)

        assert len(coordinator.devices) == 0

    @pytest.mark.asyncio
    async def test_fetch_devices_rejects_non_dict_rows_atomically(
        self,
        coordinator,
        mock_lipro_api_client,
        patch_anonymous_share_manager,
    ):
        """Non-dict rows must reject the full refresh atomically."""
        mock_lipro_api_client.get_devices.return_value = make_device_page(
            [
                make_api_device(serial="03ab5ccd7c000001"),
                "bad-row",
                123,
            ]
        )

        with pytest.raises(Exception, match="stage=page_row"):
            await refresh_and_sync_devices(coordinator)

        assert coordinator.devices == {}

    @pytest.mark.asyncio
    async def test_gateway_devices_filtered_out(
        self,
        coordinator,
        mock_lipro_api_client,
        patch_anonymous_share_manager,
    ):
        """Gateway devices must be excluded from the coordinator cache."""
        devices = [
            make_api_device(serial="03ab5ccd7c000001", physical_model="light"),
            make_api_device(
                serial="03ab5ccd7c000002",
                physical_model="gateway",
                device_type=11,
            ),
        ]
        mock_lipro_api_client.get_devices.return_value = make_device_page(devices)

        await refresh_and_sync_devices(coordinator)

        assert len(coordinator.devices) == 1
        assert "03ab5ccd7c000001" in coordinator.devices
        assert "03ab5ccd7c000002" not in coordinator.devices


class TestCoordinatorErrorHandling:
    """Test error handling in _async_update_data."""

    @pytest.mark.asyncio
    async def test_refresh_token_expired_raises_config_entry_auth_failed(
        self, coordinator, mock_auth_manager
    ):
        """Refresh token expiry should raise ConfigEntryAuthFailed."""
        mock_auth_manager.async_ensure_authenticated.side_effect = (
            LiproRefreshTokenExpiredError("expired")
        )

        with pytest.raises(ConfigEntryAuthFailed):
            await coordinator._async_update_data()

    @pytest.mark.asyncio
    async def test_auth_error_raises_config_entry_auth_failed(
        self, coordinator, mock_auth_manager
    ):
        """Auth errors should raise ConfigEntryAuthFailed."""
        mock_auth_manager.async_ensure_authenticated.side_effect = LiproAuthError(
            "unauthorized"
        )

        with pytest.raises(ConfigEntryAuthFailed):
            await coordinator._async_update_data()

    @pytest.mark.asyncio
    async def test_connection_error_raises_update_failed(
        self, coordinator, mock_auth_manager
    ):
        """Connection errors should raise UpdateFailed."""
        mock_auth_manager.async_ensure_authenticated.side_effect = (
            LiproConnectionError("timeout")
        )

        with pytest.raises(UpdateFailed):
            await coordinator._async_update_data()

    @pytest.mark.asyncio
    async def test_api_error_raises_update_failed(
        self,
        coordinator,
        mock_lipro_api_client,
        patch_anonymous_share_manager,
    ):
        """API errors during device fetch should raise UpdateFailed."""
        mock_lipro_api_client.get_devices.side_effect = LiproApiError("server error")

        with pytest.raises(UpdateFailed, match="server error"):
            await coordinator._async_update_data()

    @pytest.mark.asyncio
    async def test_auth_error_during_fetch_raises_config_entry_auth_failed(
        self,
        coordinator,
        mock_lipro_api_client,
        patch_anonymous_share_manager,
    ):
        """Auth errors during get_devices should raise ConfigEntryAuthFailed."""
        mock_lipro_api_client.get_devices.side_effect = LiproAuthError("unauthorized")

        with pytest.raises(ConfigEntryAuthFailed):
            await coordinator._async_update_data()

    @pytest.mark.asyncio
    async def test_rejected_refresh_keeps_last_known_good_state(
        self,
        coordinator,
        mock_lipro_api_client,
        patch_anonymous_share_manager,
    ):
        """Rejected page-2 refresh must preserve current coordinator state."""
        serial = "03ab5ccd7c000001"
        mock_lipro_api_client.get_devices.return_value = make_device_page(
            [make_api_device(serial=serial)]
        )

        await coordinator._async_update_data()

        coordinator.device_refresh_service.request_force_refresh()
        mock_lipro_api_client.get_devices.side_effect = [
            make_device_page([make_api_device(serial=serial)], total=2),
            RuntimeError("Network error"),
        ]

        with pytest.raises(UpdateFailed, match="page=2"):
            await coordinator._async_update_data()

        assert set(coordinator.devices) == {serial}
        telemetry = coordinator.telemetry_service.build_snapshot()
        assert telemetry["last_runtime_failure_stage"] == "runtime"
        assert telemetry["failure_summary"]["error_type"] == (
            "RuntimeSnapshotRefreshRejectedError"
        )


class TestCoordinatorRefreshDevices:
    """Test force-refresh behavior exposed through the service surface."""

    @pytest.mark.asyncio
    async def test_refresh_devices_requests_force_refresh(
        self,
        coordinator,
        mock_lipro_api_client,
        patch_anonymous_share_manager,
    ):
        """Requesting force refresh should re-fetch devices on next update."""
        mock_lipro_api_client.get_devices.return_value = make_device_page(
            [make_api_device(serial="03ab5ccd7c000001")]
        )

        await coordinator._async_update_data()
        mock_lipro_api_client.get_devices.reset_mock()

        coordinator.device_refresh_service.request_force_refresh()
        await coordinator._async_update_data()

        mock_lipro_api_client.get_devices.assert_awaited_once_with(
            offset=0,
            limit=MAX_DEVICES_PER_QUERY,
        )
