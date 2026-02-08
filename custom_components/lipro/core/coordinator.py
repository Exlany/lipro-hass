"""Data update coordinator for Lipro integration."""

from __future__ import annotations

import asyncio
from datetime import timedelta
import logging
from typing import TYPE_CHECKING, Any

from homeassistant.components.persistent_notification import async_create
from homeassistant.exceptions import ConfigEntryAuthFailed
from homeassistant.helpers import device_registry as dr
from homeassistant.helpers.translation import async_get_translations
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed

from ..const import (
    CONF_ANONYMOUS_SHARE_ENABLED,
    CONF_ANONYMOUS_SHARE_ERRORS,
    CONF_PHONE_ID,
    DEFAULT_ANONYMOUS_SHARE_ENABLED,
    DEFAULT_ANONYMOUS_SHARE_ERRORS,
    DEFAULT_SCAN_INTERVAL,
    DOMAIN,
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
    from homeassistant.const import __version__ as HA_VERSION
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
        self._iot_id_to_device: dict[str, LiproDevice] = {}  # IoT ID -> Device mapping
        self._device_ids_to_query: list[str] = []
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

        # Initialize anonymous share system based on config
        self._setup_anonymous_share()

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
            import hashlib

            installation_id = hashlib.sha256(
                self.config_entry.entry_id.encode()
            ).hexdigest()[:16]
            # Use HA config directory for storage
            storage_path = self.hass.config.config_dir

        share_manager = get_anonymous_share_manager()
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

    def get_device_by_iot_id(self, iot_id: str) -> LiproDevice | None:
        """Get a device by IoT device ID.

        Args:
            iot_id: IoT device ID (e.g., "03ab5ccd7cxxxxxx").

        Returns:
            Device or None if not found.

        """
        # First try direct lookup in mapping
        device = self._iot_id_to_device.get(iot_id)
        if device:
            return device

        # Fallback to serial lookup (for groups or legacy)
        return self._devices.get(iot_id)

    @property
    def mqtt_connected(self) -> bool:
        """Return True if MQTT is connected."""
        return self._mqtt_connected

    async def async_setup_mqtt(self) -> bool:
        """Set up MQTT client for real-time updates.

        Returns:
            True if MQTT setup was successful.

        """
        try:
            # Get MQTT config from API
            mqtt_config = await self.client.get_mqtt_config()

            encrypted_access_key = mqtt_config.get("accessKey")
            encrypted_secret_key = mqtt_config.get("secretKey")

            if not encrypted_access_key or not encrypted_secret_key:
                _LOGGER.warning("MQTT config missing accessKey or secretKey")
                return False

            # Decrypt credentials
            access_key = decrypt_mqtt_credential(encrypted_access_key)
            secret_key = decrypt_mqtt_credential(encrypted_secret_key)

            # Get biz_id from config entry data
            biz_id = self.config_entry.data.get("biz_id")
            if not biz_id:
                # Try to get from user_id (fallback)
                user_id = self.config_entry.data.get("user_id")
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

            # Get device IDs to subscribe (exclude groups for now)
            device_ids = [
                dev.iot_device_id for dev in self._devices.values() if not dev.is_group
            ]

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

    async def async_shutdown(self) -> None:
        """Shutdown coordinator and release all resources."""
        # Submit anonymous share report before shutdown (if enabled)
        try:
            share_manager = get_anonymous_share_manager()
            if share_manager.is_enabled:
                await share_manager.submit_report()
        except (OSError, asyncio.TimeoutError):
            _LOGGER.exception("Failed to submit anonymous share report on shutdown")

        # Stop MQTT client
        try:
            await self.async_stop_mqtt()
        except (OSError, asyncio.TimeoutError):
            _LOGGER.exception("Failed to stop MQTT client on shutdown")

        # Close API client session
        try:
            await self.client.close()
        except (OSError, asyncio.TimeoutError):
            _LOGGER.exception("Failed to close API client on shutdown")

        # Clear all data structures to break circular references
        self._entities.clear()
        self._entities_by_device.clear()
        self._devices.clear()
        self._iot_id_to_device.clear()
        self._product_configs.clear()

        _LOGGER.debug("Coordinator shutdown complete")

    def _on_mqtt_connect(self) -> None:
        """Handle MQTT connection."""
        self._mqtt_connected = True
        _LOGGER.info("MQTT connected, real-time updates enabled")

    def _on_mqtt_disconnect(self) -> None:
        """Handle MQTT disconnection."""
        self._mqtt_connected = False
        _LOGGER.warning("MQTT disconnected, falling back to polling")

    def _on_mqtt_message(self, device_id: str, properties: dict[str, Any]) -> None:
        """Handle MQTT message with device status update.

        This callback may be called from a different thread (MQTT client thread),
        so we schedule the actual processing on the event loop thread-safely.

        Args:
            device_id: IoT device ID.
            properties: Flattened device properties.

        """
        # Schedule processing on the event loop (thread-safe)
        self.hass.loop.call_soon_threadsafe(
            self._process_mqtt_message, device_id, properties
        )

    def _process_mqtt_message(self, device_id: str, properties: dict[str, Any]) -> None:
        """Process MQTT message on the event loop thread.

        Args:
            device_id: IoT device ID.
            properties: Flattened device properties.

        """
        # Find device using IoT ID mapping
        device = self.get_device_by_iot_id(device_id)

        if not device:
            _LOGGER.debug("MQTT message for unknown device: %s...", device_id[:8])
            return

        self._apply_properties_update(device, properties)

        if properties:
            # Notify listeners of the update
            self.async_set_updated_data(self._devices)

    async def _async_show_auth_notification(
        self,
        key: str,
        **placeholders: str,
    ) -> None:
        """Show a localized authentication notification.

        Args:
            key: The translation key (e.g., "auth_expired", "auth_error").
            **placeholders: Placeholder values for the translation string.

        """
        # Default fallback values
        if key == "auth_expired":
            title = "Lipro Authentication Expired"
            message = "Your Lipro session has expired. Please re-authenticate."
        else:
            title = "Lipro Authentication Error"
            error_msg = placeholders.get("error", "Unknown error")
            message = f"Lipro authentication failed: {error_msg}"

        # Try to get localized translations
        try:
            translations = await async_get_translations(
                self.hass,
                self.hass.config.language,
                "exceptions",
                {DOMAIN},
            )

            # Build translation keys
            title_key = f"component.{DOMAIN}.exceptions.{key}.title"
            message_key = f"component.{DOMAIN}.exceptions.{key}.message"

            # Get translated strings (use defaults if not found)
            title = translations.get(title_key, title)
            message = translations.get(message_key, message)

            # Replace placeholders in message
            for placeholder, value in placeholders.items():
                message = message.replace(f"{{{placeholder}}}", value)

        except (KeyError, ValueError, TypeError):
            # Use fallback values already set above
            _LOGGER.debug("Failed to get translations, using fallback")

        async_create(
            self.hass,
            message,
            title=title,
            notification_id=f"{DOMAIN}_{key}",
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

            # Fetch device list if we don't have devices yet
            if not self._devices:
                await self._fetch_devices()
                # Load product configs and apply color temp ranges
                await self._load_product_configs()

            # Query device status
            await self._update_device_status()

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

        self._devices.clear()
        self._iot_id_to_device.clear()
        self._device_ids_to_query.clear()
        self._group_ids_to_query.clear()
        self._outlet_ids_to_query.clear()

        for device_data in devices_data:
            device = LiproDevice.from_api_data(device_data)

            # Skip gateways for now
            if device.is_gateway:
                _LOGGER.debug("Skipping gateway device: %s", device.name)
                continue

            self._devices[device.serial] = device

            # Build IoT ID to device mapping for fast lookup
            if not device.is_group:
                self._iot_id_to_device[device.iot_device_id] = device

            # Collect IDs for status query
            if device.is_group:
                self._group_ids_to_query.append(device.serial)
            else:
                # Use iot_device_id for IoT API queries
                # Log warning if format is unexpected (for debugging only)
                if not device.has_valid_iot_id:
                    _LOGGER.debug(
                        "Device %s has unexpected IoT ID format: %s",
                        device.name,
                        device.serial,
                    )
                self._device_ids_to_query.append(device.iot_device_id)

                # Collect outlet device IDs for power monitoring
                if device.category == DeviceCategory.OUTLET:
                    self._outlet_ids_to_query.append(device.iot_device_id)

        _LOGGER.info(
            "Fetched %d devices (%d groups, %d individual, %d outlets)",
            len(self._devices),
            len(self._group_ids_to_query),
            len(self._device_ids_to_query),
            len(self._outlet_ids_to_query),
        )

        # Record devices for anonymous share (if enabled)
        share_manager = get_anonymous_share_manager()
        if share_manager.is_enabled:
            share_manager.record_devices(list(self._devices.values()))

        # Remove stale devices that no longer exist in the cloud
        current_serials = set(self._devices.keys())
        stale_serials = previous_serials - current_serials
        if stale_serials:
            await self._async_remove_stale_devices(stale_serials)

        # Start MQTT client for real-time updates (if not already running)
        if not self._mqtt_client and not self._mqtt_setup_in_progress and self._devices:
            self._mqtt_setup_in_progress = True
            self.hass.async_create_task(self._async_setup_mqtt_safe())

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
        """
        if self._product_configs:
            # Already loaded
            return

        try:
            configs = await self.client.get_product_configs()
            _LOGGER.debug("Loaded %d product configurations", len(configs))

            # Build lookup by fwIotName (matches device iotName)
            for config in configs:
                fw_iot_name = config.get("fwIotName")
                if fw_iot_name:
                    # Normalize to lowercase for case-insensitive matching
                    self._product_configs[fw_iot_name.lower()] = config

            # Apply color temp ranges to devices
            for device in self._devices.values():
                if not device.iot_name:
                    continue

                # Look up config by iotName
                config = self._product_configs.get(device.iot_name.lower())
                if config:
                    min_temp = config.get("minTemperature", 0)
                    max_temp = config.get("maxTemperature", 0)

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

        except LiproApiError as err:
            _LOGGER.warning("Failed to load product configs: %s", err)
            # Continue with default values

    async def _update_device_status(self) -> None:
        """Update status for all devices."""
        tasks = []

        # Query individual devices
        if self._device_ids_to_query:
            tasks.append(self._query_device_status())

        # Query mesh groups
        if self._group_ids_to_query:
            tasks.append(self._query_group_status())

        # Query outlet power info
        if self._outlet_ids_to_query:
            tasks.append(self._query_outlet_power())

        # Query real-time connection status (more accurate than cached connectState)
        if self._device_ids_to_query:
            tasks.append(self._query_connect_status())

        if tasks:
            results = await asyncio.gather(*tasks, return_exceptions=True)
            # Log any exceptions that occurred
            for result in results:
                if isinstance(result, Exception):
                    _LOGGER.debug("Task failed during status update: %s", result)

    async def _query_device_status(self) -> None:
        """Query status for individual devices."""
        try:
            status_list = await self.client.query_device_status(
                self._device_ids_to_query,
            )

            for status_data in status_list:
                device_id = status_data.get("deviceId")
                if not device_id:
                    continue

                # Find device using IoT ID mapping
                device = self.get_device_by_iot_id(device_id)

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

                # Parse group-level properties (powerState, brightness, etc.)
                properties = parse_properties_list(status_data.get("properties", []))
                self._apply_properties_update(device, properties)

        except LiproApiError as err:
            _LOGGER.warning("Failed to query group status: %s", err)

    async def _query_outlet_power(self) -> None:
        """Query power information for outlet devices.

        The API returns aggregated data (single nowPower + energyList) for all
        requested devices, so we query each outlet individually to get accurate
        per-device power data.
        """
        if not self._outlet_ids_to_query:
            return

        try:
            for device_id in self._outlet_ids_to_query:
                power_data = await self.client.fetch_outlet_power_info([device_id])

                if not power_data:
                    continue

                device = self.get_device_by_iot_id(device_id)
                if device:
                    device.extra_data["power_info"] = power_data
                    _LOGGER.debug(
                        "Updated power info for %s: nowPower=%s",
                        device.name,
                        power_data.get("nowPower"),
                    )

        except LiproApiError as err:
            _LOGGER.debug("Failed to query outlet power: %s", err)

    async def _query_connect_status(self) -> None:
        """Query real-time connection status for devices.

        This provides more accurate online/offline status than the cached
        connectState property from device status queries.
        """
        if not self._device_ids_to_query:
            return

        try:
            connect_status = await self.client.query_connect_status(
                self._device_ids_to_query,
            )

            if not connect_status:
                return

            for device_id, is_online in connect_status.items():
                device = self.get_device_by_iot_id(device_id)
                if device:
                    # Update connectState property
                    device.update_properties(
                        {
                            "connectState": "1" if is_online else "0",
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
        """Force refresh of device list."""
        self._devices.clear()
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
                await self.client.send_group_command(
                    device.serial,
                    command,
                    device.device_type,
                    properties,
                )
            else:
                await self.client.send_command(
                    device.serial,
                    command,
                    device.device_type,
                    properties,
                    device.iot_name,
                )

            # Schedule a refresh to get updated state
            self.hass.async_create_task(self.async_request_refresh())

            return True

        except LiproApiError:
            _LOGGER.exception("Failed to send command to %s", device.name)
            return False
