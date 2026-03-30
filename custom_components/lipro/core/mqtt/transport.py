"""Localized MQTT transport implementation for Lipro real-time device state."""

from __future__ import annotations

import asyncio
from collections.abc import Callable
import ssl
from typing import Final

import aiomqtt

from .connection_manager import MqttConnectionManager
from .credentials import MqttCredentials
from .message_processor import MqttMessageProcessor, MqttPayload, decode_payload_text
from .subscription_manager import MqttSubscriptionManager
from .topic_builder import MqttTopicBuilder
from .transport_runtime import (
    MqttTransportCallbacks,
    MqttTransportOwnerState,
    MqttTransportRuntime,
    MqttTransportRuntimeOwner,
)

_MQTT_SUBSCRIPTION_BATCH_SIZE: Final[int] = 50


class MqttTransport:
    """Concrete MQTT transport composed from focused runtime helpers."""

    def __init__(
        self,
        access_key: str,
        secret_key: str,
        biz_id: str,
        phone_id: str,
        on_message: Callable[[str, MqttPayload], None] | None = None,
        on_connect: Callable[[], None] | None = None,
        on_disconnect: Callable[[], None] | None = None,
        on_error: Callable[[Exception], None] | None = None,
    ) -> None:
        """Initialize the transport and bind its focused runtime helpers."""
        self._credentials = MqttCredentials.create(
            access_key, secret_key, biz_id, phone_id
        )
        self._biz_id = biz_id
        self._on_message = on_message
        self._on_connect = on_connect
        self._on_disconnect = on_disconnect
        self._on_error = on_error
        self._message_processor = MqttMessageProcessor(biz_id)
        self._topic_builder = MqttTopicBuilder(
            biz_id, batch_size=_MQTT_SUBSCRIPTION_BATCH_SIZE
        )
        self._connection_manager = MqttConnectionManager(
            on_connect, on_disconnect, on_error
        )
        self._subscription_manager = MqttSubscriptionManager(self._topic_builder)
        self._runtime_callbacks = MqttTransportCallbacks(
            on_message=on_message,
            on_connect=on_connect,
            on_disconnect=on_disconnect,
            on_error=on_error,
        )
        self._runtime_state = MqttTransportOwnerState()
        self._runtime_owner = MqttTransportRuntimeOwner(
            credentials=self._credentials,
            callbacks=self._runtime_callbacks,
            state=self._runtime_state,
            topic_builder_provider=lambda: self._topic_builder,
            message_processor_provider=lambda: self._message_processor,
            connection_manager_provider=lambda: self._connection_manager,
            subscription_manager_provider=lambda: self._subscription_manager,
            clear_task_ref=self._clear_task_ref,
            process_message_entrypoint_provider=lambda: self._process_message,
            connect_and_listen_entrypoint_provider=lambda: self._connect_and_listen,
        )
        transport_runtime = MqttTransportRuntime(self._runtime_owner)
        self._build_topic_pairs = transport_runtime.build_topic_pairs
        self._batched_topic_pairs = transport_runtime.batched_topic_pairs
        self._set_last_error = transport_runtime.set_last_error
        self._clear_last_error = transport_runtime.clear_last_error
        self._invoke_callback = transport_runtime.invoke_callback
        self._handle_disconnect = transport_runtime.handle_disconnect
        self._process_message = transport_runtime.process_message
        self._async_finalize_connection_task = (
            transport_runtime.async_finalize_connection_task
        )
        self._connect_and_listen = transport_runtime.connect_and_listen
        self._connection_loop = transport_runtime.connection_loop

    @property
    def is_connected(self) -> bool:
        """Return whether the MQTT transport is currently connected.

        Note: This is a synchronous property that reads `_connected` without
        locking. For critical decisions, use async methods that acquire the lock.
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

    @property
    def _subscribed_devices(self) -> set[str]:
        return self._runtime_state.subscribed_devices

    @_subscribed_devices.setter
    def _subscribed_devices(self, value: set[str]) -> None:
        self._runtime_state.subscribed_devices = value

    @property
    def _pending_unsubscribe(self) -> set[str]:
        return self._runtime_state.pending_unsubscribe

    @_pending_unsubscribe.setter
    def _pending_unsubscribe(self, value: set[str]) -> None:
        self._runtime_state.pending_unsubscribe = value

    @property
    def _broker_client(self) -> aiomqtt.Client | None:
        return self._runtime_state.broker_client

    @_broker_client.setter
    def _broker_client(self, value: aiomqtt.Client | None) -> None:
        self._runtime_state.broker_client = value

    @property
    def _task(self) -> asyncio.Task[None] | None:
        return self._runtime_state.task

    @_task.setter
    def _task(self, value: asyncio.Task[None] | None) -> None:
        self._runtime_state.task = value

    @property
    def _last_error(self) -> Exception | None:
        return self._runtime_state.last_error

    @_last_error.setter
    def _last_error(self, value: Exception | None) -> None:
        self._runtime_state.last_error = value

    @property
    def _running(self) -> bool:
        return self._runtime_state.running

    @_running.setter
    def _running(self, value: bool) -> None:
        self._runtime_state.running = value

    @property
    def _connected(self) -> bool:
        return self._runtime_state.connected

    @_connected.setter
    def _connected(self, value: bool) -> None:
        self._runtime_state.connected = value

    @property
    def _connected_lock(self) -> asyncio.Lock:
        return self._runtime_state.connected_lock

    @_connected_lock.setter
    def _connected_lock(self, value: asyncio.Lock) -> None:
        self._runtime_state.connected_lock = value

    @property
    def _connected_event(self) -> asyncio.Event:
        return self._runtime_state.connected_event

    @_connected_event.setter
    def _connected_event(self, value: asyncio.Event) -> None:
        self._runtime_state.connected_event = value

    @property
    def _tls_context(self) -> ssl.SSLContext | None:
        return self._runtime_state.tls_context

    @_tls_context.setter
    def _tls_context(self, value: ssl.SSLContext | None) -> None:
        self._runtime_state.tls_context = value

    @property
    def _reconnect_delay(self) -> float:
        return self._runtime_state.reconnect_delay

    @_reconnect_delay.setter
    def _reconnect_delay(self, value: float) -> None:
        self._runtime_state.reconnect_delay = value

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
        self._broker_client = None
        self._tls_context = None
        self._subscribed_devices.clear()
        self._pending_unsubscribe.clear()

    async def sync_subscriptions(self, device_ids: set[str]) -> None:
        """Synchronize tracked subscriptions to match the desired device set."""
        await self._subscription_manager.sync_subscriptions(
            client=self._broker_client,
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


__all__ = ["MqttTransport"]
