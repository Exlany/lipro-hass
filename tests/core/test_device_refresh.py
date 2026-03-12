"""Tests for device refresh functionality using new Runtime architecture.

This test suite covers:
- DeviceFilter: Device filtering with include/exclude rules
- SnapshotBuilder: Full device snapshot building
- DeviceRuntime: Device refresh orchestration
- IncrementalRefreshStrategy: Incremental state updates
"""

from __future__ import annotations

from unittest.mock import AsyncMock, Mock, patch

import pytest

from custom_components.lipro.const.config import (
    CONF_DEVICE_FILTER_DID_LIST,
    CONF_DEVICE_FILTER_DID_MODE,
    CONF_DEVICE_FILTER_HOME_LIST,
    CONF_DEVICE_FILTER_HOME_MODE,
    CONF_DEVICE_FILTER_MODEL_LIST,
    CONF_DEVICE_FILTER_MODEL_MODE,
    CONF_DEVICE_FILTER_SSID_LIST,
    CONF_DEVICE_FILTER_SSID_MODE,
    DEVICE_FILTER_MODE_EXCLUDE,
    DEVICE_FILTER_MODE_INCLUDE,
    DEVICE_FILTER_MODE_OFF,
)
from custom_components.lipro.core.coordinator.runtime.device.batch_optimizer import (
    DeviceBatchOptimizer,
)
from custom_components.lipro.core.coordinator.runtime.device.filter import (
    DeviceFilter,
    DeviceFilterConfig,
    DeviceFilterRule,
    parse_filter_config,
)
from custom_components.lipro.core.coordinator.runtime.device.incremental import (
    IncrementalRefreshStrategy,
)
from custom_components.lipro.core.coordinator.runtime.device.snapshot import (
    SnapshotBuilder,
)
from custom_components.lipro.core.coordinator.runtime.device_runtime import (
    DeviceRuntime,
)

# =========================================================================
# Test: parse_filter_config
# =========================================================================


def test_parse_filter_config_empty():
    """Test parsing empty filter config returns default OFF rules."""
    config = parse_filter_config({})

    assert isinstance(config, DeviceFilterConfig)
    assert config.home.mode == DEVICE_FILTER_MODE_OFF
    assert config.model.mode == DEVICE_FILTER_MODE_OFF
    assert config.ssid.mode == DEVICE_FILTER_MODE_OFF
    assert config.did.mode == DEVICE_FILTER_MODE_OFF


def test_parse_filter_config_with_include_rules():
    """Test parsing filter config with include rules."""
    config = parse_filter_config(
        {
            CONF_DEVICE_FILTER_DID_MODE: DEVICE_FILTER_MODE_INCLUDE,
            CONF_DEVICE_FILTER_DID_LIST: "device1,device2",
            CONF_DEVICE_FILTER_MODEL_MODE: DEVICE_FILTER_MODE_INCLUDE,
            CONF_DEVICE_FILTER_MODEL_LIST: "light,switch",
        }
    )

    assert config.did.mode == DEVICE_FILTER_MODE_INCLUDE
    assert "device1" in config.did.values
    assert "device2" in config.did.values

    assert config.model.mode == DEVICE_FILTER_MODE_INCLUDE
    assert "light" in config.model.values
    assert "switch" in config.model.values


def test_parse_filter_config_with_exclude_rules():
    """Test parsing filter config with exclude rules."""
    config = parse_filter_config(
        {
            CONF_DEVICE_FILTER_HOME_MODE: DEVICE_FILTER_MODE_EXCLUDE,
            CONF_DEVICE_FILTER_HOME_LIST: "home1",
            CONF_DEVICE_FILTER_SSID_MODE: DEVICE_FILTER_MODE_EXCLUDE,
            CONF_DEVICE_FILTER_SSID_LIST: "guest_wifi",
        }
    )

    assert config.home.mode == DEVICE_FILTER_MODE_EXCLUDE
    assert "home1" in config.home.values

    assert config.ssid.mode == DEVICE_FILTER_MODE_EXCLUDE
    assert "guest_wifi" in config.ssid.values


def test_parse_filter_config_normalizes_to_lowercase():
    """Test that filter values are normalized to lowercase."""
    config = parse_filter_config(
        {
            CONF_DEVICE_FILTER_MODEL_MODE: DEVICE_FILTER_MODE_INCLUDE,
            CONF_DEVICE_FILTER_MODEL_LIST: "Light,SWITCH,FanLight",
        }
    )

    assert "light" in config.model.values
    assert "switch" in config.model.values
    assert "fanlight" in config.model.values
    # Original case should not exist
    assert "Light" not in config.model.values


def test_parse_filter_config_handles_multiple_separators():
    """Test parsing with comma, newline, and semicolon separators."""
    config = parse_filter_config(
        {
            CONF_DEVICE_FILTER_DID_MODE: DEVICE_FILTER_MODE_INCLUDE,
            CONF_DEVICE_FILTER_DID_LIST: "device1,device2\ndevice3;device4",
        }
    )

    assert len(config.did.values) == 4
    assert "device1" in config.did.values
    assert "device2" in config.did.values
    assert "device3" in config.did.values
    assert "device4" in config.did.values


# =========================================================================
# Test: DeviceFilter
# =========================================================================


def test_device_filter_has_active_filter_returns_false_when_all_off():
    """Test _has_active_filter returns False when all rules are OFF."""
    config = DeviceFilterConfig()
    device_filter = DeviceFilter(config=config)

    assert not device_filter._has_active_filter()


def test_device_filter_has_active_filter_returns_true_when_any_active():
    """Test _has_active_filter returns True when any rule is active."""
    config = DeviceFilterConfig(
        did=DeviceFilterRule(mode=DEVICE_FILTER_MODE_INCLUDE, values=frozenset({"device1"}))
    )
    device_filter = DeviceFilter(config=config)

    assert device_filter._has_active_filter()


def test_device_filter_is_device_included_no_filter():
    """Test device is included when no filter is active."""
    config = DeviceFilterConfig()
    device_filter = DeviceFilter(config=config)

    device_data = {"serial": "03ab000000000001"}
    assert device_filter.is_device_included(device_data)


def test_device_filter_is_device_included_by_did_include():
    """Test device inclusion by DID include rule."""
    config = DeviceFilterConfig(
        did=DeviceFilterRule(
            mode=DEVICE_FILTER_MODE_INCLUDE,
            values=frozenset({"03ab000000000001", "03ab000000000002"}),
        )
    )
    device_filter = DeviceFilter(config=config)

    # Should include
    assert device_filter.is_device_included({"serial": "03ab000000000001"})
    assert device_filter.is_device_included({"serial": "03ab000000000002"})

    # Should exclude
    assert not device_filter.is_device_included({"serial": "03ab000000000003"})


def test_device_filter_is_device_included_by_did_exclude():
    """Test device exclusion by DID exclude rule."""
    config = DeviceFilterConfig(
        did=DeviceFilterRule(
            mode=DEVICE_FILTER_MODE_EXCLUDE,
            values=frozenset({"03ab000000000001"}),
        )
    )
    device_filter = DeviceFilter(config=config)

    # Should exclude
    assert not device_filter.is_device_included({"serial": "03ab000000000001"})

    # Should include
    assert device_filter.is_device_included({"serial": "03ab000000000002"})


def test_device_filter_is_device_included_by_model_include():
    """Test device inclusion by model include rule."""
    config = DeviceFilterConfig(
        model=DeviceFilterRule(
            mode=DEVICE_FILTER_MODE_INCLUDE,
            values=frozenset({"light", "switch"}),
        )
    )
    device_filter = DeviceFilter(config=config)

    # Should include
    assert device_filter.is_device_included({"serial": "xxx", "physicalModel": "light"})
    assert device_filter.is_device_included({"serial": "xxx", "physicalModel": "switch"})

    # Should exclude
    assert not device_filter.is_device_included({"serial": "xxx", "physicalModel": "outlet"})


def test_device_filter_is_device_included_by_home_include():
    """Test device inclusion by home include rule."""
    config = DeviceFilterConfig(
        home=DeviceFilterRule(
            mode=DEVICE_FILTER_MODE_INCLUDE,
            values=frozenset({"home1", "home2"}),
        )
    )
    device_filter = DeviceFilter(config=config)

    # Should include
    assert device_filter.is_device_included({"serial": "xxx", "homeName": "Home1"})
    assert device_filter.is_device_included({"serial": "xxx", "homeName": "HOME2"})

    # Should exclude
    assert not device_filter.is_device_included({"serial": "xxx", "homeName": "Home3"})


def test_device_filter_is_device_included_by_ssid_exclude():
    """Test device exclusion by SSID exclude rule."""
    config = DeviceFilterConfig(
        ssid=DeviceFilterRule(
            mode=DEVICE_FILTER_MODE_EXCLUDE,
            values=frozenset({"guest_wifi"}),
        )
    )
    device_filter = DeviceFilter(config=config)

    # Should exclude
    assert not device_filter.is_device_included(
        {"serial": "xxx", "deviceInfo": '{"wifi_ssid":"guest_wifi"}'}
    )

    # Should include
    assert device_filter.is_device_included(
        {"serial": "xxx", "deviceInfo": '{"wifi_ssid":"main_wifi"}'}
    )


def test_device_filter_is_device_included_multiple_rules_all_must_pass():
    """Test that device must pass ALL active filter rules."""
    config = DeviceFilterConfig(
        did=DeviceFilterRule(
            mode=DEVICE_FILTER_MODE_INCLUDE,
            values=frozenset({"03ab000000000001"}),
        ),
        model=DeviceFilterRule(
            mode=DEVICE_FILTER_MODE_INCLUDE,
            values=frozenset({"light"}),
        ),
    )
    device_filter = DeviceFilter(config=config)

    # Passes both rules
    assert device_filter.is_device_included(
        {"serial": "03ab000000000001", "physicalModel": "light"}
    )

    # Fails DID rule
    assert not device_filter.is_device_included(
        {"serial": "03ab000000000002", "physicalModel": "light"}
    )

    # Fails model rule
    assert not device_filter.is_device_included(
        {"serial": "03ab000000000001", "physicalModel": "switch"}
    )


def test_device_filter_skips_ssid_check_when_mode_off():
    """Test that SSID filter is skipped when mode is OFF."""
    config = DeviceFilterConfig(
        did=DeviceFilterRule(
            mode=DEVICE_FILTER_MODE_INCLUDE,
            values=frozenset({"03ab5ccd7c000001"}),
        ),
        ssid=DeviceFilterRule(mode=DEVICE_FILTER_MODE_OFF),
    )
    device_filter = DeviceFilter(config=config)

    # Should not parse deviceInfo JSON when SSID mode is OFF
    with patch("custom_components.lipro.core.coordinator.runtime.device.filter.json.loads") as json_loads:
        assert device_filter.is_device_included(
            {
                "serial": "03ab5ccd7c000001",
                "deviceInfo": '{"wifi_ssid":"MyWiFi"}',
            }
        )
        json_loads.assert_not_called()


# =========================================================================
# Test: SnapshotBuilder
# =========================================================================


@pytest.fixture
def mock_client():
    """Create mock LiproClient."""
    return AsyncMock()


@pytest.fixture
def mock_device_identity_index():
    """Create mock DeviceIdentityIndex."""
    from custom_components.lipro.core.device.identity_index import DeviceIdentityIndex

    return DeviceIdentityIndex()


@pytest.fixture
def snapshot_builder(mock_client, mock_device_identity_index):
    """Create SnapshotBuilder with mocked dependencies."""
    device_filter = DeviceFilter(config=DeviceFilterConfig())
    return SnapshotBuilder(
        client=mock_client,
        device_identity_index=mock_device_identity_index,
        device_filter=device_filter,
    )


@pytest.mark.asyncio
async def test_snapshot_builder_build_full_snapshot_single_page(
    snapshot_builder, mock_client, make_device
):
    """Test building full snapshot with single page of devices."""
    mock_client.get_device_list = AsyncMock(
        return_value={
            "data": [
                {"serial": "03ab000000000001", "name": "Device 1", "deviceType": 1},
                {"serial": "03ab000000000002", "name": "Device 2", "deviceType": 1},
            ],
            "hasMore": False,
        }
    )

    with patch("custom_components.lipro.core.device.LiproDevice.from_api_data") as from_api:
        from_api.side_effect = lambda data: make_device(
            "light", serial=data["serial"], name=data["name"]
        )

        snapshot = await snapshot_builder.build_full_snapshot()

    assert len(snapshot.devices) == 2
    assert "03ab000000000001" in snapshot.devices
    assert "03ab000000000002" in snapshot.devices
    assert len(snapshot.cloud_serials) == 2
    mock_client.get_device_list.assert_called_once_with(page=1)


@pytest.mark.asyncio
async def test_snapshot_builder_build_full_snapshot_multiple_pages(
    snapshot_builder, mock_client, make_device
):
    """Test building full snapshot with pagination."""
    mock_client.get_device_list = AsyncMock(
        side_effect=[
            {
                "data": [{"serial": "03ab000000000001", "name": "Device 1", "deviceType": 1}],
                "hasMore": True,
            },
            {
                "data": [{"serial": "03ab000000000002", "name": "Device 2", "deviceType": 1}],
                "hasMore": False,
            },
        ]
    )

    with patch("custom_components.lipro.core.device.LiproDevice.from_api_data") as from_api:
        from_api.side_effect = lambda data: make_device(
            "light", serial=data["serial"], name=data["name"]
        )

        snapshot = await snapshot_builder.build_full_snapshot()

    assert len(snapshot.devices) == 2
    assert mock_client.get_device_list.call_count == 2


@pytest.mark.asyncio
async def test_snapshot_builder_applies_device_filter(
    mock_client, mock_device_identity_index, make_device
):
    """Test that SnapshotBuilder applies device filter."""
    # Create filter that only includes device1
    config = DeviceFilterConfig(
        did=DeviceFilterRule(
            mode=DEVICE_FILTER_MODE_INCLUDE,
            values=frozenset({"03ab000000000001"}),
        )
    )
    device_filter = DeviceFilter(config=config)

    snapshot_builder = SnapshotBuilder(
        client=mock_client,
        device_identity_index=mock_device_identity_index,
        device_filter=device_filter,
    )

    mock_client.get_device_list = AsyncMock(
        return_value={
            "data": [
                {"serial": "03ab000000000001", "name": "Device 1", "deviceType": 1},
                {"serial": "03ab000000000002", "name": "Device 2", "deviceType": 1},
            ],
            "hasMore": False,
        }
    )

    with patch("custom_components.lipro.core.device.LiproDevice.from_api_data") as from_api:
        from_api.side_effect = lambda data: make_device(
            "light", serial=data["serial"], name=data["name"]
        )

        snapshot = await snapshot_builder.build_full_snapshot()

    # Only device1 should be included
    assert len(snapshot.devices) == 1
    assert "03ab000000000001" in snapshot.devices
    assert "03ab000000000002" not in snapshot.devices


@pytest.mark.asyncio
async def test_snapshot_builder_categorizes_devices_by_type(
    snapshot_builder, mock_client, make_device
):
    """Test that devices are categorized into iot_ids, group_ids, outlet_ids."""
    mock_client.get_device_list = AsyncMock(
        return_value={
            "data": [
                {"serial": "light1", "name": "Light", "deviceType": 1},
                {"serial": "group1", "name": "Group", "deviceType": 1},
                {"serial": "outlet1", "name": "Outlet", "deviceType": 6},
            ],
            "hasMore": False,
        }
    )

    with patch("custom_components.lipro.core.device.LiproDevice.from_api_data") as from_api:

        def make_device_by_serial(data):
            serial = data["serial"]
            if serial == "light1":
                return make_device("light", serial=serial)
            if serial == "group1":
                return make_device("light", serial=serial, is_group=True)
            # outlet1
            return make_device("outlet", serial=serial)

        from_api.side_effect = make_device_by_serial

        snapshot = await snapshot_builder.build_full_snapshot()

    # iot_device_id is the serial for devices
    assert "light1" in snapshot.iot_ids
    assert "group1" in snapshot.group_ids
    assert "outlet1" in snapshot.outlet_ids


@pytest.mark.asyncio
async def test_snapshot_builder_handles_parse_errors_gracefully(
    snapshot_builder, mock_client
):
    """Test that snapshot builder skips devices that fail to parse."""
    mock_client.get_device_list = AsyncMock(
        return_value={
            "data": [
                {"serial": "03ab000000000001", "name": "Valid Device", "deviceType": 1},
                {"serial": "invalid", "name": "Invalid Device"},  # Missing deviceType
            ],
            "hasMore": False,
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
                name=data["name"],
                device_type=data["deviceType"],
                iot_name="lipro_led",
                physical_model="light",
            )

        from_api.side_effect = parse_device

        snapshot = await snapshot_builder.build_full_snapshot()

    # Should only include valid device
    assert len(snapshot.devices) == 1
    assert "03ab000000000001" in snapshot.devices


# =========================================================================
# Test: DeviceRuntime
# =========================================================================


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
        client=mock_client,
        auth_manager=mock_auth_manager,
        device_identity_index=mock_device_identity_index,
        filter_config_options={},
    )


@pytest.mark.asyncio
async def test_device_runtime_refresh_devices_force(
    device_runtime, mock_client, make_device
):
    """Test forced device refresh."""
    mock_client.get_device_list = AsyncMock(
        return_value={
            "data": [
                {"serial": "03ab000000000001", "name": "Device 1", "deviceType": 1},
            ],
            "hasMore": False,
        }
    )

    with patch("custom_components.lipro.core.device.LiproDevice.from_api_data") as from_api:
        from_api.side_effect = lambda data: make_device("light", serial=data["serial"])

        snapshot = await device_runtime.refresh_devices(force=True)

    assert snapshot is not None
    assert len(snapshot.devices) == 1
    mock_client.get_device_list.assert_called_once()


@pytest.mark.asyncio
async def test_device_runtime_first_refresh_is_always_full(
    device_runtime, mock_client, make_device
):
    """Test that first refresh is always full even without force."""
    mock_client.get_device_list = AsyncMock(
        return_value={
            "data": [
                {"serial": "03ab000000000001", "name": "Device 1", "deviceType": 1},
            ],
            "hasMore": False,
        }
    )

    with patch("custom_components.lipro.core.device.LiproDevice.from_api_data") as from_api:
        from_api.side_effect = lambda data: make_device("light", serial=data["serial"])

        snapshot = await device_runtime.refresh_devices(force=False)

    assert snapshot is not None
    assert len(snapshot.devices) == 1
    mock_client.get_device_list.assert_called_once()


@pytest.mark.asyncio
async def test_device_runtime_incremental_refresh_uses_existing_snapshot(
    device_runtime, mock_client, make_device
):
    """Test that incremental refresh reuses existing snapshot."""
    # First refresh (full)
    mock_client.get_device_list = AsyncMock(
        return_value={
            "data": [
                {"serial": "03ab000000000001", "name": "Device 1", "deviceType": 1},
            ],
            "hasMore": False,
        }
    )

    with patch("custom_components.lipro.core.device.LiproDevice.from_api_data") as from_api:
        from_api.side_effect = lambda data: make_device(
            "light", serial=data["serial"], iot_device_id="iot_001"
        )

        first_snapshot = await device_runtime.refresh_devices(force=True)

    # Mock incremental queries
    mock_client.query_iot_devices = AsyncMock(return_value={"data": []})
    mock_client.query_group_devices = AsyncMock(return_value={"data": []})
    mock_client.query_outlet_devices = AsyncMock(return_value={"data": []})

    # Second refresh (incremental) - should not call get_device_list again
    mock_client.get_device_list.reset_mock()

    second_snapshot = await device_runtime.refresh_devices(force=False)

    # Should reuse snapshot
    assert second_snapshot is first_snapshot
    mock_client.get_device_list.assert_not_called()


def test_device_runtime_should_refresh_device_list(device_runtime):
    """Test refresh decision logic."""
    # Initially should refresh (first time)
    assert device_runtime.should_refresh_device_list()

    # After force refresh request
    device_runtime.request_force_refresh()
    assert device_runtime.should_refresh_device_list()


def test_device_runtime_compute_stale_devices(device_runtime):
    """Test stale device computation."""
    from custom_components.lipro.core.coordinator.runtime.device.snapshot import (
        FetchedDeviceSnapshot,
    )

    # First snapshot
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

    # First time, no missing devices
    assert len(missing_cycles) == 0
    assert len(removable) == 0

    # Second snapshot with device2 missing
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

    # device2 should be tracked as missing
    assert "device2" in missing_cycles
    assert missing_cycles["device2"] == 1


def test_device_runtime_reset(device_runtime):
    """Test runtime reset clears state."""
    device_runtime.request_force_refresh()
    device_runtime._cloud_serials_last_seen = {"device1"}

    device_runtime.reset()

    assert device_runtime.get_last_snapshot() is None
    assert len(device_runtime._cloud_serials_last_seen) == 0


# =========================================================================
# Test: IncrementalRefreshStrategy
# =========================================================================


@pytest.mark.asyncio
async def test_incremental_refresh_strategy_queries_iot_devices(mock_client, make_device):
    """Test incremental refresh queries IoT devices."""
    strategy = IncrementalRefreshStrategy(client=mock_client)

    mock_client.query_iot_devices = AsyncMock(
        return_value={
            "data": [
                {"id": "iot_001", "powerState": "1"},
            ]
        }
    )

    device = make_device("light", properties={"id": "iot_001"})
    devices = {"iot_001": device}

    from custom_components.lipro.core.coordinator.runtime.device.batch_optimizer import (
        DeviceBatchOptimizer,
    )

    batch_optimizer = DeviceBatchOptimizer()

    updated_states = await strategy.refresh_device_states(
        iot_ids=["iot_001"],
        group_ids=[],
        outlet_ids=[],
        devices=devices,
        batch_optimizer=batch_optimizer,
    )

    assert "iot_001" in updated_states
    mock_client.query_iot_devices.assert_called_once()


@pytest.mark.asyncio
async def test_incremental_refresh_strategy_queries_all_device_types(
    mock_client, make_device
):
    """Test incremental refresh queries all device types."""
    strategy = IncrementalRefreshStrategy(client=mock_client)

    mock_client.query_iot_devices = AsyncMock(
        return_value={"data": [{"id": "iot_001", "powerState": "1"}]}
    )
    mock_client.query_group_devices = AsyncMock(
        return_value={"data": [{"id": "group_001", "powerState": "1"}]}
    )
    mock_client.query_outlet_devices = AsyncMock(
        return_value={"data": [{"id": "outlet_001", "powerState": "1"}]}
    )

    devices = {
        "iot_001": make_device("light", properties={"id": "iot_001"}),
        "group_001": make_device("light", properties={"id": "group_001"}, is_group=True),
        "outlet_001": make_device("outlet", properties={"id": "outlet_001"}),
    }

    from custom_components.lipro.core.coordinator.runtime.device.batch_optimizer import (
        DeviceBatchOptimizer,
    )

    batch_optimizer = DeviceBatchOptimizer()

    updated_states = await strategy.refresh_device_states(
        iot_ids=["iot_001"],
        group_ids=["group_001"],
        outlet_ids=["outlet_001"],
        devices=devices,
        batch_optimizer=batch_optimizer,
    )

    assert len(updated_states) == 3
    mock_client.query_iot_devices.assert_called_once()
    mock_client.query_group_devices.assert_called_once()
    mock_client.query_outlet_devices.assert_called_once()


@pytest.mark.asyncio
async def test_incremental_refresh_strategy_handles_query_errors_gracefully(
    mock_client, make_device
):
    """Test incremental refresh continues on query errors."""
    strategy = IncrementalRefreshStrategy(client=mock_client)

    # First batch fails, second succeeds
    mock_client.query_iot_devices = AsyncMock(side_effect=Exception("Network error"))

    devices = {"iot_001": make_device("light", properties={"id": "iot_001"})}

    from custom_components.lipro.core.coordinator.runtime.device.batch_optimizer import (
        DeviceBatchOptimizer,
    )

    batch_optimizer = DeviceBatchOptimizer()

    # Should not raise exception
    updated_states = await strategy.refresh_device_states(
        iot_ids=["iot_001"],
        group_ids=[],
        outlet_ids=[],
        devices=devices,
        batch_optimizer=batch_optimizer,
    )

    # Should return empty dict on error
    assert len(updated_states) == 0


@pytest.mark.asyncio
async def test_incremental_refresh_strategy_updates_existing_device_properties(
    mock_client,
) -> None:
    """Incremental refresh should apply fresh properties onto known devices."""
    strategy = IncrementalRefreshStrategy(client=mock_client)
    mock_client.query_iot_devices = AsyncMock(
        return_value={"data": [{"id": "iot_001", "properties": {"powerState": "1"}}]}
    )
    device = Mock()
    batch_optimizer = DeviceBatchOptimizer()

    updated_states = await strategy.refresh_device_states(
        iot_ids=["iot_001"],
        group_ids=[],
        outlet_ids=[],
        devices={"iot_001": device},
        batch_optimizer=batch_optimizer,
    )

    assert updated_states["iot_001"]["properties"] == {"powerState": "1"}
    device.update_properties.assert_called_once_with({"powerState": "1"})


@pytest.mark.asyncio
async def test_incremental_refresh_strategy_uses_device_resolver_for_alias_ids(
    mock_client,
) -> None:
    """Alias-based refresh results should still resolve onto the live device."""
    device = Mock()
    strategy = IncrementalRefreshStrategy(
        client=mock_client,
        device_resolver=lambda device_id: device if device_id == "dev1" else None,
    )
    mock_client.query_iot_devices = AsyncMock(
        return_value={"data": [{"id": "dev1", "properties": {"powerState": "1"}}]}
    )
    batch_optimizer = DeviceBatchOptimizer()

    updated_states = await strategy.refresh_device_states(
        iot_ids=["dev1"],
        group_ids=[],
        outlet_ids=[],
        devices={},
        batch_optimizer=batch_optimizer,
    )

    assert updated_states["dev1"]["properties"] == {"powerState": "1"}
    device.update_properties.assert_called_once_with({"powerState": "1"})


@pytest.mark.asyncio
async def test_incremental_refresh_strategy_reraises_iot_query_cancellation(
    mock_client,
) -> None:
    """IoT query cancellation should bubble up instead of being swallowed."""
    import asyncio

    strategy = IncrementalRefreshStrategy(client=mock_client)
    mock_client.query_iot_devices = AsyncMock(side_effect=asyncio.CancelledError())
    batch_optimizer = DeviceBatchOptimizer()

    with pytest.raises(asyncio.CancelledError):
        await strategy.refresh_device_states(
            iot_ids=["iot_001"],
            group_ids=[],
            outlet_ids=[],
            devices={},
            batch_optimizer=batch_optimizer,
        )


@pytest.mark.asyncio
async def test_incremental_refresh_strategy_reraises_group_query_cancellation(
    mock_client,
) -> None:
    """Group query cancellation should bubble up instead of being swallowed."""
    import asyncio

    strategy = IncrementalRefreshStrategy(client=mock_client)
    mock_client.query_group_devices = AsyncMock(side_effect=asyncio.CancelledError())
    batch_optimizer = DeviceBatchOptimizer()

    with pytest.raises(asyncio.CancelledError):
        await strategy.refresh_device_states(
            iot_ids=[],
            group_ids=["group_001"],
            outlet_ids=[],
            devices={},
            batch_optimizer=batch_optimizer,
        )


@pytest.mark.asyncio
async def test_incremental_refresh_strategy_reraises_outlet_query_cancellation(
    mock_client,
) -> None:
    """Outlet query cancellation should bubble up instead of being swallowed."""
    import asyncio

    strategy = IncrementalRefreshStrategy(client=mock_client)
    mock_client.query_outlet_devices = AsyncMock(side_effect=asyncio.CancelledError())
    batch_optimizer = DeviceBatchOptimizer()

    with pytest.raises(asyncio.CancelledError):
        await strategy.refresh_device_states(
            iot_ids=[],
            group_ids=[],
            outlet_ids=["outlet_001"],
            devices={},
            batch_optimizer=batch_optimizer,
        )
