"""Internal protocol-boundary decoder family home.

This package is owned by the protocol plane. It concentrates decode /
normalize responsibilities at the transport edge without creating a second
protocol root or leaking decoder-private types to runtime, domain, or control.
"""

from __future__ import annotations

from collections.abc import Callable

from .mqtt_decoder import (
    MqttBoundaryDecoder,
    MqttDecodeContext,
    MqttPropertiesDecoder,
    decode_mqtt_properties_payload,
)
from .rest_decoder import (
    MqttConfigRestDecoder,
    RestBoundaryDecoder,
    RestDecodeContext,
    decode_mqtt_config_payload,
)
from .result import BoundaryDecodeResult, BoundaryDecoderKey
from .schema_registry import (
    BoundaryDecoder,
    BoundaryDecoderDescriptor,
    BoundaryDecoderRegistry,
)


def build_protocol_boundary_registry(
    *,
    is_success_code: Callable[[object], bool],
) -> BoundaryDecoderRegistry:
    """Build the protocol-owned registry for the first boundary families."""
    registry = BoundaryDecoderRegistry()
    registry.register(MqttConfigRestDecoder(is_success_code=is_success_code), channel="rest")
    registry.register(MqttPropertiesDecoder(), channel="mqtt")
    return registry


__all__ = [
    "BoundaryDecodeResult",
    "BoundaryDecoder",
    "BoundaryDecoderDescriptor",
    "BoundaryDecoderKey",
    "BoundaryDecoderRegistry",
    "MqttBoundaryDecoder",
    "MqttConfigRestDecoder",
    "MqttDecodeContext",
    "MqttPropertiesDecoder",
    "RestBoundaryDecoder",
    "RestDecodeContext",
    "build_protocol_boundary_registry",
    "decode_mqtt_config_payload",
    "decode_mqtt_properties_payload",
]
