"""Endpoint collaborators for the formal REST facade."""

from __future__ import annotations

from .auth import AuthEndpoints
from .commands import CommandEndpoints
from .devices import DeviceEndpoints
from .misc import MiscEndpoints
from .schedule import ScheduleEndpoints
from .status import StatusEndpoints

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
]
