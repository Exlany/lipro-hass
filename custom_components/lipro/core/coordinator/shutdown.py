"""Coordinator shutdown and background-task lifecycle management."""

from __future__ import annotations

import asyncio
from collections.abc import Coroutine
import logging
from typing import Any

from homeassistant.helpers.aiohttp_client import async_get_clientsession

from .status_polling import _CoordinatorStatusPollingMixin

_LOGGER = logging.getLogger(__name__)


class _CoordinatorShutdownMixin(_CoordinatorStatusPollingMixin):
    """Mixin: async_shutdown + background task tracking."""

    async def async_shutdown(self) -> None:
        """Shutdown coordinator and release all resources."""
        await super().async_shutdown()

        if self._mqtt_listener_update_handle is not None:
            self._mqtt_listener_update_handle.cancel()
            self._mqtt_listener_update_handle = None

        if self._entry_reload_handle is not None:
            self._entry_reload_handle.cancel()
            self._entry_reload_handle = None
            self._entry_reload_reasons.clear()

        delayed_tasks = list(self._post_command_refresh_tasks.values())
        self._post_command_refresh_tasks.clear()
        for task in delayed_tasks:
            if not task.done():
                task.cancel()

        await self._async_cancel_background_tasks()

        try:
            share_manager = self._get_anonymous_share_manager()
            if share_manager.is_enabled:
                session = async_get_clientsession(self.hass)
                await share_manager.submit_report(session)
        except asyncio.CancelledError:
            raise
        except Exception as err:  # noqa: BLE001
            _LOGGER.warning(
                "Failed to submit anonymous share report on shutdown (%s)",
                type(err).__name__,
            )

        try:
            await self.async_stop_mqtt()
        except asyncio.CancelledError:
            raise
        except Exception as err:  # noqa: BLE001
            _LOGGER.warning(
                "Failed to stop MQTT client on shutdown (%s)",
                type(err).__name__,
            )

        try:
            await self.client.close()
        except asyncio.CancelledError:
            raise
        except Exception as err:  # noqa: BLE001
            _LOGGER.warning(
                "Failed to close API client on shutdown (%s)",
                type(err).__name__,
            )

        self._reset_runtime_state()

        _LOGGER.debug("Coordinator shutdown complete")

    def _track_background_task(
        self, coro: Coroutine[Any, Any, Any]
    ) -> asyncio.Task[Any]:
        """Create and track a background task for centralized shutdown cleanup."""
        return self._background_task_manager.create(
            coro,
            create_task=self.hass.async_create_task,
        )

    async def _async_cancel_background_tasks(self) -> None:
        """Cancel and await tracked background tasks."""
        await self._background_task_manager.cancel_all()


__all__ = ["_CoordinatorShutdownMixin"]
