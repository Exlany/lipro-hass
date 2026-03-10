"""Lipro API client package."""

from __future__ import annotations

from .client import LiproClient
from .errors import (
    LiproApiError,
    LiproAuthError,
    LiproConnectionError,
    LiproRateLimitError,
    LiproRefreshTokenExpiredError,
)
from .types import (
    CommandResultApiResponse,
    DeviceApiResponse,
    DevicePropertyRow,
    DiagnosticsApiResponse,
    OtaInfoRow,
    ScheduleApiResponse,
    ScheduleTimingRow,
)

__all__ = [
    "CommandResultApiResponse",
    "DeviceApiResponse",
    "DevicePropertyRow",
    "DiagnosticsApiResponse",
    "LiproApiError",
    "LiproAuthError",
    "LiproClient",
    "LiproConnectionError",
    "LiproRateLimitError",
    "LiproRefreshTokenExpiredError",
    "OtaInfoRow",
    "ScheduleApiResponse",
    "ScheduleTimingRow",
]
