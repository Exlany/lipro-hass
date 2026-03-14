"""Lipro REST protocol facade and transitional compat shell."""

from __future__ import annotations

import asyncio
from collections.abc import Awaitable, Callable, Sequence
import logging
from typing import Any, TypeVar

import aiohttp

from ...const.api import (
    CONTENT_TYPE_FORM,
    HEADER_CONTENT_TYPE,
    HEADER_USER_AGENT,
    IOT_API_URL,
    REQUEST_TIMEOUT,
    SMART_HOME_API_URL,
    USER_AGENT,
)
from ...const.base import APP_VERSION_CODE, APP_VERSION_NAME
from . import client_pacing as _client_pacing
from .auth_service import AuthApiService
from .client_auth_recovery import AuthRecoveryCoordinator
from .client_base import ClientSessionState, _ClientBase
from .client_transport import TransportExecutor
from .command_api_service import iot_request_with_busy_retry as _iot_busy_retry_service
from .endpoints import (
    AuthEndpoints,
    CommandEndpoints,
    DeviceEndpoints,
    MiscEndpoints,
    ScheduleEndpoints,
    StatusEndpoints,
)
from .endpoints.payloads import EndpointPayloadNormalizers
from .errors import LiproApiError, LiproAuthError
from .request_codec import (
    build_smart_home_request_data,
    encode_iot_request_body,
    extract_smart_home_success_payload,
)
from .request_policy import (
    RequestPolicy,
    throttle_change_state as _throttle_change_state_policy,
)
from .schedule_service import ScheduleApiService
from .types import DeviceListResponse, LoginResponse, OtaInfoRow, ScheduleTimingRow

_LOGGER = logging.getLogger(__name__)
MappingRequestSender = Callable[[], Awaitable[tuple[int, Any, dict[str, str], str | None]]]
TokenRefreshCallback = Callable[[], Awaitable[None]]
_MappingPayloadT = TypeVar("_MappingPayloadT")


class LiproRestFacade(_ClientBase):
    """Formal REST root built from explicit collaborators.

    This is the canonical REST facade under the unified protocol root.
    It owns the only supported REST entry surface for runtime/control consumers.
    """

    _extract_list_payload = staticmethod(EndpointPayloadNormalizers.extract_list_payload)
    _extract_data_list = staticmethod(EndpointPayloadNormalizers.extract_data_list)
    _extract_timings_list = staticmethod(EndpointPayloadNormalizers.extract_timings_list)
    _sanitize_iot_device_ids = staticmethod(EndpointPayloadNormalizers.sanitize_iot_device_ids)
    _normalize_power_target_id = staticmethod(EndpointPayloadNormalizers.normalize_power_target_id)
    _is_retriable_device_error = staticmethod(StatusEndpoints.is_retriable_device_error)
    _coerce_int_list = staticmethod(ScheduleEndpoints.coerce_int_list)

    @classmethod
    def _parse_mesh_schedule_json(cls, schedule_json: object) -> dict[str, list[int]]:
        return ScheduleEndpoints.parse_mesh_schedule_json(schedule_json)

    @classmethod
    def _normalize_mesh_timing_rows(
        cls,
        rows: Sequence[object],
        *,
        fallback_device_id: str = "",
    ) -> list[ScheduleTimingRow]:
        return ScheduleEndpoints.normalize_mesh_timing_rows(
            rows,
            fallback_device_id=fallback_device_id,
        )

    def __init__(
        self,
        phone_id: str,
        session: aiohttp.ClientSession | None = None,
        request_timeout: int = REQUEST_TIMEOUT,
        *,
        entry_id: str | None = None,
        session_state: ClientSessionState | None = None,
        request_policy: RequestPolicy | None = None,
    ) -> None:
        """Initialize the formal REST facade and its explicit collaborators."""
        self._session_state = session_state or ClientSessionState(
            phone_id=phone_id,
            session=session,
            request_timeout=request_timeout,
            entry_id=entry_id,
        )
        self._request_policy = request_policy or RequestPolicy()
        self._command_pacing_lock = self._request_policy.command_pacing_lock
        self._command_pacing_target_locks = self._request_policy.command_pacing_target_locks
        self._last_change_state_at = self._request_policy.last_change_state_at
        self._change_state_min_interval = self._request_policy.change_state_min_interval
        self._change_state_busy_count = self._request_policy.change_state_busy_count
        self._auth_recovery = AuthRecoveryCoordinator(self._session_state)
        self._transport_executor = TransportExecutor(
            self._session_state,
            self._auth_recovery,
            self._request_policy,
        )
        self._auth_api = AuthApiService(self, LiproAuthError, _LOGGER)
        self._schedule_api = ScheduleApiService(self)
        self._auth_endpoints = AuthEndpoints(self)
        self._device_endpoints = DeviceEndpoints(self)
        self._status_endpoints = StatusEndpoints(self)
        self._command_endpoints = CommandEndpoints(self)
        self._misc_endpoints = MiscEndpoints(self)
        self._schedule_endpoints = ScheduleEndpoints(self)

    @property
    def phone_id(self) -> str:
        """Return the phone identifier bound to this REST facade."""
        return self._session_state.phone_id

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
    def _phone_id(self) -> str:
        return self._session_state.phone_id

    @_phone_id.setter
    def _phone_id(self, value: str) -> None:
        self._session_state.phone_id = value

    @property
    def _session(self) -> aiohttp.ClientSession | None:
        return self._session_state.session

    @_session.setter
    def _session(self, value: aiohttp.ClientSession | None) -> None:
        self._transport_executor.sync_session(value)

    @property
    def _request_timeout(self) -> int:
        return self._session_state.request_timeout

    @_request_timeout.setter
    def _request_timeout(self, value: int) -> None:
        self._session_state.request_timeout = value

    @property
    def _access_token(self) -> str | None:
        return self._session_state.access_token

    @_access_token.setter
    def _access_token(self, value: str | None) -> None:
        self._session_state.access_token = value

    @property
    def _refresh_token(self) -> str | None:
        return self._session_state.refresh_token

    @_refresh_token.setter
    def _refresh_token(self, value: str | None) -> None:
        self._session_state.refresh_token = value

    @property
    def _user_id(self) -> int | None:
        return self._session_state.user_id

    @_user_id.setter
    def _user_id(self, value: int | None) -> None:
        self._session_state.user_id = value

    @property
    def _biz_id(self) -> str | None:
        return self._session_state.biz_id

    @_biz_id.setter
    def _biz_id(self, value: str | None) -> None:
        self._session_state.biz_id = value

    @property
    def _entry_id(self) -> str | None:
        return self._session_state.entry_id

    @_entry_id.setter
    def _entry_id(self, value: str | None) -> None:
        self._session_state.entry_id = value

    @property
    def _refresh_lock(self) -> asyncio.Lock:
        return self._session_state.refresh_lock

    @property
    def _on_token_refresh(self) -> TokenRefreshCallback | None:
        return self._session_state.on_token_refresh

    @_on_token_refresh.setter
    def _on_token_refresh(self, value: TokenRefreshCallback | None) -> None:
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

    def auth_recovery_telemetry_snapshot(self) -> dict[str, Any]:
        """Return sanitized auth-recovery telemetry for protocol diagnostics."""
        return self._auth_recovery.telemetry_snapshot()

    async def login(
        self,
        phone: str,
        password: str,
        *,
        password_is_hashed: bool = False,
    ) -> LoginResponse:
        """Compatibility auth entrypoint for auth-manager consumers."""
        return await self._auth_endpoints.login(
            phone,
            password,
            password_is_hashed=password_is_hashed,
        )

    async def refresh_access_token(self) -> LoginResponse:
        """Compatibility refresh entrypoint for auth-manager consumers."""
        return await self._auth_endpoints.refresh_access_token()

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
        request_ctx: Any,
        path: str,
    ) -> tuple[int, dict[str, Any], dict[str, str]]:
        return await self._transport_executor.execute_request(request_ctx, path)

    async def _execute_mapping_request_with_rate_limit(
        self,
        *,
        path: str,
        retry_count: int,
        send_request: MappingRequestSender,
    ) -> tuple[int, dict[str, Any], str | None]:
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
        result: dict[str, Any],
        request_token: str | None,
        is_retry: bool,
        retry_on_auth_error: bool,
        retry_request: Callable[[], Awaitable[_MappingPayloadT]] | None,
        success_payload: Callable[[dict[str, Any]], _MappingPayloadT],
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

    async def _handle_rate_limit(
        self,
        path: str,
        headers: dict[str, str],
        retry_count: int,
    ) -> float:
        return await self._request_policy.handle_rate_limit(path, headers, retry_count)

    async def _record_change_state_busy(
        self,
        target_id: str,
        command: str,
    ) -> tuple[float, int]:
        return await self._request_policy.record_change_state_busy(target_id, command)

    async def _record_change_state_success(self, target_id: str, command: str) -> None:
        await self._request_policy.record_change_state_success(target_id, command)

    async def _throttle_change_state(self, target_id: str, command: str) -> None:
        await _throttle_change_state_policy(
            target_id=target_id,
            command=command,
            command_pacing_lock=self._command_pacing_lock,
            command_pacing_target_locks=self._command_pacing_target_locks,
            last_change_state_at=self._last_change_state_at,
            change_state_min_interval=self._change_state_min_interval,
            change_state_busy_count=self._change_state_busy_count,
            monotonic=_client_pacing.time.monotonic,
            sleep=_client_pacing.asyncio.sleep,
        )

    @staticmethod
    def _parse_retry_after(headers: dict[str, str]) -> float | None:
        return RequestPolicy.parse_retry_after(headers)

    @staticmethod
    def _is_auth_error_code(code: Any) -> bool:
        return AuthRecoveryCoordinator.is_auth_error_code(code)

    @classmethod
    def _resolve_auth_error_code(
        cls,
        code: Any,
        error_code: Any,
    ) -> int | str | None:
        return AuthRecoveryCoordinator.resolve_auth_error_code(code, error_code)

    @staticmethod
    def _resolve_error_code(code: Any, error_code: Any) -> int | str | None:
        return AuthRecoveryCoordinator.resolve_error_code(code, error_code)

    @staticmethod
    def _is_success_code(code: Any) -> bool:
        return AuthRecoveryCoordinator.is_success_code(code)

    @staticmethod
    def _unwrap_iot_success_payload(result: dict[str, Any]) -> Any:
        return AuthRecoveryCoordinator.unwrap_iot_success_payload(result)

    @staticmethod
    def _is_command_busy_error(err: Exception) -> bool:
        return RequestPolicy.is_command_busy_error(err)

    @staticmethod
    def _is_change_state_command(command: str) -> bool:
        return RequestPolicy.is_change_state_command(command)

    @staticmethod
    def _normalize_pacing_target(target_id: str) -> str:
        return RequestPolicy.normalize_pacing_target(target_id)

    def _enforce_command_pacing_cache_limit(self) -> None:
        self._request_policy.enforce_command_pacing_cache_limit()

    async def close(self) -> None:
        """Close transport-owned session resources for this facade."""
        self._transport_executor.close()

    async def _request_smart_home_mapping(
        self,
        path: str,
        data: dict[str, Any],
        require_auth: bool = True,
        *,
        is_retry: bool = False,
        retry_count: int = 0,
    ) -> tuple[dict[str, Any], str | None]:
        url = f"{SMART_HOME_API_URL}{path}"

        async def _send_request() -> tuple[int, Any, dict[str, str], str | None]:
            request_token = self._access_token
            if require_auth and not request_token:
                msg = "No access token available"
                raise LiproAuthError(msg)

            request_data = build_smart_home_request_data(
                sign=self._smart_home_sign(),
                phone_id=self._phone_id,
                timestamp_ms=self._get_timestamp_ms(),
                app_version_name=APP_VERSION_NAME,
                app_version_code=APP_VERSION_CODE,
                data=data,
                access_token=request_token if require_auth else None,
            )

            session = await self._get_session()
            status, result, headers = await self._execute_request(
                session.post(
                    url,
                    data=request_data,
                    headers={
                        HEADER_CONTENT_TYPE: CONTENT_TYPE_FORM,
                        HEADER_USER_AGENT: USER_AGENT,
                    },
                    timeout=aiohttp.ClientTimeout(total=self._request_timeout),
                ),
                path,
            )
            return status, result, headers, request_token

        _, result, request_token = await self._execute_mapping_request_with_rate_limit(
            path=path,
            retry_count=retry_count,
            send_request=_send_request,
        )
        return result, request_token

    async def _smart_home_request(
        self,
        path: str,
        data: dict[str, Any],
        require_auth: bool = True,
        is_retry: bool = False,
        retry_count: int = 0,
    ) -> Any:
        result, request_token = await self._request_smart_home_mapping(
            path,
            data,
            require_auth=require_auth,
            is_retry=is_retry,
            retry_count=retry_count,
        )
        return await self._finalize_mapping_result(
            path=path,
            result=result,
            request_token=request_token,
            is_retry=is_retry,
            retry_on_auth_error=require_auth,
            retry_request=(
                lambda: self._smart_home_request(
                    path,
                    data,
                    require_auth,
                    is_retry=True,
                )
            ),
            success_payload=extract_smart_home_success_payload,
        )


    async def _request_iot_mapping_raw(
        self,
        path: str,
        body: str,
        *,
        is_retry: bool = False,
        retry_count: int = 0,
    ) -> tuple[dict[str, Any], str | None]:
        url = f"{IOT_API_URL}{path}"

        async def _send_request() -> tuple[int, Any, dict[str, str], str | None]:
            request_token = self._access_token
            if not request_token:
                msg = "No access token available"
                raise LiproAuthError(msg)

            session = await self._get_session()
            req_headers = self._build_iot_headers(body)
            status, result, resp_headers = await self._execute_request(
                session.post(
                    url,
                    data=body,
                    headers=req_headers,
                    timeout=aiohttp.ClientTimeout(total=self._request_timeout),
                ),
                path,
            )
            return status, result, resp_headers, request_token

        status, result, request_token = await self._execute_mapping_request_with_rate_limit(
            path=path,
            retry_count=retry_count,
            send_request=_send_request,
        )

        if status == 401:
            if await self._handle_auth_error_and_retry(path, request_token, is_retry):
                return await self._request_iot_mapping_raw(
                    path,
                    body,
                    is_retry=True,
                )
            msg = "HTTP 401 Unauthorized"
            raise LiproAuthError(msg, 401)

        return result, request_token

    async def _request_iot_mapping(
        self,
        path: str,
        body_data: dict[str, Any],
        *,
        is_retry: bool = False,
        retry_count: int = 0,
    ) -> tuple[dict[str, Any], str | None]:
        body = encode_iot_request_body(body_data)
        return await self._request_iot_mapping_raw(
            path,
            body,
            is_retry=is_retry,
            retry_count=retry_count,
        )

    async def _iot_request(
        self,
        path: str,
        body_data: dict[str, Any],
        is_retry: bool = False,
        retry_count: int = 0,
    ) -> Any:
        result, request_token = await self._request_iot_mapping(
            path,
            body_data,
            is_retry=is_retry,
            retry_count=retry_count,
        )
        return await self._finalize_mapping_result(
            path=path,
            result=result,
            request_token=request_token,
            is_retry=is_retry,
            retry_on_auth_error=True,
            retry_request=lambda: self._iot_request(path, body_data, is_retry=True),
            success_payload=self._unwrap_iot_success_payload,
        )

    async def _iot_request_with_busy_retry(
        self,
        path: str,
        body_data: dict[str, Any],
        *,
        target_id: str,
        command: str,
    ) -> dict[str, Any]:
        return await _iot_busy_retry_service(
            path=path,
            body_data=body_data,
            target_id=target_id,
            command=command,
            attempt_limit=3,
            base_delay_seconds=0.25,
            iot_request=self._iot_request,
            throttle_change_state=self._throttle_change_state,
            record_change_state_success=self._record_change_state_success,
            is_command_busy_error=self._is_command_busy_error,
            lipro_api_error=LiproApiError,
            record_change_state_busy=self._record_change_state_busy,
            sleep=asyncio.sleep,
            logger=_LOGGER,
        )

    def _to_device_type_hex(self, device_type: int | str) -> str:
        return self._transport_executor.to_device_type_hex(device_type)

    @staticmethod
    def _require_mapping_response(path: str, result: Any) -> dict[str, Any]:
        return TransportExecutor.require_mapping_response(path, result)

    @staticmethod
    def _is_invalid_param_error_code(code: Any) -> bool:
        return AuthRecoveryCoordinator.is_invalid_param_error_code(code)

    async def get_devices(self, offset: int = 0, limit: int = 100) -> DeviceListResponse:
        """Return canonical device rows through the explicit device endpoint."""
        return await self._device_endpoints.get_devices(offset=offset, limit=limit)

    async def get_product_configs(self) -> list[dict[str, Any]]:
        """Return canonical product configuration rows."""
        return await self._device_endpoints.get_product_configs()

    async def query_device_status(
        self,
        device_ids: list[str],
        *,
        max_devices_per_query: int = 100,
        on_batch_metric: Any = None,
    ) -> list[dict[str, Any]]:
        """Return canonical device-status rows through the explicit status endpoint."""
        return await self._status_endpoints.query_device_status(
            device_ids,
            max_devices_per_query=max_devices_per_query,
            on_batch_metric=on_batch_metric,
        )

    async def query_mesh_group_status(
        self,
        group_ids: list[str],
    ) -> list[dict[str, Any]]:
        """Return canonical mesh-group status rows."""
        return await self._status_endpoints.query_mesh_group_status(group_ids)

    async def query_connect_status(self, device_ids: list[str]) -> dict[str, bool]:
        """Return connectivity status for the requested devices."""
        return await self._status_endpoints.query_connect_status(device_ids)

    async def send_command(
        self,
        device_id: str,
        command: str,
        device_type: int | str,
        properties: list[dict[str, str]] | None = None,
        iot_name: str = "",
    ) -> dict[str, Any]:
        """Send one device command through the explicit command endpoint."""
        return await self._command_endpoints.send_command(
            device_id=device_id,
            command=command,
            device_type=device_type,
            properties=properties,
            iot_name=iot_name,
        )

    async def send_group_command(
        self,
        group_id: str,
        command: str,
        device_type: int | str,
        properties: list[dict[str, str]] | None = None,
        iot_name: str = "",
    ) -> dict[str, Any]:
        """Send one group command through the explicit command endpoint."""
        return await self._command_endpoints.send_group_command(
            group_id=group_id,
            command=command,
            device_type=device_type,
            properties=properties,
            iot_name=iot_name,
        )

    async def get_mqtt_config(self) -> dict[str, Any]:
        """Return MQTT configuration through the explicit misc endpoint."""
        return await self._misc_endpoints.get_mqtt_config()

    async def fetch_outlet_power_info(self, device_id: str) -> dict[str, Any]:
        """Return outlet power information for one device."""
        return await self._misc_endpoints.fetch_outlet_power_info(device_id)

    async def query_command_result(
        self,
        *,
        msg_sn: str,
        device_id: str,
        device_type: int | str,
    ) -> dict[str, Any]:
        """Return the command-result payload for one message serial number."""
        return await self._misc_endpoints.query_command_result(
            msg_sn=msg_sn,
            device_id=device_id,
            device_type=device_type,
        )

    async def get_city(self) -> dict[str, Any]:
        """Return the current city capability payload."""
        return await self._misc_endpoints.get_city()

    async def query_user_cloud(self) -> dict[str, Any]:
        """Return the user-cloud capability payload."""
        return await self._misc_endpoints.query_user_cloud()

    async def query_ota_info(
        self,
        device_id: str,
        device_type: int | str,
        *,
        iot_name: str | None = None,
        allow_rich_v2_fallback: bool = False,
    ) -> list[OtaInfoRow]:
        """Return OTA metadata for one device through the explicit misc endpoint."""
        return await self._misc_endpoints.query_ota_info(
            device_id=device_id,
            device_type=device_type,
            iot_name=iot_name,
            allow_rich_v2_fallback=allow_rich_v2_fallback,
        )

    async def fetch_body_sensor_history(
        self,
        device_id: str,
        device_type: int | str,
        sensor_device_id: str,
        mesh_type: str,
    ) -> dict[str, Any]:
        """Return body-sensor history through the explicit misc endpoint."""
        return await self._misc_endpoints.fetch_body_sensor_history(
            device_id=device_id,
            device_type=device_type,
            sensor_device_id=sensor_device_id,
            mesh_type=mesh_type,
        )

    async def fetch_door_sensor_history(
        self,
        device_id: str,
        device_type: int | str,
        sensor_device_id: str,
        mesh_type: str,
    ) -> dict[str, Any]:
        """Return door-sensor history through the explicit misc endpoint."""
        return await self._misc_endpoints.fetch_door_sensor_history(
            device_id=device_id,
            device_type=device_type,
            sensor_device_id=sensor_device_id,
            mesh_type=mesh_type,
        )

    async def get_device_schedules(
        self,
        device_id: str,
        device_type: int | str,
        *,
        mesh_gateway_id: str = "",
        mesh_member_ids: list[str] | None = None,
    ) -> list[ScheduleTimingRow]:
        """Return device schedules through the explicit schedule endpoint."""
        return await self._schedule_endpoints.get_device_schedules(
            device_id=device_id,
            device_type=device_type,
            mesh_gateway_id=mesh_gateway_id,
            mesh_member_ids=mesh_member_ids,
        )

    async def add_device_schedule(
        self,
        device_id: str,
        device_type: int | str,
        days: list[int],
        times: list[int],
        events: list[int],
        *,
        mesh_gateway_id: str = "",
        mesh_member_ids: list[str] | None = None,
    ) -> list[ScheduleTimingRow]:
        """Add schedules through the explicit schedule endpoint."""
        return await self._schedule_endpoints.add_device_schedule(
            device_id=device_id,
            device_type=device_type,
            days=days,
            times=times,
            events=events,
            mesh_gateway_id=mesh_gateway_id,
            mesh_member_ids=mesh_member_ids,
        )

    async def delete_device_schedules(
        self,
        device_id: str,
        device_type: int | str,
        schedule_ids: list[int],
        *,
        mesh_gateway_id: str = "",
        mesh_member_ids: list[str] | None = None,
    ) -> list[ScheduleTimingRow]:
        """Delete schedules through the explicit schedule endpoint."""
        return await self._schedule_endpoints.delete_device_schedules(
            device_id=device_id,
            device_type=device_type,
            schedule_ids=schedule_ids,
            mesh_gateway_id=mesh_gateway_id,
            mesh_member_ids=mesh_member_ids,
        )

    def _is_mesh_group_id(self, device_id: str) -> bool:
        """Return whether the given identifier is a mesh-group id."""
        return self._schedule_endpoints._is_mesh_group_id(device_id)  # noqa: SLF001

    def _require_mesh_schedule_candidate_ids(
        self,
        *,
        device_id: str,
        mesh_gateway_id: str,
        mesh_member_ids: list[str] | None,
    ) -> list[str]:
        """Resolve candidate ids for mesh-schedule operations."""
        return self._schedule_endpoints._require_mesh_schedule_candidate_ids(  # noqa: SLF001
            device_id=device_id,
            mesh_gateway_id=mesh_gateway_id,
            mesh_member_ids=mesh_member_ids,
        )

    async def _get_mesh_schedules_by_candidates(
        self,
        candidate_device_ids: list[str],
    ) -> list[ScheduleTimingRow]:
        """Return mesh schedules aggregated from candidate devices."""
        return await self._schedule_endpoints._get_mesh_schedules_by_candidates(  # noqa: SLF001
            candidate_device_ids
        )

    async def _request_schedule_timings(
        self,
        path: str,
        body: dict[str, object],
    ) -> list[ScheduleTimingRow]:
        """Execute one schedule timing request through the explicit schedule endpoint."""
        return await self._schedule_endpoints._request_schedule_timings(path, body)  # noqa: SLF001

    async def _add_mesh_schedule_by_candidates(
        self,
        candidate_device_ids: list[str],
        *,
        days: list[int],
        times: list[int],
        events: list[int],
    ) -> list[ScheduleTimingRow]:
        """Add mesh schedules across candidate devices."""
        return await self._schedule_endpoints._add_mesh_schedule_by_candidates(  # noqa: SLF001
            candidate_device_ids,
            days=days,
            times=times,
            events=events,
        )

    async def _delete_mesh_schedules_by_candidates(
        self,
        candidate_device_ids: list[str],
        *,
        schedule_ids: list[int],
    ) -> list[ScheduleTimingRow]:
        """Delete mesh schedules across candidate devices."""
        return await self._schedule_endpoints._delete_mesh_schedules_by_candidates(  # noqa: SLF001
            candidate_device_ids,
            schedule_ids=schedule_ids,
        )



__all__ = ["LiproRestFacade"]
