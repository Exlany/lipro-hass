"""Private transport/request wrappers owned by the REST child facade."""

from __future__ import annotations

from collections.abc import Awaitable, Callable
from typing import TYPE_CHECKING, TypeVar

import aiohttp

from .auth_recovery import RestAuthRecoveryCoordinator
from .request_policy import RequestPolicy
from .transport_executor import RestTransportExecutor
from .types import JsonObject, JsonValue

if TYPE_CHECKING:
    from .rest_facade import LiproRestFacade


_MappingPayloadT = TypeVar('_MappingPayloadT')


async def _get_session(self: LiproRestFacade) -> aiohttp.ClientSession:
    return await self._transport_executor.get_session()


def _smart_home_sign(self: LiproRestFacade) -> str:
    return self._transport_executor.smart_home_sign()


def _iot_sign(self: LiproRestFacade, nonce: int, body: str) -> str:
    return self._transport_executor.iot_sign(nonce, body)


def _get_timestamp_ms(self: LiproRestFacade) -> int:
    return self._transport_executor.get_timestamp_ms()


async def _execute_request(
    self: LiproRestFacade,
    request_ctx: object,
    path: str,
) -> tuple[int, JsonObject, dict[str, str]]:
    return await self._transport_executor.execute_request(request_ctx, path)


async def _execute_mapping_request_with_rate_limit(
    self: LiproRestFacade,
    *,
    path: str,
    retry_count: int,
    send_request: Callable[[], Awaitable[tuple[int, object, dict[str, str], str | None]]],
) -> tuple[int, JsonObject, str | None]:
    return await self._transport_executor.execute_mapping_request_with_rate_limit(
        path=path,
        retry_count=retry_count,
        send_request=send_request,
    )


def _build_iot_headers(self: LiproRestFacade, body: str) -> dict[str, str]:
    return self._transport_executor.build_iot_headers(body)


async def _handle_auth_error_and_retry(
    self: LiproRestFacade,
    path: str,
    request_token: str | None,
    is_retry: bool,
) -> bool:
    return await self._auth_recovery.handle_auth_error_and_retry(
        path,
        request_token,
        is_retry,
    )


async def _finalize_mapping_result(
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
    return await self._auth_recovery.finalize_mapping_result(
        path=path,
        result=result,
        request_token=request_token,
        is_retry=is_retry,
        retry_on_auth_error=retry_on_auth_error,
        retry_request=retry_request,
        success_payload=success_payload,
    )


async def _handle_401_with_refresh(
    self: LiproRestFacade,
    request_token: str | None,
) -> bool:
    return await self._auth_recovery.handle_401_with_refresh(request_token)


def _resolve_error_code(code: object, error_code: object) -> int | str | None:
    return RestAuthRecoveryCoordinator.resolve_error_code(code, error_code)


def _unwrap_iot_success_payload(result: JsonObject) -> JsonValue:
    return RestAuthRecoveryCoordinator.unwrap_iot_success_payload(result)


def _is_command_busy_error(err: Exception) -> bool:
    return RequestPolicy.is_command_busy_error(err)


def _is_change_state_command(command: str) -> bool:
    return RequestPolicy.is_change_state_command(command)


def _normalize_pacing_target(target_id: str) -> str:
    return RequestPolicy.normalize_pacing_target(target_id)


async def close(self: LiproRestFacade) -> None:
    """Close transport-owned session resources for this facade."""
    self._transport_executor.close()


async def _request_smart_home_mapping(
    self: LiproRestFacade,
    path: str,
    data: JsonObject,
    require_auth: bool = True,
    *,
    is_retry: bool = False,
    retry_count: int = 0,
) -> tuple[JsonObject, str | None]:
    return await self._request_gateway.request_smart_home_mapping(
        path,
        data,
        require_auth=require_auth,
        is_retry=is_retry,
        retry_count=retry_count,
    )


async def _smart_home_request(
    self: LiproRestFacade,
    path: str,
    data: JsonObject,
    require_auth: bool = True,
    is_retry: bool = False,
    retry_count: int = 0,
) -> JsonValue:
    return await self._request_gateway.smart_home_request(
        path,
        data,
        require_auth=require_auth,
        is_retry=is_retry,
        retry_count=retry_count,
    )


async def _request_iot_mapping_raw(
    self: LiproRestFacade,
    path: str,
    body: str,
    *,
    is_retry: bool = False,
    retry_count: int = 0,
) -> tuple[JsonObject, str | None]:
    return await self._request_gateway.request_iot_mapping_raw(
        path,
        body,
        is_retry=is_retry,
        retry_count=retry_count,
    )


async def _request_iot_mapping(
    self: LiproRestFacade,
    path: str,
    body_data: JsonObject,
    *,
    is_retry: bool = False,
    retry_count: int = 0,
) -> tuple[JsonObject, str | None]:
    return await self._request_gateway.request_iot_mapping(
        path,
        body_data,
        is_retry=is_retry,
        retry_count=retry_count,
    )


async def _iot_request(
    self: LiproRestFacade,
    path: str,
    body_data: JsonObject,
    is_retry: bool = False,
    retry_count: int = 0,
) -> JsonValue:
    return await self._request_gateway.iot_request(
        path,
        body_data,
        is_retry=is_retry,
        retry_count=retry_count,
    )


def _to_device_type_hex(self: LiproRestFacade, device_type: int | str) -> str:
    return self._transport_executor.to_device_type_hex(device_type)


def _require_mapping_response(path: str, result: object) -> JsonObject:
    return RestTransportExecutor.require_mapping_response(path, result)


def _is_invalid_param_error_code(code: object) -> bool:
    return RestAuthRecoveryCoordinator.is_invalid_param_error_code(code)


__all__ = [
    '_build_iot_headers',
    '_execute_mapping_request_with_rate_limit',
    '_execute_request',
    '_finalize_mapping_result',
    '_get_session',
    '_get_timestamp_ms',
    '_handle_401_with_refresh',
    '_handle_auth_error_and_retry',
    '_iot_request',
    '_iot_sign',
    '_is_change_state_command',
    '_is_command_busy_error',
    '_is_invalid_param_error_code',
    '_normalize_pacing_target',
    '_request_iot_mapping',
    '_request_iot_mapping_raw',
    '_request_smart_home_mapping',
    '_require_mapping_response',
    '_resolve_error_code',
    '_smart_home_request',
    '_smart_home_sign',
    '_to_device_type_hex',
    '_unwrap_iot_success_payload',
    'close',
]
