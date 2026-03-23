"""Device-resolution init service-handler topical suites."""

from __future__ import annotations

import pytest
from pytest_homeassistant_custom_component.common import MockConfigEntry

from custom_components.lipro.const.base import DOMAIN
from custom_components.lipro.const.config import CONF_DEBUG_MODE
from custom_components.lipro.control.service_router import _get_device_and_coordinator
from custom_components.lipro.services.contracts import ATTR_DEVICE_ID
from homeassistant.const import ATTR_ENTITY_ID
from homeassistant.exceptions import ServiceValidationError
from homeassistant.helpers import entity_registry as er
from tests.helpers.service_call import service_call

from .test_init_service_handlers import _InitServiceHandlerBase


class TestInitServiceHandlerDeviceTargeting(_InitServiceHandlerBase):
    """Tests for device targeting and resolver behavior."""

    async def test_get_device_from_entity_target(self, hass) -> None:
        """Resolve target entity unique_id to device serial."""
        device = self._create_device()
        coordinator = self._create_runtime_coordinator()
        coordinator.get_device.return_value = device

        entry = MockConfigEntry(
            domain=DOMAIN,
            data={"phone": "13800000000"},
            options={CONF_DEBUG_MODE: True},
        )
        entry.add_to_hass(hass)
        entry.runtime_data = coordinator

        entity_id = (
            er.async_get(hass)
            .async_get_or_create(
                "light",
                DOMAIN,
                f"lipro_{device.serial}_light",
                suggested_object_id="lipro_test_device",
            )
            .entity_id
        )

        call = service_call(hass, {ATTR_ENTITY_ID: [entity_id]})
        got_device, got_coordinator = await _get_device_and_coordinator(hass, call)

        assert got_device is device
        assert got_coordinator is entry.runtime_data

    async def test_get_device_from_target_entity_id(self, hass) -> None:
        """Resolve device via ServiceCall.target.entity_id."""
        device = self._create_device()
        coordinator = self._create_runtime_coordinator()
        coordinator.get_device.return_value = device

        entry = MockConfigEntry(
            domain=DOMAIN,
            data={"phone": "13800000000"},
            options={CONF_DEBUG_MODE: True},
        )
        entry.add_to_hass(hass)
        entry.runtime_data = coordinator

        entity_id = (
            er.async_get(hass)
            .async_get_or_create(
                "light",
                DOMAIN,
                f"lipro_{device.serial}_light",
                suggested_object_id="lipro_target_test_device",
            )
            .entity_id
        )

        call = service_call(hass, {}, target_entity_ids=[entity_id])
        got_device, got_coordinator = await _get_device_and_coordinator(hass, call)

        assert got_device is device
        assert got_coordinator is entry.runtime_data

    async def test_get_device_from_multiple_entity_targets_same_device_resolves(
        self, hass
    ) -> None:
        """Multiple entities that map to one device should resolve successfully."""
        device = self._create_device()
        coordinator = self._create_runtime_coordinator()
        coordinator.get_device.return_value = device

        entry = MockConfigEntry(
            domain=DOMAIN,
            data={"phone": "13800000000"},
            options={CONF_DEBUG_MODE: True},
        )
        entry.add_to_hass(hass)
        entry.runtime_data = coordinator

        entity_registry = er.async_get(hass)
        entity_1 = entity_registry.async_get_or_create(
            "light",
            DOMAIN,
            f"lipro_{device.serial}_light",
            suggested_object_id="lipro_test_device_1",
        ).entity_id
        entity_2 = entity_registry.async_get_or_create(
            "switch",
            DOMAIN,
            f"lipro_{device.serial}_switch",
            suggested_object_id="lipro_test_device_2",
        ).entity_id

        got_device, got_coordinator = await _get_device_and_coordinator(
            hass,
            service_call(hass, {ATTR_ENTITY_ID: [entity_1, entity_2]}),
        )

        assert got_device is device
        assert got_coordinator is entry.runtime_data

    async def test_get_device_from_multiple_entity_targets_different_devices_raises(
        self, hass
    ) -> None:
        """Multiple entities from different devices should still be rejected."""
        first_device = self._create_device(serial="03ab5ccd7c123456")
        second_device = self._create_device(serial="03ab5ccd7c654321")
        coordinator = self._create_runtime_coordinator()
        coordinator.get_device.side_effect = [first_device, second_device]

        entry = MockConfigEntry(
            domain=DOMAIN,
            data={"phone": "13800000000"},
            options={CONF_DEBUG_MODE: True},
        )
        entry.add_to_hass(hass)
        entry.runtime_data = coordinator

        entity_registry = er.async_get(hass)
        first_entity = entity_registry.async_get_or_create(
            "light",
            DOMAIN,
            f"lipro_{first_device.serial}_light",
            suggested_object_id="lipro_device_first",
        ).entity_id
        second_entity = entity_registry.async_get_or_create(
            "switch",
            DOMAIN,
            f"lipro_{second_device.serial}_switch",
            suggested_object_id="lipro_device_second",
        ).entity_id

        with pytest.raises(ServiceValidationError):
            await _get_device_and_coordinator(
                hass,
                service_call(hass, {ATTR_ENTITY_ID: [first_entity, second_entity]}),
            )

    async def test_get_device_falls_back_to_get_device_by_id(self, hass) -> None:
        """Fallback to coordinator alias lookup when serial lookup misses."""
        device = self._create_device(serial="mesh_group_10001")
        coordinator = self._create_runtime_coordinator()
        coordinator.get_device.return_value = None
        coordinator.get_device_by_id.return_value = device

        entry = MockConfigEntry(
            domain=DOMAIN,
            data={"phone": "13800000000"},
            options={CONF_DEBUG_MODE: True},
        )
        entry.add_to_hass(hass)
        entry.runtime_data = coordinator

        call = service_call(hass, {ATTR_DEVICE_ID: "03AB5CCD7C716177"})
        got_device, got_coordinator = await _get_device_and_coordinator(hass, call)

        assert got_device is device
        assert got_coordinator is entry.runtime_data
        coordinator.get_device.assert_called_once_with("03AB5CCD7C716177")
        coordinator.get_device_by_id.assert_called_once_with("03AB5CCD7C716177")

    async def test_get_device_without_id_or_entity_raises(self, hass) -> None:
        """Missing device_id and entity target should raise validation error."""
        with pytest.raises(ServiceValidationError):
            await _get_device_and_coordinator(hass, service_call(hass, {}))
