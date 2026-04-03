"""Tests for service registry helpers."""

from __future__ import annotations

from unittest.mock import AsyncMock, MagicMock

import pytest

from custom_components.lipro.const.base import DOMAIN, IOT_DEVICE_ID_PREFIX
from custom_components.lipro.control import service_router, service_router_support
from custom_components.lipro.control.service_registry import SERVICE_REGISTRATIONS
from custom_components.lipro.services.contracts import ATTR_DEVICE_ID
from custom_components.lipro.services.registry import (
    ServiceRegistration,
    register_service,
)
from homeassistant.core import SupportsResponse


@pytest.mark.asyncio
async def test_register_service_executes_handler() -> None:
    hass = MagicMock()
    hass.services = MagicMock()
    hass.services.async_register = MagicMock()

    handler = AsyncMock(return_value={"ok": True})
    registration = ServiceRegistration(
        name="test_service",
        handler=handler,
        schema=None,
        supports_response=SupportsResponse.OPTIONAL,
    )

    register_service(hass, domain="lipro", registration=registration)

    assert (
        hass.services.async_register.call_args.kwargs["supports_response"]
        is SupportsResponse.OPTIONAL
    )
    handle = hass.services.async_register.call_args.args[2]
    call = MagicMock()

    result = await handle(call)

    assert result == {"ok": True}
    handler.assert_awaited_once_with(hass, call)


def test_service_registrations_bind_formal_router_handlers() -> None:
    """All service registrations must bind to the formal control-plane router."""
    assert SERVICE_REGISTRATIONS
    assert all(
        registration.handler.__module__ == service_router.__name__
        for registration in SERVICE_REGISTRATIONS
    )


def test_service_router_device_getter_stays_control_owned() -> None:
    """The sanctioned device getter seam must stay in the control plane."""
    getter = service_router_support.build_device_and_coordinator_getter(
        domain=DOMAIN,
        serial_pattern=service_router_support.build_serial_pattern(
            IOT_DEVICE_ID_PREFIX
        ),
        attr_device_id=ATTR_DEVICE_ID,
    )

    assert getter.func.__module__ == service_router_support.__name__
    assert "_get_device_and_coordinator" not in service_router.__all__
    assert "get_anonymous_share_manager" not in service_router.__all__
