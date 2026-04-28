"""Tests for device-refresh runtime behavior."""

from __future__ import annotations

from unittest.mock import AsyncMock, patch

import pytest

from custom_components.lipro.core.coordinator.runtime.device_runtime import (
    DeviceRuntime,
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
def mock_auth_manager():
    """Create mock LiproAuthManager."""
    auth = AsyncMock()
    auth.ensure_valid_token = AsyncMock()
    auth.is_authenticated = True
    return auth


@pytest.fixture
def device_runtime(mock_client, mock_auth_manager, mock_device_identity_index):
    """Create DeviceRuntime with mocked dependencies."""
    return DeviceRuntime(
        protocol=mock_client,
        auth_manager=mock_auth_manager,
        device_identity_index=mock_device_identity_index,
        filter_config_options={},
    )


@pytest.mark.asyncio
async def test_device_runtime_refresh_devices_force(
    device_runtime, mock_client, make_device
):
    """Test forced device refresh."""
    mock_client.get_devices = AsyncMock(
        return_value={
            "devices": [
                {"serial": "03ab000000000001", "deviceName": "Device 1", "type": 1},
            ],
            "total": 1,
        }
    )

    with patch(
        "custom_components.lipro.core.device.LiproDevice.from_api_data"
    ) as from_api:
        from_api.side_effect = lambda data: make_device("light", serial=data["serial"])

        snapshot = await device_runtime.refresh_devices(force=True)

    assert snapshot is not None
    assert len(snapshot.devices) == 1
    mock_client.get_devices.assert_awaited_once()


@pytest.mark.asyncio
async def test_device_runtime_first_refresh_is_always_full(
    device_runtime, mock_client, make_device
):
    """Test that first refresh is always full even without force."""
    mock_client.get_devices = AsyncMock(
        return_value={
            "devices": [
                {"serial": "03ab000000000001", "deviceName": "Device 1", "type": 1},
            ],
            "total": 1,
        }
    )

    with patch(
        "custom_components.lipro.core.device.LiproDevice.from_api_data"
    ) as from_api:
        from_api.side_effect = lambda data: make_device("light", serial=data["serial"])

        snapshot = await device_runtime.refresh_devices(force=False)

    assert snapshot is not None
    assert len(snapshot.devices) == 1
    mock_client.get_devices.assert_awaited_once()


@pytest.mark.asyncio
async def test_device_runtime_cached_refresh_reuses_existing_snapshot(
    device_runtime, mock_client, make_device
):
    """Test that a non-due refresh reuses the cached snapshot."""
    mock_client.get_devices = AsyncMock(
        return_value={
            "devices": [
                {"serial": "03ab000000000001", "deviceName": "Device 1", "type": 1},
            ],
            "total": 1,
        }
    )

    with patch(
        "custom_components.lipro.core.device.LiproDevice.from_api_data"
    ) as from_api:
        from_api.side_effect = lambda data: make_device("light", serial=data["serial"])

        first_snapshot = await device_runtime.refresh_devices(force=True)

    mock_client.get_devices.reset_mock()

    second_snapshot = await device_runtime.refresh_devices(force=False)

    assert second_snapshot is first_snapshot
    mock_client.get_devices.assert_not_called()


def test_device_runtime_should_refresh_device_list(device_runtime):
    """Test refresh decision logic."""
    assert device_runtime.should_refresh_device_list()

    device_runtime.request_force_refresh()
    assert device_runtime.should_refresh_device_list()


def test_device_runtime_compute_stale_devices(device_runtime):
    """Test stale device computation."""
    from custom_components.lipro.core.coordinator.runtime.device.snapshot import (
        FetchedDeviceSnapshot,
    )

    snapshot1 = FetchedDeviceSnapshot(
        devices={},
        device_by_id={},
        iot_ids=[],
        group_ids=[],
        outlet_ids=[],
        cloud_serials={"device1", "device2", "device3"},
    )

    missing_cycles, removable = device_runtime.compute_stale_devices(
        current_snapshot=snapshot1
    )

    assert len(missing_cycles) == 0
    assert len(removable) == 0

    snapshot2 = FetchedDeviceSnapshot(
        devices={},
        device_by_id={},
        iot_ids=[],
        group_ids=[],
        outlet_ids=[],
        cloud_serials={"device1", "device3"},
    )

    missing_cycles, removable = device_runtime.compute_stale_devices(
        current_snapshot=snapshot2
    )

    assert "device2" in missing_cycles
    assert missing_cycles["device2"] == 1


def test_device_runtime_reset(device_runtime):
    """Test runtime reset clears state."""
    device_runtime.request_force_refresh()
    device_runtime._cloud_serials_last_seen = {"device1"}

    device_runtime.reset()

    assert device_runtime.get_last_snapshot() is None
    assert len(device_runtime._cloud_serials_last_seen) == 0
