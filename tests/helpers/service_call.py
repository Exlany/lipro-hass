"""ServiceCall helpers for Lipro service handler tests."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from custom_components.lipro.const.base import DOMAIN
from homeassistant.core import HomeAssistant, ServiceCall


@dataclass(slots=True)
class _ServiceTarget:
    entity_id: list[str]


class _ServiceCallWithTarget(ServiceCall):
    __slots__ = ("target",)
    target: _ServiceTarget | None


def service_call(
    hass: HomeAssistant,
    data: dict[str, Any] | None = None,
    *,
    target_entity_ids: list[str] | None = None,
    domain: str = DOMAIN,
    service: str = "test",
) -> ServiceCall:
    """Build a Home Assistant ServiceCall for direct handler invocation."""
    call = _ServiceCallWithTarget(hass, domain, service, data or {})
    call.target = None
    if target_entity_ids is not None:
        call.target = _ServiceTarget(entity_id=target_entity_ids)
    return call
