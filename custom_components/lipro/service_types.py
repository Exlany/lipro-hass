"""Shared service-facing types reused across root/runtime and service layers."""

from __future__ import annotations

from typing import TypedDict


class ServiceProperty(TypedDict):
    """One key/value property item accepted by send_command."""

    key: str
    value: str


type ServicePropertyList = list[ServiceProperty]


class ServicePropertySummary(TypedDict):
    """Log-safe summary of the requested command properties."""

    count: int
    keys: list[str]


class CommandFailureSummary(TypedDict, total=False):
    """Normalized command failure details exposed to control/service callers."""

    reason: str
    code: int | str
    route: str
    device_id: str
