"""Local helpers for firmware update entity state and task handling."""

from __future__ import annotations

import asyncio
from collections.abc import Callable
from dataclasses import dataclass
from datetime import datetime, timedelta
import logging
from typing import TYPE_CHECKING, TypedDict

from ..core.ota.candidate import (
    _OtaCandidate,
    build_candidate,
    evaluate_install,
    has_pending_confirmation,
    project_candidate,
)
from ..core.ota.row_selector import OtaDeviceFingerprint, build_device_fingerprint
from ..core.ota.rows_cache import OtaRowsCacheKey, build_ota_rows_cache_key
from ..core.utils.log_safety import safe_error_placeholder

if TYPE_CHECKING:
    from collections.abc import Mapping

    from ..core.device import LiproDevice
    from ..runtime_types import LiproRuntimeCoordinator

type FirmwareManifestVersions = tuple[frozenset[str], dict[str, frozenset[str]]]
type FirmwareOtaCandidate = _OtaCandidate | None


class FirmwareStateAttributes(TypedDict, total=False):
    """Typed extra-state projection exposed by the firmware entity."""

    certified: bool
    confirmation_required: bool
    ota_checked_at: str
    last_error: str
    last_error_type: str


@dataclass(frozen=True, slots=True)
class FirmwareInstallRequest:
    """Validated firmware install request payload."""

    command: str
    properties: list[dict[str, str]] | None


@dataclass(frozen=True, slots=True)
class FirmwareInstallDecision:
    """Install decision normalized for entity-side translated errors."""

    request: FirmwareInstallRequest | None
    confirm_until: float
    error_key: str | None
    error_placeholders: dict[str, str] | None


@dataclass(frozen=True, slots=True)
class FirmwareOtaQueryContext:
    """Shared OTA query context built from runtime/device identity."""

    cache_key: OtaRowsCacheKey
    fingerprint: OtaDeviceFingerprint


@dataclass(frozen=True, slots=True)
class FirmwareRefreshProjection:
    """OTA candidate plus entity-facing projection fields."""

    ota_candidate: _OtaCandidate
    installed_version: str | None
    latest_version: str | None
    release_summary: str | None
    release_url: str | None


@dataclass(frozen=True, slots=True)
class FirmwareRefreshTaskOutcome:
    """Outcome after consuming one background OTA refresh task."""

    active_task: asyncio.Task[None] | None
    error: Exception | None


def build_firmware_state_attributes(
    *,
    ota_candidate: FirmwareOtaCandidate,
    confirm_until: float,
    last_ota_refresh: datetime,
    last_error: Exception | None,
    time_min_utc: datetime,
    now_monotonic: Callable[[], float],
) -> FirmwareStateAttributes:
    """Project entity-private OTA state into stable extra attributes."""
    attrs: FirmwareStateAttributes = {
        "certified": ota_candidate.certified if ota_candidate else False,
        "confirmation_required": has_pending_confirmation(
            confirm_until,
            now_monotonic=now_monotonic(),
        ),
    }
    if last_ota_refresh != time_min_utc:
        attrs["ota_checked_at"] = last_ota_refresh.isoformat()
    if last_error is not None:
        attrs["last_error"] = safe_error_placeholder(last_error)
        attrs["last_error_type"] = type(last_error).__name__
    return attrs


def resolve_install_request(
    *,
    ota_candidate: FirmwareOtaCandidate,
    requested_version: str | None,
    confirm_until: float,
    now_monotonic: float,
    confirmation_window_seconds: int,
) -> FirmwareInstallDecision:
    """Resolve install command/error state without HA translation coupling."""
    install_eval = evaluate_install(
        ota_candidate,
        requested_version=requested_version,
        confirm_until=confirm_until,
        now_monotonic=now_monotonic,
        confirmation_window_seconds=confirmation_window_seconds,
    )
    if install_eval.error_key is not None:
        return FirmwareInstallDecision(
            request=None,
            confirm_until=install_eval.confirm_until,
            error_key=install_eval.error_key,
            error_placeholders=install_eval.error_placeholders,
        )

    install_command = install_eval.install_command
    if install_command is None:
        return FirmwareInstallDecision(
            request=None,
            confirm_until=install_eval.confirm_until,
            error_key="firmware_install_unsupported",
            error_placeholders=None,
        )

    return FirmwareInstallDecision(
        request=FirmwareInstallRequest(
            command=install_command.command,
            properties=install_command.properties,
        ),
        confirm_until=install_eval.confirm_until,
        error_key=None,
        error_placeholders=None,
    )


def build_ota_query_context(
    coordinator: LiproRuntimeCoordinator,
    device: LiproDevice,
) -> FirmwareOtaQueryContext:
    """Build shared OTA cache/fingerprint context for one device."""
    return FirmwareOtaQueryContext(
        cache_key=build_ota_rows_cache_key(
            coordinator,
            device_type=device.device_type_hex,
            iot_name=device.iot_name,
            product_id=device.product_id,
        ),
        fingerprint=build_device_fingerprint(
            serial=device.serial,
            device_type=device.device_type_hex,
            iot_name=device.iot_name,
            product_id=device.product_id,
            physical_model=device.physical_model,
        ),
    )


def build_refresh_projection(
    row: Mapping[str, object] | None,
    *,
    device_firmware_version: str | None,
    device_iot_name: str | None,
    local_manifest: FirmwareManifestVersions,
    current_installed_version: str | None,
    is_version_newer: Callable[[str, str], bool],
) -> FirmwareRefreshProjection:
    """Build one OTA candidate and its entity-facing field projection."""
    ota_candidate = build_candidate(
        row,
        device_firmware_version=device_firmware_version,
        device_iot_name=device_iot_name,
        local_manifest=local_manifest,
        is_version_newer=is_version_newer,
    )
    projection = project_candidate(
        ota_candidate,
        current_installed_version=current_installed_version,
    )
    return FirmwareRefreshProjection(
        ota_candidate=ota_candidate,
        installed_version=projection.installed_version,
        latest_version=projection.latest_version,
        release_summary=projection.release_summary,
        release_url=projection.release_url,
    )


def consume_wait_result(result: object) -> Exception | None:
    """Normalize gather(return_exceptions=True) output into an exception."""
    if isinstance(result, asyncio.CancelledError):
        return None
    return result if isinstance(result, Exception) else None


def clear_refresh_task(
    task: asyncio.Task[None],
    *,
    logger: logging.Logger,
) -> Exception | None:
    """Consume task exceptions to avoid background warning noise."""
    try:
        err = task.exception()
    except asyncio.CancelledError:
        return None
    if isinstance(err, Exception):
        logger.debug(
            "Background OTA refresh task failed (%s)",
            safe_error_placeholder(err),
        )
        return err
    return None


def resolve_refresh_task_outcome(
    *,
    active_task: asyncio.Task[None] | None,
    completed_task: asyncio.Task[None],
    logger: logging.Logger,
) -> FirmwareRefreshTaskOutcome:
    """Resolve next active task pointer plus observable completion error."""
    return FirmwareRefreshTaskOutcome(
        active_task=None if active_task is completed_task else active_task,
        error=clear_refresh_task(completed_task, logger=logger),
    )


def notify_ota_error_callback(
    on_error: Callable[[Exception], None] | None,
    err: Exception,
    *,
    logger: logging.Logger,
) -> None:
    """Notify optional OTA error observer while swallowing callback noise."""
    if on_error is None:
        return
    try:
        on_error(err)
    except (
        AttributeError,
        LookupError,
        RuntimeError,
        TypeError,
        ValueError,
    ) as callback_err:
        logger.error(
            "OTA error callback failed (%s)",
            safe_error_placeholder(callback_err),
            exc_info=logger.isEnabledFor(logging.DEBUG),
        )


def should_refresh_ota(
    *,
    last_ota_refresh: datetime,
    refresh_interval: timedelta,
    now: Callable[[], datetime],
) -> bool:
    """Return True when cached OTA metadata is stale enough to refresh."""
    return now() - last_ota_refresh >= refresh_interval
