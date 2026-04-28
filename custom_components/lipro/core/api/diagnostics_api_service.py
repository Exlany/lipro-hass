"""Diagnostic endpoint helpers for Lipro API client."""

from __future__ import annotations

from .diagnostics_api_history import (
    fetch_body_sensor_history,
    fetch_door_sensor_history,
    fetch_sensor_history,
)
from .diagnostics_api_ota import (
    OtaQueryResult,
    _build_rich_ota_v2_payload,
    _merge_ota_rows,
    _ota_row_dedupe_key,
    query_ota_info,
    query_ota_info_with_outcome,
)
from .diagnostics_api_queries import get_city, query_command_result, query_user_cloud

__all__ = [
    "OtaQueryResult",
    "_build_rich_ota_v2_payload",
    "_merge_ota_rows",
    "_ota_row_dedupe_key",
    "fetch_body_sensor_history",
    "fetch_door_sensor_history",
    "fetch_sensor_history",
    "get_city",
    "query_command_result",
    "query_ota_info",
    "query_ota_info_with_outcome",
    "query_user_cloud",
]
