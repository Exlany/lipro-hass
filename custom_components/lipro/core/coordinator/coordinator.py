"""Native coordinator runtime for the Lipro integration."""

from __future__ import annotations

from datetime import timedelta
import logging
from typing import TYPE_CHECKING

from ...const.config import DEFAULT_SCAN_INTERVAL
from ..api import LiproClient
from .auth_issues import CoordinatorAuthIssuesRuntime
from .command_confirm import CoordinatorCommandConfirmationRuntime
from .command_send import CoordinatorCommandRuntime
from .device_refresh import CoordinatorDeviceRefreshRuntime
from .mqtt.lifecycle import CoordinatorMqttLifecycleRuntime
from .mqtt.messages import CoordinatorMqttMessageRuntime
from .properties import CoordinatorPropertiesRuntime
from .services import (
    CoordinatorCommandService,
    CoordinatorDeviceRefreshService,
    CoordinatorMqttService,
    CoordinatorStateService,
)
from .shutdown import CoordinatorShutdownRuntime
from .state import CoordinatorStateRuntime
from .status_polling import CoordinatorStatusRuntime
from .tuning import CoordinatorAdaptiveTuningRuntime

if TYPE_CHECKING:
    from homeassistant.config_entries import ConfigEntry
    from homeassistant.core import HomeAssistant

    from ..auth import LiproAuthManager

_LOGGER = logging.getLogger(__name__)


class Coordinator(
    CoordinatorAdaptiveTuningRuntime,
    CoordinatorCommandConfirmationRuntime,
    CoordinatorCommandRuntime,
    CoordinatorMqttLifecycleRuntime,
    CoordinatorMqttMessageRuntime,
    CoordinatorDeviceRefreshRuntime,
    CoordinatorStateRuntime,
    CoordinatorPropertiesRuntime,
    CoordinatorAuthIssuesRuntime,
    CoordinatorStatusRuntime,
    CoordinatorShutdownRuntime,
):
    """Coordinator runtime built directly on the final service boundaries."""

    def __init__(
        self,
        hass: HomeAssistant,
        client: LiproClient,
        auth_manager: LiproAuthManager,
        config_entry: ConfigEntry,
        update_interval: int = DEFAULT_SCAN_INTERVAL,
    ) -> None:
        """Initialize the native coordinator runtime."""
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


LiproDataUpdateCoordinator = Coordinator

__all__ = ["Coordinator", "LiproDataUpdateCoordinator"]
