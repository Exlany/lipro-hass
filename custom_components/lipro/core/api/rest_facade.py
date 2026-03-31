"""Lipro REST protocol child façade under the unified protocol root."""

from __future__ import annotations

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
from .request_gateway import RestRequestGateway
from .request_policy import RequestPolicy
from .session_state import RestSessionState
from .transport_executor import RestTransportExecutor
from .types import JsonObject, JsonValue

_LOGGER = logging.getLogger(__name__)
TokenRefreshCallback = Callable[[], Awaitable[None]]
_MappingPayloadT = TypeVar("_MappingPayloadT")


def _session_state_property(
    attr: str,
    *,
    doc: str | None = None,
    sync_setter: str | None = None,
    readonly: bool = False,
) -> property:
    """Build one `LiproRestFacade` property bound to `_session_state`."""

    def _getter(owner: object) -> object:
        return getattr(owner._session_state, attr)  # noqa: SLF001

    if readonly:
        return property(_getter, doc=doc)

    def _setter(owner: object, value: object) -> None:
        if sync_setter is None:
            setattr(owner._session_state, attr, value)  # noqa: SLF001
            return
        getattr(owner._transport_executor, sync_setter)(value)  # noqa: SLF001

    return property(_getter, _setter, doc=doc)


def _component_method(component_name: str, method_name: str):
    """Create one explicit façade method backed by a composed collaborator."""

    def _method(owner: object, *args: object, **kwargs: object) -> object:
        return getattr(getattr(owner, component_name), method_name)(*args, **kwargs)

    _method.__name__ = method_name
    return _method


def _component_async_method(component_name: str, method_name: str):
    """Create one explicit async façade method backed by a composed collaborator."""

    async def _method(owner: object, *args: object, **kwargs: object) -> object:
        return await getattr(getattr(owner, component_name), method_name)(*args, **kwargs)

    _method.__name__ = method_name
    return _method


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
        self._endpoint_surface = self._build_endpoint_surface()
        self._request_gateway = self._build_request_gateway()

    def _build_endpoint_surface(self) -> RestEndpointSurface:
        """Assemble endpoint collaborators behind one localized helper."""
        self._auth_endpoints = AuthEndpoints(self)
        self._device_endpoints = DeviceEndpoints(self)
        self._status_endpoints = StatusEndpoints(self)
        self._command_endpoints = CommandEndpoints(self)
        self._misc_endpoints = MiscEndpoints(self)
        self._schedule_endpoints = ScheduleEndpoints(self)
        return RestEndpointSurface(
            device_endpoints=self._device_endpoints,
            status_endpoints=self._status_endpoints,
            command_endpoints=self._command_endpoints,
            misc_endpoints=self._misc_endpoints,
            schedule_endpoints=self._schedule_endpoints,
        )

    def _build_request_gateway(self) -> RestRequestGateway:
        """Create the formal retry-aware request gateway."""
        return RestRequestGateway(self)

    phone_id = _session_state_property(
        "phone_id",
        doc="Return the phone identifier bound to this REST facade.",
        readonly=True,
    )

    session = _session_state_property(
        "session",
        doc="Return the injected aiohttp session reference.",
        sync_setter="sync_session",
    )

    request_timeout = _session_state_property(
        "request_timeout",
        doc="Return the configured request timeout in seconds.",
    )
    entry_id = _session_state_property(
        "entry_id",
        doc="Return the owning config-entry identifier when available.",
    )
    access_token = _session_state_property(
        "access_token",
        doc="Return the current access token stored in session state.",
    )
    refresh_token = _session_state_property(
        "refresh_token",
        doc="Return the current refresh token stored in session state.",
    )
    user_id = _session_state_property(
        "user_id",
        doc="Return the authenticated user identifier stored in session state.",
    )
    biz_id = _session_state_property(
        "biz_id",
        doc="Return the authenticated biz identifier stored in session state.",
    )

    @property
    def auth_api(self) -> AuthApiService:
        """Return the canonical auth collaborator for endpoint adapters."""
        return self._auth_api

    @property
    def request_policy(self) -> RequestPolicy:
        """Return the canonical retry/rate-limit policy for REST calls."""
        return self._request_policy

    refresh_lock = _session_state_property(
        "refresh_lock",
        doc="Return the shared refresh lock guarding token refresh.",
        readonly=True,
    )
    on_token_refresh = _session_state_property(
        "on_token_refresh",
        doc="Return the registered token-refresh callback.",
    )

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

    _get_session = _component_async_method("_transport_executor", "get_session")
    _smart_home_sign = _component_method("_transport_executor", "smart_home_sign")
    _iot_sign = _component_method("_transport_executor", "iot_sign")
    _get_timestamp_ms = _component_method("_transport_executor", "get_timestamp_ms")
    _execute_request = _component_async_method("_transport_executor", "execute_request")
    _execute_mapping_request_with_rate_limit = _component_async_method(
        "_transport_executor",
        "execute_mapping_request_with_rate_limit",
    )
    _build_iot_headers = _component_method("_transport_executor", "build_iot_headers")

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

    _handle_401_with_refresh = _component_async_method(
        "_auth_recovery",
        "handle_401_with_refresh",
    )

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

    _request_smart_home_mapping = _component_async_method(
        "_request_gateway",
        "request_smart_home_mapping",
    )
    _smart_home_request = _component_async_method(
        "_request_gateway",
        "smart_home_request",
    )
    _request_iot_mapping_raw = _component_async_method(
        "_request_gateway",
        "request_iot_mapping_raw",
    )
    _request_iot_mapping = _component_async_method(
        "_request_gateway",
        "request_iot_mapping",
    )
    _iot_request = _component_async_method("_request_gateway", "iot_request")
    _to_device_type_hex = _component_method(
        "_transport_executor",
        "to_device_type_hex",
    )

    @staticmethod
    def _require_mapping_response(path: str, result: object) -> JsonObject:
        return RestTransportExecutor.require_mapping_response(path, result)

    @staticmethod
    def _is_invalid_param_error_code(code: object) -> bool:
        return RestAuthRecoveryCoordinator.is_invalid_param_error_code(code)

__all__ = ["LiproRestFacade"]
