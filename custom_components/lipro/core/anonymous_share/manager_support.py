"""Support-only helpers for anonymous-share manager mechanics."""

from __future__ import annotations

import asyncio
from collections.abc import Callable
from dataclasses import dataclass, field
import logging
import time

from ..telemetry.models import OperationOutcome
from .collector import AnonymousShareCollector
from .const import (
    AUTO_UPLOAD_INTERVAL,
    MAX_PENDING_DEVICES,
    MAX_PENDING_ERRORS,
    MIN_UPLOAD_INTERVAL,
)
from .models import SharedDevice, SharedError
from .report_builder import build_anonymous_share_report
from .share_client import ShareWorkerClient
from .storage import load_reported_device_keys, save_reported_device_keys

_DEFAULT_SCOPE = "__default__"


@dataclass(slots=True)
class _ScopeState:
    """Mutable anonymous-share state for a single logical scope."""

    collector: AnonymousShareCollector = field(default_factory=AnonymousShareCollector)
    last_upload_time: float = 0.0
    installation_id: str | None = None
    ha_version: str | None = None
    upload_lock: asyncio.Lock = field(default_factory=asyncio.Lock)
    share_client: ShareWorkerClient = field(default_factory=ShareWorkerClient)
    reported_device_keys: set[str] = field(default_factory=set)
    storage_path: str | None = None
    cache_loaded: bool = True
    storage_key: str = _DEFAULT_SCOPE
    last_submit_outcome: OperationOutcome | None = None


def get_scope_state(
    registry: dict[str, _ScopeState],
    scope_key: str,
) -> _ScopeState:
    """Return the scope state, creating it when needed."""
    state = registry.get(scope_key)
    if state is None:
        state = _ScopeState(storage_key=scope_key)
        registry[scope_key] = state
    return state


def iter_scope_states(
    registry: dict[str, _ScopeState],
) -> list[tuple[str, _ScopeState]]:
    """Return a stable snapshot of scope states."""
    return list(registry.items())


def primary_scope_state(registry: dict[str, _ScopeState]) -> _ScopeState:
    """Return the preferred state for aggregate-only operations."""
    for _, state in iter_scope_states(registry):
        if state.collector.is_enabled or state.collector.pending_count != (0, 0):
            return state
    return get_scope_state(registry, _DEFAULT_SCOPE)


def load_reported_device_keys_for_state(
    state: _ScopeState,
    *,
    logger: logging.Logger,
) -> set[str] | None:
    """Load one state's reported-device cache."""
    storage_path = state.storage_path
    if not storage_path:
        return None
    loaded, keys = load_reported_device_keys(
        storage_path,
        logger=logger,
        cache_key=state.storage_key,
    )
    return keys if loaded else None


def save_reported_device_keys_for_state(
    state: _ScopeState,
    *,
    logger: logging.Logger,
) -> None:
    """Persist one state's reported-device cache."""
    storage_path = state.storage_path
    if not storage_path:
        return
    save_reported_device_keys(
        storage_path,
        state.reported_device_keys,
        logger=logger,
        cache_key=state.storage_key,
    )


def build_scope_report_payload(state: _ScopeState) -> dict[str, object]:
    """Build a report payload for one scope."""
    return build_anonymous_share_report(
        installation_id=state.installation_id,
        ha_version=state.ha_version,
        devices=state.collector.devices,
        errors=list(state.collector.errors),
    )


def build_aggregate_report_payload(
    registry: dict[str, _ScopeState],
) -> dict[str, object]:
    """Build an aggregate report payload across all scopes."""
    devices: dict[str, SharedDevice] = {}
    errors: list[SharedError] = []
    for scope_key, state in iter_scope_states(registry):
        devices.update(
            {
                f"{scope_key}:{key}": value
                for key, value in state.collector.devices.items()
            }
        )
        errors.extend(state.collector.errors)

    primary = primary_scope_state(registry)
    installation_id = primary.installation_id if len(registry) == 1 else None
    return build_anonymous_share_report(
        installation_id=installation_id,
        ha_version=primary.ha_version,
        devices=devices,
        errors=errors,
    )


def has_pending_report_data(
    state: _ScopeState,
    *,
    logger: logging.Logger,
) -> bool:
    """Return whether a state has reportable pending data."""
    if state.collector.devices or state.collector.errors:
        return True
    logger.debug("No anonymous share data to report")
    return False


def should_skip_report_submission(
    *,
    last_upload_time: float,
    force: bool,
    logger: logging.Logger,
    now: Callable[[], float] = time.time,
) -> bool:
    """Return whether the current upload attempt should be skipped."""
    if force:
        return False
    elapsed = now() - last_upload_time
    if elapsed >= MIN_UPLOAD_INTERVAL:
        return False
    logger.debug(
        "Skipping anonymous share upload, last upload was %d seconds ago",
        int(elapsed),
    )
    return True


def should_submit_if_needed(
    *,
    pending_count: tuple[int, int],
    last_upload_time: float,
    now: Callable[[], float] = time.time,
) -> bool:
    """Return whether automatic submission thresholds are met."""
    device_count, error_count = pending_count
    return (
        device_count >= MAX_PENDING_DEVICES
        or error_count >= MAX_PENDING_ERRORS
        or (now() - last_upload_time) > AUTO_UPLOAD_INTERVAL
    )


def mark_reported_devices(state: _ScopeState) -> None:
    """Move current devices into the reported-device cache."""
    for device in state.collector.devices.values():
        state.reported_device_keys.add(device.iot_name)
