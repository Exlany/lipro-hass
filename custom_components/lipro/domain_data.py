"""Helpers for accessing Lipro domain data in Home Assistant runtime state."""

from __future__ import annotations

from typing import Any

from homeassistant.core import HomeAssistant

from .const.base import DOMAIN

type DomainData = dict[str, Any]


def get_domain_data(hass: HomeAssistant) -> DomainData | None:
    """Return existing domain data when it is a dictionary."""
    domain_data = hass.data.get(DOMAIN)
    return domain_data if isinstance(domain_data, dict) else None


def ensure_domain_data(hass: HomeAssistant) -> DomainData | None:
    """Return domain data, creating an empty dictionary when missing."""
    domain_data = hass.data.setdefault(DOMAIN, {})
    return domain_data if isinstance(domain_data, dict) else None
