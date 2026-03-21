"""Unified protocol root and transport child façades."""

from __future__ import annotations

import aiohttp

from ...const.api import REQUEST_TIMEOUT
from ..api.client import LiproRestFacade
from ..api.request_policy import RequestPolicy
from ..api.session_state import RestSessionState
from . import protocol_facade_rest_methods as _rest_methods
from .contracts import CanonicalProtocolContracts
from .diagnostics_context import ProtocolDiagnosticsContext
from .mqtt_facade import (
    LiproMqttFacade,
    MqttErrorCallback,
    MqttMessageCallback,
    MqttSignalCallback,
    bind_active_protocol_mqtt_facade,
    build_protocol_diagnostics_snapshot,
)
from .rest_port import ProtocolRestPortFamily, bind_protocol_rest_port_family
from .session import ProtocolSessionState
from .telemetry import ProtocolTelemetry


class LiproProtocolFacade:
    """Unified protocol root owning shared protocol truth above child façades."""

    def __init__(
        self,
        phone_id: str,
        session: aiohttp.ClientSession | None = None,
        request_timeout: int = REQUEST_TIMEOUT,
        *,
        entry_id: str | None = None,
        session_state: RestSessionState | None = None,
        request_policy: RequestPolicy | None = None,
        rest_facade_factory: type[LiproRestFacade] = LiproRestFacade,
    ) -> None:
        """Create the unified protocol root and inject shared child collaborators."""
        rest_state = session_state or RestSessionState(
            phone_id=phone_id,
            session=session,
            request_timeout=request_timeout,
            entry_id=entry_id,
        )
        policy = request_policy or RequestPolicy()

        self._session_state = ProtocolSessionState(rest_state)
        self._request_policy = policy
        self._telemetry = ProtocolTelemetry()
        self._diagnostics_context = ProtocolDiagnosticsContext(
            session_state=self._session_state,
            telemetry=self._telemetry,
            entry_id=entry_id,
        )
        self._contracts = CanonicalProtocolContracts()
        self._rest = rest_facade_factory(
            phone_id,
            session,
            request_timeout=request_timeout,
            entry_id=entry_id,
            session_state=rest_state,
            request_policy=policy,
        )
        self._rest_ports: ProtocolRestPortFamily = bind_protocol_rest_port_family(
            self._rest
        )
        self._mqtt: LiproMqttFacade | None = None

    @property
    def rest(self) -> LiproRestFacade:
        """Return the REST child façade owned by this protocol root."""
        return self._rest

    @property
    def mqtt(self) -> LiproMqttFacade | None:
        """Return the currently attached MQTT child façade when available."""
        return self._mqtt

    @property
    def phone_id(self) -> str:
        """Return the canonical phone identifier for this protocol root."""
        return self._session_state.phone_id

    @property
    def entry_id(self) -> str | None:
        """Return the owning config-entry identifier when available."""
        return self._session_state.entry_id

    @property
    def session(self) -> aiohttp.ClientSession | None:
        """Expose the underlying aiohttp session for formal child surfaces."""
        return self._session_state.session

    @property
    def request_timeout(self) -> int:
        """Return the protocol request-timeout policy."""
        return self._session_state.request_timeout

    @property
    def access_token(self) -> str | None:
        """Return the current protocol access token."""
        return self._session_state.access_token

    @access_token.setter
    def access_token(self, value: str | None) -> None:
        self._session_state.access_token = value

    @property
    def refresh_token(self) -> str | None:
        """Return the current protocol refresh token."""
        return self._session_state.refresh_token

    @refresh_token.setter
    def refresh_token(self, value: str | None) -> None:
        self._session_state.refresh_token = value

    @property
    def user_id(self) -> int | None:
        """Return the authenticated user identifier when present."""
        return self._session_state.user_id

    @user_id.setter
    def user_id(self, value: int | None) -> None:
        self._session_state.user_id = value

    @property
    def biz_id(self) -> str | None:
        """Return the canonical biz-id view shared across child façades."""
        return self._session_state.biz_id

    @biz_id.setter
    def biz_id(self, value: str | None) -> None:
        self._session_state.biz_id = value

    @property
    def session_state(self) -> ProtocolSessionState:
        """Return the shared protocol session state."""
        return self._session_state

    @property
    def protocol_session_state(self) -> ProtocolSessionState:
        """Alias the shared protocol session state for explicit callers."""
        return self._session_state

    @property
    def request_policy(self) -> RequestPolicy:
        """Return the canonical request policy shared with the REST child façade."""
        return self._request_policy

    @property
    def telemetry(self) -> ProtocolTelemetry:
        """Return the shared protocol telemetry owned by the root."""
        return self._telemetry

    @property
    def diagnostics_context(self) -> ProtocolDiagnosticsContext:
        """Return the protocol-owned diagnostics context."""
        return self._diagnostics_context

    @property
    def contracts(self) -> CanonicalProtocolContracts:
        """Return the canonical contract helpers owned by the protocol root."""
        return self._contracts

    set_tokens = _rest_methods.set_tokens
    set_token_refresh_callback = _rest_methods.set_token_refresh_callback
    login = _rest_methods.login
    refresh_access_token = _rest_methods.refresh_access_token
    get_devices = _rest_methods.get_devices
    get_product_configs = _rest_methods.get_product_configs
    query_device_status = _rest_methods.query_device_status
    query_mesh_group_status = _rest_methods.query_mesh_group_status
    query_connect_status = _rest_methods.query_connect_status
    send_command = _rest_methods.send_command
    send_group_command = _rest_methods.send_group_command
    get_mqtt_config = _rest_methods.get_mqtt_config
    fetch_outlet_power_info = _rest_methods.fetch_outlet_power_info
    query_command_result = _rest_methods.query_command_result
    get_city = _rest_methods.get_city
    query_user_cloud = _rest_methods.query_user_cloud
    query_ota_info = _rest_methods.query_ota_info
    fetch_body_sensor_history = _rest_methods.fetch_body_sensor_history
    fetch_door_sensor_history = _rest_methods.fetch_door_sensor_history
    get_device_schedules = _rest_methods.get_device_schedules
    add_device_schedule = _rest_methods.add_device_schedule
    delete_device_schedules = _rest_methods.delete_device_schedules

    def _bind_active_mqtt_facade(self, mqtt_facade: LiproMqttFacade | None) -> None:
        """Bind one MQTT child façade and synchronize shared protocol state."""
        self._mqtt = bind_active_protocol_mqtt_facade(self._session_state, mqtt_facade)

    def _build_protocol_diagnostics_snapshot(self) -> dict[str, object]:
        """Build one root-owned diagnostics snapshot from active child state."""
        return build_protocol_diagnostics_snapshot(
            diagnostics_context=self._diagnostics_context,
            mqtt_facade=self._mqtt,
            auth_recovery=self._rest_ports.diagnostics.auth_recovery_telemetry_snapshot(),
        )

    def attach_mqtt_facade(self, mqtt_facade: LiproMqttFacade | None) -> None:
        """Attach or clear the active MQTT child façade."""
        self._bind_active_mqtt_facade(mqtt_facade)

    def build_mqtt_facade(
        self,
        *,
        access_key: str,
        secret_key: str,
        biz_id: str,
        phone_id: str,
        on_message: MqttMessageCallback | None = None,
        on_connect: MqttSignalCallback | None = None,
        on_disconnect: MqttSignalCallback | None = None,
        on_error: MqttErrorCallback | None = None,
    ) -> LiproMqttFacade:
        """Build and register the active MQTT child façade."""
        mqtt_facade = LiproMqttFacade.from_credentials(
            access_key=access_key,
            secret_key=secret_key,
            biz_id=biz_id,
            phone_id=phone_id,
            session_state=self._session_state,
            telemetry=self._telemetry,
            diagnostics_context=self._diagnostics_context,
            on_message=on_message,
            on_connect=on_connect,
            on_disconnect=on_disconnect,
            on_error=on_error,
        )
        self._bind_active_mqtt_facade(mqtt_facade)
        return mqtt_facade

    def protocol_diagnostics_snapshot(self) -> dict[str, object]:
        """Return one root-owned diagnostics snapshot."""
        return self._build_protocol_diagnostics_snapshot()


__all__ = ["LiproMqttFacade", "LiproProtocolFacade"]
