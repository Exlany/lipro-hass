"""Lipro REST protocol child façade under the unified protocol root."""

from __future__ import annotations

import asyncio
from collections.abc import Awaitable, Callable
import logging
from typing import Any, TypeVar

import aiohttp

from ...const.api import REQUEST_TIMEOUT
from .auth_service import AuthApiService
from .client_auth_recovery import AuthRecoveryCoordinator
from .client_base import ClientSessionState
from .client_endpoint_surface import ClientEndpointSurface
from .client_request_gateway import ClientRequestGateway
from .client_transport import TransportExecutor
from .endpoints import (
    AuthEndpoints,
    CommandEndpoints,
    DeviceEndpoints,
    MiscEndpoints,
    ScheduleEndpoints,
    StatusEndpoints,
)
from .errors import LiproAuthError
from .power_service import OutletPowerInfoResult
from .request_policy import RequestPolicy
from .types import DeviceListResponse, LoginResponse, OtaInfoRow, ScheduleTimingRow

_LOGGER = logging.getLogger(__name__)
MappingRequestSender = Callable[[], Awaitable[tuple[int, Any, dict[str, str], str | None]]]
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
        self._auth_recovery = AuthRecoveryCoordinator(self._session_state)
        self._transport_executor = TransportExecutor(
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
        self._request_gateway = ClientRequestGateway(self)
        self._endpoint_surface = ClientEndpointSurface(self)

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
    def biz_id(self) -> str | None:
        """Return the authenticated biz identifier stored in session state."""
        return self._session_state.biz_id

    @biz_id.setter
    def biz_id(self, value: str | None) -> None:
        self._session_state.biz_id = value

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
        return dict(self._auth_recovery.telemetry_snapshot())

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

    @staticmethod
    def _resolve_error_code(code: Any, error_code: Any) -> int | str | None:
        return AuthRecoveryCoordinator.resolve_error_code(code, error_code)

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
        return await self._request_gateway.request_smart_home_mapping(
            path,
            data,
            require_auth=require_auth,
            retry_count=retry_count,
        )

    async def _smart_home_request(
        self,
        path: str,
        data: dict[str, Any],
        require_auth: bool = True,
        is_retry: bool = False,
        retry_count: int = 0,
    ) -> Any:
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
    ) -> tuple[dict[str, Any], str | None]:
        return await self._request_gateway.request_iot_mapping_raw(
            path,
            body,
            is_retry=is_retry,
            retry_count=retry_count,
        )

    async def _request_iot_mapping(
        self,
        path: str,
        body_data: dict[str, Any],
        *,
        is_retry: bool = False,
        retry_count: int = 0,
    ) -> tuple[dict[str, Any], str | None]:
        return await self._request_gateway.request_iot_mapping(
            path,
            body_data,
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
        return await self._request_gateway.iot_request(
            path,
            body_data,
            is_retry=is_retry,
            retry_count=retry_count,
        )

    def _to_device_type_hex(self, device_type: int | str) -> str:
        return self._transport_executor.to_device_type_hex(device_type)

    @staticmethod
    def _require_mapping_response(path: str, result: Any) -> dict[str, Any]:
        return TransportExecutor.require_mapping_response(path, result)

    @staticmethod
    def _is_invalid_param_error_code(code: Any) -> bool:
        return AuthRecoveryCoordinator.is_invalid_param_error_code(code)

    async def smart_home_request(
        self,
        path: str,
        data: dict[str, Any],
        require_auth: bool = True,
        is_retry: bool = False,
        retry_count: int = 0,
    ) -> Any:
        """Execute one Smart Home request through the formal transport pipeline."""
        if require_auth is True and not is_retry and not retry_count:
            return await self._smart_home_request(path, data)
        return await self._smart_home_request(
            path,
            data,
            require_auth=require_auth,
            is_retry=is_retry,
            retry_count=retry_count,
        )

    async def iot_request(
        self,
        path: str,
        body_data: dict[str, Any],
        is_retry: bool = False,
        retry_count: int = 0,
    ) -> Any:
        """Execute one IoT request through the formal transport pipeline."""
        if not is_retry and not retry_count:
            return await self._iot_request(path, body_data)
        return await self._iot_request(
            path,
            body_data,
            is_retry=is_retry,
            retry_count=retry_count,
        )

    async def request_iot_mapping(
        self,
        path: str,
        body_data: dict[str, Any],
        *,
        is_retry: bool = False,
        retry_count: int = 0,
    ) -> tuple[dict[str, Any], str | None]:
        """Request one IoT mapping payload with retry context preserved."""
        if not is_retry and not retry_count:
            return await self._request_iot_mapping(path, body_data)
        return await self._request_iot_mapping(
            path,
            body_data,
            is_retry=is_retry,
            retry_count=retry_count,
        )

    async def request_iot_mapping_raw(
        self,
        path: str,
        body: str,
        *,
        is_retry: bool = False,
        retry_count: int = 0,
    ) -> tuple[dict[str, Any], str | None]:
        """Request one raw IoT mapping payload without result finalization."""
        if not is_retry and not retry_count:
            return await self._request_iot_mapping_raw(path, body)
        return await self._request_iot_mapping_raw(
            path,
            body,
            is_retry=is_retry,
            retry_count=retry_count,
        )

    async def iot_request_with_busy_retry(
        self,
        path: str,
        body_data: dict[str, Any],
        *,
        target_id: str,
        command: str,
    ) -> dict[str, Any]:
        """Execute one IoT command with the formal busy-retry policy."""
        result = await self._request_policy.iot_request_with_busy_retry(
            path,
            body_data,
            target_id=target_id,
            command=command,
            iot_request=self._iot_request,
            logger=_LOGGER,
        )
        return dict(result)

    def to_device_type_hex(self, device_type: int | str) -> str:
        """Normalize one device type into the transport hex representation."""
        return self._to_device_type_hex(device_type)

    @staticmethod
    def is_success_code(code: Any) -> bool:
        """Return whether one vendor response code represents success."""
        return AuthRecoveryCoordinator.is_success_code(code)

    @staticmethod
    def unwrap_iot_success_payload(result: dict[str, Any]) -> Any:
        """Extract the canonical success payload from one IoT response."""
        return AuthRecoveryCoordinator.unwrap_iot_success_payload(result)

    @staticmethod
    def require_mapping_response(path: str, result: Any) -> dict[str, Any]:
        """Require one mapping response payload to be a JSON object."""
        return TransportExecutor.require_mapping_response(path, result)

    @staticmethod
    def is_invalid_param_error_code(code: Any) -> bool:
        """Return whether one response code indicates an invalid-parameter error."""
        return AuthRecoveryCoordinator.is_invalid_param_error_code(code)

    async def get_devices(self, offset: int = 0, limit: int = 100) -> DeviceListResponse:
        """Return canonical device rows through the explicit device endpoint."""
        return await self._endpoint_surface.get_devices(offset=offset, limit=limit)

    async def get_product_configs(self) -> list[dict[str, Any]]:
        """Return canonical product configuration rows."""
        return await self._endpoint_surface.get_product_configs()

    async def query_device_status(
        self,
        device_ids: list[str],
        *,
        max_devices_per_query: int = 100,
        on_batch_metric: Any = None,
    ) -> list[dict[str, Any]]:
        """Return canonical device-status rows through the explicit status endpoint."""
        return await self._endpoint_surface.query_device_status(
            device_ids,
            max_devices_per_query=max_devices_per_query,
            on_batch_metric=on_batch_metric,
        )

    async def query_mesh_group_status(
        self,
        group_ids: list[str],
    ) -> list[dict[str, Any]]:
        """Return canonical mesh-group status rows."""
        return await self._endpoint_surface.query_mesh_group_status(group_ids)

    async def query_connect_status(self, device_ids: list[str]) -> dict[str, bool]:
        """Return connectivity status for the requested devices."""
        return await self._endpoint_surface.query_connect_status(device_ids)

    async def send_command(
        self,
        device_id: str,
        command: str,
        device_type: int | str,
        properties: list[dict[str, str]] | None = None,
        iot_name: str = "",
    ) -> dict[str, Any]:
        """Send one device command through the explicit command endpoint."""
        return await self._endpoint_surface.send_command(
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
        return await self._endpoint_surface.send_group_command(
            group_id=group_id,
            command=command,
            device_type=device_type,
            properties=properties,
            iot_name=iot_name,
        )

    async def get_mqtt_config(self) -> dict[str, Any]:
        """Return MQTT configuration through the explicit misc endpoint."""
        return await self._endpoint_surface.get_mqtt_config()

    async def fetch_outlet_power_info(self, device_id: str) -> OutletPowerInfoResult:
        """Return outlet power information for one device."""
        return await self._endpoint_surface.fetch_outlet_power_info(device_id)

    async def query_command_result(
        self,
        *,
        msg_sn: str,
        device_id: str,
        device_type: int | str,
    ) -> dict[str, Any]:
        """Return the command-result payload for one message serial number."""
        return await self._endpoint_surface.query_command_result(
            msg_sn=msg_sn,
            device_id=device_id,
            device_type=device_type,
        )

    async def get_city(self) -> dict[str, Any]:
        """Return the current city capability payload."""
        return await self._endpoint_surface.get_city()

    async def query_user_cloud(self) -> dict[str, Any]:
        """Return the user-cloud capability payload."""
        return await self._endpoint_surface.query_user_cloud()

    async def query_ota_info(
        self,
        device_id: str,
        device_type: int | str,
        *,
        iot_name: str | None = None,
        allow_rich_v2_fallback: bool = False,
    ) -> list[OtaInfoRow]:
        """Return OTA metadata for one device through the explicit misc endpoint."""
        return await self._endpoint_surface.query_ota_info(
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
        return await self._endpoint_surface.fetch_body_sensor_history(
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
        return await self._endpoint_surface.fetch_door_sensor_history(
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
        return await self._endpoint_surface.get_device_schedules(
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
        return await self._endpoint_surface.add_device_schedule(
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
        return await self._endpoint_surface.delete_device_schedules(
            device_id=device_id,
            device_type=device_type,
            schedule_ids=schedule_ids,
            mesh_gateway_id=mesh_gateway_id,
            mesh_member_ids=mesh_member_ids,
        )


__all__ = ["LiproRestFacade"]
