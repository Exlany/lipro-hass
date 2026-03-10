"""Native CoordinatorV2 runtime for the Lipro integration."""

from __future__ import annotations

from datetime import timedelta
import logging
from typing import TYPE_CHECKING

from ...const.config import DEFAULT_SCAN_INTERVAL
from ..api import LiproClient
from .services import (
    CoordinatorCommandService,
    CoordinatorDeviceRefreshService,
    CoordinatorMqttService,
    CoordinatorStateService,
)
from .shutdown import _CoordinatorShutdownMixin

if TYPE_CHECKING:
    from homeassistant.config_entries import ConfigEntry
    from homeassistant.core import HomeAssistant

    from ..auth import LiproAuthManager

_LOGGER = logging.getLogger(__name__)


class CoordinatorV2(_CoordinatorShutdownMixin):
    """Coordinator runtime built directly on the final service boundaries."""

    def __init__(
        self,
        hass: HomeAssistant,
        client: LiproClient,
        auth_manager: LiproAuthManager,
        config_entry: ConfigEntry,
        update_interval: int = DEFAULT_SCAN_INTERVAL,
    ) -> None:
        """Initialize the native CoordinatorV2 runtime."""
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
        self.command_service = CoordinatorCommandService(self)
        self.device_refresh_service = CoordinatorDeviceRefreshService(self)
        self.mqtt_service = CoordinatorMqttService(self)
        self.state_service = CoordinatorStateService(self)


LiproDataUpdateCoordinator = CoordinatorV2

__all__ = ["CoordinatorV2", "LiproDataUpdateCoordinator"]
