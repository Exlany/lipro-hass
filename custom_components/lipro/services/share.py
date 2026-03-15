"""Anonymous-share related service handlers for Lipro integration."""

from __future__ import annotations

from collections.abc import Mapping
from typing import Protocol

from aiohttp import ClientSession

from homeassistant.core import HomeAssistant, ServiceCall
from homeassistant.exceptions import ServiceValidationError

from .execution import ServiceErrorRaiser

type SharePreviewReport = Mapping[str, object]
type ShareServiceResponse = dict[str, object]


class AnonymousShareManager(Protocol):
    """Anonymous-share manager contract used by service handlers."""

    is_enabled: bool
    pending_count: tuple[int, int]

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



def build_submit_anonymous_share_response(
    *,
    device_count: int,
    error_count: int,
    requested_entry_id: str | None = None,
) -> ShareServiceResponse:
    """Build the canonical submit_anonymous_share success payload."""
    result: ShareServiceResponse = {
        "success": True,
        "devices": device_count,
        "errors": error_count,
    }
    if requested_entry_id:
        result["requested_entry_id"] = requested_entry_id
    return result



def build_anonymous_share_preview_response(
    report: SharePreviewReport | None,
    *,
    requested_entry_id: str | None = None,
) -> ShareServiceResponse:
    """Build the canonical get_anonymous_share_report service payload."""
    if report is None:
        result: ShareServiceResponse = {
            "has_data": False,
            "devices": [],
            "errors": [],
        }
    else:
        result = {
            "has_data": True,
            "device_count": report.get("device_count", 0),
            "error_count": report.get("error_count", 0),
            "devices": report.get("devices", []),
            "errors": report.get("errors", []),
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
) -> ShareServiceResponse:
    """Handle submit_anonymous_share service."""
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
        return {
            **build_submit_anonymous_share_response(
                device_count=0,
                error_count=0,
                requested_entry_id=requested_entry_id,
            ),
            "message": "No data to submit",
        }

    session = get_client_session(hass)
    success = await share_manager.submit_report(session, force=True)
    if not success:
        raise_service_error("anonymous_share_submit_failed")

    return build_submit_anonymous_share_response(
        device_count=device_count,
        error_count=error_count,
        requested_entry_id=requested_entry_id,
    )


async def async_handle_get_anonymous_share_report(
    hass: HomeAssistant,
    call: ServiceCall,
    *,
    get_anonymous_share_manager: AnonymousShareManagerFactory,
    attr_entry_id: str,
) -> ShareServiceResponse:
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
