"""MQTT lifecycle mixin for the coordinator."""

from __future__ import annotations

import asyncio
import logging
from time import monotonic
from typing import TYPE_CHECKING, Final

from homeassistant.helpers.issue_registry import (
    IssueSeverity,
    async_create_issue,
    async_delete_issue,
)

from ....const.base import DOMAIN
from ....const.config import CONF_PHONE_ID
from ...api import LiproApiError
from ...mqtt.setup_backoff import MqttSetupBackoff
from ...utils.log_safety import safe_error_placeholder
from ...utils.redaction import redact_identifier as _redact_identifier
from ..command_send import _CommandSendMixin
from ..runtime.coordinator_runtime import should_schedule_mqtt_setup
from ..tuning import _CONNECT_STATUS_MQTT_STALE_SECONDS
from .runtime import MqttRuntime
from .setup import (
    build_mqtt_subscription_device_ids,
    extract_mqtt_encrypted_credentials,
    iter_mesh_group_serials,
    resolve_mqtt_biz_id,
)

if TYPE_CHECKING:
    from ...mqtt.client import LiproMqttClient

_LOGGER = logging.getLogger(__name__)

# Polling interval multiplier when MQTT provides real-time updates.
# Use 2x (not higher) to still catch sub-device state drift in mesh groups.
_MQTT_POLLING_MULTIPLIER: Final[int] = 2


class _MqttLifecycleMixin(_CommandSendMixin):
    """Coordinator mixin for MQTT setup/teardown and connection lifecycle."""

    def _init_mqtt_state(self) -> None:
        """Initialize MQTT runtime state containers and caches."""
        self._mqtt_client = None
        self._mqtt_connected = False
        self._mqtt_setup_in_progress = False
        self._mqtt_setup_backoff = MqttSetupBackoff()
        self._mqtt_setup_backoff_gate_logged = False
        self._biz_id = None

        # Listener debounce handle + message dedup cache.
        self._mqtt_listener_update_handle = None
        self._mqtt_message_cache = {}
        self._mqtt_dedup_window = 0.5

        # MQTT disconnect tracking for user notification.
        self._mqtt_disconnect_time = None
        self._mqtt_disconnect_notified = False

        # Single-flight + cooldown for group-online MQTT reconciliation refresh.
        self._mqtt_group_online_reconcile_task = None
        self._mqtt_group_online_reconcile_last_at = 0.0

        # Last MQTT connectState observation per device (normalized key).
        self._last_mqtt_connect_state_at = {}

        self._mqtt_runtime = MqttRuntime(
            self,
            polling_multiplier=_MQTT_POLLING_MULTIPLIER,
            connect_status_mqtt_stale_seconds=_CONNECT_STATUS_MQTT_STALE_SECONDS,
            logger=_LOGGER,
        )

    def _reset_mqtt_state(self) -> None:
        """Clear MQTT runtime state on shutdown to break circular references."""
        self._mqtt_message_cache.clear()
        self._mqtt_group_online_reconcile_task = None
        self._mqtt_group_online_reconcile_last_at = 0.0
        self._mqtt_runtime = None

    def _ensure_mqtt_runtime(self) -> MqttRuntime:
        """Ensure extracted MQTT runtime helper is available."""
        if self._mqtt_runtime is None:
            self._mqtt_runtime = MqttRuntime(
                self,
                polling_multiplier=_MQTT_POLLING_MULTIPLIER,
                connect_status_mqtt_stale_seconds=_CONNECT_STATUS_MQTT_STALE_SECONDS,
                logger=_LOGGER,
            )
        return self._mqtt_runtime

    @property
    def mqtt_connected(self) -> bool:
        """Return True if MQTT is connected."""
        return self._mqtt_connected

    async def _resolve_mqtt_decrypted_credentials(self) -> tuple[str, str] | None:
        """Fetch MQTT config and decrypt access credentials."""
        from ...mqtt.credentials import decrypt_mqtt_credential  # noqa: PLC0415

        mqtt_config = await self.client.get_mqtt_config()
        credentials = extract_mqtt_encrypted_credentials(mqtt_config)
        if credentials is None:
            _LOGGER.warning("MQTT config missing accessKey or secretKey")
            return None

        encrypted_access_key, encrypted_secret_key = credentials
        access_key = await asyncio.to_thread(
            decrypt_mqtt_credential, encrypted_access_key
        )
        secret_key = await asyncio.to_thread(
            decrypt_mqtt_credential, encrypted_secret_key
        )
        return access_key, secret_key

    def _create_mqtt_client(
        self,
        *,
        access_key: str,
        secret_key: str,
        biz_id: str,
        phone_id: str,
    ) -> LiproMqttClient:
        """Create configured MQTT client instance."""
        from ...mqtt.client import LiproMqttClient  # noqa: PLC0415

        return LiproMqttClient(
            access_key=access_key,
            secret_key=secret_key,
            biz_id=biz_id,
            phone_id=phone_id,
            on_message=self._on_mqtt_message,
            on_connect=self._on_mqtt_connect,
            on_disconnect=self._on_mqtt_disconnect,
        )

    async def _start_mqtt_for_current_devices(
        self, mqtt_client: LiproMqttClient
    ) -> None:
        """Start MQTT client with subscriptions for current devices."""
        device_ids = build_mqtt_subscription_device_ids(self._devices)
        for mesh_group_serial in iter_mesh_group_serials(self._devices):
            _LOGGER.debug(
                "MQTT: subscribing to mesh group %s",
                _redact_identifier(mesh_group_serial) or "***",
            )

        await mqtt_client.start(device_ids)
        _LOGGER.info(
            "MQTT client setup complete, subscribing to %d devices",
            len(device_ids),
        )

    async def async_setup_mqtt(self) -> bool:
        """Set up MQTT through the injected MQTT service."""
        return await self.mqtt_service.async_setup()

    async def async_setup_mqtt_runtime(self) -> bool:
        """Set up MQTT client for real-time updates."""
        if self.config_entry is None:
            _LOGGER.error("Cannot setup MQTT: config_entry is None")
            return False
        try:
            credentials = await self._resolve_mqtt_decrypted_credentials()
            if credentials is None:
                return False
            access_key, secret_key = credentials

            biz_id = resolve_mqtt_biz_id(self.config_entry.data)
            if biz_id is None:
                _LOGGER.warning("No biz_id available for MQTT")
                return False
            self._biz_id = biz_id
            phone_id = self.config_entry.data.get(CONF_PHONE_ID, "")

            self._mqtt_client = self._create_mqtt_client(
                access_key=access_key,
                secret_key=secret_key,
                biz_id=biz_id,
                phone_id=phone_id,
            )
            await self._start_mqtt_for_current_devices(self._mqtt_client)
            return True

        except (LiproApiError, ValueError) as err:
            _LOGGER.warning("Failed to setup MQTT (%s)", safe_error_placeholder(err))
            return False

    async def _async_setup_mqtt_safe(self) -> None:
        """Safely set up MQTT client, resetting flag on completion."""
        setup_succeeded = False
        cancelled = False
        try:
            setup_succeeded = await self.async_setup_mqtt()
        except asyncio.CancelledError:
            cancelled = True
            raise
        finally:
            if not cancelled:
                if setup_succeeded:
                    self._mqtt_setup_backoff.on_success()
                else:
                    self._mqtt_setup_backoff.on_failure(monotonic())
                    self._mqtt_setup_backoff_gate_logged = False
            self._mqtt_setup_in_progress = False

    async def async_stop_mqtt(self) -> None:
        """Stop MQTT through the injected MQTT service."""
        await self.mqtt_service.async_stop()

    async def async_stop_mqtt_runtime(self) -> None:
        """Stop MQTT client."""
        if self._mqtt_client:
            await self._mqtt_client.stop()
            self._mqtt_client = None
            self._mqtt_connected = False
            _LOGGER.info("MQTT client stopped")

    async def async_sync_mqtt_subscriptions(self) -> None:
        """Sync subscriptions through the injected MQTT service."""
        await self.mqtt_service.async_sync_subscriptions()

    async def async_sync_mqtt_subscriptions_runtime(self) -> None:
        """Public runtime bridge for syncing MQTT subscriptions."""
        await self._sync_mqtt_subscriptions()

    async def _sync_mqtt_subscriptions(self) -> None:
        """Sync MQTT subscriptions with current device list."""
        if not self._mqtt_client:
            return

        expected = {dev.serial for dev in self._devices.values()}
        await self._mqtt_client.sync_subscriptions(expected)

    def _on_mqtt_connect(self) -> None:
        """Handle MQTT connection."""
        async_delete_issue(self.hass, DOMAIN, "mqtt_disconnected")
        self._ensure_mqtt_runtime().on_connect()

    def _on_mqtt_disconnect(self) -> None:
        """Handle MQTT disconnection."""
        self._ensure_mqtt_runtime().on_disconnect()

    def _check_mqtt_disconnect_notification(self) -> None:
        """Send persistent notification if MQTT has been disconnected too long."""
        self._ensure_mqtt_runtime().check_disconnect_notification()

    async def _async_show_mqtt_disconnect_notification(self, minutes: int) -> None:
        """Create a repair issue for MQTT disconnect."""
        async_create_issue(
            self.hass,
            domain=DOMAIN,
            issue_id="mqtt_disconnected",
            is_fixable=False,
            severity=IssueSeverity.WARNING,
            translation_key="mqtt_disconnected",
            translation_placeholders={"minutes": str(minutes)},
        )

    def _schedule_mqtt_setup_if_needed(self) -> None:
        """Ensure MQTT setup task is scheduled when runtime conditions match."""
        if not should_schedule_mqtt_setup(
            mqtt_enabled=self._mqtt_enabled,
            has_mqtt_client=self._mqtt_client is not None,
            mqtt_setup_in_progress=self._mqtt_setup_in_progress,
            has_devices=bool(self._devices),
        ):
            return

        now = monotonic()
        if not self._mqtt_setup_backoff.should_attempt(now):
            if not self._mqtt_setup_backoff_gate_logged:
                _LOGGER.debug("Skipping MQTT setup attempt due to retry backoff gate")
                self._mqtt_setup_backoff_gate_logged = True
            return

        self._mqtt_setup_backoff_gate_logged = False

        self._mqtt_setup_in_progress = True
        self._track_background_task(self._async_setup_mqtt_safe())


__all__ = ["_MqttLifecycleMixin"]
