"""Compatibility crypto helpers required by the vendor protocol."""

from __future__ import annotations

import hashlib


def md5_compat_hexdigest(value: str) -> str:
    """Return the MD5 hex digest required by Lipro's upstream protocol.

    This helper centralizes MD5 usage so the codebase clearly distinguishes
    vendor-mandated compatibility hashing from security-sensitive hashing.
    """

    return hashlib.md5(
        value.encode("utf-8"),
        usedforsecurity=False,
    ).hexdigest()


__all__ = ["md5_compat_hexdigest"]
