"""Lipro API package.

`LiproRestFacade` is the explicit REST child facade under the unified
`LiproProtocolFacade` protocol root. `LiproClient` remains a transitional
compatibility shell for legacy constructors and wrapper methods.
"""

from __future__ import annotations

from .client import LiproClient, LiproRestFacade
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
    "LiproRestFacade",
    "OtaInfoRow",
    "ScheduleApiResponse",
    "ScheduleTimingRow",
]
