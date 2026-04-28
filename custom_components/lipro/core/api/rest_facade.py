"""Lipro REST protocol child façade under the unified protocol root."""

from __future__ import annotations

import asyncio
from collections.abc import Awaitable, Callable
import logging

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
from .rest_facade_internal_methods import (
    _build_iot_headers as _build_iot_headers_impl,
    _execute_mapping_request_with_rate_limit as _execute_mapping_request_with_rate_limit_impl,
    _execute_request as _execute_request_impl,
    _finalize_mapping_result as _finalize_mapping_result_impl,
    _get_session as _get_session_impl,
    _get_timestamp_ms as _get_timestamp_ms_impl,
    _handle_401_with_refresh as _handle_401_with_refresh_impl,
    _handle_auth_error_and_retry as _handle_auth_error_and_retry_impl,
    _iot_request as _iot_request_impl,
    _iot_sign as _iot_sign_impl,
    _is_change_state_command as _is_change_state_command_impl,
    _is_command_busy_error as _is_command_busy_error_impl,
    _is_invalid_param_error_code as _is_invalid_param_error_code_impl,
    _normalize_pacing_target as _normalize_pacing_target_impl,
    _request_iot_mapping as _request_iot_mapping_impl,
    _request_iot_mapping_raw as _request_iot_mapping_raw_impl,
    _request_smart_home_mapping as _request_smart_home_mapping_impl,
    _require_mapping_response as _require_mapping_response_impl,
    _resolve_error_code as _resolve_error_code_impl,
    _smart_home_request as _smart_home_request_impl,
    _smart_home_sign as _smart_home_sign_impl,
    _to_device_type_hex as _to_device_type_hex_impl,
    _unwrap_iot_success_payload as _unwrap_iot_success_payload_impl,
    close as _close_impl,
)
from .session_state import RestSessionState
from .transport_executor import RestTransportExecutor

_LOGGER = logging.getLogger(__name__)
TokenRefreshCallback = Callable[[], Awaitable[None]]


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

    @property
    def phone_id(self) -> str:
        """Return the phone identifier bound to this REST facade."""
        return self._session_state.phone_id

    @property
    def session(self) -> aiohttp.ClientSession | None:
        """Return the injected aiohttp session reference."""
        return self._session_state.session

    @session.setter
    def session(self, session: aiohttp.ClientSession | None) -> None:
        self._transport_executor.sync_session(session)

    @property
    def request_timeout(self) -> int:
        """Return the configured request timeout in seconds."""
        return self._session_state.request_timeout

    @request_timeout.setter
    def request_timeout(self, request_timeout: int) -> None:
        self._session_state.request_timeout = request_timeout

    @property
    def entry_id(self) -> str | None:
        """Return the owning config-entry identifier when available."""
        return self._session_state.entry_id

    @entry_id.setter
    def entry_id(self, entry_id: str | None) -> None:
        self._session_state.entry_id = entry_id

    @property
    def access_token(self) -> str | None:
        """Return the current access token stored in session state."""
        return self._session_state.access_token

    @access_token.setter
    def access_token(self, access_token: str | None) -> None:
        self._session_state.access_token = access_token

    @property
    def refresh_token(self) -> str | None:
        """Return the current refresh token stored in session state."""
        return self._session_state.refresh_token

    @refresh_token.setter
    def refresh_token(self, refresh_token: str | None) -> None:
        self._session_state.refresh_token = refresh_token

    @property
    def user_id(self) -> int | None:
        """Return the authenticated user identifier stored in session state."""
        return self._session_state.user_id

    @user_id.setter
    def user_id(self, user_id: int | None) -> None:
        self._session_state.user_id = user_id

    @property
    def biz_id(self) -> str | None:
        """Return the authenticated biz identifier stored in session state."""
        return self._session_state.biz_id

    @biz_id.setter
    def biz_id(self, biz_id: str | None) -> None:
        self._session_state.biz_id = biz_id

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
    def on_token_refresh(self, callback: TokenRefreshCallback | None) -> None:
        self._session_state.on_token_refresh = callback

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
    execute_mapping_request_with_rate_limit = (
        _request_methods.execute_mapping_request_with_rate_limit
    )
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
    unwrap_iot_success_payload = staticmethod(
        _request_methods.unwrap_iot_success_payload
    )
    require_mapping_response = staticmethod(_request_methods.require_mapping_response)
    is_invalid_param_error_code = staticmethod(
        _request_methods.is_invalid_param_error_code
    )
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

    _get_session = _get_session_impl
    _smart_home_sign = _smart_home_sign_impl
    _iot_sign = _iot_sign_impl
    _get_timestamp_ms = _get_timestamp_ms_impl
    _execute_request = _execute_request_impl
    _execute_mapping_request_with_rate_limit = (
        _execute_mapping_request_with_rate_limit_impl
    )
    _build_iot_headers = _build_iot_headers_impl
    _handle_auth_error_and_retry = _handle_auth_error_and_retry_impl
    _finalize_mapping_result = _finalize_mapping_result_impl
    _handle_401_with_refresh = _handle_401_with_refresh_impl
    _resolve_error_code = staticmethod(_resolve_error_code_impl)
    _unwrap_iot_success_payload = staticmethod(_unwrap_iot_success_payload_impl)
    _is_command_busy_error = staticmethod(_is_command_busy_error_impl)
    _is_change_state_command = staticmethod(_is_change_state_command_impl)
    _normalize_pacing_target = staticmethod(_normalize_pacing_target_impl)
    close = _close_impl
    _request_smart_home_mapping = _request_smart_home_mapping_impl
    _smart_home_request = _smart_home_request_impl
    _request_iot_mapping_raw = _request_iot_mapping_raw_impl
    _request_iot_mapping = _request_iot_mapping_impl
    _iot_request = _iot_request_impl
    _to_device_type_hex = _to_device_type_hex_impl
    _require_mapping_response = staticmethod(_require_mapping_response_impl)
    _is_invalid_param_error_code = staticmethod(_is_invalid_param_error_code_impl)


__all__ = ["LiproRestFacade"]
