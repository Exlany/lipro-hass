"""Coordinator root smoke, service-layer, and entity-lifecycle tests."""

from __future__ import annotations

from unittest.mock import MagicMock

import pytest

from tests.conftest_shared import (
    make_api_device,
    make_device_page,
    refresh_and_sync_devices,
)
from tests.core.coordinator.conftest import (
    coordinator as _coordinator_source,  # noqa: F401
    patch_anonymous_share_manager as _patch_anonymous_share_manager_source,  # noqa: F401
)


@pytest.fixture(name="coordinator")
def coordinator_fixture(request: pytest.FixtureRequest):
    return request.getfixturevalue("_coordinator_source")


@pytest.fixture(name="patch_anonymous_share_manager")
def patch_anonymous_share_manager_fixture(request: pytest.FixtureRequest):
    return request.getfixturevalue("_patch_anonymous_share_manager_source")


class _Entity:
    """Simple entity stub with identity-based equality semantics."""

    def __init__(self, entity_id: str, device) -> None:
        self.entity_id = entity_id
        self.device = device


class TestCoordinatorServices:
    """Test coordinator service-layer accessors."""

    @pytest.mark.asyncio
    async def test_device_refresh_service_provides_devices(
        self,
        coordinator,
        mock_lipro_api_client,
        patch_anonymous_share_manager,
    ):
        """Device refresh service should expose synced devices."""
        mock_lipro_api_client.get_devices.return_value = make_device_page(
            [make_api_device(serial="03ab5ccd7c000001")]
        )

        await refresh_and_sync_devices(coordinator)

        devices = coordinator.device_refresh_service.devices
        assert len(devices) == 1
        assert "03ab5ccd7c000001" in devices

    @pytest.mark.asyncio
    async def test_device_refresh_service_get_device_by_id(
        self,
        coordinator,
        mock_lipro_api_client,
        patch_anonymous_share_manager,
    ):
        """Device lookup by ID should flow through the service layer."""
        mock_lipro_api_client.get_devices.return_value = make_device_page(
            [make_api_device(serial="03ab5ccd7c000001")]
        )

        await refresh_and_sync_devices(coordinator)

        device = coordinator.device_refresh_service.get_device_by_id("03ab5ccd7c000001")
        assert device is not None
        assert device.serial == "03ab5ccd7c000001"

    @pytest.mark.asyncio
    async def test_state_service_provides_device_access(
        self,
        coordinator,
        mock_lipro_api_client,
        patch_anonymous_share_manager,
    ):
        """State service should expose the same synced device cache."""
        mock_lipro_api_client.get_devices.return_value = make_device_page(
            [make_api_device(serial="03ab5ccd7c000001")]
        )

        await refresh_and_sync_devices(coordinator)

        devices = coordinator.state_service.devices
        assert len(devices) == 1
        assert "03ab5ccd7c000001" in devices


class TestCoordinatorEntityLifecycle:
    """Test public entity lifecycle behavior exposed by the coordinator."""

    @pytest.mark.asyncio
    async def test_register_entity_tracks_device_subscription_once(
        self,
        coordinator,
        mock_lipro_api_client,
        patch_anonymous_share_manager,
    ):
        """Registering the same entity twice should keep one active subscription."""
        serial = "03ab5ccd7c000001"
        mock_lipro_api_client.get_devices.return_value = make_device_page(
            [make_api_device(serial=serial)]
        )

        await refresh_and_sync_devices(coordinator)

        device = coordinator.get_device(serial)
        assert device is not None
        entity = _Entity("light.test_device", device)

        coordinator.register_entity(entity)
        coordinator.register_entity(entity)

        assert coordinator._runtimes.state.get_entities_for_device(serial) == [entity]

    @pytest.mark.asyncio
    async def test_register_entity_accepts_non_canonical_device_identifier(
        self,
        coordinator,
        mock_lipro_api_client,
        patch_anonymous_share_manager,
    ):
        """Entity registration should normalize formatted serial values."""
        serial = "03ab5ccd7c000001"
        mock_lipro_api_client.get_devices.return_value = make_device_page(
            [make_api_device(serial=serial)]
        )

        await refresh_and_sync_devices(coordinator)

        entity = _Entity(
            "light.test_device_alias",
            MagicMock(serial=f" {serial.upper()} "),
        )

        coordinator.register_entity(entity)

        assert coordinator._runtimes.state.get_entities_for_device(serial) == [entity]

        coordinator.unregister_entity(entity)

        assert coordinator._runtimes.state.get_entities_for_device(serial) == []

    def test_register_entity_ignores_missing_entity_id(self, coordinator):
        """Registering an anonymous entity should be a no-op."""
        coordinator.register_entity(_Entity("", MagicMock(serial="03ab5ccd7c000001")))

        assert coordinator._runtimes.state.get_entity_count() == 0

    @pytest.mark.asyncio
    async def test_unregister_entity_keeps_active_entity_until_matching_instance_removed(
        self,
        coordinator,
        mock_lipro_api_client,
        patch_anonymous_share_manager,
    ):
        """Unregistering a stale instance must not drop the live entity."""
        serial = "03ab5ccd7c000001"
        mock_lipro_api_client.get_devices.return_value = make_device_page(
            [make_api_device(serial=serial)]
        )

        await refresh_and_sync_devices(coordinator)

        device = coordinator.get_device(serial)
        assert device is not None
        active_entity = _Entity("light.test_device", device)
        stale_entity = _Entity("light.test_device", device)

        coordinator.register_entity(active_entity)
        coordinator.unregister_entity(stale_entity)

        assert coordinator._runtimes.state.get_entities_for_device(serial) == [
            active_entity
        ]

        coordinator.unregister_entity(active_entity)

        assert coordinator._runtimes.state.get_entities_for_device(serial) == []

    def test_unregister_entity_ignores_missing_entity_id(self, coordinator):
        """Unregistering an anonymous entity should be a no-op."""
        coordinator.unregister_entity(_Entity("", MagicMock(serial="03ab5ccd7c000001")))

        assert coordinator._runtimes.state.get_entity_count() == 0
