"""Anonymous-share handler family for ``control.service_router``."""

from __future__ import annotations

from homeassistant.core import HomeAssistant, ServiceCall

from ..const.base import DOMAIN
from ..services import contracts as _contracts
from ..services.errors import raise_service_error as _raise_service_error
from ..services.share import (
    AnonymousShareManagerFactory,
    ClientSessionFactory,
    ShareServiceResponse,
    async_handle_get_anonymous_share_report as _async_handle_get_anonymous_share_report_service,
    async_handle_submit_anonymous_share as _async_handle_submit_anonymous_share_service,
)


async def async_handle_submit_anonymous_share(
    hass: HomeAssistant,
    call: ServiceCall,
    *,
    get_share_manager: AnonymousShareManagerFactory,
    get_client_session: ClientSessionFactory,
) -> ShareServiceResponse:
    """Handle the public anonymous-share submission service."""
    return await _async_handle_submit_anonymous_share_service(
        hass,
        call,
        get_anonymous_share_manager=get_share_manager,
        get_client_session=get_client_session,
        raise_service_error=_raise_service_error,
        domain=DOMAIN,
        attr_entry_id=_contracts.ATTR_ENTRY_ID,
    )


async def async_handle_get_anonymous_share_report(
    hass: HomeAssistant,
    call: ServiceCall,
    *,
    get_share_manager: AnonymousShareManagerFactory,
) -> ShareServiceResponse:
    """Handle the public anonymous-share preview service."""
    return await _async_handle_get_anonymous_share_report_service(
        hass,
        call,
        get_anonymous_share_manager=get_share_manager,
        attr_entry_id=_contracts.ATTR_ENTRY_ID,
    )


__all__ = [
    'async_handle_get_anonymous_share_report',
    'async_handle_submit_anonymous_share',
]
