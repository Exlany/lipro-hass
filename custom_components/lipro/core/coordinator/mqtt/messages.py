"""MQTT message handling mixin for the coordinator."""

from __future__ import annotations

import asyncio
import logging
from time import monotonic
from typing import Any, Final

from ....const import PROP_CONNECT_STATE
from ....const.api import MAX_MQTT_CACHE_SIZE
from ...device import LiproDevice
from ...mqtt.message import (
    build_dedup_cache_key,
    cleanup_dedup_cache,
    compute_properties_hash,
    is_duplicate_within_window,
    is_online_connect_state,
)
from ...utils.redaction import redact_identifier as _redact_identifier
from .lifecycle import _MqttLifecycleMixin

_LOGGER = logging.getLogger(__name__)

# Coalesce MQTT-driven listener updates to reduce event-loop churn under bursts.
_MQTT_LISTENER_UPDATE_DEBOUNCE_SECONDS: Final[float] = 0.05

# Time threshold (seconds) for cleaning stale MQTT dedup cache entries.
_MQTT_CACHE_STALE_SECONDS: Final[float] = 5.0

# Cooldown for MQTT group online reconciliation refresh to avoid refresh storms
# when connectState flaps or multiple sub-devices reconnect in bursts.
_MQTT_GROUP_ONLINE_RECONCILE_COOLDOWN_SECONDS: Final[float] = 5.0


class _MqttMixin(_MqttLifecycleMixin):
    """Coordinator mixin for MQTT message handling, dedup, and reconciliation."""

    def _on_mqtt_message(self, device_id: str, properties: dict[str, Any]) -> None:
        """Handle MQTT message with device status update."""
        device = self._resolve_mqtt_message_device(device_id)
        if not device:
            return

        current_time = monotonic()
        if self._is_duplicate_mqtt_payload(
            device_id=device_id,
            device_name=device.name,
            properties=properties,
            current_time=current_time,
        ):
            return

        applied = self._apply_properties_update(device, properties)
        self._after_mqtt_properties_applied(device, applied, current_time=current_time)

    def _schedule_mqtt_listener_update(self) -> None:
        """Coalesce listener updates triggered by MQTT bursts."""
        if not self.hass.loop.is_running():
            self.async_update_listeners()
            return

        if self._mqtt_listener_update_handle is not None:
            return

        self._mqtt_listener_update_handle = self.hass.loop.call_later(
            _MQTT_LISTENER_UPDATE_DEBOUNCE_SECONDS,
            self._flush_mqtt_listener_update,
        )

    def _flush_mqtt_listener_update(self) -> None:
        """Flush one coalesced MQTT listener update."""
        self._mqtt_listener_update_handle = None
        self.async_update_listeners()

    def _resolve_mqtt_message_device(self, device_id: str) -> LiproDevice | None:
        """Resolve MQTT message target device by known identifier mappings."""
        device = self.get_device_by_id(device_id)
        if device is not None:
            return device

        _LOGGER.debug(
            "MQTT message for unknown device: %s",
            _redact_identifier(device_id) or "***",
        )
        return None

    @staticmethod
    def _normalize_device_key(device_id: str) -> str:
        """Normalize runtime device identifiers for per-device caches."""
        return device_id.strip().lower()

    def _is_duplicate_mqtt_payload(
        self,
        *,
        device_id: str,
        device_name: str,
        properties: dict[str, Any],
        current_time: float,
    ) -> bool:
        """Return True when payload duplicates a recent MQTT message for the device."""
        props_hash = compute_properties_hash(properties)
        if props_hash is None:
            _LOGGER.debug(
                "MQTT: cannot hash properties for %s, skipping dedup", device_name
            )
            return False

        cache_key = build_dedup_cache_key(device_id, props_hash)
        if is_duplicate_within_window(
            self._mqtt_message_cache,
            cache_key=cache_key,
            current_time=current_time,
            dedup_window=self._mqtt_dedup_window,
        ):
            if self._debug_mode:
                last_time = self._mqtt_message_cache.get(cache_key)
                if last_time is not None:
                    _LOGGER.debug(
                        "MQTT: skipping duplicate message for %s (%.2fs ago)",
                        device_name,
                        current_time - last_time,
                    )
            return True

        self._mqtt_message_cache[cache_key] = current_time
        if len(self._mqtt_message_cache) > MAX_MQTT_CACHE_SIZE:
            self._cleanup_mqtt_cache(current_time)
        return False

    def _schedule_mqtt_group_online_reconciliation(
        self, *, device_name: str, now: float
    ) -> None:
        """Schedule one REST refresh for group-online MQTT reconnect bursts."""
        task = self._mqtt_group_online_reconcile_task
        if task is not None and not task.done():
            return

        if (
            self._mqtt_group_online_reconcile_last_at > 0
            and now - self._mqtt_group_online_reconcile_last_at
            < _MQTT_GROUP_ONLINE_RECONCILE_COOLDOWN_SECONDS
        ):
            return

        self._mqtt_group_online_reconcile_last_at = now
        _LOGGER.debug(
            "MQTT: device %s online, scheduling REST API reconciliation",
            device_name,
        )
        task = self._track_background_task(self.async_request_refresh())
        self._mqtt_group_online_reconcile_task = task
        task.add_done_callback(self._clear_mqtt_group_online_reconcile_task)

    def _clear_mqtt_group_online_reconcile_task(self, task: asyncio.Task[Any]) -> None:
        """Clear single-flight task handle once reconciliation completes."""
        if task is self._mqtt_group_online_reconcile_task:
            self._mqtt_group_online_reconcile_task = None

    def _after_mqtt_properties_applied(
        self,
        device: LiproDevice,
        properties: dict[str, Any],
        *,
        current_time: float | None = None,
    ) -> None:
        """Run post-update notifications and reconciliation scheduling hooks."""
        if not properties:
            return

        self._schedule_mqtt_listener_update()

        connect_state = properties.get(PROP_CONNECT_STATE)
        now = monotonic() if current_time is None else current_time
        if connect_state is not None:
            normalized = self._normalize_device_key(device.serial)
            self._last_mqtt_connect_state_at[normalized] = now
            self._connect_status_priority_ids.discard(normalized)
        if device.is_group and is_online_connect_state(connect_state):
            self._schedule_mqtt_group_online_reconciliation(
                device_name=device.name,
                now=now,
            )

    def _cleanup_mqtt_cache(self, current_time: float) -> None:
        """Clean up stale MQTT dedup cache entries."""
        self._mqtt_message_cache = cleanup_dedup_cache(
            self._mqtt_message_cache,
            current_time=current_time,
            stale_seconds=_MQTT_CACHE_STALE_SECONDS,
            max_entries=MAX_MQTT_CACHE_SIZE,
        )


__all__ = ["_MqttMixin"]
