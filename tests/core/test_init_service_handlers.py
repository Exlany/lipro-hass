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
    def _materialize_runtime_lookup_surface(coordinator: object) -> object:
        """Bind explicit runtime lookup members so runtime-access sees one honest coordinator."""
        members = vars(coordinator)
        if "devices" not in members:
            coordinator.devices = {}
        if "get_device" not in members:
            coordinator.get_device = MagicMock(return_value=None)
        if "get_device_by_id" not in members:
            coordinator.get_device_by_id = MagicMock(return_value=None)
        return coordinator

    @classmethod
    def _create_runtime_coordinator(cls) -> object:
        """Create one explicit runtime coordinator test double."""
        return cls._materialize_runtime_lookup_surface(MagicMock())

    @classmethod
    def _attach_auth_service(cls, coordinator: object) -> object:
        """Attach the formal async auth and protocol surfaces expected by services."""
        coordinator = cls._materialize_runtime_lookup_surface(coordinator)
        coordinator.auth_service = MagicMock(
            async_ensure_authenticated=AsyncMock(),
            async_trigger_reauth=AsyncMock(),
        )
        coordinator.protocol_service = MagicMock()
        return coordinator
