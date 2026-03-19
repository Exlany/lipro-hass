"""Small shared helpers for REST-facade status endpoints."""

from __future__ import annotations

import logging
from typing import Any

from ...utils.coerce import coerce_boollike

_LOGGER = logging.getLogger("custom_components.lipro.core.api")


def coerce_connect_status(value: Any) -> bool:
    """Normalize backend connection-state variants to boolean."""
    return coerce_boollike(value, logger=_LOGGER, context="connect-status")


__all__ = ["coerce_connect_status"]
