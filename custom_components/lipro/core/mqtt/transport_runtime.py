# ruff: noqa: SLF001
"""Runtime bridge that keeps the MQTT transport thin."""

from __future__ import annotations

import asyncio
import logging
import random
import ssl
from typing import TYPE_CHECKING

import aiomqtt

from ...const.api import (
    MQTT_BROKER_HOST,
    MQTT_BROKER_PORT,
    MQTT_KEEP_ALIVE,
    MQTT_RECONNECT_MIN_DELAY,
)
from .payload import parse_mqtt_payload

if TYPE_CHECKING:
    from collections.abc import Callable

    from .transport import MqttTransport

_LOGGER = logging.getLogger(__package__ or __name__)


class MqttTransportRuntime:
    """Bridge owner state into focused MQTT runtime helpers."""

    def __init__(self, transport: MqttTransport) -> None:
        """Bind one transport owner to the runtime bridge."""
        self._transport = transport

    def build_topic_pairs(
        self,
        device_ids: list[str] | set[str],
        *,
        invalid_log_message: str,
        on_invalid: Callable[[str], None] | None = None,
    ) -> list[tuple[str, str]]:
        """Build MQTT topic pairs for device ids."""
        return self._transport._topic_builder.build_topic_pairs(
            device_ids,
            invalid_log_message=invalid_log_message,
            on_invalid=on_invalid,
        )

    def batched_topic_pairs(
        self,
        topic_pairs: list[tuple[str, str]],
    ) -> list[list[tuple[str, str]]]:
        """Batch topic pairs for subscribe/unsubscribe calls."""
        return self._transport._topic_builder.batch_topic_pairs(topic_pairs)

    def set_last_error(self, err: Exception) -> None:
        """Store and report one runtime error."""
        self._transport._connection_manager.set_last_error(
            err,
            assign_last_error=self._assign_last_error,
        )

    def clear_last_error(self) -> None:
        """Clear the tracked runtime error."""
        self._transport._connection_manager.clear_last_error(
            assign_last_error=self._assign_last_error,
        )

    def invoke_callback(
        self,
        callback: Callable[..., None] | None,
        callback_name: str,
        *args: object,
    ) -> bool:
        """Invoke one optional callback with defensive error handling."""
        return self._transport._connection_manager.invoke_callback(
            callback,
            callback_name,
            self.set_last_error,
            *args,
        )

    def handle_disconnect(self, reason: str) -> None:
        """Clear runtime state after one disconnect event."""
        self._transport._connection_manager.handle_disconnect(
            reason,
            assign_connected=self._assign_connected,
            clear_client=self._clear_broker_client,
            set_last_error=self.set_last_error,
        )

    def process_message(self, message: aiomqtt.Message) -> None:
        """Parse one MQTT message and forward it to the owner callback."""
        self._transport._message_processor.process_message(
            message,
            parse_payload=parse_mqtt_payload,
            on_message=self._transport._on_message,
            invoke_callback=self.invoke_callback,
            set_last_error=self.set_last_error,
            clear_last_error=self.clear_last_error,
        )

    def async_finalize_connection_task(self, task: asyncio.Task[None]) -> None:
        """Handle background task completion for the owner transport."""
        self._transport._connection_manager.finalize_connection_task(
            task,
            clear_task_ref=self._transport._clear_task_ref,
            set_last_error=self.set_last_error,
        )

    async def connect_and_listen(self) -> None:
        """Open one MQTT connection and consume the message stream."""
        if self._transport._tls_context is None:
            self._transport._tls_context = ssl.create_default_context()
        stream_ended = False
        async with aiomqtt.Client(
            hostname=MQTT_BROKER_HOST,
            port=MQTT_BROKER_PORT,
            username=self._transport._credentials.username,
            password=self._transport._credentials.password,
            identifier=self._transport._credentials.client_id,
            clean_session=False,
            keepalive=MQTT_KEEP_ALIVE,
            tls_context=self._transport._tls_context,
        ) as broker_client:
            self._transport._broker_client = broker_client
            self._transport._reconnect_delay = MQTT_RECONNECT_MIN_DELAY
            await self._transport._subscription_manager.apply_pending_unsubscribes(
                broker_client,
                pending_unsubscribe=self._transport._pending_unsubscribe,
                subscribed_devices=self._transport._subscribed_devices,
            )
            await self._transport._subscription_manager.subscribe_current_devices(
                broker_client,
                subscribed_devices=self._transport._subscribed_devices,
            )
            await self._assign_connected_async(True)
            _LOGGER.info("Connected to MQTT broker")
            if self._transport._invoke_callback(
                self._transport._on_connect, "on_connect"
            ):
                self._transport._clear_last_error()
            async for message in broker_client.messages:
                self._transport._process_message(message)
            stream_ended = True
        if stream_ended and self._transport._running:
            self._transport._handle_disconnect("MQTT message stream ended")
        elif not self._transport._running:
            await self._assign_connected_async(False)
            self._transport._broker_client = None

    async def connection_loop(self) -> None:
        """Run the background reconnect loop until the owner stops."""
        await self._transport._connection_manager.run_connection_loop(
            is_running=lambda: self._transport._running,
            connect_and_listen=self._transport._connect_and_listen,
            set_last_error=self._transport._set_last_error,
            handle_disconnect=self._transport._handle_disconnect,
            sleep=asyncio.sleep,
            jitter_source=random.uniform,
        )
        await self._assign_connected_async(False)
        self._transport._broker_client = None

    async def _assign_connected_async(self, connected: bool) -> None:
        """Assign connection state with lock protection."""
        async with self._transport._connected_lock:
            self._transport._connected = connected
            if connected:
                self._transport._connected_event.set()
            else:
                self._transport._connected_event.clear()

    def _assign_connected(self, connected: bool) -> None:
        """Synchronous assignment for callback contexts (best-effort)."""
        self._transport._connected = connected
        if connected:
            self._transport._connected_event.set()
        else:
            self._transport._connected_event.clear()

    def _assign_last_error(self, value: Exception | None) -> None:
        self._transport._last_error = value

    def _clear_broker_client(self) -> None:
        self._transport._broker_client = None


__all__ = ["MqttTransportRuntime"]
