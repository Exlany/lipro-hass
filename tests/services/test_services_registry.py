"""Tests for service registry helpers."""

from __future__ import annotations

from unittest.mock import AsyncMock, MagicMock

import pytest

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
