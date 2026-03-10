# ruff: noqa: SLF001
"""Runtime bridge that keeps the MQTT facade thin."""

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

    from .client import LiproMqttClient

_LOGGER = logging.getLogger(__package__ or __name__)


class MqttClientRuntime:
    """Bridge owner state into focused MQTT runtime helpers."""

    def __init__(self, client: LiproMqttClient) -> None:
        """Bind one thin client facade to the runtime bridge."""
        self._client = client

    def build_topic_pairs(
        self,
        device_ids: list[str] | set[str],
        *,
        invalid_log_message: str,
        on_invalid: Callable[[str], None] | None = None,
    ) -> list[tuple[str, str]]:
        """Build MQTT topic pairs for device ids."""
        return self._client._topic_builder.build_topic_pairs(
            device_ids,
            invalid_log_message=invalid_log_message,
            on_invalid=on_invalid,
        )

    def batched_topic_pairs(
        self,
        topic_pairs: list[tuple[str, str]],
    ) -> list[list[tuple[str, str]]]:
        """Batch topic pairs for subscribe/unsubscribe calls."""
        return self._client._topic_builder.batch_topic_pairs(topic_pairs)

    def set_last_error(self, err: Exception) -> None:
        """Store and report one runtime error."""
        self._client._connection_manager.set_last_error(
            err,
            assign_last_error=self._assign_last_error,
        )

    def clear_last_error(self) -> None:
        """Clear the tracked runtime error."""
        self._client._connection_manager.clear_last_error(
            assign_last_error=self._assign_last_error,
        )

    def invoke_callback(
        self,
        callback: Callable[..., None] | None,
        callback_name: str,
        *args: object,
    ) -> bool:
        """Invoke one optional callback with defensive error handling."""
        return self._client._connection_manager.invoke_callback(
            callback,
            callback_name,
            self.set_last_error,
            *args,
        )

    def handle_disconnect(self, reason: str) -> None:
        """Clear runtime state after one disconnect event."""
        self._client._connection_manager.handle_disconnect(
            reason,
            assign_connected=self._assign_connected,
            clear_client=self._clear_client,
            set_last_error=self.set_last_error,
        )

    def process_message(self, message: aiomqtt.Message) -> None:
        """Parse one MQTT message and forward it to the owner callback."""
        self._client._message_processor.process_message(
            message,
            parse_payload=parse_mqtt_payload,
            on_message=self._client._on_message,
            invoke_callback=self.invoke_callback,
            set_last_error=self.set_last_error,
            clear_last_error=self.clear_last_error,
        )

    def async_finalize_connection_task(self, task: asyncio.Task[None]) -> None:
        """Handle background task completion for the owner facade."""
        self._client._connection_manager.finalize_connection_task(
            task,
            clear_task_ref=self._client._clear_task_ref,
            set_last_error=self.set_last_error,
        )

    async def connect_and_listen(self) -> None:
        """Open one MQTT connection and consume the message stream."""
        if self._client._tls_context is None:
            self._client._tls_context = ssl.create_default_context()
        stream_ended = False
        async with aiomqtt.Client(
            hostname=MQTT_BROKER_HOST,
            port=MQTT_BROKER_PORT,
            username=self._client._credentials.username,
            password=self._client._credentials.password,
            identifier=self._client._credentials.client_id,
            clean_session=False,
            keepalive=MQTT_KEEP_ALIVE,
            tls_context=self._client._tls_context,
        ) as mqtt_client:
            self._client._client = mqtt_client
            self._client._reconnect_delay = MQTT_RECONNECT_MIN_DELAY
            await self._client._subscription_manager.apply_pending_unsubscribes(
                mqtt_client,
                pending_unsubscribe=self._client._pending_unsubscribe,
            )
            await self._client._subscription_manager.subscribe_current_devices(
                mqtt_client,
                subscribed_devices=self._client._subscribed_devices,
            )
            self._client._connected = True
            _LOGGER.info("Connected to MQTT broker")
            if self._client._invoke_callback(self._client._on_connect, "on_connect"):
                self._client._clear_last_error()
            async for message in mqtt_client.messages:
                self._client._process_message(message)
            stream_ended = True
        if stream_ended and self._client._running:
            self._client._handle_disconnect("MQTT message stream ended")
        elif not self._client._running:
            self._client._connected = False
            self._client._client = None

    async def connection_loop(self) -> None:
        """Run the background reconnect loop until the owner stops."""
        await self._client._connection_manager.run_connection_loop(
            is_running=lambda: self._client._running,
            connect_and_listen=self._client._connect_and_listen,
            set_last_error=self._client._set_last_error,
            handle_disconnect=self._client._handle_disconnect,
            sleep=asyncio.sleep,
            jitter_source=random.uniform,
        )
        self._client._connected = False
        self._client._client = None

    def _assign_connected(self, connected: bool) -> None:
        self._client._connected = connected

    def _assign_last_error(self, value: Exception | None) -> None:
        self._client._last_error = value

    def _clear_client(self) -> None:
        self._client._client = None


__all__ = ["MqttClientRuntime"]
