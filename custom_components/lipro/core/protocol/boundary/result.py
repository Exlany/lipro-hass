"""Canonical result models for protocol-boundary decode passes."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Generic, TypeVar, cast

CanonicalT_co = TypeVar("CanonicalT_co", covariant=True)


@dataclass(frozen=True, slots=True)
class BoundaryDecoderKey:
    """Stable identifier for one boundary decoder family version."""

    family: str
    version: str

    def __post_init__(self) -> None:
        """Reject empty family/version identifiers early."""
        if not self.family:
            raise ValueError("decoder family must not be empty")
        if not self.version:
            raise ValueError("decoder version must not be empty")

    @property
    def label(self) -> str:
        """Return the normalized `family@version` label."""
        return f"{self.family}@{self.version}"


@dataclass(frozen=True, slots=True, init=False)
class BoundaryDecodeResult(Generic[CanonicalT_co]):
    """Canonical output of one protocol-boundary decode pass."""

    key: BoundaryDecoderKey
    _canonical: object = field(repr=False)
    authority: str
    fingerprint: str | None
    drift_flags: tuple[str, ...]
    notes: tuple[str, ...]

    def __init__(
        self,
        key: BoundaryDecoderKey,
        canonical: object,
        authority: str,
        fingerprint: str | None = None,
        drift_flags: tuple[str, ...] = (),
        notes: tuple[str, ...] = (),
    ) -> None:
        """Store one immutable decode result while keeping the payload covariant."""
        object.__setattr__(self, "key", key)
        object.__setattr__(self, "_canonical", canonical)
        object.__setattr__(self, "authority", authority)
        object.__setattr__(self, "fingerprint", fingerprint)
        object.__setattr__(self, "drift_flags", drift_flags)
        object.__setattr__(self, "notes", notes)

    @property
    def canonical(self) -> CanonicalT_co:
        """Return the canonical payload with the caller-selected covariance."""
        return cast(CanonicalT_co, self._canonical)

    @property
    def family(self) -> str:
        """Return the decoder family name."""
        return self.key.family

    @property
    def version(self) -> str:
        """Return the decoder family version."""
        return self.key.version
