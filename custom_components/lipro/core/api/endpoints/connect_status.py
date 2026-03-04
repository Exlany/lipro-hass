"""Small shared helpers for LiproClient endpoints."""

from __future__ import annotations

import logging
from typing import Any

from ...utils.coerce import coerce_boollike

# Use the same logger instance as custom_components.lipro.core.api.client._LOGGER
# so tests patching client._LOGGER.* still intercept logs here.
_LOGGER = logging.getLogger("custom_components.lipro.core.api.client")


def coerce_connect_status(value: Any) -> bool:
    """Normalize backend connection-state variants to boolean."""
    return coerce_boollike(value, logger=_LOGGER, context="connect-status")


__all__ = ["coerce_connect_status"]
