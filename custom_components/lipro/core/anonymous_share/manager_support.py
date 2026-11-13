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
from .report_builder import LITE_REPORT_ITEM_LIMIT, build_anonymous_share_report
from .share_client import ShareWorkerClient
from .storage import load_reported_device_keys

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


@dataclass(slots=True)
class _AggregateViewState:
    """Shared aggregate-view state reused across manager views."""

    last_submit_outcome: OperationOutcome | None = None


@dataclass(frozen=True, slots=True)
class ShareReportSnapshot:
    """Capture the payload and identities/counts eligible for acknowledgement."""

    payload: dict[str, object]
    devices: tuple[tuple[str, SharedDevice], ...]
    errors: tuple[tuple[SharedError, int], ...]
    unknown_properties: frozenset[tuple[str, str]]
    unknown_device_types: frozenset[tuple[str | None, int]]


def build_scope_report_snapshot(state: _ScopeState) -> ShareReportSnapshot:
    """Snapshot pending records synchronously before yielding to upload I/O."""
    return ShareReportSnapshot(
        payload=build_scope_report_payload(state),
        devices=tuple(state.collector.devices.items()),
        errors=tuple((error, error.count) for error in state.collector.errors),
        unknown_properties=frozenset(state.collector.unknown_properties),
        unknown_device_types=frozenset(state.collector.unknown_device_types),
    )


def scope_state_property(attr: str) -> property:
    """Build one internal `AnonymousShareManager` property bound to `_scope_state`."""

    def _getter(owner: object) -> object:
        state = object.__getattribute__(owner, "_scope_state")
        return getattr(state, attr)

    def _setter(owner: object, value: object) -> None:
        state = object.__getattribute__(owner, "_scope_state")
        setattr(state, attr, value)

    return property(_getter, _setter)


def collector_method(
    method_name: str,
    *,
    doc: str | None = None,
    inject_reported_device_keys: bool = False,
) -> Callable[..., object]:
    """Build one internal `AnonymousShareManager` method bound to `_share_collector`."""

    def _method(owner: object, *args: object, **kwargs: object) -> object:
        if inject_reported_device_keys:
            reported_device_keys = object.__getattribute__(
                owner, "_reported_device_keys"
            )
            kwargs.setdefault("reported_device_keys", reported_device_keys)
        collector = object.__getattribute__(owner, "_share_collector")
        return getattr(collector, method_name)(*args, **kwargs)

    _method.__name__ = method_name
    _method.__doc__ = doc
    return _method


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


def configure_scope_state(
    state: _ScopeState,
    *,
    enabled: bool,
    error_reporting: bool,
    installation_id: str | None,
    storage_path: str | None,
    ha_version: str | None,
) -> None:
    """Apply enabled/metadata settings to one scope state."""
    storage_path_changed = state.storage_path != storage_path
    state.collector.set_enabled(enabled, error_reporting=error_reporting)
    state.installation_id = installation_id
    state.storage_path = storage_path
    state.ha_version = ha_version
    if storage_path_changed:
        state.reported_device_keys.clear()
    state.cache_loaded = not (enabled and storage_path)


def aggregate_pending_count(registry: dict[str, _ScopeState]) -> tuple[int, int]:
    """Return aggregate pending counts across all registered scopes."""
    device_total = 0
    error_total = 0
    for _, state in iter_scope_states(registry):
        devices, errors = state.collector.pending_count
        device_total += devices
        error_total += errors
    return device_total, error_total


def clear_scope_collectors(registry: dict[str, _ScopeState]) -> None:
    """Clear pending collector data for all states in one registry."""
    for _, state in iter_scope_states(registry):
        state.collector.clear()


def load_reported_device_keys_for_state(
    state: _ScopeState,
    *,
    logger: logging.Logger,
) -> tuple[bool, set[str]]:
    """Load one state's reported-device cache."""
    storage_path = state.storage_path
    if not storage_path:
        return False, set()
    return load_reported_device_keys(
        storage_path,
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


def build_pending_report_payload(
    *,
    aggregate: bool,
    state: _ScopeState,
    registry: dict[str, _ScopeState],
) -> dict[str, object] | None:
    """Build one pending-report payload when reportable data exists."""
    if aggregate:
        pending = aggregate_pending_count(registry)
        if pending == (0, 0):
            return None
        return build_aggregate_report_payload(registry)
    if state.collector.pending_count == (0, 0):
        return None
    return build_scope_report_payload(state)


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


def finalize_successful_submit_state(
    state: _ScopeState,
    snapshot: ShareReportSnapshot,
    *,
    logger: logging.Logger,
    lite: bool = False,
) -> None:
    """Acknowledge only delivered records on the collector's event loop."""
    devices = snapshot.devices[:LITE_REPORT_ITEM_LIMIT] if lite else snapshot.devices
    errors = snapshot.errors[:LITE_REPORT_ITEM_LIMIT] if lite else snapshot.errors
    logger.info(
        "Anonymous share report submitted: %d devices, %d errors",
        len(devices),
        len(errors),
    )
    state.last_upload_time = time.time()
    for key, device in devices:
        state.reported_device_keys.add(device.iot_name)
        if state.collector.devices.get(key) is device:
            del state.collector.devices[key]

    delivered_counts = {id(error): count for error, count in errors}
    remaining_errors = []
    for error in state.collector.errors:
        error.count -= delivered_counts.get(id(error), 0)
        if error.count > 0:
            remaining_errors.append(error)
    state.collector.errors.clear()
    state.collector.errors.extend(remaining_errors)
    if not lite:
        state.collector.unknown_properties.difference_update(
            snapshot.unknown_properties
        )
        state.collector.unknown_device_types.difference_update(
            snapshot.unknown_device_types
        )
