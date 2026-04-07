"""Registry/refresh init runtime topical suites."""

from __future__ import annotations

from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from pytest_homeassistant_custom_component.common import MockConfigEntry

from custom_components.lipro import async_setup, async_unload_entry
from custom_components.lipro.const.base import DOMAIN
from custom_components.lipro.const.config import CONF_DEBUG_MODE
from custom_components.lipro.control.service_router import async_handle_refresh_devices
from custom_components.lipro.services.contracts import ATTR_ENTRY_ID
from homeassistant.exceptions import ServiceValidationError
from homeassistant.helpers import device_registry as dr
from tests.helpers.service_call import service_call

from .test_init_runtime_behavior import _InitRuntimeBehaviorBase


class TestInitRefreshAndRegistryBehavior(_InitRuntimeBehaviorBase):
    """Tests for refresh handler and device-registry reactions."""

    async def test_refresh_devices_handler_refreshes_all_loaded_entries(
        self, hass
    ) -> None:
        """refresh_devices should refresh all loaded entry coordinators by default."""
        first = MockConfigEntry(
            domain=DOMAIN,
            data={"phone": "13800000000"},
            options={CONF_DEBUG_MODE: True},
        )
        first.add_to_hass(hass)
        first_service = MagicMock()
        first_service.async_refresh_devices = AsyncMock()
        first.runtime_data = MagicMock(device_refresh_service=first_service)

        second = MockConfigEntry(
            domain=DOMAIN,
            data={"phone": "13900000000"},
            options={CONF_DEBUG_MODE: True},
        )
        second.add_to_hass(hass)
        second_service = MagicMock()
        second_service.async_refresh_devices = AsyncMock()
        second.runtime_data = MagicMock(device_refresh_service=second_service)

        result = await async_handle_refresh_devices(hass, service_call(hass, {}))

        assert result["success"] is True
        assert result["refreshed_entries"] == 2
        assert "entry_ids" not in result
        first_service.async_refresh_devices.assert_awaited_once()
        second_service.async_refresh_devices.assert_awaited_once()

    async def test_refresh_devices_handler_filters_by_entry_id(self, hass) -> None:
        """refresh_devices should refresh only the selected config entry."""
        first = MockConfigEntry(
            domain=DOMAIN,
            data={"phone": "13800000000"},
            options={CONF_DEBUG_MODE: True},
        )
        first.add_to_hass(hass)
        first_service = MagicMock()
        first_service.async_refresh_devices = AsyncMock()
        first.runtime_data = MagicMock(device_refresh_service=first_service)

        second = MockConfigEntry(
            domain=DOMAIN,
            data={"phone": "13900000000"},
            options={CONF_DEBUG_MODE: True},
        )
        second.add_to_hass(hass)
        second_service = MagicMock()
        second_service.async_refresh_devices = AsyncMock()
        second.runtime_data = MagicMock(device_refresh_service=second_service)

        result = await async_handle_refresh_devices(
            hass,
            service_call(hass, {ATTR_ENTRY_ID: second.entry_id}),
        )

        assert result["success"] is True
        assert result["refreshed_entries"] == 1
        assert result["requested_entry_id"] == second.entry_id
        first_service.async_refresh_devices.assert_not_awaited()
        second_service.async_refresh_devices.assert_awaited_once()

    async def test_refresh_devices_handler_unknown_entry_raises(self, hass) -> None:
        """refresh_devices should raise translated validation error for bad entry_id."""
        with pytest.raises(ServiceValidationError) as exc:
            await async_handle_refresh_devices(
                hass,
                service_call(hass, {ATTR_ENTRY_ID: "missing_entry"}),
            )

        assert exc.value.translation_key == "entry_not_found"

    async def test_device_registry_disable_enable_triggers_entry_reload(
        self, hass
    ) -> None:
        """Lipro device disable/enable transitions should trigger config entry reload."""
        entry = MockConfigEntry(
            domain=DOMAIN,
            data={"phone": "13800000000"},
            options={CONF_DEBUG_MODE: True},
        )
        entry.add_to_hass(hass)
        entry.runtime_data = MagicMock()

        with patch.object(
            hass.config_entries,
            "async_reload",
            AsyncMock(return_value=True),
        ) as mock_reload:
            await async_setup(hass, {})

            device_registry = dr.async_get(hass)
            device_entry = device_registry.async_get_or_create(
                config_entry_id=entry.entry_id,
                identifiers={(DOMAIN, "03ab5ccd7c123456")},
                manufacturer="Lipro",
                name="Lipro Device",
            )

            device_registry.async_update_device(
                device_entry.id,
                disabled_by=dr.DeviceEntryDisabler.USER,
            )
            await hass.async_block_till_done()

            device_registry.async_update_device(
                device_entry.id,
                disabled_by=None,
            )
            await hass.async_block_till_done()

        assert mock_reload.await_count == 2
        assert mock_reload.await_args_list[0].args == (entry.entry_id,)
        assert mock_reload.await_args_list[1].args == (entry.entry_id,)

    async def test_device_registry_listener_ignores_non_lipro_device_updates(
        self, hass
    ) -> None:
        """Only Lipro devices with disabled_by changes should trigger reload."""
        entry = MockConfigEntry(
            domain=DOMAIN,
            data={"phone": "13800000000"},
            options={CONF_DEBUG_MODE: True},
        )
        entry.add_to_hass(hass)
        entry.runtime_data = MagicMock()

        with patch.object(
            hass.config_entries,
            "async_reload",
            AsyncMock(return_value=True),
        ) as mock_reload:
            await async_setup(hass, {})

            device_registry = dr.async_get(hass)
            non_lipro = device_registry.async_get_or_create(
                config_entry_id=entry.entry_id,
                identifiers={("other_domain", "dev-1")},
                manufacturer="Other",
                name="Other Device",
            )
            lipro = device_registry.async_get_or_create(
                config_entry_id=entry.entry_id,
                identifiers={(DOMAIN, "03ab5ccd7c999999")},
                manufacturer="Lipro",
                name="Lipro Device",
            )

            # Non-Lipro device: ignore even if disabled_by changed.
            device_registry.async_update_device(
                non_lipro.id,
                disabled_by=dr.DeviceEntryDisabler.USER,
            )
            # Lipro device, but unrelated update: ignore.
            device_registry.async_update_device(
                lipro.id,
                name="Renamed Lipro Device",
            )
            await hass.async_block_till_done()

        mock_reload.assert_not_awaited()

    async def test_async_unload_entry_removes_device_registry_listener(
        self, hass
    ) -> None:
        """Device registry updates should stop reloading after the last unload."""
        entry = MockConfigEntry(
            domain=DOMAIN,
            data={"phone": "13800000000"},
            options={CONF_DEBUG_MODE: True},
        )
        entry.add_to_hass(hass)
        entry.runtime_data = MagicMock(async_shutdown=AsyncMock())

        with patch.object(
            hass.config_entries,
            "async_reload",
            AsyncMock(return_value=True),
        ) as mock_reload:
            await async_setup(hass, {})

            device_registry = dr.async_get(hass)
            device_entry = device_registry.async_get_or_create(
                config_entry_id=entry.entry_id,
                identifiers={(DOMAIN, "03ab5ccd7c111111")},
                manufacturer="Lipro",
                name="Lipro Device",
            )

            with patch.object(
                hass.config_entries,
                "async_unload_platforms",
                AsyncMock(return_value=True),
            ):
                assert await async_unload_entry(hass, entry) is True

            device_registry.async_update_device(
                device_entry.id,
                disabled_by=dr.DeviceEntryDisabler.USER,
            )
            await hass.async_block_till_done()

        mock_reload.assert_not_awaited()
