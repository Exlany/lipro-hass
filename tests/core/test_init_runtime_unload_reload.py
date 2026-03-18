"""Unload/reload init runtime topical suites."""

from __future__ import annotations

from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from pytest_homeassistant_custom_component.common import MockConfigEntry

from custom_components.lipro import async_reload_entry, async_setup, async_unload_entry
from custom_components.lipro.const.base import DOMAIN
from custom_components.lipro.const.config import CONF_DEBUG_MODE
from custom_components.lipro.services.contracts import (
    SERVICE_GET_CITY,
    SERVICE_GET_DEVELOPER_REPORT,
    SERVICE_GET_SCHEDULES,
    SERVICE_QUERY_COMMAND_RESULT,
    SERVICE_QUERY_USER_CLOUD,
    SERVICE_REFRESH_DEVICES,
    SERVICE_SEND_COMMAND,
    SERVICE_SUBMIT_DEVELOPER_FEEDBACK,
)
from homeassistant.exceptions import ConfigEntryNotReady

from .test_init_runtime_behavior import _InitRuntimeBehaviorBase


class TestInitUnloadAndReloadBehavior(_InitRuntimeBehaviorBase):
    """Tests for unload/reload lifecycle behavior."""

    async def test_async_unload_entry_removes_services_on_last_entry(
        self, hass
    ) -> None:
        """Service registrations are removed when last entry unloads."""
        await async_setup(hass, {})
        entry = MockConfigEntry(
            domain=DOMAIN,
            data={"phone": "13800000000"},
            options={CONF_DEBUG_MODE: True},
        )
        entry.add_to_hass(hass)

        with patch.object(
            hass.config_entries,
            "async_unload_platforms",
            AsyncMock(return_value=True),
        ):
            assert await async_unload_entry(hass, entry) is True

        assert not hass.services.has_service(DOMAIN, SERVICE_SEND_COMMAND)
        assert not hass.services.has_service(DOMAIN, SERVICE_GET_SCHEDULES)
        assert not hass.services.has_service(DOMAIN, SERVICE_GET_DEVELOPER_REPORT)
        assert not hass.services.has_service(DOMAIN, SERVICE_SUBMIT_DEVELOPER_FEEDBACK)
        assert not hass.services.has_service(DOMAIN, SERVICE_QUERY_COMMAND_RESULT)
        assert not hass.services.has_service(DOMAIN, SERVICE_GET_CITY)
        assert not hass.services.has_service(DOMAIN, SERVICE_QUERY_USER_CLOUD)
        assert not hass.services.has_service(DOMAIN, SERVICE_REFRESH_DEVICES)

    async def test_async_unload_entry_shuts_down_runtime_data_coordinator(
        self, hass
    ) -> None:
        """Coordinator runtime data should be shut down on successful unload."""
        await async_setup(hass, {})
        entry = MockConfigEntry(
            domain=DOMAIN,
            data={"phone": "13800000000"},
            options={CONF_DEBUG_MODE: True},
        )
        entry.add_to_hass(hass)

        coordinator = MagicMock()
        coordinator.async_shutdown = AsyncMock()
        entry.runtime_data = coordinator

        with patch.object(
            hass.config_entries,
            "async_unload_platforms",
            AsyncMock(return_value=True),
        ):
            assert await async_unload_entry(hass, entry) is True

        coordinator.async_shutdown.assert_awaited_once()
        assert getattr(entry, "runtime_data", None) is None

    async def test_async_unload_entry_logs_and_continues_on_shutdown_error(
        self,
        hass,
    ) -> None:
        """Unload should catch shutdown errors so unload can complete."""
        await async_setup(hass, {})
        entry = MockConfigEntry(
            domain=DOMAIN,
            data={"phone": "13800000000"},
            options={CONF_DEBUG_MODE: True},
        )
        entry.add_to_hass(hass)

        coordinator = MagicMock()
        coordinator.async_shutdown = AsyncMock(side_effect=RuntimeError("boom"))
        entry.runtime_data = coordinator

        with (
            patch.object(
                hass.config_entries,
                "async_unload_platforms",
                AsyncMock(return_value=True),
            ),
            patch("custom_components.lipro._LOGGER.warning") as mock_warning,
        ):
            assert await async_unload_entry(hass, entry) is True

        assert mock_warning.call_args.args[1:] == (
            "unload",
            "unload_shutdown_degraded",
            "log_and_continue",
            "RuntimeError",
        )
        assert getattr(entry, "runtime_data", None) is None

    async def test_async_unload_entry_removes_services_when_lock_unavailable(
        self,
        hass,
    ) -> None:
        """Unload should remove shared infra when lock store is unavailable."""
        await async_setup(hass, {})
        entry = MockConfigEntry(
            domain=DOMAIN,
            data={"phone": "13800000000"},
            options={CONF_DEBUG_MODE: True},
        )
        entry.add_to_hass(hass)

        hass.data[DOMAIN] = "not-a-dict"

        with (
            patch.object(
                hass.config_entries,
                "async_unload_platforms",
                AsyncMock(return_value=True),
            ),
            patch(
                "custom_components.lipro.has_other_runtime_entries", return_value=False
            ),
            patch("custom_components.lipro.remove_services") as mock_remove_services,
            patch(
                "custom_components.lipro.remove_device_registry_listener"
            ) as mock_remove_listener,
        ):
            assert await async_unload_entry(hass, entry) is True

        from custom_components.lipro.services.registrations import SERVICE_REGISTRATIONS

        mock_remove_services.assert_called_once_with(
            hass,
            domain=DOMAIN,
            registrations=SERVICE_REGISTRATIONS,
        )
        mock_remove_listener.assert_called_once_with(hass)

    async def test_async_reload_entry_forwards_to_hass(self, hass) -> None:
        """async_reload_entry should delegate to hass reload."""
        entry = MockConfigEntry(
            domain=DOMAIN,
            data={"phone": "13800000000"},
            options={CONF_DEBUG_MODE: True},
        )
        entry.add_to_hass(hass)

        mock_reload = AsyncMock()
        with patch.object(hass.config_entries, "async_reload", mock_reload):
            await async_reload_entry(hass, entry)

        mock_reload.assert_awaited_once_with(entry.entry_id)

    async def test_async_reload_entry_uses_named_not_ready_contract(self, hass) -> None:
        """Reload failures should preserve a named contract before re-raising."""
        entry = MockConfigEntry(
            domain=DOMAIN,
            data={"phone": "13800000000"},
            options={CONF_DEBUG_MODE: True},
        )
        entry.add_to_hass(hass)

        with (
            patch.object(
                hass.config_entries,
                "async_reload",
                AsyncMock(side_effect=ConfigEntryNotReady("retry reload")),
            ),
            patch("custom_components.lipro._LOGGER.debug") as mock_debug,
            pytest.raises(ConfigEntryNotReady),
        ):
            await async_reload_entry(hass, entry)

        assert mock_debug.call_args.args[1:] == (
            "reload",
            "reload_not_ready",
            "propagate",
            "ConfigEntryNotReady",
        )

    async def test_async_unload_entry_removes_services_when_only_non_runtime_entries_remain(
        self, hass
    ) -> None:
        """Services should be removed when no other runtime-loaded entry remains."""
        await async_setup(hass, {})
        active_entry = MockConfigEntry(
            domain=DOMAIN,
            data={"phone": "13800000000"},
            options={CONF_DEBUG_MODE: True},
        )
        active_entry.add_to_hass(hass)
        active_entry.runtime_data = MagicMock(async_shutdown=AsyncMock())

        # Simulate a configured but not loaded entry (no runtime_data).
        passive_entry = MockConfigEntry(
            domain=DOMAIN,
            data={"phone": "13900000000"},
            options={CONF_DEBUG_MODE: True},
        )
        passive_entry.add_to_hass(hass)

        with patch.object(
            hass.config_entries,
            "async_unload_platforms",
            AsyncMock(return_value=True),
        ):
            assert await async_unload_entry(hass, active_entry) is True

        assert not hass.services.has_service(DOMAIN, SERVICE_SEND_COMMAND)
        assert not hass.services.has_service(DOMAIN, SERVICE_GET_SCHEDULES)
        assert getattr(passive_entry, "runtime_data", None) is None

    async def test_async_unload_entry_does_not_shutdown_on_failed_unload(
        self, hass
    ) -> None:
        """Coordinator shutdown should not run when platform unload fails."""
        entry = MockConfigEntry(
            domain=DOMAIN,
            data={"phone": "13800000000"},
            options={CONF_DEBUG_MODE: True},
        )
        entry.add_to_hass(hass)

        coordinator = MagicMock()
        coordinator.async_shutdown = AsyncMock()
        entry.runtime_data = coordinator

        with patch.object(
            hass.config_entries,
            "async_unload_platforms",
            AsyncMock(return_value=False),
        ):
            assert await async_unload_entry(hass, entry) is False

        coordinator.async_shutdown.assert_not_awaited()
