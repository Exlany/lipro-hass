"""Command builder for constructing command payloads and traces."""

from __future__ import annotations

from time import monotonic
from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from ....device import LiproDevice


class CommandBuilder:
    """Build command traces and prepare command metadata."""

    def __init__(self, *, debug_mode: bool = False) -> None:
        """Initialize command builder.

        Args:
            debug_mode: Whether to enable detailed trace recording
        """
        self._debug_mode = debug_mode

    def build_trace(
        self,
        *,
        device: LiproDevice,
        command: str,
        properties: list[dict[str, str]] | None,
    ) -> dict[str, Any]:
        """Build initial command trace with device and timing metadata.

        Args:
            device: Target device
            command: Command name
            properties: Optional command properties

        Returns:
            Trace dictionary with initial metadata
        """
        return {
            "device_serial": device.serial,
            "device_name": device.name,
            "device_type": device.device_type,
            "is_group": device.is_group,
            "command": command,
            "properties": properties,
            "start_time": monotonic(),
            "success": False,
        }

    def should_skip_immediate_refresh(
        self,
        *,
        command: str,
        properties: list[dict[str, str]] | None,
    ) -> bool:
        """Determine if immediate post-command refresh should be skipped.

        Slider-like properties (brightness, temperature, fan gear, position)
        generate rapid updates. Skip immediate refresh to reduce API load.

        Args:
            command: Command name
            properties: Command properties

        Returns:
            True if immediate refresh should be skipped
        """
        if command.upper() != "CHANGE_STATE" or not properties:
            return False

        slider_properties = frozenset(
            {"brightness", "colorTemperature", "fanGear", "position"}
        )

        for prop in properties:
            key = prop.get("key")
            if isinstance(key, str) and key in slider_properties:
                return True

        return False


__all__ = ["CommandBuilder"]
