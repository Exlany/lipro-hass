"""Thin anchor for the unified protocol contract root."""

from __future__ import annotations

from custom_components.lipro.core.protocol import LiproProtocolFacade


def test_lipro_protocol_facade_is_available_as_unified_protocol_root() -> None:
    assert LiproProtocolFacade.__name__ == "LiproProtocolFacade"

