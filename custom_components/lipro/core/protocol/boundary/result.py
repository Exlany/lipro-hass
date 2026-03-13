"""Canonical result models for protocol-boundary decode passes."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Generic, TypeVar

CanonicalT = TypeVar("CanonicalT")


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


@dataclass(frozen=True, slots=True)
class BoundaryDecodeResult(Generic[CanonicalT]):
    """Canonical output of one protocol-boundary decode pass."""

    key: BoundaryDecoderKey
    canonical: CanonicalT
    authority: str
    fingerprint: str | None = None
    drift_flags: tuple[str, ...] = ()
    notes: tuple[str, ...] = ()

    @property
    def family(self) -> str:
        """Return the decoder family name."""
        return self.key.family

    @property
    def version(self) -> str:
        """Return the decoder family version."""
        return self.key.version
