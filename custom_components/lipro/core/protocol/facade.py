"""Unified protocol root and transport child façades."""

from __future__ import annotations

from typing import Any

from ...const.api import REQUEST_TIMEOUT
from ..api.client import LiproRestFacade
from ..api.client_base import ClientSessionState
from ..api.request_policy import RequestPolicy
from ..mqtt.mqtt_client import LiproMqttClient
from .contracts import CanonicalProtocolContracts
from .diagnostics_context import ProtocolDiagnosticsContext
from .session import ProtocolSessionState
from .telemetry import ProtocolTelemetry


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
        on_message=None,
        on_connect=None,
        on_disconnect=None,
        on_error=None,
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

    def __getattr__(self, name: str) -> Any:
        """Delegate unknown attributes to the wrapped concrete MQTT transport."""
        return getattr(self._client, name)

    def __dir__(self) -> list[str]:
        """Expose child-transport members for introspection and testing."""
        return sorted(set(super().__dir__()) | set(dir(self._client)))

    @property
    def raw_client(self) -> LiproMqttClient:
        """Expose the wrapped concrete transport for explicit compat seams only."""
        return self._client

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
        session=None,
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
        self._mqtt: LiproMqttFacade | None = None

    def __getattr__(self, name: str) -> Any:
        """Delegate protocol operations to the REST child façade by default."""
        return getattr(self._rest, name)

    def __dir__(self) -> list[str]:
        """Expose child-façade members for compatibility-friendly introspection."""
        return sorted(set(super().__dir__()) | set(dir(self._rest)))

    @property
    def rest(self) -> LiproRestFacade:
        """Return the REST child façade owned by this protocol root."""
        return self._rest

    @property
    def mqtt(self) -> LiproMqttFacade | None:
        """Return the currently attached MQTT child façade when available."""
        return self._mqtt

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
        on_message=None,
        on_connect=None,
        on_disconnect=None,
        on_error=None,
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
        )


__all__ = ["LiproMqttFacade", "LiproProtocolFacade"]
