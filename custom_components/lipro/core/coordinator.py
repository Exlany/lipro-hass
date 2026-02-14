"""Data update coordinator for Lipro integration."""

from __future__ import annotations

import asyncio
from datetime import timedelta
import hashlib
import logging
from time import monotonic
from typing import TYPE_CHECKING, Any

from homeassistant.exceptions import ConfigEntryAuthFailed
from homeassistant.helpers import device_registry as dr
from homeassistant.helpers.aiohttp_client import async_get_clientsession
from homeassistant.helpers.issue_registry import (
    IssueSeverity,
    async_create_issue,
    async_delete_issue,
)
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed

from ..const import (
    CONF_ANONYMOUS_SHARE_ENABLED,
    CONF_ANONYMOUS_SHARE_ERRORS,
    CONF_BIZ_ID,
    CONF_DEBUG_MODE,
    CONF_ENABLE_POWER_MONITORING,
    CONF_MQTT_ENABLED,
    CONF_PHONE_ID,
    CONF_POWER_QUERY_INTERVAL,
    CONF_REQUEST_TIMEOUT,
    CONF_SCAN_INTERVAL,
    CONF_USER_ID,
    DEFAULT_ANONYMOUS_SHARE_ENABLED,
    DEFAULT_ANONYMOUS_SHARE_ERRORS,
    DEFAULT_DEBUG_MODE,
    DEFAULT_ENABLE_POWER_MONITORING,
    DEFAULT_MQTT_ENABLED,
    DEFAULT_POWER_QUERY_INTERVAL,
    DEFAULT_REQUEST_TIMEOUT,
    DEFAULT_SCAN_INTERVAL,
    DOMAIN,
    PROP_CONNECT_STATE,
)
from ..const.categories import DeviceCategory
from .anonymous_share import get_anonymous_share_manager
from .api import (
    LiproApiError,
    LiproAuthError,
    LiproClient,
    LiproConnectionError,
    LiproRefreshTokenExpiredError,
)
from .const import MAX_MQTT_CACHE_SIZE, MQTT_DISCONNECT_NOTIFY_THRESHOLD
from .device import LiproDevice, parse_properties_list
from .mqtt import LiproMqttClient, decrypt_mqtt_credential

if TYPE_CHECKING:
    from homeassistant.config_entries import ConfigEntry
    from homeassistant.core import HomeAssistant

    from ..entities.base import LiproEntity
    from .auth import LiproAuthManager

_LOGGER = logging.getLogger(__name__)

# HA version for anonymous share reporting
try:
    from homeassistant.const import __version__ as _ha_ver

    HA_VERSION: str | None = _ha_ver
except ImportError:
    HA_VERSION = None


class LiproDataUpdateCoordinator(DataUpdateCoordinator[dict[str, LiproDevice]]):
    """Coordinator to manage fetching Lipro data."""

    def __init__(
        self,
        hass: HomeAssistant,
        client: LiproClient,
        auth_manager: LiproAuthManager,
        config_entry: ConfigEntry,
        update_interval: int = DEFAULT_SCAN_INTERVAL,
    ) -> None:
        """Initialize the coordinator.

        Args:
            hass: Home Assistant instance.
            client: Lipro API client.
            auth_manager: Authentication manager.
            config_entry: The config entry for this coordinator.
            update_interval: Update interval in seconds.

        """
        super().__init__(
            hass,
            _LOGGER,
            name="Lipro",
            update_interval=timedelta(seconds=update_interval),
            config_entry=config_entry,
            always_update=False,  # Skip listener callbacks if data unchanged
        )
        self.client = client
        self.auth_manager = auth_manager
        self._devices: dict[str, LiproDevice] = {}
        self._device_by_id: dict[str, LiproDevice] = {}  # Any known ID -> Device
        self._iot_ids_to_query: list[str] = []
        self._group_ids_to_query: list[str] = []
        self._outlet_ids_to_query: list[str] = []  # Outlet device IDs for power query
        # Track entities for debounce protection (indexed by device serial)
        self._entities: dict[str, LiproEntity] = {}
        self._entities_by_device: dict[str, list[LiproEntity]] = {}
        # MQTT client for real-time updates
        self._mqtt_client: LiproMqttClient | None = None
        self._mqtt_connected = False
        self._mqtt_setup_in_progress = False
        self._biz_id: str | None = None
        # Product configs cache (iotName -> config)
        self._product_configs: dict[str, dict[str, Any]] = {}
        # MQTT message deduplication cache: "device_id:hash" -> timestamp
        self._mqtt_message_cache: dict[str, float] = {}
        # Deduplication window in seconds (ignore duplicate messages within this window)
        self._mqtt_dedup_window: float = 0.5
        # Power query tracking
        self._last_power_query_time: float = 0.0
        # Flag to force device list re-fetch on next update
        self._force_device_refresh: bool = False
        # MQTT disconnect tracking for user notification
        self._mqtt_disconnect_time: float | None = None
        self._mqtt_disconnect_notified: bool = False

        # Load options from config entry
        self._load_options()

        # Initialize anonymous share system based on config
        self._setup_anonymous_share()

    def _load_options(self) -> None:
        """Load options from config entry."""
        options = self.config_entry.options if self.config_entry else {}

        # MQTT enabled
        self._mqtt_enabled = options.get(CONF_MQTT_ENABLED, DEFAULT_MQTT_ENABLED)

        # Power monitoring
        self._power_monitoring_enabled = options.get(
            CONF_ENABLE_POWER_MONITORING, DEFAULT_ENABLE_POWER_MONITORING
        )
        self._power_query_interval = options.get(
            CONF_POWER_QUERY_INTERVAL, DEFAULT_POWER_QUERY_INTERVAL
        )

        # Request timeout
        self._request_timeout = options.get(
            CONF_REQUEST_TIMEOUT, DEFAULT_REQUEST_TIMEOUT
        )

        # Debug mode
        self._debug_mode = options.get(CONF_DEBUG_MODE, DEFAULT_DEBUG_MODE)

        # Apply debug mode to all lipro loggers
        lipro_logger = logging.getLogger("custom_components.lipro")
        if self._debug_mode:
            lipro_logger.setLevel(logging.DEBUG)
            _LOGGER.debug("Debug mode enabled for all Lipro modules")
        else:
            lipro_logger.setLevel(logging.NOTSET)

    def _setup_anonymous_share(self) -> None:
        """Set up the anonymous share system based on config options."""
        options = self.config_entry.options if self.config_entry else {}
        enabled = options.get(
            CONF_ANONYMOUS_SHARE_ENABLED, DEFAULT_ANONYMOUS_SHARE_ENABLED
        )
        errors = options.get(
            CONF_ANONYMOUS_SHARE_ERRORS, DEFAULT_ANONYMOUS_SHARE_ERRORS
        )

        # Generate anonymous installation ID from config entry ID
        installation_id = None
        storage_path = None
        if self.config_entry:
            installation_id = hashlib.sha256(
                self.config_entry.entry_id.encode()
            ).hexdigest()[:16]
            # Use HA config directory for storage
            storage_path = self.hass.config.config_dir

        share_manager = get_anonymous_share_manager(self.hass)
        share_manager.set_enabled(
            enabled, errors, installation_id, storage_path, ha_version=HA_VERSION
        )
        _LOGGER.debug(
            "Anonymous share: enabled=%s, errors=%s",
            enabled,
            errors,
        )

    def register_entity(self, entity: LiproEntity) -> None:
        """Register an entity for debounce protection tracking.

        Args:
            entity: The entity to register.

        """
        if entity.unique_id:
            self._entities[entity.unique_id] = entity
            # Index by device serial for efficient lookup
            device_serial = entity.device.serial
            if device_serial not in self._entities_by_device:
                self._entities_by_device[device_serial] = []
            self._entities_by_device[device_serial].append(entity)

    def unregister_entity(self, entity: LiproEntity) -> None:
        """Unregister an entity.

        Args:
            entity: The entity to unregister.

        """
        if entity.unique_id and entity.unique_id in self._entities:
            del self._entities[entity.unique_id]
            # Remove from device index
            device_serial = entity.device.serial
            if device_serial in self._entities_by_device:
                entities = self._entities_by_device[device_serial]
                self._entities_by_device[device_serial] = [
                    e for e in entities if e.unique_id != entity.unique_id
                ]
                if not self._entities_by_device[device_serial]:
                    del self._entities_by_device[device_serial]

    def _get_protected_keys_for_device(self, device_serial: str) -> set[str]:
        """Get all protected property keys for a device.

        When entities are debouncing (user dragging slider), we should not
        overwrite their optimistic state with stale data from the cloud.

        Args:
            device_serial: The device serial number.

        Returns:
            Set of property keys that should not be overwritten.

        """
        protected_keys: set[str] = set()
        # Use indexed lookup for O(1) access instead of O(n) iteration
        for entity in self._entities_by_device.get(device_serial, []):
            protected_keys.update(entity.get_protected_keys())
        return protected_keys

    def _filter_protected_properties(
        self,
        device_serial: str,
        properties: dict[str, Any],
    ) -> dict[str, Any]:
        """Filter out debounce-protected properties.

        Args:
            device_serial: The device serial number.
            properties: Properties to filter.

        Returns:
            Filtered properties dict.

        """
        protected_keys = self._get_protected_keys_for_device(device_serial)
        if not protected_keys:
            return properties

        filtered = {k: v for k, v in properties.items() if k not in protected_keys}

        if filtered != properties:
            _LOGGER.debug(
                "Skipping protected keys for device %s: %s",
                device_serial[:8] + "...",  # Redact for privacy
                protected_keys & set(properties.keys()),
            )

        return filtered

    def _apply_properties_update(
        self,
        device: LiproDevice,
        properties: dict[str, Any],
        *,
        apply_protection: bool = True,
    ) -> None:
        """Apply property updates to a device with optional debounce protection.

        Args:
            device: Target device.
            properties: Properties to update.
            apply_protection: Whether to filter debounce-protected keys.

        """
        if apply_protection:
            properties = self._filter_protected_properties(device.serial, properties)

        if properties:
            device.update_properties(properties)
            _LOGGER.debug(
                "Updated %s: %s",
                device.name,
                properties,
            )

    async def _trigger_reauth(self, key: str, **placeholders: str) -> None:
        """Show auth notification and trigger reauth flow.

        Args:
            key: Translation key for the notification.
            **placeholders: Placeholder values for the notification message.

        """
        await self._async_show_auth_notification(key, **placeholders)
        if self.config_entry:
            self.config_entry.async_start_reauth(self.hass)

    @property
    def devices(self) -> dict[str, LiproDevice]:
        """Return all devices."""
        return self._devices

    def get_device(self, serial: str) -> LiproDevice | None:
        """Get a device by serial number.

        Args:
            serial: Device serial number.

        Returns:
            Device or None if not found.

        """
        return self._devices.get(serial)

    def get_device_by_id(self, device_id: str) -> LiproDevice | None:
        """Look up a device by any known identifier.

        Supports:
        - serial / iot_device_id: "03ab5ccd7cxxxxxx"
        - mesh group serial: "mesh_group_xxxxx"
        - gateway device ID (mapped via _query_group_status)

        Args:
            device_id: Any known device identifier.

        Returns:
            Device or None if not found.

        """
        return self._device_by_id.get(device_id)

    @property
    def mqtt_connected(self) -> bool:
        """Return True if MQTT is connected."""
        return self._mqtt_connected

    async def async_setup_mqtt(self) -> bool:
        """Set up MQTT client for real-time updates.

        Returns:
            True if MQTT setup was successful.

        """
        if self.config_entry is None:
            _LOGGER.error("Cannot setup MQTT: config_entry is None")
            return False
        try:
            # Get MQTT config from API
            mqtt_config = await self.client.get_mqtt_config()

            encrypted_access_key = mqtt_config.get("accessKey")
            encrypted_secret_key = mqtt_config.get("secretKey")

            if not encrypted_access_key or not encrypted_secret_key:
                _LOGGER.warning("MQTT config missing accessKey or secretKey")
                return False

            # Decrypt credentials (C extension, run in thread for async safety)
            access_key = await asyncio.to_thread(
                decrypt_mqtt_credential, encrypted_access_key
            )
            secret_key = await asyncio.to_thread(
                decrypt_mqtt_credential, encrypted_secret_key
            )

            # Get biz_id from config entry data
            biz_id = self.config_entry.data.get(CONF_BIZ_ID)
            if not biz_id:
                # Try to get from user_id (fallback)
                user_id = self.config_entry.data.get(CONF_USER_ID)
                if user_id is not None:
                    biz_id = str(user_id)
                else:
                    _LOGGER.warning("No biz_id available for MQTT")
                    return False

            # Remove 'lip_' prefix if present
            biz_id = biz_id.removeprefix("lip_")

            self._biz_id = biz_id
            phone_id = self.config_entry.data.get(CONF_PHONE_ID, "")

            # Create MQTT client
            self._mqtt_client = LiproMqttClient(
                access_key=access_key,
                secret_key=secret_key,
                biz_id=biz_id,
                phone_id=phone_id,
                on_message=self._on_mqtt_message,
                on_connect=self._on_mqtt_connect,
                on_disconnect=self._on_mqtt_disconnect,
            )

            # Get device IDs to subscribe
            # For mesh groups: use their serial (mesh_group_xxx) as the topic
            # For non-group devices: use their serial directly
            # Note: iot_device_id is an alias for serial, so we always use serial
            device_id_set: set[str] = set()
            for dev in self._devices.values():
                if dev.serial not in device_id_set:
                    device_id_set.add(dev.serial)
                    if dev.is_group:
                        _LOGGER.debug(
                            "MQTT: subscribing to mesh group %s",
                            dev.serial,
                        )

            device_ids = list(device_id_set)

            # Start MQTT client
            await self._mqtt_client.start(device_ids)
            _LOGGER.info(
                "MQTT client setup complete, subscribing to %d devices",
                len(device_ids),
            )
            return True

        except (LiproApiError, ValueError) as err:
            _LOGGER.warning("Failed to setup MQTT: %s", err)
            return False

    async def _async_setup_mqtt_safe(self) -> None:
        """Safely set up MQTT client, resetting flag on completion."""
        try:
            await self.async_setup_mqtt()
        finally:
            self._mqtt_setup_in_progress = False

    async def async_stop_mqtt(self) -> None:
        """Stop MQTT client."""
        if self._mqtt_client:
            await self._mqtt_client.stop()
            self._mqtt_client = None
            self._mqtt_connected = False
            _LOGGER.info("MQTT client stopped")

    async def _sync_mqtt_subscriptions(self) -> None:
        """Sync MQTT subscriptions with current device list."""
        if not self._mqtt_client:
            return

        # serial works for both: mesh_group_xxx (groups) and iot_device_id (non-groups)
        expected = {dev.serial for dev in self._devices.values()}
        await self._mqtt_client.sync_subscriptions(expected)

    async def async_shutdown(self) -> None:
        """Shutdown coordinator and release all resources."""
        # Cancel update timer FIRST to prevent polls during cleanup.
        # Without this, a scheduled poll could fire after _devices is cleared,
        # triggering _fetch_devices() and unnecessary API calls during shutdown.
        await super().async_shutdown()

        # Submit anonymous share report before shutdown (if enabled)
        try:
            share_manager = get_anonymous_share_manager(self.hass)
            if share_manager.is_enabled:
                session = async_get_clientsession(self.hass)
                await share_manager.submit_report(session)
        except (OSError, TimeoutError):
            _LOGGER.exception("Failed to submit anonymous share report on shutdown")

        # Stop MQTT client
        try:
            await self.async_stop_mqtt()
        except (OSError, TimeoutError):
            _LOGGER.exception("Failed to stop MQTT client on shutdown")

        # Close API client session
        try:
            await self.client.close()
        except (OSError, TimeoutError):
            _LOGGER.exception("Failed to close API client on shutdown")

        # Clear all data structures to break circular references
        self._entities.clear()
        self._entities_by_device.clear()
        self._devices.clear()
        self._device_by_id.clear()
        self._product_configs.clear()
        self._mqtt_message_cache.clear()

        _LOGGER.debug("Coordinator shutdown complete")

    def _on_mqtt_connect(self) -> None:
        """Handle MQTT connection."""
        self._mqtt_connected = True
        self._mqtt_disconnect_time = None
        self._mqtt_disconnect_notified = False
        # Dismiss any previous disconnect issue
        async_delete_issue(self.hass, DOMAIN, "mqtt_disconnected")
        # Reduce polling frequency when MQTT provides real-time updates
        # Use 2x (not higher) to still catch sub-device state drift in mesh groups
        base = self._base_scan_interval
        self.update_interval = timedelta(seconds=base * 2)
        _LOGGER.info("MQTT connected, polling interval relaxed to %ds", base * 2)

    def _on_mqtt_disconnect(self) -> None:
        """Handle MQTT disconnection."""
        self._mqtt_connected = False
        if self._mqtt_disconnect_time is None:
            self._mqtt_disconnect_time = monotonic()
        # Restore normal polling frequency
        base = self._base_scan_interval
        self.update_interval = timedelta(seconds=base)
        _LOGGER.warning("MQTT disconnected, polling interval restored to %ds", base)

    def _check_mqtt_disconnect_notification(self) -> None:
        """Send persistent notification if MQTT has been disconnected too long."""
        if (
            not self._mqtt_enabled
            or self._mqtt_connected
            or self._mqtt_disconnect_time is None
            or self._mqtt_disconnect_notified
        ):
            return

        elapsed = monotonic() - self._mqtt_disconnect_time
        if elapsed >= MQTT_DISCONNECT_NOTIFY_THRESHOLD:
            self._mqtt_disconnect_notified = True
            minutes = int(elapsed // 60)
            self.hass.async_create_task(
                self._async_show_mqtt_disconnect_notification(minutes)
            )

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

    @property
    def _base_scan_interval(self) -> int:
        """Get the configured base scan interval in seconds."""
        if self.config_entry:
            return self.config_entry.options.get(  # type: ignore[no-any-return]
                CONF_SCAN_INTERVAL, DEFAULT_SCAN_INTERVAL
            )
        return DEFAULT_SCAN_INTERVAL

    def _on_mqtt_message(self, device_id: str, properties: dict[str, Any]) -> None:
        """Handle MQTT message with device status update.

        This callback is invoked from aiomqtt's async message iterator,
        which runs on the event loop, so no thread-safety wrapper is needed.

        Implements deduplication to handle duplicate MQTT messages that may
        arrive in quick succession (common with Lipro devices).

        Args:
            device_id: IoT device ID.
            properties: Flattened device properties.

        """
        # Find device using IoT ID mapping
        device = self.get_device_by_id(device_id)

        if not device:
            _LOGGER.debug("MQTT message for unknown device: %s...", device_id[:8])
            return

        # Deduplication: check if this is a duplicate message
        current_time = monotonic()
        # Use hash of sorted items tuple for fast dedup (no JSON serialization needed)
        try:
            props_hash = hash(tuple(sorted(properties.items())))
        except TypeError:
            # Properties contain unhashable values, skip dedup
            _LOGGER.debug(
                "MQTT: cannot hash properties for %s, skipping dedup", device.name
            )
            props_hash = None

        # Only perform deduplication if we have a valid hash
        if props_hash is not None:
            cache_key = f"{device_id}:{props_hash}"
            last_time = self._mqtt_message_cache.get(cache_key)

            if last_time is not None:
                if current_time - last_time < self._mqtt_dedup_window:
                    # Duplicate message within dedup window, skip
                    if self._debug_mode:
                        _LOGGER.debug(
                            "MQTT: skipping duplicate message for %s (%.2fs ago)",
                            device.name,
                            current_time - last_time,
                        )
                    return

            # Update cache
            self._mqtt_message_cache[cache_key] = current_time

            # Periodic cleanup: only run when cache exceeds threshold
            if len(self._mqtt_message_cache) > MAX_MQTT_CACHE_SIZE:
                self._cleanup_mqtt_cache(current_time)

        self._apply_properties_update(device, properties)

        if properties:
            # Force notify all listeners of the update
            # Note: async_set_updated_data won't trigger updates when always_update=False
            # and the same dict object is passed, so we use async_update_listeners directly
            self.async_update_listeners()

            # Fallback: when a device comes back online, schedule an immediate
            # REST API refresh to reconcile state. In mesh groups, sub-devices
            # may reconnect with a different state than the group reports.
            connect_state = properties.get(PROP_CONNECT_STATE)
            if connect_state == "1" and device.is_group:
                _LOGGER.debug(
                    "MQTT: device %s online, scheduling REST API reconciliation",
                    device.name,
                )
                self.hass.async_create_task(self.async_request_refresh())

    def _cleanup_mqtt_cache(self, current_time: float) -> None:
        """Clean up stale MQTT dedup cache entries.

        Removes entries older than 5 seconds. If cache still exceeds limit,
        keeps the newest half.

        Args:
            current_time: Current monotonic time.

        """
        # Remove entries older than 5 seconds
        stale_keys = [
            k for k, t in self._mqtt_message_cache.items() if current_time - t > 5.0
        ]
        for k in stale_keys:
            del self._mqtt_message_cache[k]

        # Hard cap: if cache still exceeds limit, keep newest half
        if len(self._mqtt_message_cache) > MAX_MQTT_CACHE_SIZE:
            sorted_items = sorted(self._mqtt_message_cache.items(), key=lambda x: x[1])
            self._mqtt_message_cache = dict(sorted_items[len(sorted_items) // 2 :])

    async def _async_show_auth_notification(
        self,
        key: str,
        **placeholders: str,
    ) -> None:
        """Create a repair issue for authentication errors.

        Args:
            key: The translation key (e.g., "auth_expired", "auth_error").
            **placeholders: Placeholder values for the translation string.

        """
        async_create_issue(
            self.hass,
            domain=DOMAIN,
            issue_id=key,
            is_fixable=True,
            severity=IssueSeverity.ERROR,
            translation_key=key,
            translation_placeholders=placeholders or None,
        )

    async def _async_update_data(self) -> dict[str, LiproDevice]:
        """Fetch data from API.

        Returns:
            Dictionary of devices keyed by serial.

        Raises:
            UpdateFailed: If update fails.

        """
        try:
            # Ensure we have a valid token
            await self.auth_manager.ensure_valid_token()

            # Fetch device list if we don't have devices yet or refresh was forced
            if not self._devices or self._force_device_refresh:
                self._force_device_refresh = False
                await self._fetch_devices()
                # Load product configs and apply color temp ranges
                await self._load_product_configs()

            # Query device status
            await self._update_device_status()

            # Ensure MQTT client is running (retry if previous setup failed)
            # Only if MQTT is enabled in options
            if (
                self._mqtt_enabled
                and not self._mqtt_client
                and not self._mqtt_setup_in_progress
                and self._devices
            ):
                self._mqtt_setup_in_progress = True
                self.hass.async_create_task(self._async_setup_mqtt_safe())

            # Notify user if MQTT has been disconnected for too long
            self._check_mqtt_disconnect_notification()

            return self._devices

        except LiproRefreshTokenExpiredError as err:
            # Refresh token expired, trigger reauth flow
            await self._trigger_reauth("auth_expired")
            msg = f"Refresh token expired, re-authentication required: {err}"
            raise ConfigEntryAuthFailed(msg) from err
        except LiproAuthError as err:
            # Trigger reauth flow when authentication fails
            await self._trigger_reauth("auth_error", error=str(err))
            msg = f"Authentication error: {err}"
            raise ConfigEntryAuthFailed(msg) from err
        except LiproConnectionError as err:
            msg = f"Connection error: {err}"
            raise UpdateFailed(msg) from err
        except LiproApiError as err:
            msg = f"API error: {err}"
            raise UpdateFailed(msg) from err

    async def _fetch_devices(self) -> None:
        """Fetch all devices from API."""
        _LOGGER.debug("Fetching device list")

        result = await self.client.get_devices(offset=0, limit=100)
        devices_data = result.get("devices", [])

        # Track previous device serials for stale device detection
        previous_serials = set(self._devices.keys())

        # Build new data structures atomically — only swap on success
        new_devices: dict[str, LiproDevice] = {}
        new_device_by_id: dict[str, LiproDevice] = {}
        new_iot_ids: list[str] = []
        new_group_ids: list[str] = []
        new_outlet_ids: list[str] = []

        for device_data in devices_data:
            device = LiproDevice.from_api_data(device_data)

            # Skip gateways for now
            if device.is_gateway:
                _LOGGER.debug("Skipping gateway device: %s", device.name)
                continue

            new_devices[device.serial] = device

            # Build IoT ID to device mapping for fast lookup
            # Groups use serial (mesh_group_xxx) as MQTT topic device ID
            # Non-groups use serial which equals iot_device_id (03ab...)
            new_device_by_id[device.serial] = device

            # Collect IDs for status query
            if device.is_group:
                new_group_ids.append(device.serial)
            else:
                # Use iot_device_id for IoT API queries
                # Log warning if format is unexpected (for debugging only)
                if not device.has_valid_iot_id:
                    _LOGGER.debug(
                        "Device %s has unexpected IoT ID format: %s",
                        device.name,
                        device.serial,
                    )
                new_iot_ids.append(device.iot_device_id)

                # Collect outlet device IDs for power monitoring
                if device.category == DeviceCategory.OUTLET:
                    new_outlet_ids.append(device.iot_device_id)

        # Atomic swap — all-or-nothing update
        self._devices = new_devices
        self._device_by_id = new_device_by_id
        self._iot_ids_to_query = new_iot_ids
        self._group_ids_to_query = new_group_ids
        self._outlet_ids_to_query = new_outlet_ids

        _LOGGER.info(
            "Fetched %d devices (%d groups, %d individual, %d outlets)",
            len(self._devices),
            len(self._group_ids_to_query),
            len(self._iot_ids_to_query),
            len(self._outlet_ids_to_query),
        )

        # Record devices for anonymous share (if enabled)
        share_manager = get_anonymous_share_manager(self.hass)
        if share_manager.is_enabled:
            await share_manager.async_ensure_loaded()
            share_manager.record_devices(list(self._devices.values()))

        # Remove stale devices that no longer exist in the cloud
        current_serials = set(self._devices.keys())
        stale_serials = previous_serials - current_serials
        if stale_serials:
            await self._async_remove_stale_devices(stale_serials)

        # Sync MQTT subscriptions with current device list
        if self._mqtt_client and self._mqtt_connected:
            await self._sync_mqtt_subscriptions()

    async def _async_remove_stale_devices(self, stale_serials: set[str]) -> None:
        """Remove devices that no longer exist in the cloud.

        Args:
            stale_serials: Set of device serial numbers that are no longer present.

        """
        if not self.config_entry:
            return

        device_registry = dr.async_get(self.hass)

        for serial in stale_serials:
            # Find device in registry by identifier
            device_entry = device_registry.async_get_device(
                identifiers={(DOMAIN, serial)},
            )
            if device_entry:
                _LOGGER.info(
                    "Removing stale device: %s (serial: %s)",
                    device_entry.name,
                    serial,
                )
                device_registry.async_remove_device(device_entry.id)

    async def _load_product_configs(self) -> None:
        """Load product configurations and apply color temp ranges to devices.

        Product configs contain minTemperature and maxTemperature values
        which define the color temperature range for each product type.

        Matching priority (same as Lipro App):
        1. Match by productId -> config.id (most accurate)
        2. Match by iotName -> config.fwIotName (fallback)
        """
        if self._product_configs:
            # Already loaded
            return

        try:
            configs = await self.client.get_product_configs()
            _LOGGER.debug("Loaded %d product configurations", len(configs))

            # Build lookups for both matching methods
            configs_by_id: dict[int, dict[str, Any]] = {}
            configs_by_iot_name: dict[str, dict[str, Any]] = {}

            for config in configs:
                # Index by id (for productId matching)
                config_id = config.get("id")
                if config_id is not None:
                    configs_by_id[config_id] = config

                # Index by fwIotName (for iotName matching)
                fw_iot_name = config.get("fwIotName")
                if fw_iot_name:
                    # Normalize to lowercase for case-insensitive matching
                    configs_by_iot_name[fw_iot_name.lower()] = config

            # Store for potential future use
            self._product_configs = configs_by_iot_name

            # Apply color temp ranges to devices
            for device in self._devices.values():
                matched_config: dict[str, Any] | None = None

                # Priority 1: Match by productId -> config.id
                if device.product_id:
                    matched_config = configs_by_id.get(device.product_id)
                    if matched_config:
                        _LOGGER.debug(
                            "Device %s: matched config by productId=%d -> %s",
                            device.name,
                            device.product_id,
                            matched_config.get("name"),
                        )

                # Priority 2: Match by iotName -> config.fwIotName
                if not matched_config and device.iot_name:
                    matched_config = configs_by_iot_name.get(device.iot_name.lower())
                    if matched_config:
                        _LOGGER.debug(
                            "Device %s: matched config by iotName=%s -> %s",
                            device.name,
                            device.iot_name,
                            matched_config.get("name"),
                        )

                if matched_config:
                    min_temp = matched_config.get("minTemperature", 0)
                    max_temp = matched_config.get("maxTemperature", 0)

                    # Only update if we have valid values
                    # 0 means single color temp (no adjustment)
                    if max_temp > 0:
                        device.min_color_temp_kelvin = min_temp or 2700
                        device.max_color_temp_kelvin = max_temp
                        _LOGGER.debug(
                            "Device %s: color temp range %d-%d K",
                            device.name,
                            device.min_color_temp_kelvin,
                            device.max_color_temp_kelvin,
                        )
                    elif max_temp == 0 and min_temp == 0:
                        # Single color temperature device
                        device.min_color_temp_kelvin = 0
                        device.max_color_temp_kelvin = 0
                        _LOGGER.debug(
                            "Device %s: single color temperature (no adjustment)",
                            device.name,
                        )

                    # Apply fan gear range if available
                    max_fan_gear = matched_config.get("maxFanGear", 0)
                    if max_fan_gear > 0:
                        device.max_fan_gear = max_fan_gear
                        _LOGGER.debug(
                            "Device %s: fan gear range 1-%d",
                            device.name,
                            device.max_fan_gear,
                        )

        except LiproApiError as err:
            _LOGGER.warning("Failed to load product configs: %s", err)
            # Continue with default values

    async def _update_device_status(self) -> None:
        """Update status for all devices."""
        tasks = []

        # Query individual devices
        if self._iot_ids_to_query:
            tasks.append(self._query_device_status())

        # Query mesh groups
        if self._group_ids_to_query:
            tasks.append(self._query_group_status())

        # Query outlet power info (if enabled and interval has passed)
        if (
            self._power_monitoring_enabled
            and self._outlet_ids_to_query
            and self._should_query_power()
        ):
            tasks.append(self._query_outlet_power())

        # Query real-time connection status (more accurate than cached connectState)
        if self._iot_ids_to_query:
            tasks.append(self._query_connect_status())

        if tasks:
            results = await asyncio.gather(*tasks, return_exceptions=True)
            # Log any exceptions that occurred
            for result in results:
                if isinstance(result, Exception):
                    _LOGGER.debug("Task failed during status update: %s", result)

    def _should_query_power(self) -> bool:
        """Check if power query should be executed based on interval.

        Returns:
            True if power query should be executed.

        """
        current_time = monotonic()
        if current_time - self._last_power_query_time >= self._power_query_interval:
            self._last_power_query_time = current_time
            return True
        return False

    async def _query_device_status(self) -> None:
        """Query status for individual devices."""
        try:
            status_list = await self.client.query_device_status(
                self._iot_ids_to_query,
            )

            for status_data in status_list:
                device_id = status_data.get("deviceId")
                if not device_id:
                    continue

                # Find device using IoT ID mapping
                device = self.get_device_by_id(device_id)

                if device:
                    properties = parse_properties_list(
                        status_data.get("properties", []),
                    )
                    self._apply_properties_update(device, properties)

        except LiproApiError as err:
            _LOGGER.warning("Failed to query device status: %s", err)

    async def _query_group_status(self) -> None:
        """Query status for mesh groups.

        API Response structure:
        {
            "data": [
                {
                    "groupId": "mesh_group_10001",
                    "devices": [...],
                    "properties": [...],
                    "hasBindGateway": true,
                    "gatewayDeviceId": "03ab..."
                }
            ]
        }
        """
        try:
            status_list = await self.client.query_mesh_group_status(
                self._group_ids_to_query,
            )

            for status_data in status_list:
                # Get groupId directly from response
                group_id = status_data.get("groupId")
                if not group_id:
                    _LOGGER.warning(
                        "Missing groupId in mesh group status response: %s",
                        list(status_data.keys()),
                    )
                    continue

                device = self._devices.get(group_id)
                if not device:
                    _LOGGER.debug(
                        "Unknown group in status response: %s",
                        group_id,
                    )
                    continue

                # Save gateway device ID for API-level lookups
                # Note: MQTT messages use mesh_group_xxx topics, not gateway IDs
                gateway_id = status_data.get("gatewayDeviceId")
                if gateway_id:
                    device.extra_data["gateway_device_id"] = gateway_id
                    # Map gateway ID -> device for API responses that reference it
                    self._device_by_id[gateway_id] = device

                # Parse group-level properties (powerState, brightness, etc.)
                properties = parse_properties_list(status_data.get("properties", []))
                self._apply_properties_update(device, properties)

        except LiproApiError as err:
            _LOGGER.warning("Failed to query group status: %s", err)

    async def _query_outlet_power(self) -> None:
        """Query power information for outlet devices.

        The API returns aggregated data (single nowPower + energyList) for all
        requested devices, so we query each outlet individually to get accurate
        per-device power data. Queries run concurrently for better performance.
        """
        if not self._outlet_ids_to_query:
            return

        async def _query_single_outlet(device_id: str) -> None:
            """Query power for a single outlet."""
            try:
                power_data = await self.client.fetch_outlet_power_info([device_id])
                if not power_data:
                    return
                device = self.get_device_by_id(device_id)
                if device:
                    device.extra_data["power_info"] = power_data
                    _LOGGER.debug(
                        "Updated power info for %s: nowPower=%s",
                        device.name,
                        power_data.get("nowPower"),
                    )
            except LiproApiError as err:
                _LOGGER.debug("Failed to query power for %s: %s", device_id, err)

        await asyncio.gather(
            *(_query_single_outlet(did) for did in self._outlet_ids_to_query),
        )

    async def _query_connect_status(self) -> None:
        """Query real-time connection status for devices.

        This provides more accurate online/offline status than the cached
        connectState property from device status queries.
        """
        if not self._iot_ids_to_query:
            return

        try:
            connect_status = await self.client.query_connect_status(
                self._iot_ids_to_query,
            )

            if not connect_status:
                return

            for device_id, is_online in connect_status.items():
                device = self.get_device_by_id(device_id)
                if device:
                    # Update connectState property
                    device.update_properties(
                        {
                            PROP_CONNECT_STATE: "1" if is_online else "0",
                        }
                    )
                    _LOGGER.debug(
                        "Updated connect status for %s: %s",
                        device.name,
                        "online" if is_online else "offline",
                    )

        except LiproApiError as err:
            _LOGGER.debug("Failed to query connect status: %s", err)

    async def async_refresh_devices(self) -> None:
        """Force refresh of device list.

        Sets a flag so the next _async_update_data call re-fetches devices.
        Uses atomic swap in _fetch_devices, so the old device list remains
        intact if the refresh fails.
        """
        self._force_device_refresh = True
        # Clear product configs so new device types can be matched
        self._product_configs.clear()
        await self.async_refresh()

    async def async_send_command(
        self,
        device: LiproDevice,
        command: str,
        properties: list[dict[str, str]] | None = None,
    ) -> bool:
        """Send a command to a device.

        Args:
            device: Target device.
            command: Command name.
            properties: Optional properties.

        Returns:
            True if command was sent successfully.

        """
        try:
            await self.auth_manager.ensure_valid_token()

            if device.is_group:
                result = await self.client.send_group_command(
                    device.serial,
                    command,
                    device.device_type,
                    properties,
                    device.iot_name,
                )
            else:
                result = await self.client.send_command(
                    device.serial,
                    command,
                    device.device_type,
                    properties,
                    device.iot_name,
                )

            # Check pushSuccess from API response
            # Real response: {"msgSn": "...", "pushSuccess": true, "pushTimestamp": ...}
            if isinstance(result, dict) and result.get("pushSuccess") is False:
                _LOGGER.warning(
                    "Command %s sent to %s but push failed (device may be offline)",
                    command,
                    device.name,
                )

            # Schedule a refresh to get updated state
            self.hass.async_create_task(self.async_request_refresh())

            return True

        except LiproRefreshTokenExpiredError:
            _LOGGER.warning(
                "Refresh token expired while sending command to %s", device.name
            )
            await self._trigger_reauth("auth_expired")
            return False
        except LiproAuthError:
            _LOGGER.warning(
                "Auth error sending command to %s, triggering reauth", device.name
            )
            await self._trigger_reauth("auth_error")
            return False
        except LiproApiError:
            _LOGGER.exception("Failed to send command to %s", device.name)
            return False
