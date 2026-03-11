"""Lipro API client for Home Assistant integration."""

from __future__ import annotations

import logging
from typing import Any

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

    @staticmethod
    def _build_compat_list_payload(rows: list[object]) -> dict[str, Any]:
        """Return a compatibility payload shaped as ``{"data": [...]}``.

        Several coordinator runtimes and older tests still expect API helpers to
        return a mapping with a ``data`` list. The new endpoint mixins typically
        return structured lists directly.
        """
        data: list[dict[str, Any]] = []
        for row in rows:
            if not isinstance(row, dict):
                continue
            normalized = dict(row)
            if "id" not in normalized:
                for key in ("iotId", "deviceId", "groupId"):
                    candidate = normalized.get(key)
                    if isinstance(candidate, str) and candidate.strip():
                        normalized["id"] = candidate
                        break
            data.append(normalized)
        return {"data": data}

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

    async def get_device_list(
        self,
        *,
        page: int = 1,
        page_size: int = 100,
    ) -> dict[str, Any]:
        """Compatibility wrapper around :meth:`get_devices`.

        Legacy refresh code uses a 1-based ``page`` index, expecting the
        response to include a ``data`` list and ``hasMore`` flag.
        """
        resolved_page = max(1, int(page))
        resolved_page_size = max(1, int(page_size))
        offset = (resolved_page - 1) * resolved_page_size

        response = await self.get_devices(offset=offset, limit=resolved_page_size)
        devices = list(response.get("devices", []))
        total = response.get("total", len(devices))
        try:
            total_count = int(total)
        except (TypeError, ValueError):
            total_count = len(devices)

        has_more = offset + len(devices) < total_count
        return {
            "data": devices,
            "hasMore": has_more,
        }

    async def query_iot_devices(self, device_ids: list[str]) -> dict[str, Any]:
        """Compatibility wrapper for batch status polling."""
        rows = await self.query_device_status(device_ids)
        return self._build_compat_list_payload(list(rows))

    async def query_outlet_devices(self, device_ids: list[str]) -> dict[str, Any]:
        """Compatibility wrapper for outlet status polling."""
        rows = await self.query_device_status(device_ids)
        return self._build_compat_list_payload(list(rows))

    async def query_group_devices(self, group_ids: list[str]) -> dict[str, Any]:
        """Compatibility wrapper for mesh group status polling."""
        rows = await self.query_mesh_group_status(group_ids)
        return self._build_compat_list_payload(list(rows))
