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
import base64
import binascii
import contextlib
from dataclasses import dataclass
import hashlib
import hmac
import json
import logging
import random
import re
import ssl
from typing import TYPE_CHECKING, Any, Final

import aiomqtt
from Crypto.Cipher import AES

from ..const.api import (
    MQTT_AES_KEY,
    MQTT_BROKER_HOST,
    MQTT_BROKER_PORT,
    MQTT_INSTANCE_ID,
    MQTT_KEEP_ALIVE,
    MQTT_QOS,
    MQTT_RECONNECT_JITTER,
    MQTT_RECONNECT_MAX_DELAY,
    MQTT_RECONNECT_MIN_DELAY,
    MQTT_TOPIC_PREFIX,
)

if TYPE_CHECKING:
    from collections.abc import Callable

_LOGGER = logging.getLogger(__name__)


# =============================================================================
# Credential Management
# =============================================================================


def decrypt_mqtt_credential(encrypted_hex: str) -> str:
    """Decrypt MQTT credential using AES/ECB/PKCS5Padding.

    The credentials from API are AES encrypted and hex encoded.

    Args:
        encrypted_hex: Hex-encoded encrypted credential from API.

    Returns:
        Decrypted credential string.

    Raises:
        ValueError: If decryption fails.

    """
    try:
        encrypted_bytes = binascii.unhexlify(encrypted_hex)
        cipher = AES.new(MQTT_AES_KEY.encode("utf-8"), AES.MODE_ECB)
        decrypted = cipher.decrypt(encrypted_bytes)

        # Remove PKCS5 padding with validation
        padding_len = decrypted[-1]
        # AES block size is 16 bytes, padding must be 1-16
        if not 1 <= padding_len <= 16:
            msg = f"Invalid PKCS5 padding length: {padding_len}"
            raise ValueError(msg)
        # Verify all padding bytes have the same value
        if decrypted[-padding_len:] != bytes([padding_len]) * padding_len:
            msg = "Invalid PKCS5 padding bytes"
            raise ValueError(msg)
        decrypted = decrypted[:-padding_len]

        return decrypted.decode("utf-8")
    except (ValueError, UnicodeDecodeError, binascii.Error, IndexError) as err:
        msg = f"Failed to decrypt MQTT credential: {err}"
        raise ValueError(msg) from err


@dataclass
class MqttCredentials:
    """MQTT connection credentials."""

    client_id: str
    username: str
    password: str

    @classmethod
    def create(
        cls,
        access_key: str,
        secret_key: str,
        biz_id: str,
        phone_id: str,
    ) -> MqttCredentials:
        """Create MQTT credentials from decrypted keys.

        Args:
            access_key: Decrypted MQTT access key.
            secret_key: Decrypted MQTT secret key.
            biz_id: Business ID (without 'lip_' prefix).
            phone_id: Device UUID.

        Returns:
            MqttCredentials instance.

        """
        # Client ID: GID_App@@@{bizId}-android-{phoneId} (max 64 chars)
        client_id = f"GID_App@@@{biz_id}-android-{phone_id}"[:64]

        # Username: Signature|{accessKey}|{instanceId}
        username = f"Signature|{access_key}|{MQTT_INSTANCE_ID}"

        # Password: HmacSHA1(clientId, secretKey) -> Base64
        signature = hmac.new(
            secret_key.encode("utf-8"),
            client_id.encode("utf-8"),
            hashlib.sha1,
        ).digest()
        password = base64.b64encode(signature).decode("utf-8")

        return cls(client_id=client_id, username=username, password=password)


# =============================================================================
# Topic Helpers
# =============================================================================


def build_topic(biz_id: str, device_id: str) -> str:
    """Build MQTT topic for device status subscription.

    Format: Topic_Device_State/{bizId}/{deviceId}

    Args:
        biz_id: Business ID (alphanumeric and hyphens only).
        device_id: Device ID - can be IoT device ID (e.g., "03ab5ccd7cxxxxxx")
                   or mesh group serial (e.g., "mesh_group_10001").

    Returns:
        MQTT topic string.

    Raises:
        ValueError: If biz_id or device_id contains invalid characters.

    """
    # Validate inputs to prevent MQTT topic injection
    if not biz_id or not all(c.isalnum() or c in "-_" for c in biz_id):
        msg = f"Invalid biz_id format: {biz_id}"
        raise ValueError(msg)
    if not device_id or not all(c.isalnum() or c in "-_" for c in device_id):
        msg = f"Invalid device_id format: {device_id}"
        raise ValueError(msg)

    return f"{MQTT_TOPIC_PREFIX}/{biz_id}/{device_id}"


def parse_topic(topic: str) -> str | None:
    """Extract device ID from MQTT topic.

    Only accepts topics with the expected prefix to avoid extracting
    device IDs from unexpected topic formats.

    Args:
        topic: MQTT topic string.

    Returns:
        Device ID or None if invalid topic format or wrong prefix.

    """
    parts = topic.split("/")
    if len(parts) != 3:
        return None
    if parts[0] != MQTT_TOPIC_PREFIX:
        return None
    biz_id = parts[1]
    device_id = parts[2]
    if not biz_id or not all(c.isalnum() or c in "-_" for c in biz_id):
        return None
    if not device_id or not all(c.isalnum() or c in "-_" for c in device_id):
        return None
    return device_id


# =============================================================================
# Payload Parsing
# =============================================================================

# MQTT to REST API property key mappings
_PROPERTY_KEY_MAP: Final[dict[str, str]] = {
    # Fan light (different casing)
    "fanOnOff": "fanOnoff",
    # Curtain (different naming)
    "progress": "position",
    "state": "moving",
}

# Values that indicate "not supported" in MQTT payloads — skip these
_NOISE_VALUES: Final[frozenset[str]] = frozenset({"-1", ""})

# Hard limit for incoming MQTT payloads to avoid excessive memory/log churn.
_MAX_MQTT_PAYLOAD_BYTES: Final[int] = 64 * 1024
# Max payload preview length in debug logs.
_MAX_MQTT_LOG_CHARS: Final[int] = 200

# Keys frequently carrying credentials/identifiers in MQTT payloads.
_MQTT_LOG_SENSITIVE_KEYS: Final[frozenset[str]] = frozenset(
    {
        "authorization",
        "accesstoken",
        "refreshtoken",
        "apikey",
        "accesskey",
        "secretkey",
        "secret",
        "password",
        "wifissid",
        "mac",
        "macaddress",
        "blemac",
        "ip",
        "ipaddress",
        "deviceid",
        "iotdeviceid",
        "gatewaydeviceid",
        "serial",
    }
)

_MQTT_LOG_STRING_PATTERNS: Final[tuple[tuple[re.Pattern[str], str], ...]] = (
    (
        re.compile(r"(?i)(authorization\s*[:=]\s*bearer\s+)[^\s,;\"']+"),
        r"\1***",
    ),
    (
        re.compile(
            r"(?i)\b(access[_-]?token|refresh[_-]?token|api[_-]?key|secret|password)\b(\s*[:=]\s*)([^\s,;\"']+)"
        ),
        r"\1\2***",
    ),
    (
        re.compile(r"([0-9A-Fa-f]{2}[:-]){5}[0-9A-Fa-f]{2}"),
        "***",
    ),
    (
        re.compile(r"\b\d{1,3}(?:\.\d{1,3}){3}\b"),
        "***",
    ),
    (
        re.compile(r"(?<![A-Za-z0-9])[A-Za-z0-9._~+/=-]{32,}(?![A-Za-z0-9])"),
        "***",
    ),
)


# MQTT payload property groups that contain device state
_MQTT_PROPERTY_GROUPS: Final[tuple[str, ...]] = (
    "common",
    "light",
    "fanLight",
    "switchs",
    "outlet",
    "curtain",
    "gateway",
)


def parse_mqtt_payload(payload: Any) -> dict[str, Any]:
    """Parse MQTT payload and flatten properties.

    The MQTT payload contains grouped properties (common, light, fanLight, etc.).
    This function flattens them into a single dict matching REST API format.

    Args:
        payload: Raw MQTT payload with grouped properties.

    Returns:
        Flattened properties dict compatible with REST API format.

    """
    if not isinstance(payload, dict):
        return {}

    properties: dict[str, Any] = {}

    # Process each property group
    for group_name in _MQTT_PROPERTY_GROUPS:
        group_data = payload.get(group_name)
        if not isinstance(group_data, dict):
            continue

        for mqtt_key, value in group_data.items():
            # Skip noise values: "-1" means unsupported, "" means empty
            if isinstance(value, str) and value in _NOISE_VALUES:
                continue
            # Map to REST API key if needed, otherwise use original
            key = str(mqtt_key)
            rest_key: str = _PROPERTY_KEY_MAP.get(key, key)
            properties[rest_key] = value

    return properties


def _sanitize_mqtt_log_value(value: Any, key: str | None = None) -> Any:
    """Sanitize MQTT payload values before debug logging."""
    if key is not None:
        normalized_key = key.strip().lower().replace("_", "").replace("-", "")
        if normalized_key in _MQTT_LOG_SENSITIVE_KEYS:
            return "***"

    if isinstance(value, dict):
        return {str(k): _sanitize_mqtt_log_value(v, str(k)) for k, v in value.items()}

    if isinstance(value, list):
        return [_sanitize_mqtt_log_value(item) for item in value]

    if isinstance(value, str):
        stripped = value.strip()
        if stripped and stripped[0] in "{[":
            try:
                parsed = json.loads(value)
            except (TypeError, ValueError):
                pass
            else:
                redacted = _sanitize_mqtt_log_value(parsed)
                if isinstance(redacted, (dict, list)):
                    return json.dumps(
                        redacted,
                        ensure_ascii=False,
                        separators=(",", ":"),
                    )

        sanitized = value
        for pattern, replacement in _MQTT_LOG_STRING_PATTERNS:
            sanitized = pattern.sub(replacement, sanitized)
        return sanitized

    return value


def _format_mqtt_payload_for_log(payload: dict[str, Any]) -> str:
    """Return a redacted string representation suitable for debug logs."""
    sanitized = _sanitize_mqtt_log_value(payload)
    return json.dumps(
        sanitized,
        ensure_ascii=False,
        separators=(",", ":"),
    )


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

        self._subscribed_devices: set[str] = set()
        self._client: aiomqtt.Client | None = None
        self._task: asyncio.Task | None = None
        self._running = False
        self._connected = False
        self._reconnect_delay = MQTT_RECONNECT_MIN_DELAY

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

        _LOGGER.info(
            "MQTT client started, subscribing to %d devices",
            len(device_ids),
        )

    async def stop(self) -> None:
        """Stop MQTT client and clean up resources."""
        self._running = False

        if self._task:
            self._task.cancel()
            with contextlib.suppress(asyncio.CancelledError):
                await self._task
            self._task = None

        self._connected = False
        self._client = None
        self._subscribed_devices.clear()
        _LOGGER.info("MQTT client stopped")

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
                    except ValueError as err:
                        _LOGGER.warning(
                            "Skipping invalid MQTT device ID %s: %s", device_id, err
                        )
                        continue
                    subscribe_pairs.append((device_id, topic))

                for i in range(0, len(subscribe_pairs), _MQTT_SUBSCRIPTION_BATCH_SIZE):
                    batch = subscribe_pairs[i : i + _MQTT_SUBSCRIPTION_BATCH_SIZE]
                    topics = [(topic, MQTT_QOS) for _, topic in batch]
                    try:
                        await self._client.subscribe(topics)
                    except aiomqtt.MqttError:
                        _LOGGER.exception(
                            "Failed to subscribe to %d MQTT topics",
                            len(topics),
                        )
                        continue

                    for device_id, topic in batch:
                        self._subscribed_devices.add(device_id)
                        added += 1
                        _LOGGER.debug("Subscribed to: %s", topic)
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
                    except ValueError as err:
                        _LOGGER.warning(
                            "Skipping MQTT unsubscribe for invalid device ID %s: %s",
                            device_id,
                            err,
                        )
                        continue
                    unsubscribe_topics.append(topic)

                for i in range(
                    0, len(unsubscribe_topics), _MQTT_SUBSCRIPTION_BATCH_SIZE
                ):
                    batch = unsubscribe_topics[i : i + _MQTT_SUBSCRIPTION_BATCH_SIZE]
                    try:
                        await self._client.unsubscribe(batch)
                    except aiomqtt.MqttError:
                        _LOGGER.exception(
                            "Failed to unsubscribe from %d MQTT topics",
                            len(batch),
                        )
                        continue

                    for topic in batch:
                        _LOGGER.debug("Unsubscribed from: %s", topic)

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
                self._handle_disconnect(f"MQTT error: {err}")
            except asyncio.CancelledError:
                break
            except OSError as err:
                self._handle_disconnect(f"Connection error: {err}")
            except ValueError as err:
                self._handle_disconnect(f"MQTT value error: {err}")
            except Exception as err:
                _LOGGER.exception(
                    "Unexpected MQTT loop error (%s)",
                    type(err).__name__,
                )
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
        tls_context = ssl.create_default_context()
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
                except ValueError as err:
                    self._subscribed_devices.discard(device_id)
                    _LOGGER.warning(
                        "Skipping invalid MQTT subscription device ID %s: %s",
                        device_id,
                        err,
                    )
                    continue
                subscribe_pairs.append((device_id, topic))

            for i in range(0, len(subscribe_pairs), _MQTT_SUBSCRIPTION_BATCH_SIZE):
                batch = subscribe_pairs[i : i + _MQTT_SUBSCRIPTION_BATCH_SIZE]
                await client.subscribe([(topic, MQTT_QOS) for _, topic in batch])
                for _, topic in batch:
                    _LOGGER.debug("Subscribed to: %s", topic)

            # Now mark connected and fire callback
            self._connected = True
            _LOGGER.info("Connected to MQTT broker")
            if self._on_connect:
                self._on_connect()

            # Process incoming messages
            async for message in client.messages:
                self._process_message(message)

    def _handle_disconnect(self, reason: str) -> None:
        """Handle disconnection from broker."""
        self._connected = False
        self._client = None
        _LOGGER.warning("MQTT disconnected: %s", reason)

        if self._on_disconnect:
            self._on_disconnect()

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
                    device_id,
                    payload_size,
                )
                return None
            return raw_bytes.decode("utf-8")

        if isinstance(raw_payload, str):
            payload_size = len(raw_payload.encode("utf-8"))
            if payload_size > _MAX_MQTT_PAYLOAD_BYTES:
                _LOGGER.warning(
                    "MQTT [%s]: payload too large (%d bytes), skipping",
                    device_id,
                    payload_size,
                )
                return None
            return raw_payload

        _LOGGER.debug(
            "MQTT [%s]: unexpected payload type %s, skipping",
            device_id,
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
                _LOGGER.warning("Invalid topic format: %s", topic)
                return

            if not message.payload:
                _LOGGER.debug("MQTT: empty payload on topic %s, skipping", topic)
                return

            payload_text = self._decode_payload_text(message.payload, device_id)
            if payload_text is None:
                return

            payload = json.loads(payload_text)
            if not isinstance(payload, dict):
                _LOGGER.debug(
                    "MQTT [%s]: unexpected payload type %s, skipping",
                    device_id,
                    type(payload).__name__,
                )
                return

            if _LOGGER.isEnabledFor(logging.DEBUG):
                _LOGGER.debug(
                    "MQTT [%s]: %s",
                    device_id,
                    _format_mqtt_payload_for_log(payload)[:_MAX_MQTT_LOG_CHARS],
                )

            # Parse and flatten payload to REST API format
            properties = parse_mqtt_payload(payload)

            if self._on_message and properties:
                self._on_message(device_id, properties)

        except (json.JSONDecodeError, UnicodeError):
            _LOGGER.exception("Failed to decode MQTT payload")
        except Exception as err:
            _LOGGER.exception(
                "Error processing MQTT message (topic=%s, error=%s)",
                getattr(message, "topic", "unknown"),
                type(err).__name__,
            )
