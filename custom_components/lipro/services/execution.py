"""Shared service execution facade for coordinator-authenticated calls."""

from __future__ import annotations

from collections.abc import Awaitable, Callable, Mapping
from inspect import isawaitable
from typing import NoReturn, Protocol, TypeVar, cast

from ..core import LiproApiError, LiproAuthError, LiproRefreshTokenExpiredError
from ..core.utils.log_safety import safe_error_placeholder

_ResultT = TypeVar("_ResultT")


class AuthenticatedCoordinator(Protocol):
    """Coordinator contract required by authenticated service calls."""

    def _async_ensure_authenticated(self) -> Awaitable[None]:
        """Validate the coordinator auth state before a service call."""

    def _trigger_reauth(self, reason: str) -> Awaitable[None]:
        """Start the Home Assistant reauth flow for the config entry."""


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


async def _async_await_if_needed(result: object) -> None:
    """Await async results while tolerating lightweight test doubles."""
    if isawaitable(result):
        await cast(Awaitable[object], result)


async def _async_ensure_authenticated(
    coordinator: AuthenticatedCoordinator,
) -> None:
    """Run coordinator authentication when available."""
    ensure_authenticated = getattr(coordinator, "_async_ensure_authenticated", None)
    if ensure_authenticated is None:
        return
    await _async_await_if_needed(ensure_authenticated())


async def _async_trigger_reauth(
    coordinator: AuthenticatedCoordinator,
    reason: str,
) -> None:
    """Trigger coordinator reauth when available."""
    trigger_reauth = getattr(coordinator, "_trigger_reauth", None)
    if trigger_reauth is None:
        return
    await _async_await_if_needed(trigger_reauth(reason))


async def async_execute_coordinator_call(
    coordinator: AuthenticatedCoordinator,
    *,
    call: Callable[[], Awaitable[_ResultT]],
    raise_service_error: ServiceErrorRaiser,
    handle_api_error: LiproApiErrorHandler | None = None,
) -> _ResultT:
    """Execute one service call through a shared auth and error chain."""
    try:
        await _async_ensure_authenticated(coordinator)
        return await call()
    except LiproRefreshTokenExpiredError as err:
        await _async_trigger_reauth(coordinator, "auth_expired")
        raise_service_error("auth_expired", err=err)
    except LiproAuthError as err:
        safe_error = safe_error_placeholder(err)
        await _async_trigger_reauth(coordinator, f"auth_error: {safe_error}")
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
    "LiproApiErrorHandler",
    "ServiceErrorRaiser",
    "async_execute_coordinator_call",
]
