"""Logging helpers for REST status fallback batch summaries."""

from __future__ import annotations

from collections.abc import Callable
import logging
from typing import Protocol

from .types import JsonObject

type MappingRows = list[JsonObject]
type NormalizeResponseCode = Callable[[object], str | int | None]


class _BatchLoggingContext(Protocol):
    item_name: str
    path: str
    logger: logging.Logger
    normalize_response_code: NormalizeResponseCode


def log_batch_query_fallback(
    *,
    context: _BatchLoggingContext,
    err: Exception,
    expected_offline_codes: tuple[int | str, ...],
) -> str | int:
    """Record the first batch failure before binary-split fallback begins."""
    normalized_code = context.normalize_response_code(getattr(err, "code", None))
    if normalized_code is None:
        normalized_code = "unknown"
    if normalized_code in expected_offline_codes:
        context.logger.debug(
            "Batch %s query failed with expected offline code (%s). Falling back to individual queries.",
            context.item_name,
            normalized_code,
        )
        return normalized_code

    context.logger.warning(
        "Batch %s query failed (code=%s, endpoint=%s): %s. Falling back to individual queries.",
        context.item_name,
        normalized_code,
        context.path,
        err,
    )
    return normalized_code


def log_empty_fallback_summary(
    *,
    path: str,
    item_name: str,
    batch_code: str | int,
    ids: list[str],
    all_results: MappingRows,
    failed_single_queries: int,
    single_error_codes: dict[str, int],
    logger: logging.Logger,
) -> None:
    """Emit one warning when all individual fallback queries still fail."""
    if not ids or all_results or failed_single_queries != len(ids):
        return

    dominant_single_code = (
        max(single_error_codes.items(), key=lambda item: item[1])[0]
        if single_error_codes
        else "unknown"
    )
    logger.warning(
        "Batch %s query fallback returned no data: %d/%d single queries failed (batch_code=%s, dominant_single_code=%s, endpoint=%s)",
        item_name,
        failed_single_queries,
        len(ids),
        batch_code,
        dominant_single_code,
        path,
    )


__all__ = [
    "log_batch_query_fallback",
    "log_empty_fallback_summary",
]
