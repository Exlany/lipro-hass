"""Shared payload helpers for LiproClient endpoint mixins."""

from __future__ import annotations

import logging
from typing import Any

from ...utils.identifiers import (
    normalize_iot_device_id as _normalize_iot_device_id,
    normalize_mesh_group_id as _normalize_mesh_group_id,
)
from ..client_base import _ClientBase

# Use the same logger instance as custom_components.lipro.core.api.client._LOGGER
# so tests patching client._LOGGER.* still intercept logs here.
_LOGGER = logging.getLogger("custom_components.lipro.core.api.client")


class _ClientEndpointPayloadsMixin(_ClientBase):
    """Mixin providing small, shared payload utilities."""

    @staticmethod
    def _extract_list_payload(
        result: Any,
        *keys: str,
    ) -> list[dict[str, Any]]:
        """Extract list payload from direct or wrapped API responses."""
        if isinstance(result, list):
            return result
        if isinstance(result, dict):
            for key in keys:
                value = result.get(key)
                if isinstance(value, list):
                    return value
        return []

    @staticmethod
    def _extract_data_list(result: Any) -> list[dict[str, Any]]:
        """Extract list payload from ``data`` responses."""
        return _ClientEndpointPayloadsMixin._extract_list_payload(result, "data")

    @staticmethod
    def _extract_timings_list(result: Any) -> list[dict[str, Any]]:
        """Extract timing-task rows from API response variants."""
        return _ClientEndpointPayloadsMixin._extract_list_payload(
            result, "timings", "data"
        )

    @staticmethod
    def _sanitize_iot_device_ids(
        device_ids: list[str],
        *,
        endpoint: str,
    ) -> list[str]:
        """Keep only valid IoT device IDs for endpoint requests."""
        valid_ids: list[str] = []
        seen: set[str] = set()
        skipped = 0
        for raw_id in device_ids:
            normalized = _normalize_iot_device_id(raw_id)
            if normalized is None:
                skipped += 1
                continue
            if normalized in seen:
                continue
            seen.add(normalized)
            valid_ids.append(normalized)

        if skipped:
            _LOGGER.debug(
                "Skipped %d non-IoT IDs for %s",
                skipped,
                endpoint,
            )
        return valid_ids

    @staticmethod
    def _normalize_power_target_id(device_id: Any) -> str | None:
        """Normalize a power-info target ID accepted by the cloud endpoint."""
        return _normalize_iot_device_id(device_id) or _normalize_mesh_group_id(
            device_id
        )


__all__ = ["_ClientEndpointPayloadsMixin"]
