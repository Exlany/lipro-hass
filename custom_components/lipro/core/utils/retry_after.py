"""Shared Retry-After parsing helpers."""

from __future__ import annotations

from datetime import UTC, datetime
from email.utils import parsedate_to_datetime
import math


def parse_retry_after(headers: dict[str, str]) -> float | None:
    """Parse Retry-After header value."""
    retry_after = headers.get("Retry-After") or headers.get("retry-after")
    if not retry_after:
        return None

    try:
        seconds = float(retry_after)
    except ValueError:
        pass
    else:
        return seconds if math.isfinite(seconds) else None

    try:
        retry_dt = parsedate_to_datetime(retry_after)
        if retry_dt.tzinfo is None:
            retry_dt = retry_dt.replace(tzinfo=UTC)
        delta = (retry_dt - datetime.now(tz=retry_dt.tzinfo)).total_seconds()
        return max(0.0, delta)
    except (ValueError, TypeError):
        return None


__all__ = ["parse_retry_after"]
