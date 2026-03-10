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
from .coordinator import Coordinator
from .device import LiproDevice, parse_properties_list
from .exceptions import (
    ApiAuthError,
    ApiNetworkError,
    LiproError,
    LiproMqttError,
    MqttConnectionError,
    MqttPublishError,
    MqttSubscriptionError,
)

__all__ = [
    "AnonymousShareManager",
    "ApiAuthError",
    "ApiNetworkError",
    "Coordinator",
    "LiproApiError",
    "LiproAuthError",
    "LiproAuthManager",
    "LiproClient",
    "LiproConnectionError",
    "LiproDevice",
    "LiproError",
    "LiproMqttError",
    "LiproRateLimitError",
    "LiproRefreshTokenExpiredError",
    "MqttConnectionError",
    "MqttPublishError",
    "MqttSubscriptionError",
    "get_anonymous_share_manager",
    "parse_properties_list",
]
