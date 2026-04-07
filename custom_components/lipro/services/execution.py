"""Shared service execution facade for coordinator-authenticated calls."""

from __future__ import annotations

from collections.abc import Awaitable, Callable, Mapping
from typing import NoReturn, Protocol, TypeVar

from ..core import LiproApiError, LiproAuthError, LiproRefreshTokenExpiredError
from ..core.utils.log_safety import safe_error_placeholder
from ..runtime_types import (
    LiproCoordinator,
    RuntimeAuthServiceLike,
    RuntimeReauthReason,
)

_ResultT = TypeVar("_ResultT")

type CoordinatorAuthSurface = RuntimeAuthServiceLike
type AuthenticatedCoordinator = LiproCoordinator


class ServiceErrorRaiser(Protocol):
    """Callable that raises translated Home Assistant service errors."""

    def __call__(
        self,
        translation_key: str,
        *,
        err: Exception | None = None,
        translation_placeholders: Mapping[str, str] | None = None,
    ) -> NoReturn:
        """Raise a translated Home Assistant service error."""


class LiproApiErrorHandler(Protocol):
    """Translate a non-auth Lipro API error into a service exception."""

    def __call__(self, err: LiproApiError) -> NoReturn:
        """Raise a service-layer error for one API failure."""


async def _async_ensure_authenticated(
    coordinator: AuthenticatedCoordinator,
) -> None:
    """Run formal coordinator auth validation before a service call."""
    await coordinator.auth_service.async_ensure_authenticated()


async def _async_trigger_reauth(
    coordinator: AuthenticatedCoordinator,
    reason: RuntimeReauthReason,
) -> None:
    """Trigger formal coordinator reauth flow for one auth failure."""
    await coordinator.auth_service.async_trigger_reauth(reason)


async def async_capture_coordinator_call(
    coordinator: AuthenticatedCoordinator,
    *,
    call: Callable[[], Awaitable[_ResultT]],
) -> tuple[bool, _ResultT | None, LiproApiError | None]:
    """Execute one coordinator call and capture auth/API errors after reauth handling."""
    try:
        await _async_ensure_authenticated(coordinator)
        return True, await call(), None
    except LiproRefreshTokenExpiredError as err:
        await _async_trigger_reauth(coordinator, RuntimeReauthReason.AUTH_EXPIRED)
        return False, None, err
    except LiproAuthError as err:
        await _async_trigger_reauth(coordinator, RuntimeReauthReason.AUTH_ERROR)
        return False, None, err
    except LiproApiError as err:
        return False, None, err


async def async_execute_coordinator_call(
    coordinator: AuthenticatedCoordinator,
    *,
    call: Callable[[], Awaitable[_ResultT]],
    raise_service_error: ServiceErrorRaiser,
    handle_api_error: LiproApiErrorHandler | None = None,
) -> _ResultT:
    """Execute one service call through the shared auth and error chain."""
    try:
        await _async_ensure_authenticated(coordinator)
        return await call()
    except LiproRefreshTokenExpiredError as err:
        await _async_trigger_reauth(coordinator, RuntimeReauthReason.AUTH_EXPIRED)
        raise_service_error("auth_expired", err=err)
    except LiproAuthError as err:
        safe_error = safe_error_placeholder(err)
        await _async_trigger_reauth(coordinator, RuntimeReauthReason.AUTH_ERROR)
        raise_service_error(
            "auth_error",
            err=err,
            translation_placeholders={"error": safe_error},
        )
    except LiproApiError as err:
        if handle_api_error is not None:
            handle_api_error(err)
        raise


__all__ = [
    "AuthenticatedCoordinator",
    "CoordinatorAuthSurface",
    "LiproApiErrorHandler",
    "ServiceErrorRaiser",
    "async_capture_coordinator_call",
    "async_execute_coordinator_call",
]
