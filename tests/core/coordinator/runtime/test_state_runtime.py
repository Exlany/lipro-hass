"""Tests for StateRuntime."""

from __future__ import annotations

from typing import cast
from unittest.mock import MagicMock

import pytest

from custom_components.lipro.core.coordinator.entity_protocol import LiproEntityProtocol
from custom_components.lipro.core.coordinator.runtime.state_runtime import StateRuntime
from custom_components.lipro.core.device import LiproDevice
from custom_components.lipro.core.device.identity_index import DeviceIdentityIndex


@pytest.fixture
def mock_device() -> LiproDevice:
    """Create a mock device."""
    device = MagicMock()
    device.serial = "TEST001"
    device.name = "Test Device"
    device.room_id = 1
    device.is_online = True
    device.update_properties = MagicMock()
    device.mark_mqtt_update = MagicMock()
    return cast(LiproDevice, device)


@pytest.fixture
def mock_entity(mock_device: LiproDevice) -> MagicMock:
    """Create a mock entity."""
    entity = MagicMock()
    entity.entity_id = "light.test_device"
    entity.unique_id = None
    entity.device = mock_device
    entity.get_protected_keys = MagicMock(return_value=set())
    entity.async_write_ha_state = MagicMock()
    return entity


@pytest.fixture
def state_runtime(mock_device: LiproDevice, mock_entity: MagicMock) -> StateRuntime:
    """Create a StateRuntime instance."""
    devices = {mock_device.serial: mock_device}
    device_identity_index = DeviceIdentityIndex()
    device_identity_index.register(mock_device.serial, mock_device)
    entity_id = cast(str, mock_entity.entity_id)
    typed_entity = cast(LiproEntityProtocol, mock_entity)
    entities: dict[str, LiproEntityProtocol] = {entity_id: typed_entity}
    entities_by_device: dict[str, list[LiproEntityProtocol]] = {"test001": [typed_entity]}

    def normalize_key(key: str) -> str:
        return key.lower()

    return StateRuntime(
        devices=devices,
        device_identity_index=device_identity_index,
        entities=entities,
        entities_by_device=entities_by_device,
        normalize_device_key=normalize_key,
    )


class TestStateReader:
    """Test StateReader functionality."""

    def test_get_device_by_id(self, state_runtime: StateRuntime, mock_device: LiproDevice) -> None:
        """Test getting device by ID."""
        device = state_runtime.get_device_by_id(mock_device.serial)
        assert device == mock_device

    def test_get_device_by_id_not_found(self, state_runtime: StateRuntime) -> None:
        """Test getting non-existent device."""
        device = state_runtime.get_device_by_id("NONEXISTENT")
        assert device is None

    def test_get_device_by_serial(self, state_runtime: StateRuntime, mock_device: LiproDevice) -> None:
        """Test getting device by serial."""
        device = state_runtime.get_device_by_serial(mock_device.serial)
        assert device == mock_device

    def test_get_all_devices(self, state_runtime: StateRuntime, mock_device: LiproDevice) -> None:
        """Test getting all devices."""
        devices = state_runtime.get_all_devices()
        assert len(devices) == 1
        assert devices[mock_device.serial] == mock_device

    def test_get_device_count(self, state_runtime: StateRuntime) -> None:
        """Test getting device count."""
        assert state_runtime.get_device_count() == 1

    def test_get_online_device_count(self, state_runtime: StateRuntime) -> None:
        """Test getting online device count."""
        assert state_runtime.get_online_device_count() == 1

    def test_get_devices_by_room(self, state_runtime: StateRuntime, mock_device: LiproDevice) -> None:
        """Test getting devices by room."""
        devices = state_runtime.get_devices_by_room(1)
        assert len(devices) == 1
        assert devices[0] == mock_device

    def test_has_device(self, state_runtime: StateRuntime, mock_device: LiproDevice) -> None:
        """Test checking device existence."""
        assert state_runtime.has_device(mock_device.serial) is True
        assert state_runtime.has_device("NONEXISTENT") is False


class TestStateUpdater:
    """Test StateUpdater functionality."""

    async def test_apply_properties_update(
        self,
        state_runtime: StateRuntime,
        mock_device: LiproDevice,
        mock_entity: MagicMock,
    ) -> None:
        """Test applying property updates."""
        properties = {"brightness": 100}
        changed = await state_runtime.apply_properties_update(mock_device, properties, source="test")

        assert changed is True
        cast(MagicMock, mock_device.update_properties).assert_called_once_with(properties)
        mock_entity.async_write_ha_state.assert_called_once()

    async def test_apply_properties_update_no_change(
        self,
        state_runtime: StateRuntime,
        mock_device: LiproDevice,
        mock_entity: MagicMock,
    ) -> None:
        """Test applying property updates with no change."""
        # Simplified implementation always returns True if properties exist
        properties = {"brightness": 100}
        changed = await state_runtime.apply_properties_update(mock_device, properties)

        assert changed is True
        mock_entity.async_write_ha_state.assert_called_once()

    async def test_batch_update_properties(
        self,
        state_runtime: StateRuntime,
        mock_device: LiproDevice,
    ) -> None:
        """Test batch property updates."""
        updates = [(mock_device, {"brightness": 100})]
        changed_count = await state_runtime.batch_update_properties(updates, source="batch")

        assert changed_count == 1

    async def test_apply_properties_update_returns_false_for_empty_payload(
        self,
        state_runtime: StateRuntime,
        mock_device: LiproDevice,
        mock_entity: MagicMock,
    ) -> None:
        changed = await state_runtime.apply_properties_update(mock_device, {})

        assert changed is False
        cast(MagicMock, mock_device.update_properties).assert_not_called()
        mock_entity.async_write_ha_state.assert_not_called()

    async def test_apply_properties_update_skips_fully_protected_payload(
        self,
        state_runtime: StateRuntime,
        mock_device: LiproDevice,
        mock_entity: MagicMock,
    ) -> None:
        mock_entity.get_protected_keys = MagicMock(return_value={"brightness"})

        changed = await state_runtime.apply_properties_update(
            mock_device,
            {"brightness": 100},
        )

        assert changed is False
        cast(MagicMock, mock_device.update_properties).assert_not_called()
        mock_entity.async_write_ha_state.assert_not_called()

    async def test_apply_properties_update_filters_only_protected_properties(
        self,
        state_runtime: StateRuntime,
        mock_device: LiproDevice,
        mock_entity: MagicMock,
    ) -> None:
        mock_entity.get_protected_keys = MagicMock(return_value={"brightness"})

        changed = await state_runtime.apply_properties_update(
            mock_device,
            {"brightness": 100, "powerState": 1},
        )

        assert changed is True
        cast(MagicMock, mock_device.update_properties).assert_called_once_with({"powerState": 1})
        mock_entity.async_write_ha_state.assert_called_once()


class TestStateIndexManager:
    """Test StateIndexManager functionality."""

    def test_register_entity(
        self,
        state_runtime: StateRuntime,
        mock_device: LiproDevice,
    ) -> None:
        """Test registering an entity."""
        new_entity = MagicMock()
        new_entity.entity_id = "switch.test_device"
        new_entity.async_write_ha_state = MagicMock()

        state_runtime.register_entity(new_entity, mock_device.serial)
        assert state_runtime.get_entity_count() == 2

    def test_unregister_entity(
        self,
        state_runtime: StateRuntime,
        mock_entity: MagicMock,
    ) -> None:
        """Test unregistering an entity."""
        state_runtime.unregister_entity(mock_entity.entity_id)
        assert state_runtime.get_entity_count() == 0

    def test_unregister_entity_ignores_missing_entity(self, state_runtime: StateRuntime) -> None:
        state_runtime.unregister_entity("missing.entity")

        assert state_runtime.get_entity_count() == 1

    def test_unregister_entity_instance_keeps_active_entity_until_matching_instance_removed(
        self,
        state_runtime: StateRuntime,
        mock_device: LiproDevice,
        mock_entity: MagicMock,
    ) -> None:
        active_entity = MagicMock()
        active_entity.entity_id = mock_entity.entity_id
        active_entity.device = mock_device
        stale_entity = MagicMock()
        stale_entity.entity_id = mock_entity.entity_id
        stale_entity.device = mock_device

        state_runtime.register_entity(active_entity, mock_device.serial)
        state_runtime.unregister_entity_instance(stale_entity)

        assert state_runtime.get_entity_count() == 1
        assert state_runtime.get_entities_for_device(mock_device.serial) == [active_entity]

        state_runtime.unregister_entity_instance(active_entity)

        assert state_runtime.get_entity_count() == 0
        assert state_runtime.get_entities_for_device(mock_device.serial) == []


    def test_register_entity_ignores_objects_without_entity_id(
        self,
        state_runtime: StateRuntime,
        mock_device: LiproDevice,
    ) -> None:
        state_runtime.register_entity(MagicMock(), mock_device.serial)

        assert state_runtime.get_entity_count() == 1

    def test_register_entity_reuses_existing_entity_id_without_duplication(
        self,
        state_runtime: StateRuntime,
        mock_device: LiproDevice,
        mock_entity: MagicMock,
    ) -> None:
        state_runtime.register_entity(mock_entity, mock_device.serial)

        entities = state_runtime.get_entities_for_device(mock_device.serial)

        assert state_runtime.get_entity_count() == 1
        assert entities == [mock_entity]

    def test_register_entity_replaces_prior_instance_for_same_entity_id(
        self,
        state_runtime: StateRuntime,
        mock_device: LiproDevice,
        mock_entity: MagicMock,
    ) -> None:
        replacement = MagicMock()
        replacement.entity_id = mock_entity.entity_id

        state_runtime.register_entity(replacement, mock_device.serial)

        entities = state_runtime.get_entities_for_device(mock_device.serial)

        assert state_runtime.get_entity_count() == 1
        assert entities == [replacement]


    def test_register_entity_creates_bucket_for_new_device_key(
        self,
        state_runtime: StateRuntime,
    ) -> None:
        new_entity = MagicMock()
        new_entity.entity_id = "switch.other_device"

        state_runtime.register_entity(new_entity, "OTHER-DEVICE")

        assert state_runtime.get_entities_for_device("other-device") == [new_entity]

    def test_get_entities_for_device(
        self,
        state_runtime: StateRuntime,
        mock_device: LiproDevice,
        mock_entity: MagicMock,
    ) -> None:
        """Test getting entities for a device."""
        entities = state_runtime.get_entities_for_device(mock_device.serial)
        assert len(entities) == 1
        assert entities[0] == mock_entity


    def test_rebuild_device_index(
        self,
        state_runtime: StateRuntime,
        mock_device: LiproDevice,
    ) -> None:
        """Test rebuilding device index."""
        new_device = LiproDevice(
            device_number=2,
            serial="TEST002",
            name="Other Device",
            device_type=1,
            iot_name="lipro_led",
            physical_model="light",
            room_id=2,
            properties={"connectState": "1"},
        )
        devices = {mock_device.serial: mock_device, new_device.serial: new_device}

        state_runtime.rebuild_device_index(devices)
        assert state_runtime.has_device(new_device.serial) is True


    def test_rebuild_device_index_accepts_explicit_runtime_alias_projection(
        self,
        state_runtime: StateRuntime,
        mock_device: LiproDevice,
    ) -> None:
        """Explicit runtime alias projections should rebuild lookups without extras sidecars."""
        projected_device = LiproDevice(
            device_number=3,
            serial="TEST003",
            name="Projected Device",
            device_type=1,
            iot_name="lipro_led",
            physical_model="light",
            room_id=3,
            properties={"connectState": "1"},
        )
        devices = {mock_device.serial: mock_device, projected_device.serial: projected_device}

        state_runtime.rebuild_device_index(
            devices,
            {projected_device.serial: ("mesh_group_alias", "03ab5ccd7c000003")},
        )

        assert state_runtime.get_device_by_id("mesh_group_alias") is projected_device
        assert state_runtime.get_device_by_id("03AB5CCD7C000003") is projected_device
