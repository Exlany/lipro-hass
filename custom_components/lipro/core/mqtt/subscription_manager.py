"""Subscription lifecycle helpers extracted from the MQTT client."""

from __future__ import annotations

from collections.abc import Callable
import logging

import aiomqtt

from ...const.api import MQTT_QOS
from ..utils.redaction import redact_identifier as _redact_identifier
from .topic_builder import MqttTopicBuilder

_LOGGER = logging.getLogger(__package__ or __name__)


class MqttSubscriptionManager:
    """Manage desired MQTT subscriptions while keeping client API stable."""

    def __init__(self, topic_builder: MqttTopicBuilder) -> None:
        """Store the topic builder used by subscription operations."""
        self._topic_builder = topic_builder

    def build_topic_pairs(
        self,
        device_ids: list[str] | set[str],
        *,
        invalid_log_message: str,
        on_invalid: Callable[[str], None] | None = None,
    ) -> list[tuple[str, str]]:
        """Build valid MQTT topic pairs while centralizing invalid-ID handling."""
        return self._topic_builder.build_topic_pairs(
            device_ids,
            invalid_log_message=invalid_log_message,
            on_invalid=on_invalid,
        )

    def batch_topic_pairs(
        self,
        topic_pairs: list[tuple[str, str]],
    ) -> list[list[tuple[str, str]]]:
        """Split topic pairs into MQTT-sized batches."""
        return self._topic_builder.batch_topic_pairs(topic_pairs)

    async def subscribe_topic_pairs(
        self,
        client: aiomqtt.Client,
        topic_pairs: list[tuple[str, str]],
        *,
        subscribed_devices: set[str],
        update_subscription_state: bool,
        raise_on_error: bool,
    ) -> int:
        """Subscribe topic batches and optionally track successful device IDs."""
        added = 0
        for batch in self.batch_topic_pairs(topic_pairs):
            subscribe_topics = [(topic, MQTT_QOS) for _, topic in batch]
            try:
                await client.subscribe(subscribe_topics)
            except aiomqtt.MqttError:
                if raise_on_error:
                    raise
                _LOGGER.exception(
                    "Failed to subscribe to %d MQTT topics",
                    len(subscribe_topics),
                )
                continue
            for device_id, _topic in batch:
                if update_subscription_state:
                    subscribed_devices.add(device_id)
                added += 1
                _LOGGER.debug(
                    "Subscribed to device %s",
                    _redact_identifier(device_id) or "***",
                )
        return added

    async def unsubscribe_topic_pairs(
        self,
        client: aiomqtt.Client,
        topic_pairs: list[tuple[str, str]],
        *,
        pending_unsubscribe: set[str],
        subscribed_devices: set[str] | None = None,
    ) -> None:
        """Unsubscribe topic batches and clear pending removals on success."""
        for batch in self.batch_topic_pairs(topic_pairs):
            try:
                await client.unsubscribe([topic for _, topic in batch])
            except aiomqtt.MqttError:
                _LOGGER.exception(
                    "Failed to unsubscribe from %d MQTT topics",
                    len(batch),
                )
                continue
            for device_id, _topic in batch:
                pending_unsubscribe.discard(device_id)
                if subscribed_devices is not None:
                    subscribed_devices.discard(device_id)
                _LOGGER.debug(
                    "Unsubscribed from device %s",
                    _redact_identifier(device_id) or "***",
                )

    async def apply_pending_unsubscribes(
        self,
        client: aiomqtt.Client,
        *,
        pending_unsubscribe: set[str],
        subscribed_devices: set[str] | None = None,
    ) -> None:
        """Best-effort replay of queued unsubscribes after reconnect."""
        if not pending_unsubscribe:
            return

        def _drop_invalid_device(device_id: str) -> None:
            pending_unsubscribe.discard(device_id)
            if subscribed_devices is not None:
                subscribed_devices.discard(device_id)

        topic_pairs = self.build_topic_pairs(
            list(pending_unsubscribe),
            invalid_log_message=(
                "Skipping MQTT unsubscribe for invalid device ID %s: invalid characters"
            ),
            on_invalid=_drop_invalid_device,
        )
        await self.unsubscribe_topic_pairs(
            client,
            topic_pairs,
            pending_unsubscribe=pending_unsubscribe,
            subscribed_devices=subscribed_devices,
        )

    async def subscribe_current_devices(
        self,
        client: aiomqtt.Client,
        *,
        subscribed_devices: set[str],
    ) -> None:
        """Subscribe all desired devices before marking the client connected."""
        topic_pairs = self.build_topic_pairs(
            list(subscribed_devices),
            invalid_log_message=(
                "Skipping invalid MQTT subscription device ID %s: invalid characters"
            ),
            on_invalid=subscribed_devices.discard,
        )
        await self.subscribe_topic_pairs(
            client,
            topic_pairs,
            subscribed_devices=subscribed_devices,
            update_subscription_state=False,
            raise_on_error=True,
        )

    async def sync_subscriptions(
        self,
        *,
        client: aiomqtt.Client | None,
        connected: bool,
        subscribed_devices: set[str],
        pending_unsubscribe: set[str],
        device_ids: set[str],
    ) -> tuple[int, int]:
        """Sync subscriptions to match the given device ID set."""
        to_add = device_ids - subscribed_devices
        to_remove = subscribed_devices - device_ids
        if not to_add and not to_remove:
            return 0, 0
        added = 0
        if to_add:
            pending_unsubscribe.difference_update(to_add)
            if connected and client is not None:
                topic_pairs = self.build_topic_pairs(
                    to_add,
                    invalid_log_message=(
                        "Skipping invalid MQTT device ID %s: invalid characters"
                    ),
                )
                added = await self.subscribe_topic_pairs(
                    client,
                    topic_pairs,
                    subscribed_devices=subscribed_devices,
                    update_subscription_state=True,
                    raise_on_error=False,
                )
            else:
                subscribed_devices.update(to_add)
                added += len(to_add)
        removed = len(to_remove)
        if to_remove and connected and client is not None:
            pending_unsubscribe.update(to_remove)

            def _drop_invalid_device(device_id: str) -> None:
                pending_unsubscribe.discard(device_id)
                subscribed_devices.discard(device_id)

            topic_pairs = self.build_topic_pairs(
                to_remove,
                invalid_log_message=(
                    "Skipping MQTT unsubscribe for invalid device ID %s: invalid characters"
                ),
                on_invalid=_drop_invalid_device,
            )
            await self.unsubscribe_topic_pairs(
                client,
                topic_pairs,
                pending_unsubscribe=pending_unsubscribe,
                subscribed_devices=subscribed_devices,
            )
        elif to_remove:
            for device_id in to_remove:
                subscribed_devices.discard(device_id)
                pending_unsubscribe.add(device_id)
        return added, removed


__all__ = ["MqttSubscriptionManager"]
