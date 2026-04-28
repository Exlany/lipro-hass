"""Support helpers for `LiproAuthManager`."""

from __future__ import annotations

import asyncio
from dataclasses import dataclass, field

from ...const.api import (
    ACCESS_TOKEN_EXPIRY_SECONDS,
    TOKEN_EXPIRY_MIN,
    TOKEN_EXPIRY_REDUCTION_FACTOR,
    TOKEN_REFRESH_BUFFER,
    TOKEN_REFRESH_DEDUP_WINDOW,
)
from ..utils.vendor_crypto import md5_compat_hexdigest


@dataclass(slots=True)
class StoredCredentials:
    """Stored credential seed used for refresh fallback re-login."""

    phone: str | None = None
    password: str | None = None
    password_is_hashed: bool = False

    def set(
        self,
        phone: str,
        password: str,
        *,
        password_is_hashed: bool = False,
    ) -> None:
        """Store one credential seed, hashing plaintext input when needed."""
        self.phone = phone
        self.password = (
            password if password_is_hashed else md5_compat_hexdigest(password)
        )
        self.password_is_hashed = True

    @property
    def is_available(self) -> bool:
        """Return whether a complete credential seed is currently available."""
        return bool(self.phone and self.password)


@dataclass(slots=True)
class TokenLeaseState:
    """Mutable token lease bookkeeping for auth orchestration."""

    expires_at: float = 0.0
    current_expiry_seconds: int = ACCESS_TOKEN_EXPIRY_SECONDS
    last_refresh_time: float = 0.0
    refresh_lock: asyncio.Lock = field(default_factory=asyncio.Lock)

    def record_restored_tokens(self, *, now: float, expires_at: float | None) -> None:
        """Record externally restored tokens without marking a recent refresh."""
        if expires_at is not None and expires_at > 0:
            self.expires_at = expires_at
        else:
            self.expires_at = now + self.current_expiry_seconds
        self.last_refresh_time = 0.0

    def record_login(self, *, now: float) -> None:
        """Record a fresh login and reset adaptive expiry back to the default."""
        self.current_expiry_seconds = ACCESS_TOKEN_EXPIRY_SECONDS
        self.record_refresh(now=now)

    def record_refresh(self, *, now: float) -> None:
        """Record a successful refresh against the current adaptive expiry."""
        self.expires_at = now + self.current_expiry_seconds
        self.last_refresh_time = now

    def recently_refreshed(self, *, now: float) -> bool:
        """Return whether another refresh just completed inside the dedupe window."""
        return now - self.last_refresh_time < TOKEN_REFRESH_DEDUP_WINDOW

    def needs_refresh(self, *, now: float) -> bool:
        """Return whether the current lease is inside the proactive refresh buffer."""
        return now >= self.expires_at - TOKEN_REFRESH_BUFFER

    def adjust_expiry_on_401(self, *, now: float) -> tuple[int, int] | None:
        """Tighten adaptive expiry when a 401 arrives before the expected deadline."""
        time_since_refresh = now - self.last_refresh_time
        if time_since_refresh >= self.current_expiry_seconds:
            return None

        new_expiry = int(
            min(
                time_since_refresh * TOKEN_EXPIRY_REDUCTION_FACTOR,
                self.current_expiry_seconds * TOKEN_EXPIRY_REDUCTION_FACTOR,
            )
        )
        new_expiry = max(new_expiry, TOKEN_EXPIRY_MIN)
        if new_expiry >= self.current_expiry_seconds:
            return None

        previous = self.current_expiry_seconds
        self.current_expiry_seconds = new_expiry
        return previous, new_expiry


def require_text(value: object, *, field_name: str) -> str:
    """Return one required text field from an auth response mapping."""
    if isinstance(value, str):
        return value
    msg = f"Missing or invalid {field_name} in auth result"
    raise TypeError(msg)


def optional_text(value: object) -> str | None:
    """Return one optional text field when present."""
    return value if isinstance(value, str) else None


def optional_int(value: object) -> int | None:
    """Return one optional integer field when present."""
    if isinstance(value, bool):
        return None
    return value if isinstance(value, int) else None


__all__ = [
    "StoredCredentials",
    "TokenLeaseState",
    "optional_int",
    "optional_text",
    "require_text",
]
