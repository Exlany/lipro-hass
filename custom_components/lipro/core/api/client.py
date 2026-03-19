"""Compatibility import shim for the formal REST facade."""

from __future__ import annotations

import logging

from .rest_facade import LiproRestFacade

_LOGGER = logging.getLogger("custom_components.lipro.core.api.client")

__all__ = ["_LOGGER", "LiproRestFacade"]
