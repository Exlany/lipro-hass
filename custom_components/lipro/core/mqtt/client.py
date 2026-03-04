"""MQTT client for Lipro real-time device status updates.

This module provides real-time device status updates via Aliyun MQTT.
It complements the REST API polling with push-based updates for lower latency.

Architecture:
    - MqttCredentials: Handles credential decryption and generation
    - LiproMqttClient: Main MQTT client with auto-reconnect
    - Helper functions for topic/payload parsing
"""

from __future__ import annotations

import asyncio
import contextlib
import json
import logging
import random
import ssl
from typing import TYPE_CHECKING, Any, Final

import aiomqtt

from ...const.api import (
    MQTT_BROKER_HOST,
    MQTT_BROKER_PORT,
    MQTT_KEEP_ALIVE,
    MQTT_QOS,
    MQTT_RECONNECT_JITTER,
    MQTT_RECONNECT_MAX_DELAY,
    MQTT_RECONNECT_MIN_DELAY,
)
from ..utils.redaction import redact_identifier as _redact_identifier
from .credentials import MqttCredentials
from .payload import (
    _MAX_MQTT_LOG_CHARS,
    _MAX_MQTT_PAYLOAD_BYTES,
    _format_mqtt_payload_for_log,
    parse_mqtt_payload,
)
from .topics import build_topic, parse_topic

if TYPE_CHECKING:
    from collections.abc import Callable

_LOGGER = logging.getLogger(__package__ or __name__)


# =============================================================================
# MQTT Client
# =============================================================================

_MQTT_SUBSCRIPTION_BATCH_SIZE: Final[int] = 50


class LiproMqttClient:
    """MQTT client for real-time device status updates.

    Features:
        - Automatic reconnection with exponential backoff
        - QoS 2 (exactly once) message delivery
        - Session persistence (clean_session=False)
        - Dynamic device subscription/unsubscription

    Usage:
        client = LiproMqttClient(credentials, biz_id, on_message=callback)
        await client.start(device_ids)
        # ... receive updates via callback ...
        await client.stop()

    """

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
        """Initialize MQTT client.

        Args:
            access_key: Decrypted MQTT access key.
            secret_key: Decrypted MQTT secret key.
            biz_id: Business ID (without 'lip_' prefix).
            phone_id: Device UUID.
            on_message: Callback for device status updates (device_id, properties).
            on_connect: Callback when connected to broker.
            on_disconnect: Callback when disconnected from broker.
            on_error: Callback when background task/callback processing fails.

        """
        self._credentials = MqttCredentials.create(
            access_key,
            secret_key,
            biz_id,
            phone_id,
        )
        self._biz_id = biz_id
        self._on_message = on_message
        self._on_connect = on_connect
        self._on_disconnect = on_disconnect
        self._on_error = on_error

        self._subscribed_devices: set[str] = set()
        self._client: aiomqtt.Client | None = None
        self._task: asyncio.Task | None = None
        self._last_error: Exception | None = None
        self._running = False
        self._connected = False
        self._reconnect_delay = MQTT_RECONNECT_MIN_DELAY
        self._tls_context: ssl.SSLContext | None = None
        self._invalid_topic_count = 0

    @property
    def is_connected(self) -> bool:
        """Return True if connected to MQTT broker."""
        return self._connected

    @property
    def subscribed_devices(self) -> set[str]:
        """Return a snapshot of currently subscribed device IDs."""
        return self._subscribed_devices.copy()

    @property
    def subscribed_count(self) -> int:
        """Return number of subscribed devices."""
        return len(self._subscribed_devices)

    @property
    def last_error(self) -> Exception | None:
        """Return the latest background/callback exception, if any."""
        return self._last_error

    async def start(self, device_ids: list[str]) -> None:
        """Start MQTT client and subscribe to device topics.

        Args:
            device_ids: List of IoT device IDs to subscribe.

        """
        if self._running:
            _LOGGER.warning("MQTT client already running")
            return

        self._subscribed_devices = set(device_ids)
        self._running = True
        self._task = asyncio.create_task(self._connection_loop())
        self._task.add_done_callback(self._async_finalize_connection_task)

        _LOGGER.info(
            "MQTT client started, subscribing to %d devices",
            len(device_ids),
        )

    async def stop(self) -> None:
        """Stop MQTT client and clean up resources."""
        self._running = False

        task = self._task
        if task:
            task.cancel()
            with contextlib.suppress(asyncio.CancelledError):
                await task
            if self._task is task:
                self._task = None

        self._connected = False
        self._client = None
        # Preserve legacy behavior: a new start() after stop() builds a fresh context.
        self._tls_context = None
        self._subscribed_devices.clear()
        _LOGGER.info("MQTT client stopped")

    def _get_tls_context(self) -> ssl.SSLContext:
        """Return cached TLS context for MQTT connections."""
        if self._tls_context is None:
            self._tls_context = ssl.create_default_context()
        return self._tls_context

    async def sync_subscriptions(self, device_ids: set[str]) -> None:
        """Sync subscriptions to match the given device ID set.

        Subscribes to new devices and unsubscribes from removed devices.

        Args:
            device_ids: Expected set of device IDs to be subscribed.

        """
        to_add = device_ids - self._subscribed_devices
        to_remove = self._subscribed_devices - device_ids

        if not to_add and not to_remove:
            return

        added = 0
        if to_add:
            if self._client and self._connected:
                subscribe_pairs: list[tuple[str, str]] = []
                for device_id in to_add:
                    try:
                        topic = build_topic(self._biz_id, device_id)
                    except ValueError:
                        _LOGGER.warning(
                            "Skipping invalid MQTT device ID %s: invalid characters",
                            _redact_identifier(device_id) or "***",
                        )
                        continue
                    subscribe_pairs.append((device_id, topic))

                for i in range(0, len(subscribe_pairs), _MQTT_SUBSCRIPTION_BATCH_SIZE):
                    subscribe_batch = subscribe_pairs[
                        i : i + _MQTT_SUBSCRIPTION_BATCH_SIZE
                    ]
                    subscribe_topics = [
                        (topic, MQTT_QOS) for _, topic in subscribe_batch
                    ]
                    try:
                        await self._client.subscribe(subscribe_topics)
                    except aiomqtt.MqttError:
                        _LOGGER.exception(
                            "Failed to subscribe to %d MQTT topics",
                            len(subscribe_topics),
                        )
                        continue

                    for device_id, _topic in subscribe_batch:
                        self._subscribed_devices.add(device_id)
                        added += 1
                        _LOGGER.debug(
                            "Subscribed to device %s",
                            _redact_identifier(device_id) or "***",
                        )
            else:
                # Not connected yet; record for subscription on next connect.
                self._subscribed_devices.update(to_add)
                added += len(to_add)

        removed = 0
        if to_remove:
            for device_id in to_remove:
                self._subscribed_devices.discard(device_id)
                removed += 1

            if self._client and self._connected:
                unsubscribe_topics: list[str] = []
                for device_id in to_remove:
                    try:
                        topic = build_topic(self._biz_id, device_id)
                    except ValueError:
                        _LOGGER.warning(
                            "Skipping MQTT unsubscribe for invalid device ID %s: invalid characters",
                            _redact_identifier(device_id) or "***",
                        )
                        continue
                    unsubscribe_topics.append(topic)

                for i in range(
                    0, len(unsubscribe_topics), _MQTT_SUBSCRIPTION_BATCH_SIZE
                ):
                    unsubscribe_batch = unsubscribe_topics[
                        i : i + _MQTT_SUBSCRIPTION_BATCH_SIZE
                    ]
                    try:
                        await self._client.unsubscribe(unsubscribe_batch)
                    except aiomqtt.MqttError:
                        _LOGGER.exception(
                            "Failed to unsubscribe from %d MQTT topics",
                            len(unsubscribe_batch),
                        )
                        continue

                    for topic in unsubscribe_batch:
                        _LOGGER.debug(
                            "Unsubscribed from device %s",
                            _redact_identifier(parse_topic(topic)) or "***",
                        )

        if added or removed:
            _LOGGER.info(
                "MQTT subscriptions synced: +%d -%d (total %d)",
                added,
                removed,
                len(self._subscribed_devices),
            )

    async def _connection_loop(self) -> None:
        """Main connection loop with auto-reconnect and jitter."""
        while self._running:
            try:
                await self._connect_and_listen()
            except aiomqtt.MqttError as err:
                self._set_last_error(err)
                self._handle_disconnect(f"MQTT error: {err}")
            except asyncio.CancelledError:
                break
            except OSError as err:
                self._set_last_error(err)
                self._handle_disconnect(f"Connection error: {err}")
            except ValueError as err:
                self._set_last_error(err)
                self._handle_disconnect(f"MQTT value error: {err}")
            except Exception as err:
                _LOGGER.exception(
                    "Unexpected MQTT loop error (%s)",
                    type(err).__name__,
                )
                self._set_last_error(err)
                self._handle_disconnect(
                    f"Unexpected MQTT loop error ({type(err).__name__})"
                )

            # Wait before reconnecting with jitter to prevent thundering herd
            if self._running:
                # Add ±20% jitter to prevent synchronized reconnects
                jitter = 1 + random.uniform(  # noqa: S311 - not crypto, just reconnect jitter
                    -MQTT_RECONNECT_JITTER, MQTT_RECONNECT_JITTER
                )
                wait_time = self._reconnect_delay * jitter
                _LOGGER.info("Reconnecting in %.1fs...", wait_time)
                await asyncio.sleep(wait_time)
                self._reconnect_delay = min(
                    self._reconnect_delay * 2,
                    MQTT_RECONNECT_MAX_DELAY,
                )

        self._connected = False
        self._client = None

    async def _connect_and_listen(self) -> None:
        """Connect to broker and listen for messages."""
        tls_context = self._get_tls_context()
        async with aiomqtt.Client(
            hostname=MQTT_BROKER_HOST,
            port=MQTT_BROKER_PORT,
            username=self._credentials.username,
            password=self._credentials.password,
            identifier=self._credentials.client_id,
            clean_session=False,
            keepalive=MQTT_KEEP_ALIVE,
            tls_context=tls_context,
        ) as client:
            self._client = client
            self._reconnect_delay = MQTT_RECONNECT_MIN_DELAY

            # Subscribe BEFORE marking connected to avoid race with sync_subscriptions
            subscribe_pairs: list[tuple[str, str]] = []
            for device_id in list(self._subscribed_devices):
                try:
                    topic = build_topic(self._biz_id, device_id)
                except ValueError:
                    self._subscribed_devices.discard(device_id)
                    _LOGGER.warning(
                        "Skipping invalid MQTT subscription device ID %s: invalid characters",
                        _redact_identifier(device_id) or "***",
                    )
                    continue
                subscribe_pairs.append((device_id, topic))

            for i in range(0, len(subscribe_pairs), _MQTT_SUBSCRIPTION_BATCH_SIZE):
                batch = subscribe_pairs[i : i + _MQTT_SUBSCRIPTION_BATCH_SIZE]
                await client.subscribe([(topic, MQTT_QOS) for _, topic in batch])
                for device_id, _ in batch:
                    _LOGGER.debug(
                        "Subscribed to device %s",
                        _redact_identifier(device_id) or "***",
                    )

            # Now mark connected and fire callback
            self._connected = True
            _LOGGER.info("Connected to MQTT broker")
            on_connect_failed = False
            if self._on_connect:
                try:
                    self._on_connect()
                except Exception as err:
                    on_connect_failed = True
                    self._set_last_error(err)
                    _LOGGER.exception(
                        "MQTT on_connect callback failed (%s)",
                        type(err).__name__,
                    )
            if not on_connect_failed:
                self._clear_last_error()

            # Process incoming messages
            async for message in client.messages:
                self._process_message(message)

    def _handle_disconnect(self, reason: str) -> None:
        """Handle disconnection from broker."""
        self._connected = False
        self._client = None
        _LOGGER.warning("MQTT disconnected: %s", reason)

        if self._on_disconnect:
            try:
                self._on_disconnect()
            except Exception as err:
                self._set_last_error(err)
                _LOGGER.exception(
                    "MQTT on_disconnect callback failed (%s)",
                    type(err).__name__,
                )

    def _log_invalid_topic(self, topic: str) -> None:
        """Record and log invalid topic metadata without exposing topic content."""
        self._invalid_topic_count += 1
        if _LOGGER.isEnabledFor(logging.DEBUG):
            _LOGGER.debug(
                "Invalid topic format (count=%d, len=%d), skipping message",
                self._invalid_topic_count,
                len(topic),
            )
            return
        _LOGGER.warning(
            "Invalid topic format, skipping message (count=%d)",
            self._invalid_topic_count,
        )

    @staticmethod
    def _decode_payload_text(raw_payload: Any, device_id: str) -> str | None:
        """Decode MQTT payload to UTF-8 text with unified size/type checks."""
        if isinstance(raw_payload, memoryview):
            raw_payload = raw_payload.tobytes()

        if isinstance(raw_payload, (bytes, bytearray)):
            raw_bytes = bytes(raw_payload)
            payload_size = len(raw_bytes)
            if payload_size > _MAX_MQTT_PAYLOAD_BYTES:
                _LOGGER.warning(
                    "MQTT [%s]: payload too large (%d bytes), skipping",
                    _redact_identifier(device_id) or "***",
                    payload_size,
                )
                return None
            return raw_bytes.decode("utf-8")

        if isinstance(raw_payload, str):
            payload_size = len(raw_payload.encode("utf-8"))
            if payload_size > _MAX_MQTT_PAYLOAD_BYTES:
                _LOGGER.warning(
                    "MQTT [%s]: payload too large (%d bytes), skipping",
                    _redact_identifier(device_id) or "***",
                    payload_size,
                )
                return None
            return raw_payload

        _LOGGER.debug(
            "MQTT [%s]: unexpected payload type %s, skipping",
            _redact_identifier(device_id) or "***",
            type(raw_payload).__name__,
        )
        return None

    def _process_message(self, message: aiomqtt.Message) -> None:
        """Process incoming MQTT message.

        Args:
            message: MQTT message object.

        """
        try:
            topic = str(message.topic)
            device_id = parse_topic(topic)

            if not device_id:
                self._log_invalid_topic(topic)
                return

            device_id_log = _redact_identifier(device_id) or "***"

            if not message.payload:
                _LOGGER.debug("MQTT [%s]: empty payload, skipping", device_id_log)
                return

            payload_text = self._decode_payload_text(message.payload, device_id)
            if payload_text is None:
                return

            payload = json.loads(payload_text)
            if not isinstance(payload, dict):
                _LOGGER.debug(
                    "MQTT [%s]: unexpected payload type %s, skipping",
                    device_id_log,
                    type(payload).__name__,
                )
                return

            if _LOGGER.isEnabledFor(logging.DEBUG):
                _LOGGER.debug(
                    "MQTT [%s]: %s",
                    device_id_log,
                    _format_mqtt_payload_for_log(payload)[:_MAX_MQTT_LOG_CHARS],
                )

            # Parse and flatten payload to REST API format
            properties = parse_mqtt_payload(payload)

            if self._on_message and properties:
                try:
                    self._on_message(device_id, properties)
                except Exception as err:
                    self._set_last_error(err)
                    _LOGGER.exception(
                        "MQTT on_message callback failed (%s)",
                        type(err).__name__,
                    )
                    return

            self._clear_last_error()

        except (json.JSONDecodeError, UnicodeError) as err:
            self._set_last_error(err)
            _LOGGER.exception("Failed to decode MQTT payload")
        except Exception as err:
            self._set_last_error(err)
            topic = str(getattr(message, "topic", "unknown"))
            device_id = parse_topic(topic)
            topic_context = (
                f"device={_redact_identifier(device_id) or '***'}"
                if device_id
                else f"invalid_topic_len={len(topic)}"
            )
            _LOGGER.exception(
                "Error processing MQTT message (%s, error=%s)",
                topic_context,
                type(err).__name__,
            )

    def _async_finalize_connection_task(self, task: asyncio.Task[Any]) -> None:
        """Consume background connection task result and persist terminal errors."""
        if self._task is task:
            self._task = None

        err = self._consume_task_exception(task)
        if err is None:
            return
        self._set_last_error(err)

    @staticmethod
    def _consume_task_exception(task: asyncio.Task[Any]) -> Exception | None:
        """Consume task exceptions to avoid unhandled-task warnings."""
        try:
            task.result()
        except asyncio.CancelledError:
            return None
        except Exception as err:  # noqa: BLE001
            _LOGGER.debug(
                "MQTT background task failed (%s)",
                type(err).__name__,
            )
            return err
        return None

    def _set_last_error(self, err: Exception) -> None:
        """Persist latest error and notify optional observer."""
        self._last_error = err
        if self._on_error is None:
            return
        try:
            self._on_error(err)
        except Exception as callback_err:
            _LOGGER.exception(
                "MQTT error callback failed (%s)",
                type(callback_err).__name__,
            )

    def _clear_last_error(self) -> None:
        """Clear latest error state after successful processing."""
        self._last_error = None
