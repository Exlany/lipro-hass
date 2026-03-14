"""Unified protocol root and transport child façades."""

from __future__ import annotations

from collections.abc import Awaitable, Callable
from typing import Any, Protocol, cast

import aiohttp

from ...const.api import REQUEST_TIMEOUT
from ..api.client import LiproRestFacade
from ..api.client_base import ClientSessionState
from ..api.request_policy import RequestPolicy
from ..api.types import DeviceListResponse, LoginResponse, OtaInfoRow, ScheduleTimingRow
from ..mqtt.mqtt_client import LiproMqttClient
from .contracts import CanonicalProtocolContracts
from .diagnostics_context import ProtocolDiagnosticsContext
from .session import ProtocolSessionState
from .telemetry import ProtocolTelemetry

MqttMessageCallback = Callable[[str, dict[str, Any]], None]
MqttSignalCallback = Callable[[], None]
MqttErrorCallback = Callable[[Exception], None]
TokenRefreshCallback = Callable[[], Awaitable[None]]


class _RestFacadePort(Protocol):
    def set_tokens(
        self,
        access_token: str,
        refresh_token: str,
        user_id: int | None = None,
        biz_id: str | None = None,
    ) -> None: ...

    def set_token_refresh_callback(self, callback: TokenRefreshCallback) -> None: ...

    async def login(
        self,
        phone: str,
        password: str,
        *,
        password_is_hashed: bool = False,
    ) -> LoginResponse: ...

    async def refresh_access_token(self) -> LoginResponse: ...
    async def get_devices(self, offset: int = 0, limit: int = 100) -> DeviceListResponse: ...
    async def get_product_configs(self) -> list[dict[str, Any]]: ...
    async def query_device_status(
        self,
        device_ids: list[str],
        *,
        max_devices_per_query: int = 100,
        on_batch_metric: Any = None,
    ) -> list[dict[str, Any]]: ...
    async def query_mesh_group_status(self, group_ids: list[str]) -> list[dict[str, Any]]: ...
    async def query_connect_status(self, device_ids: list[str]) -> dict[str, bool]: ...
    async def send_command(
        self,
        device_id: str,
        command: str,
        device_type: int | str,
        properties: list[dict[str, str]] | None = None,
        iot_name: str = "",
    ) -> dict[str, Any]: ...
    async def send_group_command(
        self,
        group_id: str,
        command: str,
        device_type: int | str,
        properties: list[dict[str, str]] | None = None,
        iot_name: str = "",
    ) -> dict[str, Any]: ...
    async def get_mqtt_config(self) -> dict[str, Any]: ...
    async def fetch_outlet_power_info(self, device_id: str) -> dict[str, Any]: ...
    async def query_command_result(
        self,
        *,
        msg_sn: str,
        device_id: str,
        device_type: int | str,
    ) -> dict[str, Any]: ...
    async def get_city(self) -> dict[str, Any]: ...
    async def query_user_cloud(self) -> dict[str, Any]: ...
    async def query_ota_info(
        self,
        device_id: str,
        device_type: int | str,
        *,
        iot_name: str | None = None,
        allow_rich_v2_fallback: bool = False,
    ) -> list[OtaInfoRow]: ...
    async def fetch_body_sensor_history(
        self,
        device_id: str,
        device_type: int | str,
        sensor_device_id: str,
        mesh_type: str,
    ) -> dict[str, Any]: ...
    async def fetch_door_sensor_history(
        self,
        device_id: str,
        device_type: int | str,
        sensor_device_id: str,
        mesh_type: str,
    ) -> dict[str, Any]: ...
    async def get_device_schedules(
        self,
        device_id: str,
        device_type: int | str,
        *,
        mesh_gateway_id: str = "",
        mesh_member_ids: list[str] | None = None,
    ) -> list[ScheduleTimingRow]: ...
    async def add_device_schedule(
        self,
        device_id: str,
        device_type: int | str,
        days: list[int],
        times: list[int],
        events: list[int],
        group_id: str = "",
        *,
        mesh_gateway_id: str = "",
        mesh_member_ids: list[str] | None = None,
    ) -> list[ScheduleTimingRow]: ...
    async def delete_device_schedules(
        self,
        device_id: str,
        device_type: int | str,
        schedule_ids: list[int],
        group_id: str = "",
        *,
        mesh_gateway_id: str = "",
        mesh_member_ids: list[str] | None = None,
    ) -> list[ScheduleTimingRow]: ...

    def auth_recovery_telemetry_snapshot(self) -> dict[str, Any]: ...


class LiproMqttFacade:
    """Protocol child façade wrapping the concrete MQTT transport client."""

    def __init__(
        self,
        client: LiproMqttClient,
        *,
        session_state: ProtocolSessionState,
        telemetry: ProtocolTelemetry,
        diagnostics_context: ProtocolDiagnosticsContext,
    ) -> None:
        """Bind one concrete MQTT transport client to protocol-root shared truth."""
        self._client = client
        self._session_state = session_state
        self._telemetry = telemetry
        self._diagnostics_context = diagnostics_context
        self._telemetry.record_mqtt_facade_created()

    @classmethod
    def from_credentials(
        cls,
        *,
        access_key: str,
        secret_key: str,
        biz_id: str,
        phone_id: str,
        session_state: ProtocolSessionState,
        telemetry: ProtocolTelemetry,
        diagnostics_context: ProtocolDiagnosticsContext,
        on_message: MqttMessageCallback | None = None,
        on_connect: MqttSignalCallback | None = None,
        on_disconnect: MqttSignalCallback | None = None,
        on_error: MqttErrorCallback | None = None,
    ) -> LiproMqttFacade:
        """Build one MQTT child façade bound to the protocol root state."""
        session_state.bind_mqtt_biz_id(biz_id)
        return cls(
            LiproMqttClient(
                access_key=access_key,
                secret_key=secret_key,
                biz_id=biz_id,
                phone_id=phone_id,
                on_message=on_message,
                on_connect=on_connect,
                on_disconnect=on_disconnect,
                on_error=on_error,
            ),
            session_state=session_state,
            telemetry=telemetry,
            diagnostics_context=diagnostics_context,
        )

    @property
    def protocol_session_state(self) -> ProtocolSessionState:
        """Return the shared protocol session view bound to this child façade."""
        return self._session_state

    @property
    def telemetry(self) -> ProtocolTelemetry:
        """Return the shared protocol telemetry owned by the root."""
        return self._telemetry

    @property
    def diagnostics_context(self) -> ProtocolDiagnosticsContext:
        """Return the protocol-owned diagnostics context."""
        return self._diagnostics_context

    @property
    def is_connected(self) -> bool:
        """Return whether the underlying MQTT transport is connected."""
        return self._client.is_connected

    @property
    def subscribed_devices(self) -> set[str]:
        """Return the active subscribed-device identifiers."""
        return self._client.subscribed_devices

    @property
    def subscribed_count(self) -> int:
        """Return the number of tracked MQTT subscriptions."""
        return self._client.subscribed_count

    @property
    def last_error(self) -> Exception | None:
        """Return the latest transport error while syncing telemetry."""
        err = self._client.last_error
        if err is not None:
            self._telemetry.record_mqtt_error(err)
        return err

    async def start(self, device_ids: list[str]) -> None:
        """Start the wrapped MQTT transport and record telemetry."""
        self._telemetry.record_mqtt_start()
        try:
            await self._client.start(device_ids)
        except Exception as err:
            self._telemetry.record_mqtt_error(err)
            raise

    async def stop(self) -> None:
        """Stop the wrapped MQTT transport and record telemetry."""
        self._telemetry.record_mqtt_stop()
        try:
            await self._client.stop()
        except Exception as err:
            self._telemetry.record_mqtt_error(err)
            raise

    async def sync_subscriptions(self, device_ids: set[str]) -> None:
        """Sync subscriptions through the wrapped transport and record telemetry."""
        self._telemetry.record_mqtt_sync()
        try:
            await self._client.sync_subscriptions(device_ids)
        except Exception as err:
            self._telemetry.record_mqtt_error(err)
            raise

    async def wait_until_connected(self, timeout: float | None = None) -> bool:
        """Wait until the wrapped transport reports a real broker connection."""
        try:
            connected = await self._client.wait_until_connected(timeout=timeout)
        except Exception as err:
            self._telemetry.record_mqtt_error(err)
            raise
        if self._client.last_error is not None:
            self._telemetry.record_mqtt_error(self._client.last_error)
        return connected


class LiproProtocolFacade:
    """Unified protocol root owning shared protocol truth above child façades."""

    def __init__(
        self,
        phone_id: str,
        session: aiohttp.ClientSession | None = None,
        request_timeout: int = REQUEST_TIMEOUT,
        *,
        entry_id: str | None = None,
        session_state: ClientSessionState | None = None,
        request_policy: RequestPolicy | None = None,
        rest_facade_factory: type[LiproRestFacade] = LiproRestFacade,
    ) -> None:
        """Create the unified protocol root and inject shared child collaborators."""
        rest_state = session_state or ClientSessionState(
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
        self._rest_port = cast(_RestFacadePort, self._rest)
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
        return cast(aiohttp.ClientSession | None, self._session_state.session)

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

    def set_tokens(
        self,
        access_token: str,
        refresh_token: str,
        user_id: int | None = None,
        biz_id: str | None = None,
    ) -> None:
        """Set protocol tokens through the formal REST child façade."""
        self._rest_port.set_tokens(
            access_token,
            refresh_token,
            user_id=user_id,
            biz_id=biz_id,
        )

    def set_token_refresh_callback(self, callback: TokenRefreshCallback) -> None:
        """Register one token-refresh callback on the formal REST child façade."""
        self._rest_port.set_token_refresh_callback(callback)

    async def login(
        self,
        phone: str,
        password: str,
        *,
        password_is_hashed: bool = False,
    ) -> LoginResponse:
        """Run the formal login call through the REST child façade."""
        return await self._rest_port.login(
            phone,
            password,
            password_is_hashed=password_is_hashed,
        )

    async def refresh_access_token(self) -> LoginResponse:
        """Refresh access token through the REST child façade."""
        return await self._rest_port.refresh_access_token()

    async def get_devices(self, offset: int = 0, limit: int = 100) -> DeviceListResponse:
        """Return canonical device rows from the REST child façade."""
        return await self._rest_port.get_devices(offset=offset, limit=limit)

    async def get_product_configs(self) -> list[dict[str, Any]]:
        """Return canonical product-configuration rows."""
        return await self._rest_port.get_product_configs()

    async def query_device_status(
        self,
        device_ids: list[str],
        *,
        max_devices_per_query: int = 100,
        on_batch_metric: Any = None,
    ) -> list[dict[str, Any]]:
        """Query device status through the REST child façade."""
        return await self._rest_port.query_device_status(
            device_ids,
            max_devices_per_query=max_devices_per_query,
            on_batch_metric=on_batch_metric,
        )

    async def query_mesh_group_status(
        self,
        group_ids: list[str],
    ) -> list[dict[str, Any]]:
        """Query mesh-group status through the REST child façade."""
        return await self._rest_port.query_mesh_group_status(group_ids)

    async def query_connect_status(self, device_ids: list[str]) -> dict[str, bool]:
        """Query device connectivity through the REST child façade."""
        return await self._rest_port.query_connect_status(device_ids)

    async def send_command(
        self,
        device_id: str,
        command: str,
        device_type: int | str,
        properties: list[dict[str, str]] | None = None,
        iot_name: str = "",
    ) -> dict[str, Any]:
        """Send one device command through the REST child façade."""
        return await self._rest_port.send_command(
            device_id,
            command,
            device_type,
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
        """Send one group command through the REST child façade."""
        return await self._rest_port.send_group_command(
            group_id,
            command,
            device_type,
            properties=properties,
            iot_name=iot_name,
        )

    async def get_mqtt_config(self) -> dict[str, Any]:
        """Fetch MQTT credentials through the REST child façade."""
        return await self._rest_port.get_mqtt_config()

    async def fetch_outlet_power_info(self, device_id: str) -> dict[str, Any]:
        """Fetch outlet power info through the REST child façade."""
        return await self._rest_port.fetch_outlet_power_info(device_id)

    async def query_command_result(
        self,
        *,
        msg_sn: str,
        device_id: str,
        device_type: int | str,
    ) -> dict[str, Any]:
        """Query one command-result payload through the REST child façade."""
        return await self._rest_port.query_command_result(
            msg_sn=msg_sn,
            device_id=device_id,
            device_type=device_type,
        )

    async def get_city(self) -> dict[str, Any]:
        """Fetch city metadata through the REST child façade."""
        return await self._rest_port.get_city()

    async def query_user_cloud(self) -> dict[str, Any]:
        """Fetch user-cloud diagnostics through the REST child façade."""
        return await self._rest_port.query_user_cloud()

    async def query_ota_info(
        self,
        device_id: str,
        device_type: int | str,
        *,
        iot_name: str | None = None,
        allow_rich_v2_fallback: bool = False,
    ) -> list[OtaInfoRow]:
        """Fetch OTA info through the REST child façade."""
        return await self._rest_port.query_ota_info(
            device_id,
            device_type,
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
        """Fetch body-sensor history through the REST child façade."""
        return await self._rest_port.fetch_body_sensor_history(
            device_id,
            device_type,
            sensor_device_id,
            mesh_type,
        )

    async def fetch_door_sensor_history(
        self,
        device_id: str,
        device_type: int | str,
        sensor_device_id: str,
        mesh_type: str,
    ) -> dict[str, Any]:
        """Fetch door-sensor history through the REST child façade."""
        return await self._rest_port.fetch_door_sensor_history(
            device_id,
            device_type,
            sensor_device_id,
            mesh_type,
        )

    async def get_device_schedules(
        self,
        device_id: str,
        device_type: int | str,
        *,
        mesh_gateway_id: str = "",
        mesh_member_ids: list[str] | None = None,
    ) -> list[ScheduleTimingRow]:
        """Fetch device schedules through the REST child façade."""
        return await self._rest_port.get_device_schedules(
            device_id,
            device_type,
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
        group_id: str = "",
        *,
        mesh_gateway_id: str = "",
        mesh_member_ids: list[str] | None = None,
    ) -> list[ScheduleTimingRow]:
        """Add one device schedule through the REST child façade."""
        return await self._rest_port.add_device_schedule(
            device_id,
            device_type,
            days,
            times,
            events,
            group_id,
            mesh_gateway_id=mesh_gateway_id,
            mesh_member_ids=mesh_member_ids,
        )

    async def delete_device_schedules(
        self,
        device_id: str,
        device_type: int | str,
        schedule_ids: list[int],
        group_id: str = "",
        *,
        mesh_gateway_id: str = "",
        mesh_member_ids: list[str] | None = None,
    ) -> list[ScheduleTimingRow]:
        """Delete device schedules through the REST child façade."""
        return await self._rest_port.delete_device_schedules(
            device_id,
            device_type,
            schedule_ids,
            group_id,
            mesh_gateway_id=mesh_gateway_id,
            mesh_member_ids=mesh_member_ids,
        )

    def attach_mqtt_facade(self, mqtt_facade: LiproMqttFacade | None) -> None:
        """Attach or clear the active MQTT child façade."""
        self._mqtt = mqtt_facade
        if mqtt_facade is None:
            self._session_state.bind_mqtt_biz_id(None)
            return
        self._session_state.bind_mqtt_biz_id(mqtt_facade.protocol_session_state.biz_id)

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
        self.attach_mqtt_facade(mqtt_facade)
        return mqtt_facade

    def protocol_diagnostics_snapshot(self) -> dict[str, Any]:
        """Return one root-owned diagnostics snapshot."""
        mqtt = self._mqtt
        return self._diagnostics_context.snapshot(
            mqtt_connected=mqtt.is_connected if mqtt is not None else None,
            subscribed_count=mqtt.subscribed_count if mqtt is not None else None,
            auth_recovery=self._rest.auth_recovery_telemetry_snapshot(),
        )


__all__ = ["LiproMqttFacade", "LiproProtocolFacade"]
