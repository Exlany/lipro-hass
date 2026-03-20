"""Anonymous-share related service handlers for Lipro integration."""

from __future__ import annotations

from collections.abc import Mapping
from typing import Protocol, TypedDict

from aiohttp import ClientSession

from homeassistant.core import HomeAssistant, ServiceCall
from homeassistant.exceptions import ServiceValidationError

from ..core.telemetry.models import OperationOutcome, build_operation_outcome
from .execution import ServiceErrorRaiser

type SharePreviewReport = Mapping[str, object]


class ShareSubmitResponse(TypedDict, total=False):
    """Response payload returned by submit_anonymous_share."""

    success: bool
    devices: int
    errors: int
    message: str
    requested_entry_id: str
    outcome_kind: str
    reason_code: str
    failure_summary: dict[str, str | None]
    http_status: int
    retry_after_seconds: float


class SharePreviewResponse(TypedDict, total=False):
    """Response payload returned by get_anonymous_share_report."""

    has_data: bool
    device_count: int
    error_count: int
    devices: list[object]
    errors: list[object]
    requested_entry_id: str


type ShareServiceResponse = ShareSubmitResponse | SharePreviewResponse


class AnonymousShareManager(Protocol):
    """Anonymous-share manager contract used by service handlers."""

    is_enabled: bool
    pending_count: tuple[int, int]

    @property
    def last_submit_outcome(self) -> OperationOutcome | None:
        """Return the latest typed submit outcome when available."""

    async def submit_report(self, session: ClientSession, *, force: bool) -> bool:
        """Submit one report payload."""

    def get_pending_report(self) -> SharePreviewReport | None:
        """Return the current pending anonymous-share preview payload."""


class AnonymousShareManagerFactory(Protocol):
    """Resolve one anonymous-share manager for the requested entry scope."""

    def __call__(
        self,
        hass: HomeAssistant,
        *,
        entry_id: str | None = None,
    ) -> AnonymousShareManager:
        """Return an aggregate or entry-scoped anonymous-share manager."""


class ClientSessionFactory(Protocol):
    """Return the aiohttp client session used by Home Assistant."""

    def __call__(self, hass: HomeAssistant) -> ClientSession:
        """Return the shared Home Assistant client session."""


def _resolve_requested_entry_id(call: ServiceCall, attr_entry_id: str) -> str | None:
    """Return the optional entry id from one service call payload."""
    entry_id = call.data.get(attr_entry_id)
    return entry_id if isinstance(entry_id, str) and entry_id else None


def _resolve_share_manager(
    hass: HomeAssistant,
    call: ServiceCall,
    *,
    get_anonymous_share_manager: AnonymousShareManagerFactory,
    attr_entry_id: str,
) -> AnonymousShareManager:
    """Resolve aggregate or entry-scoped anonymous-share manager."""
    return get_anonymous_share_manager(
        hass,
        entry_id=_resolve_requested_entry_id(call, attr_entry_id),
    )


def _coerce_submit_outcome(value: object) -> OperationOutcome | None:
    """Normalize one optional manager-reported submit outcome."""
    return value if isinstance(value, OperationOutcome) else None


def build_submit_anonymous_share_response(
    *,
    success: bool = True,
    device_count: int,
    error_count: int,
    requested_entry_id: str | None = None,
    outcome: OperationOutcome | None = None,
) -> ShareSubmitResponse:
    """Build the canonical submit_anonymous_share service payload."""
    normalized_outcome = outcome or build_operation_outcome(
        kind=("success" if success else "failed"),
        reason_code=("submitted" if success else "submit_failed"),
    )
    result: ShareSubmitResponse = {
        "success": success,
        "devices": device_count,
        "errors": error_count,
    }
    result.update(normalized_outcome.to_dict())
    if requested_entry_id:
        result["requested_entry_id"] = requested_entry_id
    return result


def build_anonymous_share_preview_response(
    report: SharePreviewReport | None,
    *,
    requested_entry_id: str | None = None,
) -> SharePreviewResponse:
    """Build the canonical get_anonymous_share_report service payload."""
    result: SharePreviewResponse
    if report is None:
        result = {
            "has_data": False,
            "devices": [],
            "errors": [],
        }
    else:
        devices = report.get("devices")
        errors = report.get("errors")
        raw_device_count = report.get("device_count", 0)
        raw_error_count = report.get("error_count", 0)
        result = {
            "has_data": True,
            "device_count": raw_device_count if isinstance(raw_device_count, int) else 0,
            "error_count": raw_error_count if isinstance(raw_error_count, int) else 0,
            "devices": devices if isinstance(devices, list) else [],
            "errors": errors if isinstance(errors, list) else [],
        }

    if requested_entry_id:
        result["requested_entry_id"] = requested_entry_id
    return result


async def async_handle_submit_anonymous_share(
    hass: HomeAssistant,
    call: ServiceCall,
    *,
    get_anonymous_share_manager: AnonymousShareManagerFactory,
    get_client_session: ClientSessionFactory,
    raise_service_error: ServiceErrorRaiser,
    domain: str,
    attr_entry_id: str,
) -> ShareSubmitResponse:
    """Handle submit_anonymous_share service."""
    del raise_service_error
    share_manager = _resolve_share_manager(
        hass,
        call,
        get_anonymous_share_manager=get_anonymous_share_manager,
        attr_entry_id=attr_entry_id,
    )
    if not share_manager.is_enabled:
        raise ServiceValidationError(
            translation_domain=domain,
            translation_key="anonymous_share_not_enabled",
        )

    device_count, error_count = share_manager.pending_count
    requested_entry_id = _resolve_requested_entry_id(call, attr_entry_id)
    if device_count == 0 and error_count == 0:
        result = build_submit_anonymous_share_response(
            success=True,
            device_count=0,
            error_count=0,
            requested_entry_id=requested_entry_id,
            outcome=build_operation_outcome(
                kind="skipped",
                reason_code="no_pending_data",
            ),
        )
        result["message"] = "No data to submit"
        return result

    session = get_client_session(hass)
    success = await share_manager.submit_report(session, force=True)
    outcome = _coerce_submit_outcome(getattr(share_manager, "last_submit_outcome", None))
    return build_submit_anonymous_share_response(
        success=success,
        device_count=device_count,
        error_count=error_count,
        requested_entry_id=requested_entry_id,
        outcome=outcome,
    )


async def async_handle_get_anonymous_share_report(
    hass: HomeAssistant,
    call: ServiceCall,
    *,
    get_anonymous_share_manager: AnonymousShareManagerFactory,
    attr_entry_id: str,
) -> SharePreviewResponse:
    """Handle get_anonymous_share_report service."""
    share_manager = _resolve_share_manager(
        hass,
        call,
        get_anonymous_share_manager=get_anonymous_share_manager,
        attr_entry_id=attr_entry_id,
    )
    return build_anonymous_share_preview_response(
        share_manager.get_pending_report(),
        requested_entry_id=_resolve_requested_entry_id(call, attr_entry_id),
    )
