"""Local support helpers for topicized diagnostics API service suites."""

from __future__ import annotations

from typing import cast

from custom_components.lipro.core.api.types import JsonObject

__all__ = [
    "DummyApiError",
    "_extract_rows",
    "_require_mapping_response",
]


class DummyApiError(Exception):
    """Dummy API error used to trigger error branches in tests."""

    def __init__(self, message: str, code: str | int | None = None) -> None:
        super().__init__(message)
        self.code = code


def _extract_rows(payload: object) -> list[object]:
    if isinstance(payload, dict):
        rows = payload.get("rows")
        if isinstance(rows, list):
            return rows
    return []


def _require_mapping_response(_path: str, payload: object) -> JsonObject:
    if isinstance(payload, dict):
        return cast(JsonObject, payload)
    return {}
