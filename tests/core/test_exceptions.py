"""Tests for the shared Lipro exception hierarchy."""

from __future__ import annotations

from custom_components.lipro.core.api.errors import LiproAuthError, LiproConnectionError
from custom_components.lipro.core.exceptions import (
    ApiAuthError,
    ApiNetworkError,
    LiproApiError,
    LiproError,
    LiproMqttError,
    MqttConnectionError,
    MqttPublishError,
    MqttSubscriptionError,
)


def test_exception_hierarchy_is_layered_consistently() -> None:
    assert issubclass(LiproApiError, LiproError)
    assert issubclass(ApiAuthError, LiproApiError)
    assert issubclass(ApiNetworkError, LiproApiError)
    assert issubclass(LiproMqttError, LiproError)
    assert issubclass(MqttConnectionError, LiproMqttError)
    assert issubclass(MqttSubscriptionError, LiproMqttError)
    assert issubclass(MqttPublishError, LiproMqttError)


def test_api_error_keeps_code_payload() -> None:
    err = LiproApiError("boom", code=503)

    assert str(err) == "boom"
    assert err.code == 503


def test_public_api_errors_extend_shared_base_types() -> None:
    assert issubclass(LiproAuthError, ApiAuthError)
    assert issubclass(LiproConnectionError, ApiNetworkError)
