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
    MqttMessageEnvelopeDecoder,
    MqttPropertiesDecoder,
    MqttTopicDecoder,
    decode_mqtt_message_envelope_payload,
    decode_mqtt_properties_payload,
    decode_mqtt_topic_payload,
)
from .rest_decoder import (
    DeviceListRestDecoder,
    DeviceStatusRestDecoder,
    ListEnvelopeRestDecoder,
    MeshGroupStatusRestDecoder,
    MqttConfigRestDecoder,
    RestBoundaryDecoder,
    RestDecodeContext,
    ScheduleJsonRestDecoder,
    decode_device_list_payload,
    decode_device_status_payload,
    decode_list_envelope_payload,
    decode_mesh_group_status_payload,
    decode_mqtt_config_payload,
    decode_schedule_json_payload,
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
    registry.register(
        MqttConfigRestDecoder(is_success_code=is_success_code), channel="rest"
    )
    registry.register(ListEnvelopeRestDecoder(), channel="rest")
    registry.register(ScheduleJsonRestDecoder(), channel="rest")
    registry.register(DeviceListRestDecoder(), channel="rest")
    registry.register(DeviceStatusRestDecoder(), channel="rest")
    registry.register(MeshGroupStatusRestDecoder(), channel="rest")
    registry.register(MqttTopicDecoder(), channel="mqtt")
    registry.register(MqttMessageEnvelopeDecoder(), channel="mqtt")
    registry.register(MqttPropertiesDecoder(), channel="mqtt")
    return registry


__all__ = [
    "BoundaryDecodeResult",
    "BoundaryDecoder",
    "BoundaryDecoderDescriptor",
    "BoundaryDecoderKey",
    "BoundaryDecoderRegistry",
    "DeviceListRestDecoder",
    "DeviceStatusRestDecoder",
    "ListEnvelopeRestDecoder",
    "MeshGroupStatusRestDecoder",
    "MqttBoundaryDecoder",
    "MqttConfigRestDecoder",
    "MqttDecodeContext",
    "MqttMessageEnvelopeDecoder",
    "MqttPropertiesDecoder",
    "MqttTopicDecoder",
    "RestBoundaryDecoder",
    "RestDecodeContext",
    "ScheduleJsonRestDecoder",
    "build_protocol_boundary_registry",
    "decode_device_list_payload",
    "decode_device_status_payload",
    "decode_list_envelope_payload",
    "decode_mesh_group_status_payload",
    "decode_mqtt_config_payload",
    "decode_mqtt_message_envelope_payload",
    "decode_mqtt_properties_payload",
    "decode_mqtt_topic_payload",
    "decode_schedule_json_payload",
]
