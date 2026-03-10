"""Device catalog endpoints for LiproClient."""

from __future__ import annotations

from typing import Any, cast

from ....const.api import PATH_FETCH_DEVICES, PATH_GET_PRODUCT_CONFIGS
from ..client_base import _ClientBase
from ..types import DeviceListResponse


class _ClientDeviceEndpointsMixin(_ClientBase):
    """Endpoints: device list and product configs."""

    async def get_devices(self, offset: int = 0, limit: int = 100) -> DeviceListResponse:
        """Get all devices.

        Returns:
            DeviceListResponse with devices list and total count
        """
        result: Any = await self._smart_home_request(
            PATH_FETCH_DEVICES,
            {
                "offset": offset,
                "limit": limit,
            },
        )
        if isinstance(result, dict):
            return cast(DeviceListResponse, result)
        return {"devices": [], "total": 0}  # type: ignore[return-value]

    async def get_product_configs(self) -> list[dict[str, Any]]:
        """Get all product configurations."""
        result: Any = await self._smart_home_request(
            PATH_GET_PRODUCT_CONFIGS,
            {},
            require_auth=False,
        )
        if isinstance(result, list):
            return result
        return []


__all__ = ["_ClientDeviceEndpointsMixin"]
