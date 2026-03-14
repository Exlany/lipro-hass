"""Lipro API package.

`LiproRestFacade` is the explicit REST child facade under the unified
`LiproProtocolFacade` protocol root. Package exports now expose only the
formal REST surface, not legacy compat constructors.
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
