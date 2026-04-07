"""Stable import home for the formal REST child façade."""

from __future__ import annotations

import logging

from .rest_facade import LiproRestFacade

_LOGGER = logging.getLogger("custom_components.lipro.core.api")

__all__ = ["_LOGGER", "LiproRestFacade"]
