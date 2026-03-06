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
from dataclasses import dataclass, field
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
_DEFAULT_SCOPE = "__default__"
_AGGREGATE_MANAGER_KEY = "anonymous_share_manager"
_SCOPED_MANAGERS_KEY = "anonymous_share_managers"


@dataclass(slots=True)
class _ScopeState:
    """Mutable anonymous-share state for a single logical scope."""

    collector: AnonymousShareCollector = field(default_factory=AnonymousShareCollector)
    last_upload_time: float = 0.0
    upload_lock: asyncio.Lock = field(default_factory=asyncio.Lock)
    installation_id: str | None = None
    ha_version: str | None = None
    share_client: ShareWorkerClient = field(default_factory=ShareWorkerClient)
    reported_device_keys: set[str] = field(default_factory=set)
    storage_path: str | None = None
    cache_loaded: bool = True
    storage_key: str = _DEFAULT_SCOPE


class AnonymousShareManager:
    """Collects anonymous device information and error reports."""

    def __init__(
        self,
        *,
        _scope_key: str = _DEFAULT_SCOPE,
        _registry: dict[str, _ScopeState] | None = None,
        _aggregate: bool = False,
    ) -> None:
        """Initialize the share manager or a scoped facade."""
        self._scope_key = _scope_key
        self._aggregate = _aggregate
        self._registry = {} if _registry is None else _registry
        self._scoped_views: dict[str, AnonymousShareManager] = {}

    def aggregate_view(self) -> AnonymousShareManager:
        """Return an aggregate view sharing the same registry."""
        return AnonymousShareManager(_registry=self._registry, _aggregate=True)

    def for_scope(self, scope_key: str) -> AnonymousShareManager:
        """Return a manager bound to one explicit scope key."""
        manager = self._scoped_views.get(scope_key)
        if manager is None:
            manager = AnonymousShareManager(
                _scope_key=scope_key,
                _registry=self._registry,
            )
            self._scoped_views[scope_key] = manager
        return manager

    def _get_scope_state(self, scope_key: str) -> _ScopeState:
        state = self._registry.get(scope_key)
        if state is None:
            state = _ScopeState(storage_key=scope_key)
            self._registry[scope_key] = state
        return state

    @property
    def _state(self) -> _ScopeState:
        return self._get_scope_state(self._scope_key)

    def _iter_scope_states(self) -> list[tuple[str, _ScopeState]]:
        return list(self._registry.items())

    def _iter_managers(self) -> list[AnonymousShareManager]:
        return [self.for_scope(scope_key) for scope_key, _ in self._iter_scope_states()]

    def _primary_state(self) -> _ScopeState:
        for _, state in self._iter_scope_states():
            if state.collector.is_enabled or state.collector.pending_count != (0, 0):
                return state
        return self._get_scope_state(_DEFAULT_SCOPE)

    @property
    def _collector(self) -> AnonymousShareCollector:
        return self._state.collector

    @_collector.setter
    def _collector(self, value: AnonymousShareCollector) -> None:
        self._state.collector = value

    @property
    def _last_upload_time(self) -> float:
        return self._state.last_upload_time

    @_last_upload_time.setter
    def _last_upload_time(self, value: float) -> None:
        self._state.last_upload_time = value

    @property
    def _installation_id(self) -> str | None:
        return self._state.installation_id

    @_installation_id.setter
    def _installation_id(self, value: str | None) -> None:
        self._state.installation_id = value

    @property
    def _ha_version(self) -> str | None:
        return self._state.ha_version

    @_ha_version.setter
    def _ha_version(self, value: str | None) -> None:
        self._state.ha_version = value

    @property
    def _share_client(self) -> ShareWorkerClient:
        return self._state.share_client

    @_share_client.setter
    def _share_client(self, value: ShareWorkerClient) -> None:
        self._state.share_client = value

    @property
    def _reported_device_keys(self) -> set[str]:
        return self._state.reported_device_keys

    @_reported_device_keys.setter
    def _reported_device_keys(self, value: set[str]) -> None:
        self._state.reported_device_keys = value

    @property
    def _storage_path(self) -> str | None:
        return self._state.storage_path

    @_storage_path.setter
    def _storage_path(self, value: str | None) -> None:
        self._state.storage_path = value

    @property
    def _cache_loaded(self) -> bool:
        return self._state.cache_loaded

    @_cache_loaded.setter
    def _cache_loaded(self, value: bool) -> None:
        self._state.cache_loaded = value

    def set_enabled(
        self,
        enabled: bool,
        error_reporting: bool = True,
        installation_id: str | None = None,
        storage_path: str | None = None,
        ha_version: str | None = None,
    ) -> None:
        """Enable or disable anonymous sharing for the current scope."""
        state = self._state
        state.collector.set_enabled(enabled, error_reporting=error_reporting)
        state.installation_id = installation_id
        state.storage_path = storage_path
        state.ha_version = ha_version
        if enabled and storage_path:
            state.cache_loaded = False
        if not enabled:
            self.clear()

    @property
    def is_enabled(self) -> bool:
        """Return whether anonymous sharing is enabled."""
        if self._aggregate:
            return any(
                state.collector.is_enabled for _, state in self._iter_scope_states()
            )
        return self._collector.is_enabled

    @property
    def pending_count(self) -> tuple[int, int]:
        """Return count of pending items (devices, errors)."""
        if not self._aggregate:
            return self._collector.pending_count
        device_total = 0
        error_total = 0
        for _, state in self._iter_scope_states():
            devices, errors = state.collector.pending_count
            device_total += devices
            error_total += errors
        return device_total, error_total

    @property
    def _install_token(self) -> str | None:
        """Expose install-token state for tests (never persisted)."""
        return self._share_client.install_token

    def clear(self) -> None:
        """Clear all pending data (does not clear reported device cache)."""
        if self._aggregate:
            for _, state in self._iter_scope_states():
                state.collector.clear()
            return
        self._collector.clear()

    async def async_ensure_loaded(self) -> None:
        """Load reported device cache in a thread to avoid blocking the event loop."""
        state = self._state
        if state.cache_loaded:
            return
        await asyncio.to_thread(self._load_reported_devices)
        state.cache_loaded = True

    def _load_reported_devices(self) -> None:
        """Load previously reported device keys from storage."""
        storage_path = self._storage_path
        if not storage_path:
            return
        loaded, keys = load_reported_device_keys(
            storage_path,
            logger=_LOGGER,
            cache_key=self._state.storage_key,
        )
        if loaded:
            self._reported_device_keys = keys

    def _save_reported_devices(self) -> None:
        """Save reported device keys to storage."""
        storage_path = self._storage_path
        if not storage_path:
            return
        save_reported_device_keys(
            storage_path,
            self._reported_device_keys,
            logger=_LOGGER,
            cache_key=self._state.storage_key,
        )

    def record_device(self, device: LiproDevice) -> None:
        """Record device information for the current scope."""
        self._collector.record_device(
            device, reported_device_keys=self._reported_device_keys
        )

    def record_devices(self, devices: list[LiproDevice]) -> None:
        """Record multiple devices for the current scope."""
        self._collector.record_devices(
            devices, reported_device_keys=self._reported_device_keys
        )

    def record_unknown_property(self, device_type: str, key: str, value: Any) -> None:
        """Record one unknown property for the current scope."""
        self._collector.record_unknown_property(device_type, key, value)

    def record_unknown_device_type(
        self,
        physical_model: str | None,
        type_id: int,
        iot_name: str = "",
    ) -> None:
        """Record one unknown device type for the current scope."""
        self._collector.record_unknown_device_type(physical_model, type_id, iot_name)

    def record_api_error(
        self, endpoint: str, code: str | int, message: str, method: str = ""
    ) -> None:
        """Record one API error for the current scope."""
        self._collector.record_api_error(endpoint, code, message, method)

    def record_parse_error(
        self,
        location: str,
        exception: Exception,
        input_sample: str | None = None,
    ) -> None:
        """Record one parse error for the current scope."""
        self._collector.record_parse_error(location, exception, input_sample)

    def record_command_error(
        self,
        command: str,
        device_type: str,
        code: str | int,
        message: str,
        params: str = "",
    ) -> None:
        """Record one command error for the current scope."""
        self._collector.record_command_error(
            command, device_type, code, message, params
        )

    def build_report(self) -> dict[str, Any]:
        """Build the anonymous share report."""
        if not self._aggregate:
            return build_anonymous_share_report(
                installation_id=self._installation_id,
                ha_version=self._ha_version,
                devices=self._collector.devices,
                errors=list(self._collector.errors),
            )
        devices: dict[str, Any] = {}
        errors: list[Any] = []
        for scope_key, state in self._iter_scope_states():
            devices.update(
                {
                    f"{scope_key}:{key}": value
                    for key, value in state.collector.devices.items()
                }
            )
            errors.extend(state.collector.errors)
        primary = self._primary_state()
        installation_id = primary.installation_id if len(self._registry) == 1 else None
        return build_anonymous_share_report(
            installation_id=installation_id,
            ha_version=primary.ha_version,
            devices=devices,
            errors=errors,
        )

    def get_pending_report(self) -> dict[str, Any] | None:
        """Get pending report data for user review."""
        if self.pending_count == (0, 0):
            return None
        return self.build_report()

    @staticmethod
    def _build_upload_headers(*, install_token: str | None = None) -> dict[str, str]:
        headers = {
            "User-Agent": f"HomeAssistant/Lipro {VERSION}",
            "X-API-Key": SHARE_API_KEY,
        }
        if install_token:
            headers["Authorization"] = f"Bearer {install_token}"
        return headers

    async def submit_developer_feedback(
        self, session: aiohttp.ClientSession, feedback: dict[str, Any]
    ) -> bool:
        """Submit one developer-feedback payload immediately."""
        state = self._primary_state() if self._aggregate else self._state
        async with state.upload_lock:
            report = build_developer_feedback_report(
                installation_id=state.installation_id,
                ha_version=state.ha_version,
                feedback=feedback,
            )
            if not await state.share_client.submit_share_payload(
                session,
                report,
                label="Developer feedback",
                ensure_loaded=self.async_ensure_loaded,
            ):
                return False
            _LOGGER.info("Developer feedback report submitted")
            return True

    async def submit_report(
        self, session: aiohttp.ClientSession, force: bool = False
    ) -> bool:
        """Submit the anonymous share report to the server."""
        if self._aggregate:
            success = True
            for manager in self._iter_managers():
                success = await manager.submit_report(session, force=force) and success
            return success
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
        async with self._state.upload_lock:
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
        if self._aggregate:
            success = True
            for manager in self._iter_managers():
                success = await manager.submit_if_needed(session) and success
            return success
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



def _get_root_manager() -> AnonymousShareManager:
    global _share_manager  # noqa: PLW0603
    if _share_manager is None:
        _share_manager = AnonymousShareManager(_aggregate=True)
    return _share_manager


def get_anonymous_share_manager(
    hass: Any = None,
    *,
    entry_id: str | None = None,
) -> AnonymousShareManager:
    """Get the anonymous share manager for the resolved scope or aggregate view."""
    resolved_entry_id = entry_id
    root_manager = _get_root_manager()
    if hass is not None:
        from ...const import DOMAIN  # noqa: PLC0415

        domain_data = hass.data.setdefault(DOMAIN, {})
        aggregate_manager: AnonymousShareManager | None = domain_data.get(
            _AGGREGATE_MANAGER_KEY
        )
        if aggregate_manager is None:
            aggregate_manager = root_manager.aggregate_view()
            domain_data[_AGGREGATE_MANAGER_KEY] = aggregate_manager
        if resolved_entry_id is None:
            return aggregate_manager
        scoped_managers: dict[str, AnonymousShareManager] = domain_data.setdefault(
            _SCOPED_MANAGERS_KEY,
            {},
        )
        manager = scoped_managers.get(resolved_entry_id)
        if manager is None:
            manager = root_manager.for_scope(resolved_entry_id)
            scoped_managers[resolved_entry_id] = manager
        return manager
    if resolved_entry_id is not None:
        return root_manager.for_scope(resolved_entry_id)
    return root_manager
