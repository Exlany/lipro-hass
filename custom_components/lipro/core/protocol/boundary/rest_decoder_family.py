"""Concrete REST decoder families that stay below the public entry home."""

from __future__ import annotations

from typing import TYPE_CHECKING

from .rest_decoder_registry import (
    _REST_DEVICE_LIST_CONTEXT,
    _REST_DEVICE_STATUS_CONTEXT,
    _REST_LIST_ENVELOPE_CONTEXT,
    _REST_MESH_GROUP_STATUS_CONTEXT,
    RestDecodeContext,
)
from .rest_decoder_support import (
    _decode_device_list_canonical,
    _decode_device_status_canonical,
    _decode_list_envelope_canonical,
    _decode_mesh_group_status_canonical,
)
from .rest_decoder_utility import _build_payload_fingerprint
from .result import BoundaryDecodeResult, BoundaryDecoderKey

if TYPE_CHECKING:
    from ..contracts import (
        CanonicalDeviceListPage,
        CanonicalDeviceStatusRow,
        CanonicalListEnvelope,
        CanonicalMeshGroupStatusRow,
    )


class ListEnvelopeRestDecoder:
    """Decode generic REST list envelopes into a canonical transport shape."""

    def __init__(self, *, offset: int = 0) -> None:
        """Initialize the list-envelope decoder context and offset."""
        self._offset = offset
        self._context = _REST_LIST_ENVELOPE_CONTEXT

    @property
    def context(self) -> RestDecodeContext:
        """Return endpoint-bound decoder metadata."""
        return self._context

    @property
    def key(self) -> BoundaryDecoderKey:
        """Return the stable registry key for this decoder family."""
        return self._context.key

    @property
    def authority(self) -> str:
        """Return the authoritative fixture source for this decoder family."""
        return self._context.authority

    def decode(self, payload: object) -> BoundaryDecodeResult[CanonicalListEnvelope]:
        """Decode one list-envelope payload into canonical rows and paging."""
        return BoundaryDecodeResult(
            key=self.key,
            canonical=_decode_list_envelope_canonical(payload, offset=self._offset),
            authority=self.authority,
            fingerprint=_build_payload_fingerprint(payload),
        )


class DeviceListRestDecoder:
    """Decode device-list payloads into a canonical catalog page contract."""

    def __init__(self, *, offset: int = 0) -> None:
        """Initialize the device-list decoder context and offset."""
        self._offset = offset
        self._context = _REST_DEVICE_LIST_CONTEXT

    @property
    def context(self) -> RestDecodeContext:
        """Return endpoint-bound decoder metadata."""
        return self._context

    @property
    def key(self) -> BoundaryDecoderKey:
        """Return the stable registry key for this decoder family."""
        return self._context.key

    @property
    def authority(self) -> str:
        """Return the authoritative fixture source for this decoder family."""
        return self._context.authority

    def decode(self, payload: object) -> BoundaryDecodeResult[CanonicalDeviceListPage]:
        """Decode one device-list payload into the canonical catalog page."""
        return BoundaryDecodeResult(
            key=self.key,
            canonical=_decode_device_list_canonical(payload, offset=self._offset),
            authority=self.authority,
            fingerprint=_build_payload_fingerprint(payload),
        )


class DeviceStatusRestDecoder:
    """Decode device-status payloads into canonical status rows."""

    def __init__(self) -> None:
        """Initialize the device-status decoder context."""
        self._context = _REST_DEVICE_STATUS_CONTEXT

    @property
    def context(self) -> RestDecodeContext:
        """Return endpoint-bound decoder metadata."""
        return self._context

    @property
    def key(self) -> BoundaryDecoderKey:
        """Return the stable registry key for this decoder family."""
        return self._context.key

    @property
    def authority(self) -> str:
        """Return the authoritative fixture source for this decoder family."""
        return self._context.authority

    def decode(
        self,
        payload: object,
    ) -> BoundaryDecodeResult[list[CanonicalDeviceStatusRow]]:
        """Decode one device-status payload into canonical status rows."""
        return BoundaryDecodeResult(
            key=self.key,
            canonical=_decode_device_status_canonical(payload),
            authority=self.authority,
            fingerprint=_build_payload_fingerprint(payload),
        )


class MeshGroupStatusRestDecoder:
    """Decode mesh-group-status payloads into canonical topology rows."""

    def __init__(self) -> None:
        """Initialize the mesh-group-status decoder context."""
        self._context = _REST_MESH_GROUP_STATUS_CONTEXT

    @property
    def context(self) -> RestDecodeContext:
        """Return endpoint-bound decoder metadata."""
        return self._context

    @property
    def key(self) -> BoundaryDecoderKey:
        """Return the stable registry key for this decoder family."""
        return self._context.key

    @property
    def authority(self) -> str:
        """Return the authoritative fixture source for this decoder family."""
        return self._context.authority

    def decode(
        self,
        payload: object,
    ) -> BoundaryDecodeResult[list[CanonicalMeshGroupStatusRow]]:
        """Decode one mesh-group-status payload into canonical topology rows."""
        return BoundaryDecodeResult(
            key=self.key,
            canonical=_decode_mesh_group_status_canonical(payload),
            authority=self.authority,
            fingerprint=_build_payload_fingerprint(payload),
        )


__all__ = [
    "DeviceListRestDecoder",
    "DeviceStatusRestDecoder",
    "ListEnvelopeRestDecoder",
    "MeshGroupStatusRestDecoder",
]
