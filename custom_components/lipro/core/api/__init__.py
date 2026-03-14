"""Lipro API package.

`LiproRestFacade` is the explicit REST child facade under the unified
`LiproProtocolFacade` protocol root. `LiproClient` remains an explicit
transitional compatibility shell for legacy constructors and wrapper methods.
"""

from __future__ import annotations

from .client import LiproClient as _LiproClientCompat, LiproRestFacade
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

LiproClient = _LiproClientCompat

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
    "LiproRestFacade",
    "OtaInfoRow",
    "ScheduleApiResponse",
    "ScheduleTimingRow",
]
