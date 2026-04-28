"""Shared service-registration primitives for Lipro integration."""

from __future__ import annotations

from collections.abc import Awaitable, Callable, Iterable, Mapping
from dataclasses import dataclass
from typing import Any, cast

import voluptuous as vol

from homeassistant.core import HomeAssistant, ServiceCall, SupportsResponse

ServiceHandler = Callable[[HomeAssistant, ServiceCall], Awaitable[Mapping[str, object]]]


@dataclass(frozen=True, slots=True)
class ServiceRegistration:
    """Declarative description of one Home Assistant service."""

    name: str
    handler: ServiceHandler
    schema: vol.Schema | None
    supports_response: SupportsResponse


def register_service(
    hass: HomeAssistant,
    *,
    domain: str,
    registration: ServiceRegistration,
) -> None:
    """Register one Lipro service with optional schema and response mode."""
    register_kwargs: dict[str, Any] = {
        "supports_response": registration.supports_response
    }
    if registration.schema is not None:
        register_kwargs["schema"] = registration.schema

    async def _handle(call: ServiceCall) -> dict[str, object]:
        return dict(await registration.handler(hass, call))

    hass.services.async_register(
        domain,
        registration.name,
        cast(Any, _handle),
        **register_kwargs,
    )


def remove_services(
    hass: HomeAssistant,
    *,
    domain: str,
    registrations: Iterable[ServiceRegistration],
) -> None:
    """Remove all services from the given registry."""
    for registration in registrations:
        hass.services.async_remove(domain, registration.name)


async def async_setup_services(
    hass: HomeAssistant,
    *,
    domain: str,
    registrations: Iterable[ServiceRegistration],
) -> None:
    """Register all services that are not already present."""
    for registration in registrations:
        if hass.services.has_service(domain, registration.name):
            continue
        register_service(hass, domain=domain, registration=registration)
