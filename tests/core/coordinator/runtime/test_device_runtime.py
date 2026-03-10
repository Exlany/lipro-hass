"""Unit tests for DeviceRuntime component."""

from __future__ import annotations

from typing import Any
from unittest.mock import AsyncMock, MagicMock, Mock

import pytest

from custom_components.lipro.core.api import LiproClient
from custom_components.lipro.core.auth import LiproAuthManager
from custom_components.lipro.core.coordinator.runtime.device_runtime import DeviceRuntime
from custom_components.lipro.core.device import LiproDevice
from custom_components.lipro.core.device.identity_index import DeviceIdentityIndex


@pytest.fixture
def mock_client() -> LiproClient:
    """Create mock API client."""
    client = Mock(spec=LiproClient)
    client.get_device_list = AsyncMock()
    client.query_iot_devices = AsyncMock()
    client.query_group_devices = AsyncMock()
    client.query_outlet_devices = AsyncMock()
    return client


@pytest.fixture
def mock_auth_manager() -> LiproAuthManager:
    """Create mock auth manager."""
    return Mock(spec=LiproAuthManager)


@pytest.fixture
def mock_device_identity_index() -> DeviceIdentityIndex:
    """Create mock device identity index."""
    index = Mock(spec=DeviceIdentityIndex)
    index.register_device = Mock()
    return index


@pytest.fixture
def device_runtime(
    mock_client: LiproClient,
    mock_auth_manager: LiproAuthManager,
    mock_device_identity_index: DeviceIdentityIndex,
) -> DeviceRuntime:
    """Create DeviceRuntime instance."""
    return DeviceRuntime(
        client=mock_client,
        auth_manager=mock_auth_manager,
        device_identity_index=mock_device_identity_index,
    )


def create_mock_device_data(
    *,
    device_id: str = "test_id",
    serial: str = "test_serial",
    model: str = "test_model",
    is_group: bool = False,
    is_outlet: bool = False,
) -> dict[str, Any]:
    """Create mock device API data."""
    # Determine category based on device type
    if is_outlet:
        category = "socket"  # DeviceCategory.OUTLET
    else:
        category = "light"  # DeviceCategory.LIGHT

    return {
        "id": device_id,
        "iotDeviceId": device_id,  # IoT device ID
        "deviceId": 12345,  # Device number (integer)
        "serial": serial,  # Serial number (string)
        "deviceName": f"Device {device_id}",  # Device name
        "model": model,
        "name": f"Device {device_id}",
        "online": True,
        "isGroup": is_group,
        "category": category,
        "homeId": "home_1",
        "homeName": "Test Home",
        "roomId": "room_1",
        "roomName": "Test Room",
        "type": 1,  # Device type
        "iotName": model,  # IoT name
    }


class TestDeviceRuntimeInitialization:
    """Test DeviceRuntime initialization."""

    def test_init_with_minimal_args(
        self,
        mock_client: LiproClient,
        mock_auth_manager: LiproAuthManager,
        mock_device_identity_index: DeviceIdentityIndex,
    ) -> None:
        """Test initialization with minimal arguments."""
        runtime = DeviceRuntime(
            client=mock_client,
            auth_manager=mock_auth_manager,
            device_identity_index=mock_device_identity_index,
        )

        assert runtime._client is mock_client
        assert runtime._auth_manager is mock_auth_manager
        assert runtime._device_identity_index is mock_device_identity_index
        assert runtime._last_snapshot is None
        assert runtime._cloud_serials_last_seen == set()

    def test_init_with_filter_config(
        self,
        mock_client: LiproClient,
        mock_auth_manager: LiproAuthManager,
        mock_device_identity_index: DeviceIdentityIndex,
    ) -> None:
        """Test initialization with filter configuration."""
        filter_options = {
            "device_filter_home_mode": "include",
            "device_filter_home_list": "Home1,Home2",
        }

        runtime = DeviceRuntime(
            client=mock_client,
            auth_manager=mock_auth_manager,
            device_identity_index=mock_device_identity_index,
            filter_config_options=filter_options,
        )

        assert runtime._device_filter is not None


class TestDeviceRuntimeRefresh:
    """Test device refresh operations."""

    @pytest.mark.asyncio
    async def test_first_refresh_is_full(
        self,
        device_runtime: DeviceRuntime,
        mock_client: LiproClient,
    ) -> None:
        """Test that first refresh always performs full fetch."""
        mock_client.get_device_list.return_value = {
            "data": [
                create_mock_device_data(device_id="dev1", serial="serial1"),
            ],
            "hasMore": False,
        }

        snapshot = await device_runtime.refresh_devices()

        assert snapshot is not None
        assert len(snapshot.devices) == 1
        assert "serial1" in snapshot.devices
        mock_client.get_device_list.assert_called_once()

    @pytest.mark.asyncio
    async def test_force_refresh_triggers_full_fetch(
        self,
        device_runtime: DeviceRuntime,
        mock_client: LiproClient,
    ) -> None:
        """Test force refresh triggers full device list fetch."""
        mock_client.get_device_list.return_value = {
            "data": [
                create_mock_device_data(device_id="dev1", serial="serial1"),
            ],
            "hasMore": False,
        }

        # First refresh
        await device_runtime.refresh_devices()
        mock_client.get_device_list.reset_mock()

        # Force refresh
        snapshot = await device_runtime.refresh_devices(force=True)

        assert snapshot is not None
        mock_client.get_device_list.assert_called_once()

    @pytest.mark.asyncio
    async def test_incremental_refresh_without_force(
        self,
        device_runtime: DeviceRuntime,
        mock_client: LiproClient,
    ) -> None:
        """Test incremental refresh when timing not elapsed."""
        mock_client.get_device_list.return_value = {
            "data": [
                create_mock_device_data(device_id="dev1", serial="serial1"),
            ],
            "hasMore": False,
        }
        mock_client.query_iot_devices.return_value = {"data": []}

        # First refresh (full)
        await device_runtime.refresh_devices()
        mock_client.get_device_list.reset_mock()

        # Second refresh (incremental)
        snapshot = await device_runtime.refresh_devices()

        assert snapshot is not None
        # Should not call get_device_list again
        mock_client.get_device_list.assert_not_called()
        # Should call incremental query
        mock_client.query_iot_devices.assert_called()

    @pytest.mark.asyncio
    async def test_pagination_handling(
        self,
        device_runtime: DeviceRuntime,
        mock_client: LiproClient,
    ) -> None:
        """Test pagination across multiple pages."""
        mock_client.get_device_list.side_effect = [
            {
                "data": [create_mock_device_data(device_id="dev1", serial="serial1")],
                "hasMore": True,
            },
            {
                "data": [create_mock_device_data(device_id="dev2", serial="serial2")],
                "hasMore": False,
            },
        ]

        snapshot = await device_runtime.refresh_devices()

        assert len(snapshot.devices) == 2
        assert "serial1" in snapshot.devices
        assert "serial2" in snapshot.devices
        assert mock_client.get_device_list.call_count == 2

    @pytest.mark.asyncio
    async def test_device_categorization(
        self,
        device_runtime: DeviceRuntime,
        mock_client: LiproClient,
    ) -> None:
        """Test devices are categorized correctly."""
        mock_client.get_device_list.return_value = {
            "data": [
                create_mock_device_data(device_id="iot1", serial="s1", is_group=False, is_outlet=False),
                create_mock_device_data(device_id="group1", serial="s2", is_group=True),
                create_mock_device_data(device_id="iot2", serial="s3", is_outlet=False),
            ],
            "hasMore": False,
        }

        snapshot = await device_runtime.refresh_devices()

        # Verify device IDs are in correct lists
        # Note: iot_device_id is actually the serial, not the id field
        assert "s1" in snapshot.iot_ids
        assert "s2" in snapshot.group_ids
        assert "s3" in snapshot.iot_ids
        # Note: outlet categorization depends on device_type mapping, not just is_outlet flag
        # With type=1, devices are categorized as lights, not outlets


class TestStaleDeviceReconciliation:
    """Test stale device tracking and reconciliation."""

    @pytest.mark.asyncio
    async def test_compute_stale_devices_first_run(
        self,
        device_runtime: DeviceRuntime,
        mock_client: LiproClient,
    ) -> None:
        """Test stale device computation on first run."""
        mock_client.get_device_list.return_value = {
            "data": [create_mock_device_data(device_id="dev1", serial="serial1")],
            "hasMore": False,
        }

        snapshot = await device_runtime.refresh_devices()
        missing_cycles, removable = device_runtime.compute_stale_devices(
            current_snapshot=snapshot
        )

        assert missing_cycles == {}
        assert removable == set()

    @pytest.mark.asyncio
    async def test_compute_stale_devices_missing_device(
        self,
        device_runtime: DeviceRuntime,
        mock_client: LiproClient,
    ) -> None:
        """Test stale device tracking when device goes missing."""
        # First refresh with 2 devices
        mock_client.get_device_list.return_value = {
            "data": [
                create_mock_device_data(device_id="dev1", serial="serial1"),
                create_mock_device_data(device_id="dev2", serial="serial2"),
            ],
            "hasMore": False,
        }
        snapshot1 = await device_runtime.refresh_devices()
        device_runtime.compute_stale_devices(current_snapshot=snapshot1)

        # Second refresh with only 1 device
        mock_client.get_device_list.return_value = {
            "data": [
                create_mock_device_data(device_id="dev1", serial="serial1"),
            ],
            "hasMore": False,
        }
        device_runtime.request_force_refresh()
        snapshot2 = await device_runtime.refresh_devices()
        missing_cycles, removable = device_runtime.compute_stale_devices(
            current_snapshot=snapshot2
        )

        assert "serial2" in missing_cycles
        assert missing_cycles["serial2"] == 1
        assert removable == set()  # Not yet at threshold

    @pytest.mark.asyncio
    async def test_stale_device_removal_threshold(
        self,
        device_runtime: DeviceRuntime,
        mock_client: LiproClient,
    ) -> None:
        """Test device removal after threshold cycles."""
        # Initial refresh
        mock_client.get_device_list.return_value = {
            "data": [
                create_mock_device_data(device_id="dev1", serial="serial1"),
                create_mock_device_data(device_id="dev2", serial="serial2"),
            ],
            "hasMore": False,
        }
        snapshot = await device_runtime.refresh_devices()
        device_runtime.compute_stale_devices(current_snapshot=snapshot)

        # Simulate 3 cycles with dev2 missing
        mock_client.get_device_list.return_value = {
            "data": [create_mock_device_data(device_id="dev1", serial="serial1")],
            "hasMore": False,
        }

        for _ in range(3):
            device_runtime.request_force_refresh()
            snapshot = await device_runtime.refresh_devices()
            missing_cycles, removable = device_runtime.compute_stale_devices(
                current_snapshot=snapshot
            )

        # After 3 cycles, should be removable
        assert "serial2" in removable


class TestDeviceRuntimeState:
    """Test runtime state management."""

    def test_request_force_refresh(self, device_runtime: DeviceRuntime) -> None:
        """Test force refresh request."""
        device_runtime.request_force_refresh()
        assert device_runtime._refresh_strategy._force_refresh is True

    def test_get_last_snapshot_initially_none(
        self, device_runtime: DeviceRuntime
    ) -> None:
        """Test last snapshot is None initially."""
        assert device_runtime.get_last_snapshot() is None

    @pytest.mark.asyncio
    async def test_get_last_snapshot_after_refresh(
        self,
        device_runtime: DeviceRuntime,
        mock_client: LiproClient,
    ) -> None:
        """Test last snapshot is available after refresh."""
        mock_client.get_device_list.return_value = {
            "data": [create_mock_device_data(device_id="dev1", serial="serial1")],
            "hasMore": False,
        }

        await device_runtime.refresh_devices()
        snapshot = device_runtime.get_last_snapshot()

        assert snapshot is not None
        assert len(snapshot.devices) == 1

    def test_reset_clears_state(self, device_runtime: DeviceRuntime) -> None:
        """Test reset clears all runtime state."""
        device_runtime._cloud_serials_last_seen = {"serial1"}
        device_runtime.request_force_refresh()

        device_runtime.reset()

        assert device_runtime._last_snapshot is None
        assert device_runtime._cloud_serials_last_seen == set()
        assert device_runtime._refresh_strategy._force_refresh is False


class TestDeviceRuntimeErrorHandling:
    """Test error handling in DeviceRuntime."""

    @pytest.mark.asyncio
    async def test_api_error_during_refresh(
        self,
        device_runtime: DeviceRuntime,
        mock_client: LiproClient,
    ) -> None:
        """Test API error handling during refresh."""
        mock_client.get_device_list.side_effect = Exception("API Error")

        # Should not raise, but return empty snapshot
        snapshot = await device_runtime.refresh_devices()

        # Snapshot should be minimal/empty due to error
        assert snapshot.devices == {}

    @pytest.mark.asyncio
    async def test_partial_page_failure(
        self,
        device_runtime: DeviceRuntime,
        mock_client: LiproClient,
    ) -> None:
        """Test handling of partial page fetch failure."""
        mock_client.get_device_list.side_effect = [
            {
                "data": [create_mock_device_data(device_id="dev1", serial="serial1")],
                "hasMore": True,
            },
            Exception("Network error"),
        ]

        snapshot = await device_runtime.refresh_devices()

        # Should have first page data
        assert len(snapshot.devices) == 1
        assert "serial1" in snapshot.devices


class TestDeviceRuntimeIntegration:
    """Integration tests for DeviceRuntime."""

    @pytest.mark.asyncio
    async def test_full_refresh_cycle(
        self,
        device_runtime: DeviceRuntime,
        mock_client: LiproClient,
        mock_device_identity_index: DeviceIdentityIndex,
    ) -> None:
        """Test complete refresh cycle with identity registration."""
        mock_client.get_device_list.return_value = {
            "data": [
                create_mock_device_data(device_id="dev1", serial="serial1"),
            ],
            "hasMore": False,
        }

        snapshot = await device_runtime.refresh_devices()

        # Verify snapshot structure
        assert len(snapshot.devices) == 1
        assert len(snapshot.device_by_id) == 1
        assert snapshot.cloud_serials == {"serial1"}
