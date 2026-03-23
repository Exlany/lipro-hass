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
from typing import TYPE_CHECKING

import aiohttp

from ..telemetry.models import OperationOutcome
from .collector import AnonymousShareCollector
from .manager_submission import (
    submit_developer_feedback as _submit_developer_feedback_flow,
    submit_if_needed as _submit_if_needed_flow,
    submit_report as _submit_report_flow,
)
from .manager_support import (
    _ScopeState,
    build_aggregate_report_payload,
    build_scope_report_payload,
    get_scope_state,
    has_pending_report_data,
    iter_scope_states,
    load_reported_device_keys_for_state,
    mark_reported_devices,
    primary_scope_state,
    save_reported_device_keys_for_state,
    should_skip_report_submission,
    should_submit_if_needed,
)
from .share_client import ShareWorkerClient

if TYPE_CHECKING:
    from ..device import LiproDevice
    from .manager_support import _ScopeState

_LOGGER = logging.getLogger(__package__ or __name__)
_DEFAULT_SCOPE = "__default__"


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

    def is_aggregate_view(self) -> bool:
        """Return whether this manager represents the aggregate submission view."""
        return self._aggregate

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
        return get_scope_state(self._registry, scope_key)

    @property
    def _state(self) -> _ScopeState:
        return self._get_scope_state(self._scope_key)

    def _iter_scope_states(self) -> list[tuple[str, _ScopeState]]:
        return iter_scope_states(self._registry)

    def _iter_managers(self) -> list[AnonymousShareManager]:
        return [self.for_scope(scope_key) for scope_key, _ in self._iter_scope_states()]

    def iter_scoped_managers(self) -> list[AnonymousShareManager]:
        """Return scoped managers participating in aggregate submission."""
        return self._iter_managers()

    def _primary_state(self) -> _ScopeState:
        return primary_scope_state(self._registry)

    def get_submit_state(self) -> _ScopeState:
        """Return the current scope state for submit-flow helpers."""
        return self._state

    def get_primary_submit_state(self) -> _ScopeState:
        """Return the preferred state for aggregate-only submit helpers."""
        return self._primary_state()

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
    def last_submit_outcome(self) -> OperationOutcome | None:
        """Return the latest typed submit outcome for this manager view."""
        return self._state.last_submit_outcome

    def set_last_submit_outcome(self, outcome: OperationOutcome | None) -> None:
        """Persist the latest typed submit outcome for this manager view."""
        self._state.last_submit_outcome = outcome

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
        keys = load_reported_device_keys_for_state(self._state, logger=_LOGGER)
        if keys is not None:
            self._reported_device_keys = keys

    def _save_reported_devices(self) -> None:
        """Save reported device keys to storage."""
        save_reported_device_keys_for_state(self._state, logger=_LOGGER)

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

    def record_unknown_property(
        self, device_type: str, key: str, value: object
    ) -> None:
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

    def build_report(self) -> dict[str, object]:
        """Build the anonymous share report."""
        if not self._aggregate:
            return build_scope_report_payload(self._state)
        return build_aggregate_report_payload(self._registry)

    def get_pending_report(self) -> dict[str, object] | None:
        """Get pending report data for user review."""
        if self.pending_count == (0, 0):
            return None
        return self.build_report()

    async def _submit_share_payload_with_outcome(
        self,
        session: aiohttp.ClientSession,
        report: dict[str, object],
        *,
        label: str,
    ) -> OperationOutcome:
        """Submit one payload through the typed share-client outcome contract."""
        return await self._share_client.submit_share_payload_with_outcome(
            session,
            report,
            label=label,
            ensure_loaded=self.async_ensure_loaded,
        )

    async def async_submit_share_payload_with_outcome(
        self,
        session: aiohttp.ClientSession,
        report: dict[str, object],
        *,
        label: str,
    ) -> OperationOutcome:
        """Submit one prepared payload and return the typed outcome."""
        return await self._submit_share_payload_with_outcome(
            session,
            report,
            label=label,
        )

    async def _async_submit_share_payload(
        self,
        session: aiohttp.ClientSession,
        report: dict[str, object],
        *,
        label: str,
    ) -> bool:
        """Submit one prepared payload through the current scope's share client."""
        outcome = await self._submit_share_payload_with_outcome(
            session,
            report,
            label=label,
        )
        self._state.last_submit_outcome = outcome
        return outcome.is_success

    async def async_submit_share_payload(
        self,
        session: aiohttp.ClientSession,
        report: dict[str, object],
        *,
        label: str,
    ) -> bool:
        """Submit one prepared payload through the current scope's share client."""
        return await self._async_submit_share_payload(session, report, label=label)

    def _has_pending_report_data(self) -> bool:
        """Return whether the current scope has reportable pending data."""
        return has_pending_report_data(self._state, logger=_LOGGER)

    def has_pending_report_data(self) -> bool:
        """Return whether the current scope has reportable pending data."""
        return self._has_pending_report_data()

    def _should_skip_report_submission(self, *, force: bool) -> bool:
        """Return whether the current scope should skip one upload attempt."""
        return should_skip_report_submission(
            last_upload_time=self._last_upload_time,
            force=force,
            logger=_LOGGER,
        )

    def should_skip_report_submission(self, *, force: bool) -> bool:
        """Return whether the current scope should skip one upload attempt."""
        return self._should_skip_report_submission(force=force)

    async def _async_finalize_successful_submit(self) -> None:
        """Finalize a successful current-scope anonymous-share submission."""
        device_count, error_count = self.pending_count
        _LOGGER.info(
            "Anonymous share report submitted: %d devices, %d errors",
            device_count,
            error_count,
        )
        self._last_upload_time = time.time()
        mark_reported_devices(self._state)
        await asyncio.to_thread(self._save_reported_devices)
        self.clear()

    async def async_finalize_successful_submit(self) -> None:
        """Finalize one successful current-scope anonymous-share submission."""
        await self._async_finalize_successful_submit()

    def _should_submit_if_needed(self) -> bool:
        """Return whether automatic submission thresholds are currently met."""
        return should_submit_if_needed(
            pending_count=self.pending_count,
            last_upload_time=self._last_upload_time,
        )

    def should_submit_if_needed(self) -> bool:
        """Return whether automatic submission thresholds are currently met."""
        return self._should_submit_if_needed()

    async def submit_developer_feedback(
        self, session: aiohttp.ClientSession, feedback: dict[str, object]
    ) -> bool:
        """Submit one developer-feedback payload immediately."""
        return await _submit_developer_feedback_flow(
            self,
            session,
            feedback,
            logger=_LOGGER,
        )

    async def submit_report(
        self, session: aiohttp.ClientSession, force: bool = False
    ) -> bool:
        """Submit the anonymous share report to the server."""
        return await _submit_report_flow(self, session, force=force)

    async def submit_if_needed(self, session: aiohttp.ClientSession) -> bool:
        """Submit report if thresholds are met."""
        return await _submit_if_needed_flow(self, session)


from .registry import _get_root_manager, get_anonymous_share_manager  # noqa: E402

__all__ = ["AnonymousShareManager", "_get_root_manager", "get_anonymous_share_manager"]
