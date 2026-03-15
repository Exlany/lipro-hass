"""MQTT client for Lipro real-time device status updates."""

from __future__ import annotations

import asyncio
from collections.abc import Callable
import ssl
from typing import Any, Final

import aiomqtt

from ...const.api import MQTT_RECONNECT_MIN_DELAY
from .client_runtime import MqttClientRuntime
from .connection_manager import MqttConnectionManager
from .credentials import MqttCredentials
from .message_processor import MqttMessageProcessor, decode_payload_text
from .subscription_manager import MqttSubscriptionManager
from .topic_builder import MqttTopicBuilder

_MQTT_SUBSCRIPTION_BATCH_SIZE: Final[int] = 50


class MqttTransportClient:
    """Thin MQTT facade composed from focused runtime helpers."""

    def __init__(
        self,
        access_key: str,
        secret_key: str,
        biz_id: str,
        phone_id: str,
        on_message: Callable[[str, dict[str, Any]], None] | None = None,
        on_connect: Callable[[], None] | None = None,
        on_disconnect: Callable[[], None] | None = None,
        on_error: Callable[[Exception], None] | None = None,
    ) -> None:
        """Initialize the composed MQTT facade and bind runtime helpers."""
        self._credentials = MqttCredentials.create(
            access_key, secret_key, biz_id, phone_id
        )
        self._biz_id = biz_id
        self._on_message = on_message
        self._on_connect = on_connect
        self._on_disconnect = on_disconnect
        self._on_error = on_error
        self._subscribed_devices: set[str] = set()
        self._pending_unsubscribe: set[str] = set()
        self._client: aiomqtt.Client | None = None
        self._task: asyncio.Task[None] | None = None
        self._last_error: Exception | None = None
        self._running = False
        self._connected = False
        self._connected_lock = asyncio.Lock()
        self._connected_event = asyncio.Event()
        self._tls_context: ssl.SSLContext | None = None
        self._reconnect_delay = MQTT_RECONNECT_MIN_DELAY
        self._message_processor = MqttMessageProcessor(biz_id)
        self._topic_builder = MqttTopicBuilder(
            biz_id, batch_size=_MQTT_SUBSCRIPTION_BATCH_SIZE
        )
        self._connection_manager = MqttConnectionManager(
            on_connect, on_disconnect, on_error
        )
        self._subscription_manager = MqttSubscriptionManager(self._topic_builder)
        runtime = MqttClientRuntime(self)
        self._build_topic_pairs = runtime.build_topic_pairs
        self._batched_topic_pairs = runtime.batched_topic_pairs
        self._set_last_error = runtime.set_last_error
        self._clear_last_error = runtime.clear_last_error
        self._invoke_callback = runtime.invoke_callback
        self._handle_disconnect = runtime.handle_disconnect
        self._process_message = runtime.process_message
        self._async_finalize_connection_task = runtime.async_finalize_connection_task
        self._connect_and_listen = runtime.connect_and_listen
        self._connection_loop = runtime.connection_loop

    @property
    def is_connected(self) -> bool:
        """Return whether the MQTT transport is currently connected.

        Note: This is a synchronous property that reads _connected without locking.
        For critical decisions, use async methods that acquire the lock.
        """
        return self._connected

    @property
    def subscribed_devices(self) -> set[str]:
        """Return a copy of the currently tracked subscription set."""
        return self._subscribed_devices.copy()

    @property
    def subscribed_count(self) -> int:
        """Return the number of tracked subscriptions."""
        return len(self._subscribed_devices)

    @property
    def last_error(self) -> Exception | None:
        """Return the most recent background or callback error."""
        return self._last_error

    async def start(self, device_ids: list[str]) -> None:
        """Start the background MQTT connection loop."""
        if self._running:
            return
        self._subscribed_devices = set(device_ids)
        self._pending_unsubscribe.difference_update(self._subscribed_devices)
        self._connected_event.clear()
        self._running = True
        self._task = asyncio.create_task(
            self._connection_loop(), name="lipro_mqtt_connection_loop"
        )
        self._task.add_done_callback(self._async_finalize_connection_task)

    async def stop(self) -> None:
        """Stop the background MQTT connection loop and clear state."""
        self._running = False
        task = self._task
        if task:
            task.cancel()
            [task_result] = await asyncio.gather(task, return_exceptions=True)
            if isinstance(task_result, Exception):
                self._set_last_error(task_result)
            if self._task is task:
                self._task = None
        async with self._connected_lock:
            self._connected = False
            self._connected_event.clear()
        self._client = None
        self._tls_context = None
        self._subscribed_devices.clear()
        self._pending_unsubscribe.clear()

    async def sync_subscriptions(self, device_ids: set[str]) -> None:
        """Synchronize tracked subscriptions to match the desired device set."""
        await self._subscription_manager.sync_subscriptions(
            client=self._client,
            connected=self._connected,
            subscribed_devices=self._subscribed_devices,
            pending_unsubscribe=self._pending_unsubscribe,
            device_ids=device_ids,
        )

    async def wait_until_connected(self, timeout: float | None = None) -> bool:
        """Wait until the MQTT transport completes a real broker handshake."""
        if self._connected:
            return True
        if not self._running:
            return False

        try:
            if timeout is None:
                await self._connected_event.wait()
            else:
                await asyncio.wait_for(self._connected_event.wait(), timeout=timeout)
        except TimeoutError:
            return False

        return self._connected

    def _clear_task_ref(self, task: asyncio.Task[None]) -> None:
        """Clear the tracked background task when it matches the finished task."""
        if self._task is task:
            self._task = None

    @staticmethod
    def _consume_task_exception(task: asyncio.Task[None]) -> Exception | None:
        """Return the background task exception, if any."""
        return MqttConnectionManager.consume_task_exception(task)

    @staticmethod
    def _decode_payload_text(raw_payload: object, device_id: str) -> str | None:
        """Decode MQTT payload text using the shared message helper."""
        return decode_payload_text(raw_payload, device_id)


__all__ = ["MqttTransportClient"]
