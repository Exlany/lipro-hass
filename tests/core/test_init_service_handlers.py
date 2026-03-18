"""Shared helpers for init service-handler topical suites."""

from __future__ import annotations

from unittest.mock import AsyncMock, MagicMock

from custom_components.lipro.core.device import LiproDevice


class _InitServiceHandlerBase:
    """Shared helpers for init service-handler topical suites."""

    @staticmethod
    def _create_device(serial: str = "03ab5ccd7c111111") -> LiproDevice:
        """Create a minimal LiproDevice for runtime tests."""
        return LiproDevice(
            device_number=1,
            serial=serial,
            name="Test Device",
            device_type=1,
            iot_name="lipro_led",
            physical_model="light",
        )

    @staticmethod
    def _attach_auth_service(coordinator: MagicMock) -> MagicMock:
        """Attach the formal async auth and protocol surfaces expected by services."""
        coordinator.auth_service = MagicMock(
            async_ensure_authenticated=AsyncMock(),
            async_trigger_reauth=AsyncMock(),
        )
        coordinator.protocol_service = MagicMock()
        return coordinator
