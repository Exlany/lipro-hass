"""Redaction helpers for diagnostics and debug traces."""

from __future__ import annotations


def redact_identifier(identifier: str | None) -> str | None:
    """Redact an identifier for share-friendly diagnostics."""
    if not isinstance(identifier, str):
        return None

    normalized = identifier.strip()
    if not normalized:
        return None

    if len(normalized) <= 8:
        return "***"
    return f"{normalized[:4]}***{normalized[-4:]}"
