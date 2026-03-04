"""Data update coordinator for Lipro integration."""

from __future__ import annotations

from datetime import timedelta
import logging
from typing import TYPE_CHECKING

from ...const import DEFAULT_SCAN_INTERVAL
from ..api import LiproClient
from .shutdown import _CoordinatorShutdownMixin

if TYPE_CHECKING:
    from homeassistant.config_entries import ConfigEntry
    from homeassistant.core import HomeAssistant

    from ..auth import LiproAuthManager

_LOGGER = logging.getLogger(__name__)


class LiproDataUpdateCoordinator(_CoordinatorShutdownMixin):
    """Coordinator to manage fetching Lipro data."""

    def __init__(
        self,
        hass: HomeAssistant,
        client: LiproClient,
        auth_manager: LiproAuthManager,
        config_entry: ConfigEntry,
        update_interval: int = DEFAULT_SCAN_INTERVAL,
    ) -> None:
        """Initialize the coordinator."""
        super().__init__(
            hass,
            _LOGGER,
            name="Lipro",
            update_interval=timedelta(seconds=update_interval),
            config_entry=config_entry,
            always_update=True,
        )
        self.client = client
        self.auth_manager = auth_manager
        self._init_runtime_state()
        self._load_options()
        self._setup_anonymous_share()


__all__ = ["LiproDataUpdateCoordinator"]
