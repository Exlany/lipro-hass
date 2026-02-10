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
from typing import TYPE_CHECKING, Any

import aiomqtt
from Crypto.Cipher import AES

from .const import (
    MQTT_AES_KEY,
    MQTT_BROKER_HOST,
    MQTT_BROKER_PORT,
    MQTT_INSTANCE_ID,
    MQTT_KEEP_ALIVE,
    MQTT_QOS,
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
    except (ValueError, binascii.Error) as err:
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

    Args:
        topic: MQTT topic string.

    Returns:
        Device ID or None if invalid topic format.

    """
    parts = topic.split("/")
    return parts[2] if len(parts) >= 3 else None


# =============================================================================
# Payload Parsing
# =============================================================================

# MQTT to REST API property key mappings
_PROPERTY_KEY_MAP: dict[str, str] = {
    # Fan light (different casing)
    "fanOnOff": "fanOnoff",
    # Curtain (different naming)
    "progress": "position",
    "state": "moving",
}


def parse_mqtt_payload(payload: dict[str, Any]) -> dict[str, Any]:
    """Parse MQTT payload and flatten properties.

    The MQTT payload contains grouped properties (common, light, fanLight, etc.).
    This function flattens them into a single dict matching REST API format.

    Args:
        payload: Raw MQTT payload with grouped properties.

    Returns:
        Flattened properties dict compatible with REST API format.

    """
    properties: dict[str, Any] = {}

    # Process each property group
    groups = ("common", "light", "fanLight", "switchs", "outlet", "curtain", "gateway")

    for group_name in groups:
        group_data = payload.get(group_name)
        if not isinstance(group_data, dict):
            continue

        for mqtt_key, value in group_data.items():
            # Map to REST API key if needed, otherwise use original
            rest_key = _PROPERTY_KEY_MAP.get(mqtt_key, mqtt_key)
            properties[rest_key] = value

    return properties


# =============================================================================
# MQTT Client
# =============================================================================


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

    async def subscribe_device(self, device_id: str) -> None:
        """Subscribe to a new device's status updates.

        Args:
            device_id: IoT device ID to subscribe.

        """
        if device_id in self._subscribed_devices:
            return

        self._subscribed_devices.add(device_id)

        if self._client and self._connected:
            topic = build_topic(self._biz_id, device_id)
            try:
                await self._client.subscribe(topic, qos=MQTT_QOS)
                _LOGGER.debug("Subscribed to: %s", topic)
            except aiomqtt.MqttError:
                _LOGGER.exception("Failed to subscribe to %s", topic)

    async def unsubscribe_device(self, device_id: str) -> None:
        """Unsubscribe from a device's status updates.

        Args:
            device_id: IoT device ID to unsubscribe.

        """
        if device_id not in self._subscribed_devices:
            return

        self._subscribed_devices.discard(device_id)

        if self._client and self._connected:
            topic = build_topic(self._biz_id, device_id)
            try:
                await self._client.unsubscribe(topic)
                _LOGGER.debug("Unsubscribed from: %s", topic)
            except aiomqtt.MqttError:
                _LOGGER.exception("Failed to unsubscribe from %s", topic)

    async def _connection_loop(self) -> None:
        """Main connection loop with auto-reconnect."""
        while self._running:
            try:
                await self._connect_and_listen()
            except aiomqtt.MqttError as err:
                self._handle_disconnect(f"MQTT error: {err}")
            except asyncio.CancelledError:
                break
            except OSError as err:
                self._handle_disconnect(f"Connection error: {err}")

            # Wait before reconnecting
            if self._running:
                _LOGGER.info("Reconnecting in %ds...", self._reconnect_delay)
                await asyncio.sleep(self._reconnect_delay)
                self._reconnect_delay = min(
                    self._reconnect_delay * 2,
                    MQTT_RECONNECT_MAX_DELAY,
                )

        self._connected = False
        self._client = None

    async def _connect_and_listen(self) -> None:
        """Connect to broker and listen for messages."""
        async with aiomqtt.Client(
            hostname=MQTT_BROKER_HOST,
            port=MQTT_BROKER_PORT,
            username=self._credentials.username,
            password=self._credentials.password,
            identifier=self._credentials.client_id,
            clean_session=False,
            keepalive=MQTT_KEEP_ALIVE,
        ) as client:
            self._client = client
            self._connected = True
            self._reconnect_delay = MQTT_RECONNECT_MIN_DELAY

            _LOGGER.info("Connected to MQTT broker")
            if self._on_connect:
                self._on_connect()

            # Subscribe to all device topics
            for device_id in self._subscribed_devices:
                topic = build_topic(self._biz_id, device_id)
                await client.subscribe(topic, qos=MQTT_QOS)
                _LOGGER.debug("Subscribed to: %s", topic)

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

            payload = json.loads(message.payload.decode("utf-8"))
            _LOGGER.debug(
                "MQTT [%s]: %s",
                device_id,
                json.dumps(payload, ensure_ascii=False)[:200],
            )

            # Parse and flatten payload to REST API format
            properties = parse_mqtt_payload(payload)

            if self._on_message and properties:
                self._on_message(device_id, properties)

        except json.JSONDecodeError:
            _LOGGER.exception("Invalid JSON payload")
        except (TypeError, AttributeError):
            _LOGGER.exception("Error processing message")
