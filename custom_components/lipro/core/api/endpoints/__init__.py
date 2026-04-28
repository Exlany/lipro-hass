"""Endpoint collaborators for the formal REST facade."""

from __future__ import annotations

from .auth import AuthEndpoints
from .commands import CommandEndpoints
from .devices import DeviceEndpoints
from .misc import MiscEndpoints
from .schedule import ScheduleEndpoints
from .status import StatusEndpoints

__all__ = [
    "AuthEndpoints",
    "CommandEndpoints",
    "DeviceEndpoints",
    "MiscEndpoints",
    "ScheduleEndpoints",
    "StatusEndpoints",
]
