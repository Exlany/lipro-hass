"""Benchmark coverage for device refresh/update paths."""

from __future__ import annotations

from custom_components.lipro.core.device import LiproDevice


def test_device_update_properties_benchmark(benchmark) -> None:
    device = LiproDevice(
        device_number=1,
        serial="03ab5ccd7caaaaaa",
        name="Desk Light",
        device_type=1,
        iot_name="lipro_led",
        physical_model="light",
        properties={"powerState": "0", "brightness": "50"},
    )

    benchmark(
        device.update_properties,
        {"powerState": "1", "brightness": "80", "temperature": "50"},
    )

    assert device.properties["powerState"] == "1"
    assert device.properties["brightness"] == "80"
    assert device.properties["temperature"] == "50"
