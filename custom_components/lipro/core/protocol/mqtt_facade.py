# ruff: noqa: D102,D107
"""MQTT child façade under the unified protocol root."""

from __future__ import annotations

import asyncio
from collections.abc import Awaitable, Callable
from typing import TypeVar

import aiohttp
import aiomqtt

from ..api.types import JsonObject
from ..mqtt.transport import MqttTransport
from .contracts import MqttTransportFacade
from .diagnostics_context import ProtocolDiagnosticsContext
from .session import ProtocolSessionState
from .telemetry import ProtocolTelemetry

type MqttMessageCallback = Callable[[str, JsonObject], None]
type MqttSignalCallback = Callable[[], None]
type MqttErrorCallback = Callable[[Exception], None]
_TransportResultT = TypeVar("_TransportResultT")


class LiproMqttFacade:
    """Protocol child façade wrapping one concrete MQTT transport."""

    def __init__(
        self,
        transport: MqttTransportFacade,
        *,
        session_state: ProtocolSessionState,
        telemetry: ProtocolTelemetry,
        diagnostics_context: ProtocolDiagnosticsContext,
    ) -> None:
        self._transport = transport
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
        session_state.bind_mqtt_biz_id(biz_id)
        return cls(
            MqttTransport(
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
        return self._session_state

    @property
    def telemetry(self) -> ProtocolTelemetry:
        return self._telemetry

    @property
    def diagnostics_context(self) -> ProtocolDiagnosticsContext:
        return self._diagnostics_context

    @property
    def is_connected(self) -> bool:
        return self._transport.is_connected

    @property
    def subscribed_devices(self) -> set[str]:
        return self._transport.subscribed_devices

    @property
    def subscribed_count(self) -> int:
        return self._transport.subscribed_count

    @property
    def last_error(self) -> Exception | None:
        err = self._transport.last_error
        if err is not None:
            self._telemetry.record_mqtt_error(err, stage="transport")
        return err

    async def _run_transport_stage(
        self,
        *,
        stage: str,
        operation: Callable[[], Awaitable[_TransportResultT]],
    ) -> _TransportResultT:
        try:
            return await operation()
        except asyncio.CancelledError:
            raise
        except (aiomqtt.MqttError, aiohttp.ClientError, OSError, TimeoutError) as err:
            self._telemetry.record_mqtt_error(err, stage=stage)
            raise
        except (ValueError, TypeError, LookupError) as err:
            self._telemetry.record_mqtt_error(err, stage=stage)
            raise
        except RuntimeError as err:
            self._telemetry.record_mqtt_error(err, stage=stage)
            raise

    async def start(self, device_ids: list[str]) -> None:
        self._telemetry.record_mqtt_start()
        await self._run_transport_stage(
            stage="start",
            operation=lambda: self._transport.start(device_ids),
        )

    async def stop(self) -> None:
        self._telemetry.record_mqtt_stop()
        await self._run_transport_stage(
            stage="stop",
            operation=self._transport.stop,
        )

    async def sync_subscriptions(self, device_ids: set[str]) -> None:
        self._telemetry.record_mqtt_sync()
        await self._run_transport_stage(
            stage="sync_subscriptions",
            operation=lambda: self._transport.sync_subscriptions(device_ids),
        )

    async def wait_until_connected(self, timeout: float | None = None) -> bool:
        connected = await self._run_transport_stage(
            stage="wait_until_connected",
            operation=lambda: self._transport.wait_until_connected(timeout=timeout),
        )
        if self._transport.last_error is not None:
            self._telemetry.record_mqtt_error(
                self._transport.last_error,
                stage="transport",
            )
        return connected


__all__ = [
    "LiproMqttFacade",
    "MqttErrorCallback",
    "MqttMessageCallback",
    "MqttSignalCallback",
]
