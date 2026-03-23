"""Sensor-history and developer-feedback init service-handler topical suites."""

from __future__ import annotations

import logging
from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from pytest_homeassistant_custom_component.common import MockConfigEntry

from custom_components.lipro.const.base import DOMAIN
from custom_components.lipro.const.config import CONF_DEBUG_MODE
from custom_components.lipro.control.service_router import (
    async_handle_fetch_body_sensor_history,
    async_handle_fetch_door_sensor_history,
    async_handle_submit_developer_feedback,
)
from custom_components.lipro.services.contracts import (
    ATTR_DEVICE_ID,
    ATTR_ENTRY_ID,
    ATTR_MESH_TYPE,
    ATTR_SENSOR_DEVICE_ID,
)
from homeassistant.exceptions import HomeAssistantError, ServiceValidationError
from tests.helpers.service_call import service_call

from .test_init_service_handlers import _InitServiceHandlerBase

_TEST_LOGGER = logging.getLogger(__name__)


class TestInitServiceHandlerSensorHistoryAndFeedback(_InitServiceHandlerBase):
    """Tests for sensor-history and developer-feedback handlers."""

    async def test_fetch_body_sensor_history_service(self, hass) -> None:
        """fetch_body_sensor_history should pass sensor payload to client."""
        device = self._create_device(serial="mesh_group_49155")
        coordinator = self._attach_auth_service(MagicMock())
        coordinator.get_device.return_value = device
        coordinator.protocol_service.async_fetch_body_sensor_history = AsyncMock(
            return_value={"humanSensorStateList": []}
        )

        entry = MockConfigEntry(
            domain=DOMAIN,
            data={"phone": "13800000000"},
            options={CONF_DEBUG_MODE: True},
        )
        entry.add_to_hass(hass)
        entry.runtime_data = coordinator

        result = await async_handle_fetch_body_sensor_history(
            hass,
            service_call(
                hass,
                {
                    ATTR_DEVICE_ID: device.serial,
                    ATTR_SENSOR_DEVICE_ID: "03ab5ccd7c7167d8",
                    ATTR_MESH_TYPE: "2",
                },
            ),
        )

        assert result["serial"] == "mesh_group_49155"
        coordinator.protocol_service.async_fetch_body_sensor_history.assert_awaited_once_with(
            device_id="mesh_group_49155",
            device_type=device.device_type,
            sensor_device_id="03ab5ccd7c7167d8",
            mesh_type="2",
        )

    async def test_fetch_body_sensor_history_service_requires_debug_mode(
        self, hass
    ) -> None:
        """fetch_body_sensor_history should reject entries without debug opt-in."""
        device = self._create_device(serial="mesh_group_49155")
        coordinator = self._attach_auth_service(MagicMock())
        coordinator.get_device.return_value = device
        coordinator.protocol_service.async_fetch_body_sensor_history = AsyncMock(
            return_value={"humanSensorStateList": []}
        )

        entry = MockConfigEntry(domain=DOMAIN, data={"phone": "13800000000"})
        entry.add_to_hass(hass)
        entry.runtime_data = coordinator

        with pytest.raises(ServiceValidationError):
            await async_handle_fetch_body_sensor_history(
                hass,
                service_call(
                    hass,
                    {
                        ATTR_DEVICE_ID: device.serial,
                        ATTR_SENSOR_DEVICE_ID: "03ab5ccd7c7167d8",
                        ATTR_MESH_TYPE: "2",
                    },
                ),
            )

        coordinator.protocol_service.async_fetch_body_sensor_history.assert_not_awaited()

    async def test_fetch_door_sensor_history_service(self, hass) -> None:
        """fetch_door_sensor_history should pass sensor payload to client."""
        device = self._create_device(serial="mesh_group_49155")
        coordinator = self._attach_auth_service(MagicMock())
        coordinator.get_device.return_value = device
        coordinator.protocol_service.async_fetch_door_sensor_history = AsyncMock(
            return_value={"doorStateList": []}
        )

        entry = MockConfigEntry(
            domain=DOMAIN,
            data={"phone": "13800000000"},
            options={CONF_DEBUG_MODE: True},
        )
        entry.add_to_hass(hass)
        entry.runtime_data = coordinator

        result = await async_handle_fetch_door_sensor_history(
            hass,
            service_call(
                hass,
                {
                    ATTR_DEVICE_ID: device.serial,
                    ATTR_SENSOR_DEVICE_ID: "03ab5ccd7c7167d8",
                    ATTR_MESH_TYPE: "2",
                },
            ),
        )

        assert result["serial"] == "mesh_group_49155"
        coordinator.protocol_service.async_fetch_door_sensor_history.assert_awaited_once_with(
            device_id="mesh_group_49155",
            device_type=device.device_type,
            sensor_device_id="03ab5ccd7c7167d8",
            mesh_type="2",
        )

    async def test_submit_developer_feedback_success(self, hass) -> None:
        """submit_developer_feedback uploads one scoped report when entry_id is provided."""
        coordinator = self._create_runtime_coordinator()

        entry = MockConfigEntry(
            domain=DOMAIN,
            data={"phone": "13800000000"},
            options={CONF_DEBUG_MODE: True},
        )
        entry.add_to_hass(hass)
        entry.runtime_data = coordinator

        share_manager = MagicMock()
        share_manager.submit_developer_feedback = AsyncMock(return_value=True)

        with (
            patch(
                "custom_components.lipro.control.service_router.get_anonymous_share_manager",
                return_value=share_manager,
            ) as get_share_manager,
            patch(
                "custom_components.lipro.control.service_router.async_get_clientsession",
                return_value=MagicMock(),
            ),
            patch(
                "custom_components.lipro.control.telemetry_surface.get_entry_telemetry_view",
                return_value={"runtime": {"ok": True}},
            ),
        ):
            result = await async_handle_submit_developer_feedback(
                hass,
                service_call(
                    hass,
                    {ATTR_ENTRY_ID: entry.entry_id, "note": "manual validation run"},
                ),
            )

        assert result == {
            "success": True,
            "submitted_entries": 1,
            "requested_entry_id": entry.entry_id,
        }
        get_share_manager.assert_called_once_with(hass, entry_id=entry.entry_id)
        share_manager.submit_developer_feedback.assert_awaited_once()

    async def test_submit_developer_feedback_failure_raises(self, hass) -> None:
        """submit_developer_feedback raises when upload fails."""
        coordinator = self._create_runtime_coordinator()

        entry = MockConfigEntry(
            domain=DOMAIN,
            data={"phone": "13800000000"},
            options={CONF_DEBUG_MODE: True},
        )
        entry.add_to_hass(hass)
        entry.runtime_data = coordinator

        share_manager = MagicMock()
        share_manager.submit_developer_feedback = AsyncMock(return_value=False)

        with (
            patch(
                "custom_components.lipro.control.service_router.get_anonymous_share_manager",
                return_value=share_manager,
            ),
            patch(
                "custom_components.lipro.control.service_router.async_get_clientsession",
                return_value=MagicMock(),
            ),
            patch(
                "custom_components.lipro.control.telemetry_surface.get_entry_telemetry_view",
                return_value={"runtime": {"ok": True}},
            ),
            pytest.raises(HomeAssistantError),
        ):
            await async_handle_submit_developer_feedback(hass, service_call(hass, {}))

