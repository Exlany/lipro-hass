"""Public request/auth method surface for `LiproRestFacade`.

These bound methods keep the class file focused on composition and private
local mechanics while preserving an explicit, static public surface.
"""

from __future__ import annotations

from collections.abc import Awaitable, Callable
import logging
from typing import TYPE_CHECKING, TypeVar, cast

import aiohttp

from .auth_recovery import RestAuthRecoveryCoordinator
from .request_gateway import MappingRequestSender
from .transport_executor import RestTransportExecutor
from .types import (
    JsonObject,
    JsonValue,
    LoginResponse,
    ResponseHeaders,
    ValidatedMappingResult,
)

if TYPE_CHECKING:
    from .rest_facade import LiproRestFacade

_LOGGER = logging.getLogger("custom_components.lipro.core.api")
_MappingPayloadT = TypeVar("_MappingPayloadT")


async def login(
    self: LiproRestFacade,
    phone: str,
    password: str,
    *,
    password_is_hashed: bool = False,
) -> LoginResponse:
    """Authenticate through the formal auth endpoint surface."""
    return await self._auth_endpoints.login(
        phone,
        password,
        password_is_hashed=password_is_hashed,
    )


async def refresh_access_token(self: LiproRestFacade) -> LoginResponse:
    """Refresh access tokens through the formal auth endpoint surface."""
    return await self._auth_endpoints.refresh_access_token()


async def get_session(self: LiproRestFacade) -> aiohttp.ClientSession:
    """Return the active aiohttp session through the localized request gateway."""
    return await self._get_session()


def smart_home_sign(self: LiproRestFacade) -> str:
    """Return one Smart Home signature through the transport pipeline."""
    return self._smart_home_sign()


def get_timestamp_ms(self: LiproRestFacade) -> int:
    """Return the current timestamp via the transport pipeline."""
    return self._get_timestamp_ms()


async def execute_request(
    self: LiproRestFacade,
    request_ctx: object,
    path: str,
) -> tuple[int, JsonObject, ResponseHeaders]:
    """Execute one low-level request through the transport pipeline."""
    return await self._execute_request(request_ctx, path)


async def execute_mapping_request_with_rate_limit(
    self: LiproRestFacade,
    *,
    path: str,
    retry_count: int,
    send_request: MappingRequestSender,
) -> ValidatedMappingResult:
    """Execute one mapping request via the canonical rate-limit pipeline."""
    return await self._execute_mapping_request_with_rate_limit(
        path=path,
        retry_count=retry_count,
        send_request=send_request,
    )


def build_iot_headers(self: LiproRestFacade, body: str) -> dict[str, str]:
    """Build IoT headers through the transport pipeline."""
    return self._build_iot_headers(body)


async def handle_auth_error_and_retry(
    self: LiproRestFacade,
    path: str,
    request_token: str | None,
    is_retry: bool,
) -> bool:
    """Handle auth errors through the canonical auth-recovery pipeline."""
    return await self._handle_auth_error_and_retry(path, request_token, is_retry)


async def finalize_mapping_result(
    self: LiproRestFacade,
    *,
    path: str,
    result: JsonObject,
    request_token: str | None,
    is_retry: bool,
    retry_on_auth_error: bool,
    retry_request: Callable[[], Awaitable[_MappingPayloadT]] | None,
    success_payload: Callable[[JsonObject], _MappingPayloadT],
) -> _MappingPayloadT:
    """Finalize one mapping response via the canonical auth-recovery pipeline."""
    return await self._finalize_mapping_result(
        path=path,
        result=result,
        request_token=request_token,
        is_retry=is_retry,
        retry_on_auth_error=retry_on_auth_error,
        retry_request=retry_request,
        success_payload=success_payload,
    )


async def smart_home_request(
    self: LiproRestFacade,
    path: str,
    data: JsonObject,
    require_auth: bool = True,
    is_retry: bool = False,
    retry_count: int = 0,
) -> JsonValue:
    """Execute one Smart Home request through the formal transport pipeline."""
    return await self._dispatch_retry_aware_smart_home_call(
        path,
        data,
        require_auth=require_auth,
        is_retry=is_retry,
        retry_count=retry_count,
    )


async def iot_request(
    self: LiproRestFacade,
    path: str,
    body_data: JsonObject,
    is_retry: bool = False,
    retry_count: int = 0,
) -> JsonValue:
    """Execute one IoT request through the formal transport pipeline."""
    return await self._dispatch_retry_aware_call(
        self._iot_request,
        path,
        body_data,
        is_retry=is_retry,
        retry_count=retry_count,
    )


async def request_iot_mapping(
    self: LiproRestFacade,
    path: str,
    body_data: JsonObject,
    *,
    is_retry: bool = False,
    retry_count: int = 0,
) -> tuple[JsonObject, str | None]:
    """Request one IoT mapping payload with retry context preserved."""
    return await self._dispatch_retry_aware_call(
        self._request_iot_mapping,
        path,
        body_data,
        is_retry=is_retry,
        retry_count=retry_count,
    )


async def request_iot_mapping_raw(
    self: LiproRestFacade,
    path: str,
    body: str,
    *,
    is_retry: bool = False,
    retry_count: int = 0,
) -> tuple[JsonObject, str | None]:
    """Request one raw IoT mapping payload without result finalization."""
    return await self._dispatch_retry_aware_call(
        self._request_iot_mapping_raw,
        path,
        body,
        is_retry=is_retry,
        retry_count=retry_count,
    )


async def iot_request_with_busy_retry(
    self: LiproRestFacade,
    path: str,
    body_data: JsonObject,
    *,
    target_id: str,
    command: str,
) -> dict[str, object]:
    """Execute one IoT command with the formal busy-retry policy."""
    return await self._request_policy.iot_request_with_busy_retry(
        path,
        cast(dict[str, object], body_data),
        target_id=target_id,
        command=command,
        iot_request=cast(
            Callable[[str, dict[str, object]], Awaitable[object]],
            self._iot_request,
        ),
        logger=_LOGGER,
    )


def to_device_type_hex(self: LiproRestFacade, device_type: int | str) -> str:
    """Normalize one device type into the transport hex representation."""
    return self._to_device_type_hex(device_type)


def is_success_code(code: object) -> bool:
    """Return whether one vendor response code represents success."""
    return RestAuthRecoveryCoordinator.is_success_code(code)


def unwrap_iot_success_payload(result: JsonObject) -> JsonValue:
    """Extract the canonical success payload from one IoT response."""
    return RestAuthRecoveryCoordinator.unwrap_iot_success_payload(result)


def require_mapping_response(path: str, result: object) -> JsonObject:
    """Require one mapping response payload to be a JSON object."""
    return RestTransportExecutor.require_mapping_response(path, result)


def is_invalid_param_error_code(code: object) -> bool:
    """Return whether one response code indicates an invalid-parameter error."""
    return RestAuthRecoveryCoordinator.is_invalid_param_error_code(code)
