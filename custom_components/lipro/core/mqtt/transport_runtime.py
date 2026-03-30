"""Runtime bridge that keeps the MQTT transport thin."""

from __future__ import annotations

import asyncio
from collections.abc import Awaitable, Callable
from dataclasses import dataclass, field
import logging
import random
import ssl

import aiomqtt

from ...const.api import (
    MQTT_BROKER_HOST,
    MQTT_BROKER_PORT,
    MQTT_KEEP_ALIVE,
    MQTT_RECONNECT_MIN_DELAY,
)
from .connection_manager import MqttConnectionManager
from .credentials import MqttCredentials
from .message_processor import MqttMessageProcessor, MqttPayload
from .payload import parse_mqtt_payload
from .subscription_manager import MqttSubscriptionManager
from .topic_builder import MqttTopicBuilder

_LOGGER = logging.getLogger(__package__ or __name__)


@dataclass(slots=True)
class MqttTransportCallbacks:
    """Callback contract exposed by the transport owner."""

    on_message: Callable[[str, MqttPayload], None] | None = None
    on_connect: Callable[[], None] | None = None
    on_disconnect: Callable[[], None] | None = None
    on_error: Callable[[Exception], None] | None = None


@dataclass(slots=True)
class MqttTransportOwnerState:
    """Mutable state contract owned by the transport and shared with runtime."""

    subscribed_devices: set[str] = field(default_factory=set)
    pending_unsubscribe: set[str] = field(default_factory=set)
    broker_client: aiomqtt.Client | None = None
    task: asyncio.Task[None] | None = None
    last_error: Exception | None = None
    running: bool = False
    connected: bool = False
    connected_lock: asyncio.Lock = field(default_factory=asyncio.Lock)
    connected_event: asyncio.Event = field(default_factory=asyncio.Event)
    tls_context: ssl.SSLContext | None = None
    reconnect_delay: float = MQTT_RECONNECT_MIN_DELAY


@dataclass(slots=True)
class MqttTransportRuntimeOwner:
    """Explicit owner contract consumed by the MQTT runtime bridge."""

    credentials: MqttCredentials
    callbacks: MqttTransportCallbacks
    state: MqttTransportOwnerState
    topic_builder_provider: Callable[[], MqttTopicBuilder]
    message_processor_provider: Callable[[], MqttMessageProcessor]
    connection_manager_provider: Callable[[], MqttConnectionManager]
    subscription_manager_provider: Callable[[], MqttSubscriptionManager]
    clear_task_ref: Callable[[asyncio.Task[None]], None]
    process_message_entrypoint_provider: Callable[[], Callable[[aiomqtt.Message], None]]
    connect_and_listen_entrypoint_provider: Callable[[], Callable[[], Awaitable[None]]]

    @property
    def topic_builder(self) -> MqttTopicBuilder:
        """Return the current topic-builder collaborator."""
        return self.topic_builder_provider()

    @property
    def message_processor(self) -> MqttMessageProcessor:
        """Return the current message-processor collaborator."""
        return self.message_processor_provider()

    @property
    def connection_manager(self) -> MqttConnectionManager:
        """Return the current connection-manager collaborator."""
        return self.connection_manager_provider()

    @property
    def subscription_manager(self) -> MqttSubscriptionManager:
        """Return the current subscription-manager collaborator."""
        return self.subscription_manager_provider()

    @property
    def process_message_entrypoint(self) -> Callable[[aiomqtt.Message], None]:
        """Return the current transport-facing message entrypoint."""
        return self.process_message_entrypoint_provider()

    @property
    def connect_and_listen_entrypoint(self) -> Callable[[], Awaitable[None]]:
        """Return the current transport-facing connect/listen entrypoint."""
        return self.connect_and_listen_entrypoint_provider()


class MqttTransportRuntime:
    """Bridge explicit owner state into focused MQTT runtime helpers."""

    def __init__(self, owner: MqttTransportRuntimeOwner) -> None:
        """Bind one explicit owner contract to the runtime bridge."""
        self._owner = owner

    def build_topic_pairs(
        self,
        device_ids: list[str] | set[str],
        *,
        invalid_log_message: str,
        on_invalid: Callable[[str], None] | None = None,
    ) -> list[tuple[str, str]]:
        """Build MQTT topic pairs for device ids."""
        return self._owner.topic_builder.build_topic_pairs(
            device_ids,
            invalid_log_message=invalid_log_message,
            on_invalid=on_invalid,
        )

    def batched_topic_pairs(
        self,
        topic_pairs: list[tuple[str, str]],
    ) -> list[list[tuple[str, str]]]:
        """Batch topic pairs for subscribe/unsubscribe calls."""
        return self._owner.topic_builder.batch_topic_pairs(topic_pairs)

    def set_last_error(self, err: Exception) -> None:
        """Store and report one runtime error."""
        self._owner.connection_manager.set_last_error(
            err,
            assign_last_error=self._assign_last_error,
        )

    def clear_last_error(self) -> None:
        """Clear the tracked runtime error."""
        self._owner.connection_manager.clear_last_error(
            assign_last_error=self._assign_last_error,
        )

    def invoke_callback(
        self,
        callback: Callable[..., None] | None,
        callback_name: str,
        *args: object,
    ) -> bool:
        """Invoke one optional callback with defensive error handling."""
        return self._owner.connection_manager.invoke_callback(
            callback,
            callback_name,
            self.set_last_error,
            *args,
        )

    def handle_disconnect(self, reason: str) -> None:
        """Clear runtime state after one disconnect event."""
        self._owner.connection_manager.handle_disconnect(
            reason,
            assign_connected=self._assign_connected,
            clear_client=self._clear_broker_client,
            set_last_error=self.set_last_error,
        )

    def process_message(self, message: aiomqtt.Message) -> None:
        """Parse one MQTT message and forward it to the owner callback."""
        self._owner.message_processor.process_message(
            message,
            parse_payload=parse_mqtt_payload,
            on_message=self._owner.callbacks.on_message,
            invoke_callback=self.invoke_callback,
            set_last_error=self.set_last_error,
            clear_last_error=self.clear_last_error,
        )

    def async_finalize_connection_task(self, task: asyncio.Task[None]) -> None:
        """Handle background task completion for the owner transport."""
        self._owner.connection_manager.finalize_connection_task(
            task,
            clear_task_ref=self._owner.clear_task_ref,
            set_last_error=self.set_last_error,
        )

    async def connect_and_listen(self) -> None:
        """Open one MQTT connection and consume the message stream."""
        state = self._owner.state
        if state.tls_context is None:
            state.tls_context = ssl.create_default_context()
        stream_ended = False
        async with aiomqtt.Client(
            hostname=MQTT_BROKER_HOST,
            port=MQTT_BROKER_PORT,
            username=self._owner.credentials.username,
            password=self._owner.credentials.password,
            identifier=self._owner.credentials.client_id,
            clean_session=False,
            keepalive=MQTT_KEEP_ALIVE,
            tls_context=state.tls_context,
        ) as broker_client:
            state.broker_client = broker_client
            state.reconnect_delay = MQTT_RECONNECT_MIN_DELAY
            await self._owner.subscription_manager.apply_pending_unsubscribes(
                broker_client,
                pending_unsubscribe=state.pending_unsubscribe,
                subscribed_devices=state.subscribed_devices,
            )
            await self._owner.subscription_manager.subscribe_current_devices(
                broker_client,
                subscribed_devices=state.subscribed_devices,
            )
            await self._assign_connected_async(True)
            _LOGGER.info("Connected to MQTT broker")
            if self.invoke_callback(self._owner.callbacks.on_connect, "on_connect"):
                self.clear_last_error()
            async for message in broker_client.messages:
                self._owner.process_message_entrypoint(message)
            stream_ended = True
        if stream_ended and state.running:
            self.handle_disconnect("MQTT message stream ended")
        elif not state.running:
            await self._assign_connected_async(False)
            state.broker_client = None

    async def connection_loop(self) -> None:
        """Run the background reconnect loop until the owner stops."""
        state = self._owner.state
        await self._owner.connection_manager.run_connection_loop(
            is_running=lambda: state.running,
            connect_and_listen=self._owner.connect_and_listen_entrypoint,
            set_last_error=self.set_last_error,
            handle_disconnect=self.handle_disconnect,
            sleep=asyncio.sleep,
            jitter_source=random.uniform,
        )
        await self._assign_connected_async(False)
        state.broker_client = None

    async def _assign_connected_async(self, connected: bool) -> None:
        """Assign connection state with lock protection."""
        state = self._owner.state
        async with state.connected_lock:
            state.connected = connected
            if connected:
                state.connected_event.set()
            else:
                state.connected_event.clear()

    def _assign_connected(self, connected: bool) -> None:
        """Synchronous assignment for callback contexts (best-effort)."""
        state = self._owner.state
        state.connected = connected
        if connected:
            state.connected_event.set()
        else:
            state.connected_event.clear()

    def _assign_last_error(self, value: Exception | None) -> None:
        """Persist latest error in the owner state."""
        self._owner.state.last_error = value

    def _clear_broker_client(self) -> None:
        """Clear the owner-managed broker client reference."""
        self._owner.state.broker_client = None


__all__ = [
    "MqttTransportCallbacks",
    "MqttTransportOwnerState",
    "MqttTransportRuntime",
    "MqttTransportRuntimeOwner",
]
