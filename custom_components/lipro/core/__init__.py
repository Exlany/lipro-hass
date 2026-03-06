"""Core module for Lipro integration."""

from .anonymous_share import AnonymousShareManager, get_anonymous_share_manager
from .api import (
    LiproApiError,
    LiproAuthError,
    LiproClient,
    LiproConnectionError,
    LiproRateLimitError,
    LiproRefreshTokenExpiredError,
)
from .auth import LiproAuthManager
from .coordinator import LiproDataUpdateCoordinator
from .device import LiproDevice, parse_properties_list

__all__ = [
    "AnonymousShareManager",
    "LiproApiError",
    "LiproAuthError",
    "LiproAuthManager",
    "LiproClient",
    "LiproConnectionError",
    "LiproDataUpdateCoordinator",
    "LiproDevice",
    "LiproRateLimitError",
    "LiproRefreshTokenExpiredError",
    "get_anonymous_share_manager",
    "parse_properties_list",
]
