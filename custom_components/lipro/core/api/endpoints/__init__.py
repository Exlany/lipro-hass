"""Endpoint methods for LiproClient.

This module is intentionally thin: the endpoint surface is split into focused
mixins so each concern remains small and testable.
"""

from __future__ import annotations

from .auth import _ClientAuthEndpointsMixin
from .commands import _ClientCommandEndpointsMixin
from .devices import _ClientDeviceEndpointsMixin
from .misc import _ClientMiscEndpointsMixin
from .schedule import _ClientScheduleEndpointsMixin
from .status import _ClientStatusEndpointsMixin


class _ClientEndpointsMixin(
    _ClientAuthEndpointsMixin,
    _ClientDeviceEndpointsMixin,
    _ClientStatusEndpointsMixin,
    _ClientCommandEndpointsMixin,
    _ClientMiscEndpointsMixin,
    _ClientScheduleEndpointsMixin,
):
    """Aggregate mixin for all Lipro API endpoints."""


__all__ = ["_ClientEndpointsMixin"]
