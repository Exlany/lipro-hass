"""Coordinator authentication service.

Formal runtime-auth surface used by service execution and runtime callbacks.
"""

from __future__ import annotations

from dataclasses import dataclass
import logging
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from homeassistant.config_entries import ConfigEntry
    from homeassistant.core import HomeAssistant

    from ...auth import LiproAuthManager

_LOGGER = logging.getLogger(__name__)


@dataclass(slots=True)
class CoordinatorAuthService:
    """Expose coordinator authentication and reauth through a formal service."""

    hass: HomeAssistant
    auth_manager: LiproAuthManager
    config_entry: ConfigEntry

    async def async_ensure_authenticated(self) -> None:
        """Ensure runtime authentication is valid before service execution."""
        await self.auth_manager.async_ensure_authenticated()

    async def async_trigger_reauth(self, reason: str) -> None:
        """Start the Home Assistant reauth flow for one stable failure reason."""
        _LOGGER.warning("Re-authentication required: %s", reason)
        self.config_entry.async_start_reauth(self.hass)
