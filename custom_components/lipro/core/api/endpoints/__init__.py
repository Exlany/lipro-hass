"""Endpoint collaborators for the formal REST facade."""

from __future__ import annotations

from .auth import AuthEndpoints, _ClientAuthEndpointsMixin
from .commands import CommandEndpoints, _ClientCommandEndpointsMixin
from .devices import DeviceEndpoints, _ClientDeviceEndpointsMixin
from .misc import MiscEndpoints, _ClientMiscEndpointsMixin
from .schedule import ScheduleEndpoints, _ClientScheduleEndpointsMixin
from .status import StatusEndpoints, _ClientStatusEndpointsMixin


class _ClientEndpointsMixin(
    _ClientAuthEndpointsMixin,
    _ClientDeviceEndpointsMixin,
    _ClientStatusEndpointsMixin,
    _ClientCommandEndpointsMixin,
    _ClientMiscEndpointsMixin,
    _ClientScheduleEndpointsMixin,
):
    """Legacy aggregate mixin kept only for narrow compatibility tests."""


ENDPOINT_COLLABORATOR_TYPES = (
    AuthEndpoints,
    DeviceEndpoints,
    StatusEndpoints,
    CommandEndpoints,
    MiscEndpoints,
    ScheduleEndpoints,
)


__all__ = [
    "ENDPOINT_COLLABORATOR_TYPES",
    "AuthEndpoints",
    "CommandEndpoints",
    "DeviceEndpoints",
    "MiscEndpoints",
    "ScheduleEndpoints",
    "StatusEndpoints",
    "_ClientEndpointsMixin",
]
