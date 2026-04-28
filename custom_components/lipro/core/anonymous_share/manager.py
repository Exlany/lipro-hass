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
from collections.abc import Sequence
import logging
from typing import TYPE_CHECKING

import aiohttp

from ..telemetry.models import OperationOutcome
from .manager_scope import AnonymousShareScopeViews
from .manager_submission import (
    submit_developer_feedback as _submit_developer_feedback_flow,
    submit_if_needed as _submit_if_needed_flow,
    submit_report as _submit_report_flow,
)
from .manager_support import (
    _AggregateViewState,
    _ScopeState,
    build_aggregate_report_payload,
    build_pending_report_payload,
    build_scope_report_payload,
    clear_scope_collectors,
    collector_method,
    configure_scope_state,
    finalize_successful_submit_state,
    has_pending_report_data,
    load_reported_device_keys_for_state,
    save_reported_device_keys_for_state,
    scope_state_property,
    should_skip_report_submission,
    should_submit_if_needed,
)

if TYPE_CHECKING:
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
        _aggregate_submit_outcome: _AggregateViewState | None = None,
    ) -> None:
        """Initialize the share manager or a scoped facade."""
        self._scope_key = _scope_key
        self._aggregate = _aggregate
        self._registry = {} if _registry is None else _registry
        self._scope_views = AnonymousShareScopeViews(
            registry=self._registry,
            manager_factory=self._create_scoped_manager,
        )
        self._scoped_views = self._scope_views.scoped_views
        self._aggregate_submit_outcome = (
            _aggregate_submit_outcome or _AggregateViewState()
        )

    def aggregate_view(self) -> AnonymousShareManager:
        """Return an aggregate view sharing the same registry."""
        return AnonymousShareManager(
            _registry=self._registry,
            _aggregate=True,
            _aggregate_submit_outcome=self._aggregate_submit_outcome,
        )

    def is_aggregate_view(self) -> bool:
        """Return whether this manager represents the aggregate submission view."""
        return self._aggregate

    def for_scope(self, scope_key: str) -> AnonymousShareManager:
        """Return a manager bound to one explicit scope key."""
        return self._scope_views.for_scope(scope_key)

    def _create_scoped_manager(self, scope_key: str) -> AnonymousShareManager:
        """Build one scoped manager sharing this manager's state registry."""
        return AnonymousShareManager(
            _scope_key=scope_key,
            _registry=self._registry,
            _aggregate_submit_outcome=self._aggregate_submit_outcome,
        )

    def _get_scope_state(self, scope_key: str) -> _ScopeState:
        return self._scope_views.get_scope_state(scope_key)

    @property
    def _scope_state(self) -> _ScopeState:
        return self._get_scope_state(self._scope_key)

    def _iter_scope_states(self) -> list[tuple[str, _ScopeState]]:
        return self._scope_views.iter_scope_states()

    def _iter_managers(self) -> list[AnonymousShareManager]:
        return list(self._scope_views.iter_scoped_managers())

    def iter_scoped_managers(self) -> Sequence[AnonymousShareManager]:
        """Return scoped managers participating in aggregate submission."""
        return self._iter_managers()

    def _primary_scope_state(self) -> _ScopeState:
        return self._scope_views.primary_scope_state()

    def get_submit_state(self) -> _ScopeState:
        """Return the current scope state for submit-flow helpers."""
        return self._scope_state

    def get_primary_submit_state(self) -> _ScopeState:
        """Return the preferred state for aggregate-only submit helpers."""
        return self._primary_scope_state()

    def _primary_manager(self) -> AnonymousShareManager:
        """Return the scoped manager matching the preferred aggregate submit state."""
        if not self._aggregate:
            return self
        return self._scope_views.primary_manager(default_scope=_DEFAULT_SCOPE)

    _share_collector = scope_state_property("collector")
    _last_upload_time = scope_state_property("last_upload_time")
    _installation_id = scope_state_property("installation_id")
    _ha_version = scope_state_property("ha_version")
    _share_client = scope_state_property("share_client")
    _reported_device_keys = scope_state_property("reported_device_keys")
    _storage_path = scope_state_property("storage_path")
    _cache_loaded = scope_state_property("cache_loaded")

    def set_enabled(
        self,
        enabled: bool,
        error_reporting: bool = True,
        installation_id: str | None = None,
        storage_path: str | None = None,
        ha_version: str | None = None,
    ) -> None:
        """Enable or disable anonymous sharing for the current scope."""
        configure_scope_state(
            self._scope_state,
            enabled=enabled,
            error_reporting=error_reporting,
            installation_id=installation_id,
            storage_path=storage_path,
            ha_version=ha_version,
        )
        if not enabled:
            self.clear()

    @property
    def is_enabled(self) -> bool:
        """Return whether anonymous sharing is enabled."""
        if self._aggregate:
            return self._scope_views.aggregate_enabled()
        return self._share_collector.is_enabled

    @property
    def pending_count(self) -> tuple[int, int]:
        """Return count of pending items (devices, errors)."""
        if not self._aggregate:
            return self._share_collector.pending_count
        return self._scope_views.aggregate_pending_count()

    @property
    def last_submit_outcome(self) -> OperationOutcome | None:
        """Return the latest typed submit outcome for this manager view."""
        if self._aggregate:
            return self._aggregate_submit_outcome.last_submit_outcome
        return self._scope_state.last_submit_outcome

    def set_last_submit_outcome(self, outcome: OperationOutcome | None) -> None:
        """Persist the latest typed submit outcome for this manager view."""
        if self._aggregate:
            self._aggregate_submit_outcome.last_submit_outcome = outcome
            return
        self._scope_state.last_submit_outcome = outcome

    @property
    def _install_token(self) -> str | None:
        """Expose install-token state for tests (never persisted)."""
        return self._share_client.install_token

    def clear(self) -> None:
        """Clear all pending data (does not clear reported device cache)."""
        if self._aggregate:
            clear_scope_collectors(self._registry)
            return
        self._share_collector.clear()

    async def async_ensure_loaded(self) -> None:
        """Load reported device cache in a thread to avoid blocking the event loop."""
        state = self._scope_state
        if state.cache_loaded:
            return
        await asyncio.to_thread(self._load_reported_devices)
        state.cache_loaded = True

    def _load_reported_devices(self) -> None:
        """Load previously reported device keys from storage."""
        loaded, keys = load_reported_device_keys_for_state(
            self._scope_state, logger=_LOGGER
        )
        self._reported_device_keys = keys if loaded else set()

    def _save_reported_devices(self) -> None:
        """Save reported device keys to storage."""
        save_reported_device_keys_for_state(self._scope_state, logger=_LOGGER)

    record_device = collector_method(
        "record_device",
        doc="Record device information for the current scope.",
        inject_reported_device_keys=True,
    )
    record_devices = collector_method(
        "record_devices",
        doc="Record multiple devices for the current scope.",
        inject_reported_device_keys=True,
    )
    record_unknown_property = collector_method(
        "record_unknown_property",
        doc="Record one unknown property for the current scope.",
    )
    record_unknown_device_type = collector_method(
        "record_unknown_device_type",
        doc="Record one unknown device type for the current scope.",
    )
    record_api_error = collector_method(
        "record_api_error",
        doc="Record one API error for the current scope.",
    )
    record_parse_error = collector_method(
        "record_parse_error",
        doc="Record one parse error for the current scope.",
    )
    record_command_error = collector_method(
        "record_command_error",
        doc="Record one command error for the current scope.",
    )

    def build_report(self) -> dict[str, object]:
        """Build the anonymous share report."""
        if not self._aggregate:
            return build_scope_report_payload(self._scope_state)
        return build_aggregate_report_payload(self._registry)

    def get_pending_report(self) -> dict[str, object] | None:
        """Get pending report data for user review."""
        return build_pending_report_payload(
            aggregate=self._aggregate,
            state=self._scope_state,
            registry=self._registry,
        )

    async def async_submit_share_payload_with_outcome(
        self,
        session: aiohttp.ClientSession,
        report: dict[str, object],
        *,
        label: str,
    ) -> OperationOutcome:
        """Submit one prepared payload and return the typed outcome."""
        if self._aggregate:
            return (
                await self._primary_manager().async_submit_share_payload_with_outcome(
                    session,
                    report,
                    label=label,
                )
            )
        return await self._share_client.submit_share_payload_with_outcome(
            session,
            report,
            label=label,
            ensure_loaded=self.async_ensure_loaded,
        )

    async def async_submit_share_payload(
        self,
        session: aiohttp.ClientSession,
        report: dict[str, object],
        *,
        label: str,
    ) -> bool:
        """Submit one prepared payload through the current scope's share client."""
        outcome = await self.async_submit_share_payload_with_outcome(
            session,
            report,
            label=label,
        )
        self.set_last_submit_outcome(outcome)
        return outcome.is_success

    def has_pending_report_data(self) -> bool:
        """Return whether the current scope has reportable pending data."""
        return has_pending_report_data(self._scope_state, logger=_LOGGER)

    def should_skip_report_submission(self, *, force: bool) -> bool:
        """Return whether the current scope should skip one upload attempt."""
        return should_skip_report_submission(
            last_upload_time=self._last_upload_time,
            force=force,
            logger=_LOGGER,
        )

    async def async_finalize_successful_submit(self) -> None:
        """Finalize one successful current-scope anonymous-share submission."""
        pending_count = self.pending_count
        await asyncio.to_thread(
            finalize_successful_submit_state,
            self._scope_state,
            pending_count=pending_count,
            logger=_LOGGER,
            save_reported_devices=self._save_reported_devices,
        )

    def should_submit_if_needed(self) -> bool:
        """Return whether automatic submission thresholds are currently met."""
        return should_submit_if_needed(
            pending_count=self.pending_count,
            last_upload_time=self._last_upload_time,
        )

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


__all__ = ["AnonymousShareManager"]
