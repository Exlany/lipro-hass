"""Lipro REST protocol child façade under the unified protocol root."""

from __future__ import annotations

import asyncio
from collections.abc import Awaitable, Callable
import logging
from typing import TypeVar

import aiohttp

from ...const.api import REQUEST_TIMEOUT
from . import (
    rest_facade_endpoint_methods as _endpoint_methods,
    rest_facade_request_methods as _request_methods,
)
from .auth_recovery import AuthRecoveryTelemetrySnapshot, RestAuthRecoveryCoordinator
from .auth_service import AuthApiService
from .endpoint_surface import RestEndpointSurface
from .endpoints import (
    AuthEndpoints,
    CommandEndpoints,
    DeviceEndpoints,
    MiscEndpoints,
    ScheduleEndpoints,
    StatusEndpoints,
)
from .errors import LiproAuthError
from .request_gateway import MappingRequestSender, RestRequestGateway
from .request_policy import RequestPolicy
from .session_state import RestSessionState
from .transport_executor import RestTransportExecutor
from .types import JsonObject, JsonValue, ResponseHeaders, ValidatedMappingResult

_LOGGER = logging.getLogger(__name__)
TokenRefreshCallback = Callable[[], Awaitable[None]]
_MappingPayloadT = TypeVar("_MappingPayloadT")

class LiproRestFacade:
    """Formal REST root built from explicit collaborators.

    This is the canonical REST facade under the unified protocol root.
    It owns the only supported REST entry surface for runtime/control consumers.
    """

    def __init__(
        self,
        phone_id: str,
        session: aiohttp.ClientSession | None = None,
        request_timeout: int = REQUEST_TIMEOUT,
        *,
        entry_id: str | None = None,
        session_state: RestSessionState | None = None,
        request_policy: RequestPolicy | None = None,
    ) -> None:
        """Initialize the formal REST facade and its explicit collaborators."""
        self._session_state = session_state or RestSessionState(
            phone_id=phone_id,
            session=session,
            request_timeout=request_timeout,
            entry_id=entry_id,
        )
        self._request_policy = request_policy or RequestPolicy()
        self._auth_recovery = RestAuthRecoveryCoordinator(self._session_state)
        self._transport_executor = RestTransportExecutor(
            self._session_state,
            self._auth_recovery,
            self._request_policy,
        )
        self._auth_api = AuthApiService(self, LiproAuthError, _LOGGER)
        self._auth_endpoints = AuthEndpoints(self)
        self._device_endpoints = DeviceEndpoints(self)
        self._status_endpoints = StatusEndpoints(self)
        self._command_endpoints = CommandEndpoints(self)
        self._misc_endpoints = MiscEndpoints(self)
        self._schedule_endpoints = ScheduleEndpoints(self)
        self._endpoint_surface = RestEndpointSurface(
            device_endpoints=self._device_endpoints,
            status_endpoints=self._status_endpoints,
            command_endpoints=self._command_endpoints,
            misc_endpoints=self._misc_endpoints,
            schedule_endpoints=self._schedule_endpoints,
        )
        self._request_gateway = RestRequestGateway(self)

    @property
    def phone_id(self) -> str:
        """Return the phone identifier bound to this REST facade."""
        return self._session_state.phone_id

    @property
    def session(self) -> aiohttp.ClientSession | None:
        """Return the injected aiohttp session reference."""
        return self._session_state.session

    @session.setter
    def session(self, value: aiohttp.ClientSession | None) -> None:
        self._transport_executor.sync_session(value)

    @property
    def request_timeout(self) -> int:
        """Return the configured request timeout in seconds."""
        return self._session_state.request_timeout

    @request_timeout.setter
    def request_timeout(self, value: int) -> None:
        self._session_state.request_timeout = value

    @property
    def entry_id(self) -> str | None:
        """Return the owning config-entry identifier when available."""
        return self._session_state.entry_id

    @entry_id.setter
    def entry_id(self, value: str | None) -> None:
        self._session_state.entry_id = value

    @property
    def access_token(self) -> str | None:
        """Return the current access token stored in session state."""
        return self._session_state.access_token

    @access_token.setter
    def access_token(self, value: str | None) -> None:
        self._session_state.access_token = value

    @property
    def refresh_token(self) -> str | None:
        """Return the current refresh token stored in session state."""
        return self._session_state.refresh_token

    @refresh_token.setter
    def refresh_token(self, value: str | None) -> None:
        self._session_state.refresh_token = value

    @property
    def user_id(self) -> int | None:
        """Return the authenticated user identifier stored in session state."""
        return self._session_state.user_id

    @user_id.setter
    def user_id(self, value: int | None) -> None:
        self._session_state.user_id = value

    @property
    def biz_id(self) -> str | None:
        """Return the authenticated biz identifier stored in session state."""
        return self._session_state.biz_id

    @biz_id.setter
    def biz_id(self, value: str | None) -> None:
        self._session_state.biz_id = value

    @property
    def auth_api(self) -> AuthApiService:
        """Return the canonical auth collaborator for endpoint adapters."""
        return self._auth_api

    @property
    def request_policy(self) -> RequestPolicy:
        """Return the canonical retry/rate-limit policy for REST calls."""
        return self._request_policy

    @property
    def refresh_lock(self) -> asyncio.Lock:
        """Return the shared refresh lock guarding token refresh."""
        return self._session_state.refresh_lock

    @property
    def on_token_refresh(self) -> TokenRefreshCallback | None:
        """Return the registered token-refresh callback."""
        return self._session_state.on_token_refresh

    @on_token_refresh.setter
    def on_token_refresh(self, value: TokenRefreshCallback | None) -> None:
        self._session_state.on_token_refresh = value

    def set_tokens(
        self,
        access_token: str,
        refresh_token: str,
        user_id: int | None = None,
        biz_id: str | None = None,
    ) -> None:
        """Persist freshly issued authentication tokens into facade state."""
        self._auth_recovery.set_tokens(
            access_token,
            refresh_token,
            user_id=user_id,
            biz_id=biz_id,
        )

    def set_token_refresh_callback(self, callback: TokenRefreshCallback) -> None:
        """Register the async callback used to refresh access tokens."""
        self._auth_recovery.set_token_refresh_callback(callback)

    def auth_recovery_telemetry_snapshot(self) -> AuthRecoveryTelemetrySnapshot:
        """Return sanitized auth-recovery telemetry for protocol diagnostics."""
        return self._auth_recovery.telemetry_snapshot()

    # Static method binding keeps the façade explicit without reintroducing
    # mixin aggregation or dynamic delegation.
    login = _request_methods.login
    refresh_access_token = _request_methods.refresh_access_token
    get_session = _request_methods.get_session
    smart_home_sign = _request_methods.smart_home_sign
    get_timestamp_ms = _request_methods.get_timestamp_ms
    execute_request = _request_methods.execute_request
    execute_mapping_request_with_rate_limit = _request_methods.execute_mapping_request_with_rate_limit
    build_iot_headers = _request_methods.build_iot_headers
    handle_auth_error_and_retry = _request_methods.handle_auth_error_and_retry
    finalize_mapping_result = _request_methods.finalize_mapping_result
    smart_home_request = _request_methods.smart_home_request
    iot_request = _request_methods.iot_request
    request_iot_mapping = _request_methods.request_iot_mapping
    request_iot_mapping_raw = _request_methods.request_iot_mapping_raw
    iot_request_with_busy_retry = _request_methods.iot_request_with_busy_retry
    to_device_type_hex = _request_methods.to_device_type_hex
    is_success_code = staticmethod(_request_methods.is_success_code)
    unwrap_iot_success_payload = staticmethod(_request_methods.unwrap_iot_success_payload)
    require_mapping_response = staticmethod(_request_methods.require_mapping_response)
    is_invalid_param_error_code = staticmethod(_request_methods.is_invalid_param_error_code)
    get_devices = _endpoint_methods.get_devices
    get_product_configs = _endpoint_methods.get_product_configs
    query_device_status = _endpoint_methods.query_device_status
    query_mesh_group_status = _endpoint_methods.query_mesh_group_status
    query_connect_status = _endpoint_methods.query_connect_status
    send_command = _endpoint_methods.send_command
    send_group_command = _endpoint_methods.send_group_command
    get_mqtt_config = _endpoint_methods.get_mqtt_config
    fetch_outlet_power_info = _endpoint_methods.fetch_outlet_power_info
    query_command_result = _endpoint_methods.query_command_result
    get_city = _endpoint_methods.get_city
    query_user_cloud = _endpoint_methods.query_user_cloud
    query_ota_info = _endpoint_methods.query_ota_info
    fetch_body_sensor_history = _endpoint_methods.fetch_body_sensor_history
    fetch_door_sensor_history = _endpoint_methods.fetch_door_sensor_history
    get_device_schedules = _endpoint_methods.get_device_schedules
    add_device_schedule = _endpoint_methods.add_device_schedule
    delete_device_schedules = _endpoint_methods.delete_device_schedules

    async def _get_session(self) -> aiohttp.ClientSession:
        return await self._transport_executor.get_session()

    def _smart_home_sign(self) -> str:
        return self._transport_executor.smart_home_sign()

    def _iot_sign(self, nonce: int, body: str) -> str:
        return self._transport_executor.iot_sign(nonce, body)

    def _get_timestamp_ms(self) -> int:
        return self._transport_executor.get_timestamp_ms()

    async def _execute_request(
        self,
        request_ctx: object,
        path: str,
    ) -> tuple[int, JsonObject, ResponseHeaders]:
        return await self._transport_executor.execute_request(request_ctx, path)

    async def _execute_mapping_request_with_rate_limit(
        self,
        *,
        path: str,
        retry_count: int,
        send_request: MappingRequestSender,
    ) -> ValidatedMappingResult:
        return await self._transport_executor.execute_mapping_request_with_rate_limit(
            path=path,
            retry_count=retry_count,
            send_request=send_request,
        )

    def _build_iot_headers(self, body: str) -> dict[str, str]:
        return self._transport_executor.build_iot_headers(body)

    async def _handle_auth_error_and_retry(
        self,
        path: str,
        request_token: str | None,
        is_retry: bool,
    ) -> bool:
        return await self._auth_recovery.handle_auth_error_and_retry(
            path, request_token, is_retry
        )

    async def _finalize_mapping_result(
        self,
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

    async def _handle_401_with_refresh(self, request_token: str | None) -> bool:
        return await self._auth_recovery.handle_401_with_refresh(request_token)

    @staticmethod
    def _resolve_error_code(code: object, error_code: object) -> int | str | None:
        return RestAuthRecoveryCoordinator.resolve_error_code(code, error_code)

    @staticmethod
    def _unwrap_iot_success_payload(result: JsonObject) -> JsonValue:
        return RestAuthRecoveryCoordinator.unwrap_iot_success_payload(result)

    @staticmethod
    def _is_command_busy_error(err: Exception) -> bool:
        return RequestPolicy.is_command_busy_error(err)

    @staticmethod
    def _is_change_state_command(command: str) -> bool:
        return RequestPolicy.is_change_state_command(command)

    @staticmethod
    def _normalize_pacing_target(target_id: str) -> str:
        return RequestPolicy.normalize_pacing_target(target_id)

    async def close(self) -> None:
        """Close transport-owned session resources for this facade."""
        self._transport_executor.close()

    async def _request_smart_home_mapping(
        self,
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
        self,
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
        self,
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
        self,
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
        self,
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

    def _to_device_type_hex(self, device_type: int | str) -> str:
        return self._transport_executor.to_device_type_hex(device_type)

    @staticmethod
    def _require_mapping_response(path: str, result: object) -> JsonObject:
        return RestTransportExecutor.require_mapping_response(path, result)

    @staticmethod
    def _is_invalid_param_error_code(code: object) -> bool:
        return RestAuthRecoveryCoordinator.is_invalid_param_error_code(code)

__all__ = ["LiproRestFacade"]
