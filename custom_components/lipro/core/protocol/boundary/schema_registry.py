"""Registry primitives for protocol-boundary decoder families."""

from __future__ import annotations

from collections.abc import Iterable
from dataclasses import dataclass
from typing import Protocol, TypeVar, runtime_checkable

from .result import BoundaryDecodeResult, BoundaryDecoderKey

CanonicalT_co = TypeVar("CanonicalT_co", covariant=True)


@runtime_checkable
class BoundaryDecoder(Protocol[CanonicalT_co]):
    """Protocol contract for one decoder family implementation."""

    @property
    def key(self) -> BoundaryDecoderKey:
        """Return the stable family/version identity for this decoder."""
        ...

    @property
    def authority(self) -> str:
        """Return the authority source backing this decoder family."""
        ...

    def decode(self, payload: object) -> BoundaryDecodeResult[CanonicalT_co]:
        """Decode raw transport payload into one canonical contract."""
        ...


@dataclass(frozen=True, slots=True)
class BoundaryDecoderDescriptor:
    """Small metadata view used for inventory, telemetry, and governance."""

    key: BoundaryDecoderKey
    authority: str
    channel: str


class BoundaryDecoderRegistry:
    """In-memory registry owned by the protocol plane."""

    def __init__(self, decoders: Iterable[BoundaryDecoder[object]] = ()) -> None:
        """Initialize the registry with an optional seed set of decoders."""
        self._decoders: dict[BoundaryDecoderKey, BoundaryDecoder[object]] = {}
        self._descriptors: dict[BoundaryDecoderKey, BoundaryDecoderDescriptor] = {}
        for decoder in decoders:
            self.register(decoder)

    def register(
        self,
        decoder: BoundaryDecoder[object],
        *,
        channel: str = "unspecified",
    ) -> None:
        """Register one decoder family version exactly once."""
        key = decoder.key
        if key in self._decoders:
            message = f"duplicate boundary decoder registration: {key.label}"
            raise ValueError(message)
        self._decoders[key] = decoder
        self._descriptors[key] = BoundaryDecoderDescriptor(
            key=key,
            authority=decoder.authority,
            channel=channel,
        )

    def get(self, family: str, version: str) -> BoundaryDecoder[object] | None:
        """Return a decoder when the family/version pair is registered."""
        return self._decoders.get(BoundaryDecoderKey(family=family, version=version))

    def resolve(self, family: str, version: str) -> BoundaryDecoder[object]:
        """Return the registered decoder or raise a precise lookup error."""
        decoder = self.get(family, version)
        if decoder is None:
            message = f"unregistered boundary decoder: {family}@{version}"
            raise KeyError(message)
        return decoder

    def describe(self) -> tuple[BoundaryDecoderDescriptor, ...]:
        """Return stable registry metadata sorted by family/version label."""
        return tuple(
            self._descriptors[key]
            for key in sorted(self._descriptors, key=lambda item: item.label)
        )
