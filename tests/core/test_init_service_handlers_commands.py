"""Command-dispatch init service-handler topical suites."""

from __future__ import annotations

from unittest.mock import AsyncMock, MagicMock

import pytest
from pytest_homeassistant_custom_component.common import MockConfigEntry

from custom_components.lipro.const.base import DOMAIN
from custom_components.lipro.const.config import CONF_DEBUG_MODE
from custom_components.lipro.control.service_router import async_handle_send_command
from custom_components.lipro.core import LiproApiError
from custom_components.lipro.services.contracts import (
    ATTR_COMMAND,
    ATTR_DEVICE_ID,
    ATTR_PROPERTIES,
)
from homeassistant.exceptions import HomeAssistantError
from tests.helpers.service_call import service_call

from .test_init_service_handlers import _InitServiceHandlerBase


class TestInitServiceHandlerCommandDispatch(_InitServiceHandlerBase):
    """Tests for send-command handler dispatch and error mapping."""

    async def test_send_command_handler_success(self, hass) -> None:
        """send_command returns success payload on coordinator success."""
        device = self._create_device()
        coordinator = self._create_runtime_coordinator()
        coordinator.get_device.return_value = device
        command_service = MagicMock()
        command_service.async_send_command = AsyncMock(return_value=True)
        coordinator.command_service = command_service

        entry = MockConfigEntry(
            domain=DOMAIN,
            data={"phone": "13800000000"},
            options={CONF_DEBUG_MODE: True},
        )
        entry.add_to_hass(hass)
        entry.runtime_data = coordinator

        result = await async_handle_send_command(
            hass,
            service_call(
                hass,
                {
                    ATTR_DEVICE_ID: device.serial,
                    ATTR_COMMAND: "POWER_ON",
                    ATTR_PROPERTIES: [{"key": "powerState", "value": "1"}],
                },
            ),
        )
        assert result == {"success": True, "serial": device.serial}
        command_service.async_send_command.assert_awaited_once_with(
            device,
            "POWER_ON",
            [{"key": "powerState", "value": "1"}],
            fallback_device_id=device.serial,
        )

    async def test_send_command_handler_alias_resolution_metadata(self, hass) -> None:
        """send_command response includes alias-resolution metadata when remapped."""
        requested_id = "03ab0000000000f1"
        group_device = self._create_device(serial="mesh_group_10001")
        group_device.is_group = True

        coordinator = self._create_runtime_coordinator()
        coordinator.get_device.return_value = None
        coordinator.get_device_by_id.return_value = group_device
        command_service = MagicMock()
        command_service.async_send_command = AsyncMock(return_value=True)
        coordinator.command_service = command_service

        entry = MockConfigEntry(
            domain=DOMAIN,
            data={"phone": "13800000000"},
            options={CONF_DEBUG_MODE: True},
        )
        entry.add_to_hass(hass)
        entry.runtime_data = coordinator

        result = await async_handle_send_command(
            hass,
            service_call(
                hass,
                {
                    ATTR_DEVICE_ID: requested_id,
                    ATTR_COMMAND: "POWER_ON",
                },
            ),
        )

        assert result == {
            "success": True,
            "serial": "mesh_group_10001",
            "requested_device_id": requested_id,
            "resolved_device_id": "mesh_group_10001",
        }
        coordinator.get_device.assert_called_once_with(requested_id)
        coordinator.get_device_by_id.assert_called_once_with(requested_id)
        command_service.async_send_command.assert_awaited_once_with(
            group_device,
            "POWER_ON",
            None,
            fallback_device_id=requested_id,
        )

    async def test_send_command_handler_invalid_properties_fail_fast(self, hass) -> None:
        """Direct handler calls should reject invalid properties instead of dropping them."""
        with pytest.raises(HomeAssistantError) as exc:
            await async_handle_send_command(
                hass,
                service_call(
                    hass,
                    {
                        ATTR_COMMAND: "POWER_ON",
                        ATTR_PROPERTIES: {"key": "powerState", "value": "1"},
                    },
                ),
            )
        assert exc.value.translation_key == "invalid_command_request"

    async def test_send_command_handler_invalid_device_id_type_fails_fast(self, hass) -> None:
        """Direct handler calls should reject invalid device_id types."""
        with pytest.raises(HomeAssistantError) as exc:
            await async_handle_send_command(
                hass,
                service_call(
                    hass,
                    {
                        ATTR_DEVICE_ID: 12345,
                        ATTR_COMMAND: "POWER_ON",
                    },
                ),
            )
        assert exc.value.translation_key == "invalid_command_request"

    async def test_send_command_handler_empty_command_fails_schema_validation(
        self, hass
    ) -> None:
        """Direct handler calls should reject empty command strings."""
        with pytest.raises(HomeAssistantError) as exc:
            await async_handle_send_command(
                hass,
                service_call(
                    hass,
                    {
                        ATTR_DEVICE_ID: "mesh_group_49155",
                        ATTR_COMMAND: "",
                    },
                ),
            )
        assert exc.value.translation_key == "invalid_command_request"

    @pytest.mark.parametrize(
        "properties",
        [
            [{"key": "powerState"}],
            [["not-a-dict"]],
        ],
    )
    async def test_send_command_handler_invalid_property_items_fail_fast(
        self, hass, properties
    ) -> None:
        """Direct handler calls should reject malformed property list items."""
        with pytest.raises(HomeAssistantError) as exc:
            await async_handle_send_command(
                hass,
                service_call(
                    hass,
                    {
                        ATTR_COMMAND: "POWER_ON",
                        ATTR_PROPERTIES: properties,
                    },
                ),
            )
        assert exc.value.translation_key == "invalid_command_request"

    async def test_send_command_handler_failure_raises(self, hass) -> None:
        """send_command raises HomeAssistantError when coordinator reports failure."""
        device = self._create_device()
        coordinator = self._create_runtime_coordinator()
        coordinator.get_device.return_value = device
        command_service = MagicMock()
        command_service.async_send_command = AsyncMock(return_value=False)
        coordinator.command_service = command_service
        command_service.last_failure = None

        entry = MockConfigEntry(
            domain=DOMAIN,
            data={"phone": "13800000000"},
            options={CONF_DEBUG_MODE: True},
        )
        entry.add_to_hass(hass)
        entry.runtime_data = coordinator

        with pytest.raises(HomeAssistantError):
            await async_handle_send_command(
                hass,
                service_call(
                    hass,
                    {ATTR_DEVICE_ID: device.serial, ATTR_COMMAND: "POWER_ON"},
                ),
            )

    async def test_send_command_handler_push_failed_maps_translation(
        self, hass
    ) -> None:
        """pushSuccess=false style failures should use push_failed translation key."""
        device = self._create_device()
        coordinator = self._create_runtime_coordinator()
        coordinator.get_device.return_value = device
        command_service = MagicMock()
        command_service.async_send_command = AsyncMock(return_value=False)
        coordinator.command_service = command_service
        command_service.last_failure = {
            "reason": "push_failed",
            "code": "push_failed",
        }

        entry = MockConfigEntry(
            domain=DOMAIN,
            data={"phone": "13800000000"},
            options={CONF_DEBUG_MODE: True},
        )
        entry.add_to_hass(hass)
        entry.runtime_data = coordinator

        with pytest.raises(HomeAssistantError) as exc:
            await async_handle_send_command(
                hass,
                service_call(
                    hass,
                    {ATTR_DEVICE_ID: device.serial, ATTR_COMMAND: "POWER_ON"},
                ),
            )
        assert exc.value.translation_key == "command_push_failed"

    async def test_send_command_handler_offline_code_maps_translation(
        self, hass
    ) -> None:
        """140004 failures should use device-not-connected translation key."""
        device = self._create_device()
        coordinator = self._create_runtime_coordinator()
        coordinator.get_device.return_value = device
        command_service = MagicMock()
        command_service.async_send_command = AsyncMock(return_value=False)
        coordinator.command_service = command_service
        command_service.last_failure = {"reason": "api_error", "code": "140004"}

        entry = MockConfigEntry(
            domain=DOMAIN,
            data={"phone": "13800000000"},
            options={CONF_DEBUG_MODE: True},
        )
        entry.add_to_hass(hass)
        entry.runtime_data = coordinator

        with pytest.raises(HomeAssistantError) as exc:
            await async_handle_send_command(
                hass,
                service_call(
                    hass,
                    {ATTR_DEVICE_ID: device.serial, ATTR_COMMAND: "POWER_ON"},
                ),
            )
        assert exc.value.translation_key == "command_device_not_connected"

    async def test_send_command_handler_busy_code_maps_translation(self, hass) -> None:
        """250001 failures should use device-busy translation key."""
        device = self._create_device()
        coordinator = self._create_runtime_coordinator()
        coordinator.get_device.return_value = device
        command_service = MagicMock()
        command_service.async_send_command = AsyncMock(return_value=False)
        coordinator.command_service = command_service
        command_service.last_failure = {"reason": "api_error", "code": "250001"}

        entry = MockConfigEntry(
            domain=DOMAIN,
            data={"phone": "13800000000"},
            options={CONF_DEBUG_MODE: True},
        )
        entry.add_to_hass(hass)
        entry.runtime_data = coordinator

        with pytest.raises(HomeAssistantError) as exc:
            await async_handle_send_command(
                hass,
                service_call(
                    hass,
                    {ATTR_DEVICE_ID: device.serial, ATTR_COMMAND: "POWER_ON"},
                ),
            )
        assert exc.value.translation_key == "command_device_busy"

    async def test_send_command_handler_api_error_raises(self, hass) -> None:
        """send_command maps API errors to HomeAssistantError."""
        device = self._create_device()
        coordinator = self._create_runtime_coordinator()
        coordinator.get_device.return_value = device
        command_service = MagicMock()
        command_service.async_send_command = AsyncMock(
            side_effect=LiproApiError("boom")
        )
        coordinator.command_service = command_service

        entry = MockConfigEntry(
            domain=DOMAIN,
            data={"phone": "13800000000"},
            options={CONF_DEBUG_MODE: True},
        )
        entry.add_to_hass(hass)
        entry.runtime_data = coordinator

        with pytest.raises(HomeAssistantError):
            await async_handle_send_command(
                hass,
                service_call(
                    hass,
                    {ATTR_DEVICE_ID: device.serial, ATTR_COMMAND: "POWER_ON"},
                ),
            )

    async def test_send_command_handler_api_error_code_maps_translation(
        self, hass
    ) -> None:
        """API error 140003 should map to device-offline translation key."""
        device = self._create_device()
        coordinator = self._create_runtime_coordinator()
        coordinator.get_device.return_value = device
        command_service = MagicMock()
        command_service.async_send_command = AsyncMock(
            side_effect=LiproApiError("offline", "140003")
        )
        coordinator.command_service = command_service

        entry = MockConfigEntry(
            domain=DOMAIN,
            data={"phone": "13800000000"},
            options={CONF_DEBUG_MODE: True},
        )
        entry.add_to_hass(hass)
        entry.runtime_data = coordinator

        with pytest.raises(HomeAssistantError) as exc:
            await async_handle_send_command(
                hass,
                service_call(
                    hass,
                    {ATTR_DEVICE_ID: device.serial, ATTR_COMMAND: "POWER_ON"},
                ),
            )
        assert exc.value.translation_key == "command_device_offline"

    async def test_send_command_handler_api_busy_error_maps_translation(
        self, hass
    ) -> None:
        """API error 250001 should map to device-busy translation key."""
        device = self._create_device()
        coordinator = self._create_runtime_coordinator()
        coordinator.get_device.return_value = device
        command_service = MagicMock()
        command_service.async_send_command = AsyncMock(
            side_effect=LiproApiError("busy", "250001")
        )
        coordinator.command_service = command_service

        entry = MockConfigEntry(
            domain=DOMAIN,
            data={"phone": "13800000000"},
            options={CONF_DEBUG_MODE: True},
        )
        entry.add_to_hass(hass)
        entry.runtime_data = coordinator

        with pytest.raises(HomeAssistantError) as exc:
            await async_handle_send_command(
                hass,
                service_call(
                    hass,
                    {ATTR_DEVICE_ID: device.serial, ATTR_COMMAND: "POWER_ON"},
                ),
            )
        assert exc.value.translation_key == "command_device_busy"

    async def test_send_command_handler_not_found_code_maps_offline_translation(
        self, hass
    ) -> None:
        """API error 140013 should map to device-offline translation key."""
        device = self._create_device()
        coordinator = self._create_runtime_coordinator()
        coordinator.get_device.return_value = device
        command_service = MagicMock()
        command_service.async_send_command = AsyncMock(
            side_effect=LiproApiError("not found", "140013")
        )
        coordinator.command_service = command_service

        entry = MockConfigEntry(
            domain=DOMAIN,
            data={"phone": "13800000000"},
            options={CONF_DEBUG_MODE: True},
        )
        entry.add_to_hass(hass)
        entry.runtime_data = coordinator

        with pytest.raises(HomeAssistantError) as exc:
            await async_handle_send_command(
                hass,
                service_call(
                    hass,
                    {ATTR_DEVICE_ID: device.serial, ATTR_COMMAND: "POWER_ON"},
                ),
            )
        assert exc.value.translation_key == "command_device_offline"
