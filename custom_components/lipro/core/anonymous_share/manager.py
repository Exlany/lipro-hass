"""Anonymous device information sharing for Lipro integration.

This module builds privacy-preserving payloads that can be uploaded to the
optional share worker service to help improve device support and troubleshoot
errors.

Data is always sanitized before leaving the instance:
- Drops sensitive keys (account credentials, tokens, user/biz IDs, device IDs,
  WiFi SSID/MAC/IP fields).
- Masks token-like strings plus MAC/IP/device identifiers inside nested payloads.

Uploads are only triggered by explicit user opt-in (options) or explicit service
calls (developer feedback). Reports can be previewed locally before upload.
"""

from __future__ import annotations

import asyncio
import logging
import time
from typing import TYPE_CHECKING, Any

import aiohttp

from ...const import VERSION
from .collector import AnonymousShareCollector
from .const import (
    AUTO_UPLOAD_INTERVAL,
    MAX_PENDING_DEVICES,
    MAX_PENDING_ERRORS,
    MIN_UPLOAD_INTERVAL,
    SHARE_API_KEY,
)
from .report_builder import (
    build_anonymous_share_report,
    build_developer_feedback_report,
)
from .share_client import ShareWorkerClient
from .storage import load_reported_device_keys, save_reported_device_keys

if TYPE_CHECKING:
    from ..device import LiproDevice

_LOGGER = logging.getLogger(__package__ or __name__)


class AnonymousShareManager:
    """Collects anonymous device information and error reports.

    All collection is opt-in and respects user privacy.
    Only collects NEW devices that haven't been reported before.
    """

    def __init__(self) -> None:
        """Initialize the share manager."""
        self._collector = AnonymousShareCollector()
        self._last_upload_time: float = 0
        self._upload_lock = asyncio.Lock()
        self._installation_id: str | None = None
        self._ha_version: str | None = None
        self._share_client = ShareWorkerClient()
        self._reported_device_keys: set[str] = set()
        self._storage_path: str | None = None
        self._cache_loaded: bool = True  # True = no load needed

    def set_enabled(
        self,
        enabled: bool,
        error_reporting: bool = True,
        installation_id: str | None = None,
        storage_path: str | None = None,
        ha_version: str | None = None,
    ) -> None:
        """Enable or disable anonymous sharing.

        Args:
            enabled: Whether to enable device info sharing.
            error_reporting: Whether to enable error reporting.
            installation_id: Anonymous installation ID for deduplication.
            storage_path: Path to store reported device cache.
            ha_version: Home Assistant version string.

        """
        self._collector.set_enabled(enabled, error_reporting=error_reporting)
        self._installation_id = installation_id
        self._storage_path = storage_path
        self._ha_version = ha_version
        if enabled and storage_path:
            # Defer loading to async context to avoid blocking the event loop.
            self._cache_loaded = False
        if not enabled:
            self.clear()

    @property
    def is_enabled(self) -> bool:
        """Return whether anonymous sharing is enabled."""
        return self._collector.is_enabled

    @property
    def pending_count(self) -> tuple[int, int]:
        """Return count of pending items (devices, errors)."""
        return self._collector.pending_count

    @property
    def _install_token(self) -> str | None:
        """Expose install-token state for tests (never persisted)."""
        return self._share_client.install_token

    def clear(self) -> None:
        """Clear all pending data (does not clear reported device cache)."""
        self._collector.clear()

    async def async_ensure_loaded(self) -> None:
        """Load reported device cache in a thread to avoid blocking the event loop."""
        if self._cache_loaded:
            return
        await asyncio.to_thread(self._load_reported_devices)
        self._cache_loaded = True

    def _load_reported_devices(self) -> None:
        """Load previously reported device keys from storage."""
        if not self._storage_path:
            return
        loaded, keys = load_reported_device_keys(self._storage_path, logger=_LOGGER)
        if loaded:
            self._reported_device_keys = keys

    def _save_reported_devices(self) -> None:
        """Save reported device keys to storage."""
        if not self._storage_path:
            return
        save_reported_device_keys(
            self._storage_path,
            self._reported_device_keys,
            logger=_LOGGER,
        )

    # =========================================================================
    # Collection
    # =========================================================================

    def record_device(self, device: LiproDevice) -> None:
        """Record device information (only if model not already reported)."""
        self._collector.record_device(
            device, reported_device_keys=self._reported_device_keys
        )

    def record_devices(self, devices: list[LiproDevice]) -> None:
        """Record multiple devices."""
        self._collector.record_devices(
            devices, reported_device_keys=self._reported_device_keys
        )

    def record_unknown_property(
        self,
        device_type: str,
        key: str,
        value: Any,
    ) -> None:
        """Record an unknown property key."""
        self._collector.record_unknown_property(device_type, key, value)

    def record_unknown_device_type(
        self,
        physical_model: str | None,
        type_id: int,
        iot_name: str = "",
    ) -> None:
        """Record an unknown device type."""
        self._collector.record_unknown_device_type(physical_model, type_id, iot_name)

    def record_api_error(
        self,
        endpoint: str,
        code: str | int,
        message: str,
        method: str = "",
    ) -> None:
        """Record an API error."""
        self._collector.record_api_error(endpoint, code, message, method)

    def record_parse_error(
        self,
        location: str,
        exception: Exception,
        input_sample: str | None = None,
    ) -> None:
        """Record a parsing error."""
        self._collector.record_parse_error(location, exception, input_sample)

    def record_command_error(
        self,
        command: str,
        device_type: str,
        code: str | int,
        message: str,
        params: str = "",
    ) -> None:
        """Record a command execution error."""
        self._collector.record_command_error(
            command, device_type, code, message, params
        )

    # =========================================================================
    # Report generation and upload
    # =========================================================================

    def build_report(self) -> dict[str, Any]:
        """Build the anonymous share report."""
        return build_anonymous_share_report(
            installation_id=self._installation_id,
            ha_version=self._ha_version,
            devices=self._collector.devices,
            errors=list(self._collector.errors),
        )

    def get_pending_report(self) -> dict[str, Any] | None:
        """Get pending report data for user review."""
        if not self._collector.devices and not self._collector.errors:
            return None
        return self.build_report()

    @staticmethod
    def _build_upload_headers(*, install_token: str | None = None) -> dict[str, str]:
        """Build common headers for share uploads."""
        headers = {
            "User-Agent": f"HomeAssistant/Lipro {VERSION}",
            "X-API-Key": SHARE_API_KEY,
        }
        if install_token:
            headers["Authorization"] = f"Bearer {install_token}"
        return headers

    async def submit_developer_feedback(
        self,
        session: aiohttp.ClientSession,
        feedback: dict[str, Any],
    ) -> bool:
        """Submit one developer-feedback payload immediately.

        This is an explicit user action from service call, so it does not
        depend on anonymous-share opt-in switches.
        """
        async with self._upload_lock:
            report = build_developer_feedback_report(
                installation_id=self._installation_id,
                ha_version=self._ha_version,
                feedback=feedback,
            )
            if not await self._share_client.submit_share_payload(
                session,
                report,
                label="Developer feedback",
                ensure_loaded=self.async_ensure_loaded,
            ):
                return False
            _LOGGER.info("Developer feedback report submitted")
            return True

    async def submit_report(
        self,
        session: aiohttp.ClientSession,
        force: bool = False,
    ) -> bool:
        """Submit the anonymous share report to the server."""
        if not self._collector.is_enabled:
            return False

        if not self._collector.devices and not self._collector.errors:
            _LOGGER.debug("No anonymous share data to report")
            return True

        if not force:
            elapsed = time.time() - self._last_upload_time
            if elapsed < MIN_UPLOAD_INTERVAL:
                _LOGGER.debug(
                    "Skipping anonymous share upload, last upload was %d seconds ago",
                    int(elapsed),
                )
                return True

        async with self._upload_lock:
            report = self.build_report()
            if not await self._share_client.submit_share_payload(
                session,
                report,
                label="Anonymous share",
                ensure_loaded=self.async_ensure_loaded,
            ):
                return False

            device_count, error_count = self.pending_count
            _LOGGER.info(
                "Anonymous share report submitted: %d devices, %d errors",
                device_count,
                error_count,
            )
            self._last_upload_time = time.time()
            for device in self._collector.devices.values():
                self._reported_device_keys.add(device.iot_name)
            await asyncio.to_thread(self._save_reported_devices)
            self.clear()
            return True

    async def submit_if_needed(self, session: aiohttp.ClientSession) -> bool:
        """Submit report if thresholds are met."""
        if not self._collector.is_enabled:
            return True

        device_count, error_count = self.pending_count
        should_upload = (
            device_count >= MAX_PENDING_DEVICES
            or error_count >= MAX_PENDING_ERRORS
            or (time.time() - self._last_upload_time) > AUTO_UPLOAD_INTERVAL
        )

        if should_upload:
            return await self.submit_report(session)

        return True


_share_manager: AnonymousShareManager | None = None


def get_anonymous_share_manager(
    hass: Any = None,
) -> AnonymousShareManager:
    """Get the anonymous share manager for the given hass instance."""
    global _share_manager  # noqa: PLW0603

    if hass is not None:
        from ...const import DOMAIN  # noqa: PLC0415

        domain_data = hass.data.setdefault(DOMAIN, {})
        manager: AnonymousShareManager | None = domain_data.get(
            "anonymous_share_manager"
        )
        if manager is None:
            manager = AnonymousShareManager()
            domain_data["anonymous_share_manager"] = manager
        _share_manager = manager
        return manager

    if _share_manager is None:
        _share_manager = AnonymousShareManager()
    return _share_manager
