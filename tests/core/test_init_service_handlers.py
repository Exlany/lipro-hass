"""Shared helpers for init service-handler topical suites."""

from __future__ import annotations

from unittest.mock import AsyncMock

from custom_components.lipro.core.device import LiproDevice
from tests.conftest import _CoordinatorDouble


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
    def _create_runtime_coordinator() -> _CoordinatorDouble:
        """Create one explicit runtime coordinator test double."""
        return _CoordinatorDouble()

    @classmethod
    def _attach_auth_service(
        cls,
        coordinator: _CoordinatorDouble | object | None = None,
    ) -> _CoordinatorDouble:
        """Attach the formal async auth surface expected by service handlers."""
        runtime = (
            coordinator
            if isinstance(coordinator, _CoordinatorDouble)
            else cls._create_runtime_coordinator()
        )
        runtime.auth_service.async_ensure_authenticated = AsyncMock()
        runtime.auth_service.async_trigger_reauth = AsyncMock()
        return runtime
