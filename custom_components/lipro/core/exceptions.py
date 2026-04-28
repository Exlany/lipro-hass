"""Shared exception hierarchy for the Lipro integration."""

from __future__ import annotations


class LiproError(Exception):
    """Root exception for Lipro integration failures."""


class LiproMqttError(LiproError):
    """Base exception for MQTT lifecycle failures."""


class MqttConnectionError(LiproMqttError):
    """MQTT connection or reconnect failure."""


class MqttSubscriptionError(LiproMqttError):
    """MQTT subscribe or unsubscribe failure."""


class MqttPublishError(LiproMqttError):
    """MQTT publish failure."""


class LiproApiError(LiproError):
    """Base exception for Lipro API errors."""

    def __init__(self, message: str, code: int | str | None = None) -> None:
        """Store the original Lipro API error code alongside the message."""
        super().__init__(message)
        self.code = code


class ApiAuthError(LiproApiError):
    """Authentication error from the Lipro API."""


class ApiNetworkError(LiproApiError):
    """Connectivity or transport failure from the Lipro API."""


__all__ = [
    "ApiAuthError",
    "ApiNetworkError",
    "LiproApiError",
    "LiproError",
    "LiproMqttError",
    "MqttConnectionError",
    "MqttPublishError",
    "MqttSubscriptionError",
]
