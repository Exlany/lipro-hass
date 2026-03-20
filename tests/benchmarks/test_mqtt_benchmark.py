"""Benchmark coverage for MQTT message processing."""

from __future__ import annotations

from unittest.mock import MagicMock

import pytest

from custom_components.lipro.core.mqtt.message_processor import MqttMessageProcessor


@pytest.mark.benchmark(group="mqtt")
def test_mqtt_message_processing_benchmark(benchmark) -> None:
    processor = MqttMessageProcessor("biz001")
    message = MagicMock(
        topic="Topic_Device_State/biz001/03ab5ccd7cxxxxxx",
        payload=b'{"light": {"powerState": "1", "brightness": "66"}}',
    )
    received: list[tuple[str, dict[str, str]]] = []
    errors: list[Exception] = []

    benchmark(
        processor.process_message,
        message,
        parse_payload=lambda _payload: {"powerState": "1", "brightness": "66"},
        on_message=lambda device_id, properties: received.append((device_id, properties)),
        invoke_callback=lambda callback, _name, *args: True
        if callback is None
        else (callback(*args), True)[1],
        set_last_error=lambda err: errors.append(err),
        clear_last_error=errors.clear,
    )

    assert received
    device_id, properties = received[-1]
    assert device_id == "03ab5ccd7cxxxxxx"
    assert properties["powerState"] == "1"
    assert properties["brightness"] == "66"
    assert errors == []
