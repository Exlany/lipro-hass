"""Lipro API package.

`LiproRestFacade` is the explicit REST child facade under the unified
`LiproProtocolFacade` protocol root. Package exports expose only the
formal REST surface, not transport/auth internals.
"""

from __future__ import annotations

from .client import LiproRestFacade
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
    "LiproConnectionError",
    "LiproRateLimitError",
    "LiproRefreshTokenExpiredError",
    "LiproRestFacade",
    "OtaInfoRow",
    "ScheduleApiResponse",
    "ScheduleTimingRow",
]
