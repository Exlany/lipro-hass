"""Lipro API client for Home Assistant integration."""

from __future__ import annotations

import logging

import aiohttp

from ...const.api import REQUEST_TIMEOUT
from .auth_service import AuthApiService
from .client_transport import _ClientTransportMixin
from .endpoints import _ClientEndpointsMixin
from .errors import LiproAuthError
from .schedule_service import ScheduleApiService

_LOGGER = logging.getLogger(__name__)


class LiproClient(_ClientTransportMixin, _ClientEndpointsMixin):
    """Lipro API client with automatic 401 handling and token refresh."""

    def __init__(
        self,
        phone_id: str,
        session: aiohttp.ClientSession | None = None,
        request_timeout: int = REQUEST_TIMEOUT,
        *,
        entry_id: str | None = None,
    ) -> None:
        """Initialize the client.

        Args:
            phone_id: Device UUID for API signing.
            session: Optional aiohttp session to use.
            request_timeout: Request timeout in seconds.

        """
        self._init_transport(
            phone_id=phone_id,
            session=session,
            request_timeout=request_timeout,
        )
        self._init_auth_recovery(entry_id=entry_id)
        self._init_pacing()
        self._auth_api = AuthApiService(self, LiproAuthError, _LOGGER)
        self._schedule_api = ScheduleApiService(self)
