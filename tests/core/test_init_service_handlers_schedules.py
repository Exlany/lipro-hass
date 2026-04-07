"""Schedule-focused init service-handler topical suites."""

from __future__ import annotations

from unittest.mock import AsyncMock, MagicMock

import pytest
from pytest_homeassistant_custom_component.common import MockConfigEntry

from custom_components.lipro.const.base import DOMAIN
from custom_components.lipro.const.config import CONF_DEBUG_MODE
from custom_components.lipro.control.service_router import (
    async_handle_add_schedule,
    async_handle_delete_schedules,
    async_handle_get_schedules,
)
from custom_components.lipro.services.contracts import (
    ATTR_DAYS,
    ATTR_DEVICE_ID,
    ATTR_EVENTS,
    ATTR_SCHEDULE_IDS,
    ATTR_TIMES,
)
from homeassistant.const import ATTR_ENTITY_ID
from homeassistant.exceptions import ServiceValidationError
from homeassistant.helpers import entity_registry as er
from tests.helpers.service_call import service_call

from .test_init_service_handlers import _InitServiceHandlerBase


class TestInitServiceHandlerScheduleValidation(_InitServiceHandlerBase):
    """Tests for schedule-specific input validation."""

    async def test_add_schedule_times_events_mismatch_raises(self, hass) -> None:
        """Mismatched lengths in add_schedule should fail validation."""
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

        call = service_call(
            hass,
            {
                ATTR_DEVICE_ID: device.serial,
                ATTR_DAYS: [1, 2],
                ATTR_TIMES: [3600],
                ATTR_EVENTS: [1, 0],
            },
        )

        with pytest.raises(ServiceValidationError):
            await async_handle_add_schedule(hass, call)


    async def test_get_schedules_empty_device_id_fails_fast(self, hass) -> None:
        """Direct get_schedules calls should reject empty device_id values."""
        with pytest.raises(ServiceValidationError) as exc_info:
            await async_handle_get_schedules(
                hass,
                service_call(hass, {ATTR_DEVICE_ID: ""}),
            )

        assert exc_info.value.translation_key == "invalid_schedule_request"

    async def test_add_schedule_invalid_day_value_fails_fast(self, hass) -> None:
        """Direct add_schedule calls should reject malformed schedule items."""
        with pytest.raises(ServiceValidationError) as exc_info:
            await async_handle_add_schedule(
                hass,
                service_call(
                    hass,
                    {
                        ATTR_DAYS: ["bad"],
                        ATTR_TIMES: [3600],
                        ATTR_EVENTS: [1],
                    },
                ),
            )

        assert exc_info.value.translation_key == "invalid_schedule_request"

    async def test_delete_schedules_invalid_ids_fail_fast(self, hass) -> None:
        """Direct delete_schedules calls should reject malformed schedule_ids."""
        with pytest.raises(ServiceValidationError) as exc_info:
            await async_handle_delete_schedules(
                hass,
                service_call(hass, {ATTR_SCHEDULE_IDS: ["bad"]}),
            )

        assert exc_info.value.translation_key == "invalid_schedule_request"


class TestInitServiceHandlerSchedules(_InitServiceHandlerBase):
    """Tests for schedule query/mutation handlers."""

    async def test_get_schedules_formats_response(self, hass) -> None:
        """get_schedules returns normalized response payload."""
        device = self._create_device()
        client = MagicMock()
        client.get_device_schedules = AsyncMock(
            return_value=[
                {
                    "id": 5,
                    "active": True,
                    "schedule": {"days": [1], "time": [3600, 3661], "evt": [1, 0]},
                }
            ]
        )
        coordinator = self._attach_auth_service(MagicMock())
        coordinator.get_device.return_value = device
        coordinator.protocol = client
        coordinator.protocol_service.async_get_device_schedules_for_device = client.get_device_schedules
        coordinator.protocol_service.async_add_device_schedule_for_device = client.add_device_schedule
        coordinator.protocol_service.async_delete_device_schedules_for_device = client.delete_device_schedules

        entry = MockConfigEntry(
            domain=DOMAIN,
            data={"phone": "13800000000"},
            options={CONF_DEBUG_MODE: True},
        )
        entry.add_to_hass(hass)
        entry.runtime_data = coordinator

        result = await async_handle_get_schedules(
            hass, service_call(hass, {ATTR_DEVICE_ID: device.serial})
        )

        assert result == {
            "serial": device.serial,
            "schedules": [
                {
                    "id": 5,
                    "active": True,
                    "days": [1],
                    "times": ["01:00", "01:01"],
                    "events": [1, 0],
                }
            ],
        }

    async def test_get_schedules_resolves_device_from_entity_target(self, hass) -> None:
        """get_schedules should resolve target entity when device_id is omitted."""
        device = self._create_device()
        client = MagicMock()
        client.get_device_schedules = AsyncMock(return_value=[])
        coordinator = self._attach_auth_service(MagicMock())
        coordinator.get_device.return_value = device
        coordinator.protocol = client
        coordinator.protocol_service.async_get_device_schedules_for_device = client.get_device_schedules
        coordinator.protocol_service.async_add_device_schedule_for_device = client.add_device_schedule
        coordinator.protocol_service.async_delete_device_schedules_for_device = client.delete_device_schedules

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

        result = await async_handle_get_schedules(
            hass, service_call(hass, {ATTR_ENTITY_ID: entity_id})
        )

        assert result == {"serial": device.serial, "schedules": []}
        coordinator.get_device.assert_called_once_with(device.serial)
        client.get_device_schedules.assert_awaited_once_with(device)

    async def test_get_schedules_ignores_malformed_schedule_rows(self, hass) -> None:
        """Malformed schedule rows should be ignored instead of raising."""
        device = self._create_device()
        client = MagicMock()
        client.get_device_schedules = AsyncMock(
            return_value=[
                "invalid-row",
                {
                    "id": 9,
                    "active": True,
                    "schedule": {
                        "days": ["1", "x"],
                        "time": [3600, -1, 90000, "bad"],
                        "evt": [1, "0", "bad"],
                    },
                },
            ]
        )
        coordinator = self._attach_auth_service(MagicMock())
        coordinator.get_device.return_value = device
        coordinator.protocol = client
        coordinator.protocol_service.async_get_device_schedules_for_device = client.get_device_schedules
        coordinator.protocol_service.async_add_device_schedule_for_device = client.add_device_schedule
        coordinator.protocol_service.async_delete_device_schedules_for_device = client.delete_device_schedules

        entry = MockConfigEntry(
            domain=DOMAIN,
            data={"phone": "13800000000"},
            options={CONF_DEBUG_MODE: True},
        )
        entry.add_to_hass(hass)
        entry.runtime_data = coordinator

        result = await async_handle_get_schedules(
            hass, service_call(hass, {ATTR_DEVICE_ID: device.serial})
        )

        assert result == {
            "serial": device.serial,
            "schedules": [
                {
                    "id": 9,
                    "active": True,
                    "days": [1],
                    "times": ["01:00"],
                    "events": [1],
                }
            ],
        }

    async def test_get_schedules_passes_mesh_context(self, hass) -> None:
        """get_schedules should delegate the device to protocol service context resolution."""
        device = self._create_device(serial="mesh_group_10001")
        device.extra_data["gateway_device_id"] = "03ab0000000000a1"
        device.extra_data["group_member_ids"] = ["03ab0000000000a2"]

        client = MagicMock()
        client.get_device_schedules = AsyncMock(return_value=[])
        coordinator = self._attach_auth_service(MagicMock())
        coordinator.get_device.return_value = device
        coordinator.protocol = client
        coordinator.protocol_service.async_get_device_schedules_for_device = client.get_device_schedules
        coordinator.protocol_service.async_add_device_schedule_for_device = client.add_device_schedule
        coordinator.protocol_service.async_delete_device_schedules_for_device = client.delete_device_schedules

        entry = MockConfigEntry(
            domain=DOMAIN,
            data={"phone": "13800000000"},
            options={CONF_DEBUG_MODE: True},
        )
        entry.add_to_hass(hass)
        entry.runtime_data = coordinator

        await async_handle_get_schedules(
            hass, service_call(hass, {ATTR_DEVICE_ID: device.serial})
        )

        client.get_device_schedules.assert_awaited_once_with(device)

    async def test_add_schedule_passes_mesh_context(self, hass) -> None:
        """add_schedule should delegate the device to protocol service context resolution."""
        device = self._create_device(serial="mesh_group_10001")
        device.extra_data["gateway_device_id"] = "03ab0000000000a1"
        device.extra_data["group_member_ids"] = ["03ab0000000000a2"]

        client = MagicMock()
        client.add_device_schedule = AsyncMock(return_value=[{"id": 1}])
        coordinator = self._attach_auth_service(MagicMock())
        coordinator.get_device.return_value = device
        coordinator.protocol = client
        coordinator.protocol_service.async_get_device_schedules_for_device = client.get_device_schedules
        coordinator.protocol_service.async_add_device_schedule_for_device = client.add_device_schedule
        coordinator.protocol_service.async_delete_device_schedules_for_device = client.delete_device_schedules

        entry = MockConfigEntry(
            domain=DOMAIN,
            data={"phone": "13800000000"},
            options={CONF_DEBUG_MODE: True},
        )
        entry.add_to_hass(hass)
        entry.runtime_data = coordinator

        result = await async_handle_add_schedule(
            hass,
            service_call(
                hass,
                {
                    ATTR_DEVICE_ID: device.serial,
                    ATTR_DAYS: [1, 2, 3],
                    ATTR_TIMES: [3600],
                    ATTR_EVENTS: [0],
                },
            ),
        )

        assert result["schedule_count"] == 1
        client.add_device_schedule.assert_awaited_once_with(device, [1, 2, 3], [3600], [0])

    async def test_add_schedule_resolves_device_from_entity_target(self, hass) -> None:
        """add_schedule should resolve target entity when device_id is omitted."""
        device = self._create_device()
        client = MagicMock()
        client.add_device_schedule = AsyncMock(return_value=[{"id": 1}])
        coordinator = self._attach_auth_service(MagicMock())
        coordinator.get_device.return_value = device
        coordinator.protocol = client
        coordinator.protocol_service.async_get_device_schedules_for_device = client.get_device_schedules
        coordinator.protocol_service.async_add_device_schedule_for_device = client.add_device_schedule
        coordinator.protocol_service.async_delete_device_schedules_for_device = client.delete_device_schedules

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

        result = await async_handle_add_schedule(
            hass,
            service_call(
                hass,
                {
                    ATTR_ENTITY_ID: [entity_id],
                    ATTR_DAYS: [1],
                    ATTR_TIMES: [3600],
                    ATTR_EVENTS: [1],
                },
            ),
        )

        assert result == {
            "success": True,
            "serial": device.serial,
            "schedule_count": 1,
        }
        coordinator.get_device.assert_called_once_with(device.serial)
        client.add_device_schedule.assert_awaited_once_with(device, [1], [3600], [1])

    async def test_delete_schedules_returns_summary(self, hass) -> None:
        """delete_schedules returns remaining count on success."""
        device = self._create_device()
        client = MagicMock()
        client.delete_device_schedules = AsyncMock(return_value=[{"id": 2}, {"id": 3}])
        coordinator = self._attach_auth_service(MagicMock())
        coordinator.get_device.return_value = device
        coordinator.protocol = client
        coordinator.protocol_service.async_get_device_schedules_for_device = client.get_device_schedules
        coordinator.protocol_service.async_add_device_schedule_for_device = client.add_device_schedule
        coordinator.protocol_service.async_delete_device_schedules_for_device = client.delete_device_schedules

        entry = MockConfigEntry(
            domain=DOMAIN,
            data={"phone": "13800000000"},
            options={CONF_DEBUG_MODE: True},
        )
        entry.add_to_hass(hass)
        entry.runtime_data = coordinator

        result = await async_handle_delete_schedules(
            hass,
            service_call(
                hass,
                {ATTR_DEVICE_ID: device.serial, ATTR_SCHEDULE_IDS: [1]},
            ),
        )
        assert result == {
            "success": True,
            "serial": device.serial,
            "remaining_count": 2,
        }

    async def test_delete_schedules_passes_mesh_context(self, hass) -> None:
        """delete_schedules should delegate the device to protocol service context resolution."""
        device = self._create_device(serial="mesh_group_10001")
        device.extra_data["gateway_device_id"] = "03ab0000000000a1"
        device.extra_data["group_member_ids"] = ["03ab0000000000a2"]

        client = MagicMock()
        client.delete_device_schedules = AsyncMock(return_value=[])
        coordinator = self._attach_auth_service(MagicMock())
        coordinator.get_device.return_value = device
        coordinator.protocol = client
        coordinator.protocol_service.async_get_device_schedules_for_device = client.get_device_schedules
        coordinator.protocol_service.async_add_device_schedule_for_device = client.add_device_schedule
        coordinator.protocol_service.async_delete_device_schedules_for_device = client.delete_device_schedules

        entry = MockConfigEntry(
            domain=DOMAIN,
            data={"phone": "13800000000"},
            options={CONF_DEBUG_MODE: True},
        )
        entry.add_to_hass(hass)
        entry.runtime_data = coordinator

        await async_handle_delete_schedules(
            hass,
            service_call(
                hass,
                {ATTR_DEVICE_ID: device.serial, ATTR_SCHEDULE_IDS: [1, 2]},
            ),
        )

        client.delete_device_schedules.assert_awaited_once_with(device, [1, 2])

    async def test_delete_schedules_resolves_device_from_entity_target(
        self, hass
    ) -> None:
        """delete_schedules should resolve target entity when device_id is omitted."""
        device = self._create_device()
        client = MagicMock()
        client.delete_device_schedules = AsyncMock(return_value=[])
        coordinator = self._attach_auth_service(MagicMock())
        coordinator.get_device.return_value = device
        coordinator.protocol = client
        coordinator.protocol_service.async_get_device_schedules_for_device = client.get_device_schedules
        coordinator.protocol_service.async_add_device_schedule_for_device = client.add_device_schedule
        coordinator.protocol_service.async_delete_device_schedules_for_device = client.delete_device_schedules

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

        result = await async_handle_delete_schedules(
            hass,
            service_call(
                hass,
                {ATTR_ENTITY_ID: entity_id, ATTR_SCHEDULE_IDS: [1, 2]},
            ),
        )

        assert result == {
            "success": True,
            "serial": device.serial,
            "remaining_count": 0,
        }
        coordinator.get_device.assert_called_once_with(device.serial)
        client.delete_device_schedules.assert_awaited_once_with(device, [1, 2])
