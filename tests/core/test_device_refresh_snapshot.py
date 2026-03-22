"""Tests for device-refresh snapshot building."""

from __future__ import annotations

from unittest.mock import AsyncMock, call, patch

import pytest

from custom_components.lipro.const.config import DEVICE_FILTER_MODE_INCLUDE
from custom_components.lipro.core.coordinator.runtime.device.filter import (
    DeviceFilter,
    DeviceFilterConfig,
    DeviceFilterRule,
)
from custom_components.lipro.core.coordinator.runtime.device.snapshot import (
    RuntimeSnapshotRefreshRejectedError,
    SnapshotBuilder,
)


@pytest.fixture
def mock_client():
    """Create mock protocol facade."""
    return AsyncMock()


@pytest.fixture
def mock_device_identity_index():
    """Create mock DeviceIdentityIndex."""
    from custom_components.lipro.core.device.identity_index import DeviceIdentityIndex

    return DeviceIdentityIndex()


@pytest.fixture
def snapshot_builder(mock_client, mock_device_identity_index):
    """Create SnapshotBuilder with mocked dependencies."""
    return SnapshotBuilder(
        protocol=mock_client,
        device_identity_index=mock_device_identity_index,
        device_filter=DeviceFilter(config=DeviceFilterConfig()),
    )


@pytest.mark.asyncio
async def test_snapshot_builder_build_full_snapshot_single_page(
    snapshot_builder, mock_client, make_device
):
    """Test building full snapshot with single page of devices."""
    mock_client.get_devices = AsyncMock(
        return_value={
            "devices": [
                {"serial": "03ab000000000001", "deviceName": "Device 1", "type": 1},
                {"serial": "03ab000000000002", "deviceName": "Device 2", "type": 1},
            ],
            "total": 2,
        }
    )

    with patch("custom_components.lipro.core.device.LiproDevice.from_api_data") as from_api:
        from_api.side_effect = lambda data: make_device(
            "light", serial=data["serial"], name=data["deviceName"]
        )

        snapshot = await snapshot_builder.build_full_snapshot()

    assert len(snapshot.devices) == 2
    assert "03ab000000000001" in snapshot.devices
    assert "03ab000000000002" in snapshot.devices
    assert len(snapshot.cloud_serials) == 2
    mock_client.get_devices.assert_awaited_once_with(offset=0, limit=100)


@pytest.mark.asyncio
async def test_snapshot_builder_build_full_snapshot_multiple_pages(
    snapshot_builder, mock_client, make_device
):
    """Test building full snapshot with pagination."""
    mock_client.get_devices = AsyncMock(
        side_effect=[
            {
                "devices": [
                    {"serial": "03ab000000000001", "deviceName": "Device 1", "type": 1}
                ],
                "total": 2,
            },
            {
                "devices": [
                    {"serial": "03ab000000000002", "deviceName": "Device 2", "type": 1}
                ],
                "total": 2,
            },
        ]
    )

    with patch("custom_components.lipro.core.device.LiproDevice.from_api_data") as from_api:
        from_api.side_effect = lambda data: make_device(
            "light", serial=data["serial"], name=data["deviceName"]
        )

        snapshot = await snapshot_builder.build_full_snapshot()

    assert len(snapshot.devices) == 2
    assert mock_client.get_devices.await_args_list == [
        call(offset=0, limit=100),
        call(offset=100, limit=100),
    ]


@pytest.mark.asyncio
async def test_snapshot_builder_applies_device_filter(
    mock_client, mock_device_identity_index, make_device
):
    """Test that SnapshotBuilder applies device filter."""
    snapshot_builder = SnapshotBuilder(
        protocol=mock_client,
        device_identity_index=mock_device_identity_index,
        device_filter=DeviceFilter(
            config=DeviceFilterConfig(
                did=DeviceFilterRule(
                    mode=DEVICE_FILTER_MODE_INCLUDE,
                    values=frozenset({"03ab000000000001"}),
                )
            )
        ),
    )

    mock_client.get_devices = AsyncMock(
        return_value={
            "devices": [
                {"serial": "03ab000000000001", "deviceName": "Device 1", "type": 1},
                {"serial": "03ab000000000002", "deviceName": "Device 2", "type": 1},
            ],
            "total": 2,
        }
    )

    with patch("custom_components.lipro.core.device.LiproDevice.from_api_data") as from_api:
        from_api.side_effect = lambda data: make_device(
            "light", serial=data["serial"], name=data["deviceName"]
        )

        snapshot = await snapshot_builder.build_full_snapshot()

    assert len(snapshot.devices) == 1
    assert "03ab000000000001" in snapshot.devices
    assert "03ab000000000002" not in snapshot.devices


@pytest.mark.asyncio
async def test_snapshot_builder_categorizes_devices_by_type(
    snapshot_builder, mock_client, make_device
):
    """Test that devices are categorized into iot_ids, group_ids, outlet_ids."""
    mock_client.get_devices = AsyncMock(
        return_value={
            "devices": [
                {"serial": "light1", "deviceName": "Light", "type": 1},
                {"serial": "group1", "deviceName": "Group", "type": 1},
                {"serial": "outlet1", "deviceName": "Outlet", "type": 6},
            ],
            "total": 3,
        }
    )

    with patch("custom_components.lipro.core.device.LiproDevice.from_api_data") as from_api:

        def make_device_by_serial(data):
            serial = data["serial"]
            if serial == "light1":
                return make_device("light", serial=serial)
            if serial == "group1":
                return make_device("light", serial=serial, is_group=True)
            return make_device("outlet", serial=serial)

        from_api.side_effect = make_device_by_serial

        snapshot = await snapshot_builder.build_full_snapshot()

    assert "light1" in snapshot.iot_ids
    assert "group1" in snapshot.group_ids
    assert "outlet1" in snapshot.outlet_ids


@pytest.mark.asyncio
async def test_snapshot_builder_rejects_parse_errors_atomically(
    snapshot_builder, mock_client
):
    """Device parse failure must reject the full snapshot atomically."""
    mock_client.get_devices = AsyncMock(
        return_value={
            "devices": [
                {"serial": "03ab000000000001", "deviceName": "Valid Device", "type": 1},
                {"serial": "invalid", "deviceName": "Invalid Device"},
            ],
            "total": 2,
        }
    )

    with patch("custom_components.lipro.core.device.LiproDevice.from_api_data") as from_api:

        def parse_device(data):
            if data["serial"] == "invalid":
                raise ValueError("Invalid device data")
            from custom_components.lipro.core.device import LiproDevice

            return LiproDevice(
                device_number=1,
                serial=data["serial"],
                name=data["deviceName"],
                device_type=data["type"],
                iot_name="lipro_led",
                physical_model="light",
            )

        from_api.side_effect = parse_device

        with pytest.raises(RuntimeSnapshotRefreshRejectedError) as exc_info:
            await snapshot_builder.build_full_snapshot()

    assert exc_info.value.stage == "parse_device"
    assert exc_info.value.device_ref == "invalid"


@pytest.mark.asyncio
async def test_snapshot_builder_rejects_mesh_group_topology_errors_atomically(
    snapshot_builder, mock_client, make_device
):
    """Mesh-group topology normalization failure must reject the full snapshot."""
    mock_client.get_devices = AsyncMock(
        return_value={
            "devices": [
                {"serial": "mesh_group_1", "deviceName": "Group Device", "type": 1}
            ],
            "total": 1,
        }
    )
    mock_client.query_mesh_group_status = AsyncMock(return_value=[{"groupId": "mesh_group_1"}])
    mock_client.contracts.normalize_mesh_group_status_rows.side_effect = ValueError(
        "bad topology"
    )

    with patch("custom_components.lipro.core.device.LiproDevice.from_api_data") as from_api:
        from_api.side_effect = lambda data: make_device(
            "light",
            serial=data["serial"],
            name=data["deviceName"],
            is_group=True,
        )

        with pytest.raises(RuntimeSnapshotRefreshRejectedError) as exc_info:
            await snapshot_builder.build_full_snapshot()

    assert exc_info.value.stage == "mesh_group_topology"
