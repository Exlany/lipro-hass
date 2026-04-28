"""Unit tests for DeviceRuntime component."""

from __future__ import annotations

from typing import Any, cast
from unittest.mock import AsyncMock, Mock

import pytest

from custom_components.lipro.core.auth import LiproAuthManager
from custom_components.lipro.core.coordinator.runtime.device.snapshot import (
    RuntimeSnapshotRefreshRejectedError,
)
from custom_components.lipro.core.coordinator.runtime.device_runtime import (
    DeviceRuntime,
)
from custom_components.lipro.core.device.identity_index import DeviceIdentityIndex
from custom_components.lipro.core.protocol import LiproProtocolFacade
from tests.conftest_shared import make_device_page


@pytest.fixture
def mock_client() -> Mock:
    """Create mock API client."""
    client = Mock(spec=LiproProtocolFacade)
    client.get_devices = AsyncMock(return_value={"devices": [], "total": 0})
    client.query_iot_devices = AsyncMock()
    client.query_group_devices = AsyncMock()
    client.query_outlet_devices = AsyncMock()
    client.query_mesh_group_status = AsyncMock(return_value=[])
    client.contracts = Mock()
    client.contracts.normalize_mesh_group_status_rows = Mock(
        side_effect=lambda rows: rows
    )
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
    mock_client: Mock,
    mock_auth_manager: LiproAuthManager,
    mock_device_identity_index: DeviceIdentityIndex,
) -> DeviceRuntime:
    """Create DeviceRuntime instance."""
    return DeviceRuntime(
        protocol=cast(LiproProtocolFacade, mock_client),
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
        mock_client: Mock,
        mock_auth_manager: LiproAuthManager,
        mock_device_identity_index: DeviceIdentityIndex,
    ) -> None:
        """Test initialization with minimal arguments."""
        runtime = DeviceRuntime(
            protocol=cast(LiproProtocolFacade, mock_client),
            auth_manager=mock_auth_manager,
            device_identity_index=mock_device_identity_index,
        )

        assert runtime._protocol is mock_client
        assert runtime._auth_manager is mock_auth_manager
        assert runtime._device_identity_index is mock_device_identity_index
        assert runtime._last_snapshot is None
        assert runtime._cloud_serials_last_seen == set()

    def test_init_with_filter_config(
        self,
        mock_client: Mock,
        mock_auth_manager: LiproAuthManager,
        mock_device_identity_index: DeviceIdentityIndex,
    ) -> None:
        """Test initialization with filter configuration."""
        filter_options = {
            "device_filter_home_mode": "include",
            "device_filter_home_list": "Home1,Home2",
        }

        runtime = DeviceRuntime(
            protocol=cast(LiproProtocolFacade, mock_client),
            auth_manager=mock_auth_manager,
            device_identity_index=mock_device_identity_index,
            filter_config_options=filter_options,
        )

        assert runtime._device_filter is not None


class TestDeviceRuntimeRefresh:
    """Test device refresh operations."""

    @pytest.mark.asyncio
    async def test_pagination_handling(
        self,
        device_runtime: DeviceRuntime,
        mock_client: Mock,
    ) -> None:
        """Test pagination across multiple pages."""
        mock_client.get_devices.side_effect = [
            make_device_page(
                [create_mock_device_data(device_id="dev1", serial="serial1")],
                total=2,
            ),
            make_device_page(
                [create_mock_device_data(device_id="dev2", serial="serial2")],
                total=2,
            ),
        ]

        snapshot = await device_runtime.refresh_devices()

        assert len(snapshot.devices) == 2
        assert "serial1" in snapshot.devices
        assert "serial2" in snapshot.devices
        assert mock_client.get_devices.await_count == 2

    @pytest.mark.asyncio
    async def test_full_refresh_enriches_mesh_group_metadata(
        self,
        device_runtime: DeviceRuntime,
        mock_client: Mock,
    ) -> None:
        """Full snapshot should backfill gateway/member topology for mesh groups."""
        group_serial = "mesh_group_10001"
        mock_client.get_devices.return_value = make_device_page(
            [
                create_mock_device_data(
                    device_id=group_serial,
                    serial=group_serial,
                    is_group=True,
                )
            ]
        )
        mock_client.query_mesh_group_status.return_value = [
            {
                "groupId": group_serial,
                "gatewayDeviceId": " 03AB0000000000A1 ",
                "devices": [
                    {"deviceId": "03ab0000000000a2"},
                    {"deviceId": "bad"},
                ],
            }
        ]

        snapshot = await device_runtime.refresh_devices()

        assert snapshot.devices[group_serial].extra_data["gateway_device_id"] == (
            "03ab0000000000a1"
        )
        assert snapshot.devices[group_serial].extra_data["group_member_ids"] == [
            "03ab0000000000a2"
        ]
        mock_client.query_mesh_group_status.assert_awaited_once_with([group_serial])

    @pytest.mark.asyncio
    async def test_device_categorization(
        self,
        device_runtime: DeviceRuntime,
        mock_client: Mock,
    ) -> None:
        """Test devices are categorized correctly."""
        mock_client.get_devices.return_value = make_device_page(
            [
                create_mock_device_data(
                    device_id="iot1", serial="s1", is_group=False, is_outlet=False
                ),
                create_mock_device_data(device_id="group1", serial="s2", is_group=True),
                create_mock_device_data(device_id="iot2", serial="s3", is_outlet=False),
            ]
        )

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
        mock_client: Mock,
    ) -> None:
        """Test stale device computation on first run."""
        mock_client.get_devices.return_value = make_device_page(
            [create_mock_device_data(device_id="dev1", serial="serial1")]
        )

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
        mock_client: Mock,
    ) -> None:
        """Test stale device tracking when device goes missing."""
        # First refresh with 2 devices
        mock_client.get_devices.return_value = make_device_page(
            [
                create_mock_device_data(device_id="dev1", serial="serial1"),
                create_mock_device_data(device_id="dev2", serial="serial2"),
            ]
        )
        snapshot1 = await device_runtime.refresh_devices()
        device_runtime.compute_stale_devices(current_snapshot=snapshot1)

        # Second refresh with only 1 device
        mock_client.get_devices.return_value = make_device_page(
            [
                create_mock_device_data(device_id="dev1", serial="serial1"),
            ]
        )
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
        mock_client: Mock,
    ) -> None:
        """Test device removal after threshold cycles."""
        # Initial refresh
        mock_client.get_devices.return_value = make_device_page(
            [
                create_mock_device_data(device_id="dev1", serial="serial1"),
                create_mock_device_data(device_id="dev2", serial="serial2"),
            ]
        )
        snapshot = await device_runtime.refresh_devices()
        device_runtime.compute_stale_devices(current_snapshot=snapshot)

        # Simulate 3 cycles with dev2 missing
        mock_client.get_devices.return_value = make_device_page(
            [create_mock_device_data(device_id="dev1", serial="serial1")]
        )

        for _ in range(3):
            device_runtime.request_force_refresh()
            snapshot = await device_runtime.refresh_devices()
            _missing_cycles, removable = device_runtime.compute_stale_devices(
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
        mock_client: Mock,
    ) -> None:
        """Test last snapshot is available after refresh."""
        mock_client.get_devices.return_value = make_device_page(
            [create_mock_device_data(device_id="dev1", serial="serial1")]
        )

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
        assert device_runtime.get_last_refresh_failure() is None
        assert device_runtime._cloud_serials_last_seen == set()
        assert device_runtime._refresh_strategy._force_refresh is False


class TestDeviceRuntimeErrorHandling:
    """Test error handling in DeviceRuntime."""

    @pytest.mark.asyncio
    async def test_api_error_during_refresh_rejects_without_snapshot(
        self,
        device_runtime: DeviceRuntime,
        mock_client: Mock,
    ) -> None:
        """API error without LKG must reject the refresh explicitly."""
        mock_client.get_devices.side_effect = RuntimeError("API Error")

        with pytest.raises(RuntimeSnapshotRefreshRejectedError) as exc_info:
            await device_runtime.refresh_devices()

        assert exc_info.value.stage == "fetch_page"
        assert exc_info.value.page == 1
        assert exc_info.value.kept_last_known_good is False
        assert device_runtime.get_last_snapshot() is None
        failure = device_runtime.get_last_refresh_failure()
        assert failure is not None
        assert failure.stage == "fetch_page"
        assert failure.kept_last_known_good is False

    @pytest.mark.asyncio
    async def test_partial_page_failure_rejects_without_lkg(
        self,
        device_runtime: DeviceRuntime,
        mock_client: Mock,
    ) -> None:
        """Page-2 failure without LKG must reject the refresh."""
        mock_client.get_devices.side_effect = [
            make_device_page(
                [create_mock_device_data(device_id="dev1", serial="serial1")],
                total=2,
            ),
            RuntimeError("Network error"),
        ]

        with pytest.raises(RuntimeSnapshotRefreshRejectedError) as exc_info:
            await device_runtime.refresh_devices()

        assert exc_info.value.stage == "fetch_page"
        assert exc_info.value.page == 2
        assert exc_info.value.kept_last_known_good is False
        assert device_runtime.get_last_snapshot() is None

    @pytest.mark.asyncio
    async def test_partial_page_failure_retains_last_known_good_and_refresh_pressure(
        self,
        device_runtime: DeviceRuntime,
        mock_client: Mock,
    ) -> None:
        """Rejected refresh keeps LKG and does not mark refresh as complete."""
        mock_client.get_devices.return_value = make_device_page(
            [create_mock_device_data(device_id="dev1", serial="serial1")]
        )

        first_snapshot = await device_runtime.refresh_devices()
        assert first_snapshot.devices["serial1"].serial == "serial1"

        device_runtime.request_force_refresh()
        mock_client.get_devices.side_effect = [
            make_device_page(
                [create_mock_device_data(device_id="dev1", serial="serial1")],
                total=2,
            ),
            RuntimeError("Network error"),
        ]

        with pytest.raises(RuntimeSnapshotRefreshRejectedError) as exc_info:
            await device_runtime.refresh_devices()

        assert exc_info.value.kept_last_known_good is True
        assert device_runtime.get_last_snapshot() is first_snapshot
        assert device_runtime.should_refresh_device_list() is True
        failure = device_runtime.get_last_refresh_failure()
        assert failure is not None
        assert failure.page == 2
        assert failure.kept_last_known_good is True


class TestDeviceRuntimeIntegration:
    """Integration tests for DeviceRuntime."""

    @pytest.mark.asyncio
    async def test_full_refresh_cycle(
        self,
        device_runtime: DeviceRuntime,
        mock_client: Mock,
        mock_device_identity_index: DeviceIdentityIndex,
    ) -> None:
        """Test complete refresh cycle with identity registration."""
        mock_client.get_devices.return_value = make_device_page(
            [
                create_mock_device_data(device_id="dev1", serial="serial1"),
            ]
        )

        snapshot = await device_runtime.refresh_devices()

        # Verify snapshot structure
        assert len(snapshot.devices) == 1
        assert snapshot.device_by_id["serial1"] is snapshot.devices["serial1"]
        assert snapshot.device_by_id["dev1"] is snapshot.devices["serial1"]
        assert snapshot.identity_aliases_by_serial["serial1"] == ("dev1", "serial1")
        assert "identity_aliases" not in snapshot.devices["serial1"].extra_data
        assert snapshot.cloud_serials == {"serial1"}

        snapshot = await device_runtime.refresh_devices()
        refreshed_snapshot = await device_runtime.refresh_devices()

        assert refreshed_snapshot is snapshot
        assert snapshot.devices["serial1"].serial == "serial1"
        mock_client.get_devices.assert_awaited_once()
