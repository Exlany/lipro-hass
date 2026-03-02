"""Unit tests for command trace helpers."""

from __future__ import annotations

from custom_components.lipro.core.api import LiproApiError
from custom_components.lipro.core.command.command_trace import (
    build_command_trace,
    extract_command_property_keys,
    update_trace_with_exception,
    update_trace_with_resolved_request,
    update_trace_with_response,
)
from custom_components.lipro.core.device import LiproDevice


def _make_device(
    serial: str = "03ab5ccd7c000001",
    is_group: bool = False,
) -> LiproDevice:
    """Create a minimal LiproDevice for command-trace helper tests."""
    return LiproDevice(
        device_number=1,
        serial=serial,
        name="Trace Test Device",
        device_type=1,
        iot_name="lipro_led",
        physical_model="light",
        is_group=is_group,
    )


def _redact(identifier: str | None) -> str | None:
    """Simple redaction helper for deterministic test assertions."""
    if identifier is None:
        return None
    return f"redacted:{identifier}"


def test_extract_command_property_keys_skips_non_string_key() -> None:
    keys = extract_command_property_keys(
        [{"key": "powerState", "value": "1"}, {"key": 1, "value": "2"}],
    )

    assert keys == ["powerState"]


def test_build_command_trace_applies_redaction() -> None:
    trace = build_command_trace(
        device=_make_device(serial="03ab5ccd7c123456", is_group=True),
        command="CHANGE_STATE",
        properties=[{"key": "powerState", "value": "1"}],
        fallback_device_id="03ab5ccd7c654321",
        redact_identifier=_redact,
    )

    assert trace["device_id"] == "redacted:03ab5ccd7c123456"
    assert trace["requested_fallback_device_id"] == "redacted:03ab5ccd7c654321"
    assert trace["requested_property_count"] == 1
    assert trace["requested_property_keys"] == ["powerState"]
    assert isinstance(trace["timestamp"], str)


def test_update_trace_with_resolved_request_sets_fields() -> None:
    trace: dict[str, object] = {}

    update_trace_with_resolved_request(
        trace,
        command="POWER_ON",
        properties=None,
        fallback_device_id="03ab5ccd7c222222",
        redact_identifier=_redact,
    )

    assert trace["effective_fallback_device_id"] == "redacted:03ab5ccd7c222222"
    assert trace["resolved_command"] == "POWER_ON"
    assert trace["resolved_property_count"] == 0
    assert trace["resolved_property_keys"] == []


def test_update_trace_with_response_uses_error_code_fallback() -> None:
    trace: dict[str, object] = {}
    update_trace_with_response(
        trace,
        {
            "pushSuccess": False,
            "errorCode": "140003",
            "message": "group failed",
            "msgSn": "abc",
            "pushTimestamp": 123,
        },
    )

    assert trace["push_success"] is False
    assert trace["response_code"] == "140003"
    assert trace["response_message"] == "group failed"
    assert trace["response_msg_sn"] == "abc"
    assert trace["response_push_timestamp"] == 123


def test_update_trace_with_response_ignores_non_dict_payload() -> None:
    trace: dict[str, object] = {"existing": True}
    update_trace_with_response(trace, "not a dict")

    assert trace == {"existing": True}


def test_update_trace_with_exception_sets_error_fields() -> None:
    trace: dict[str, object] = {}
    err = LiproApiError("timeout", code=504)

    update_trace_with_exception(trace, route="group_direct", err=err)

    assert trace["route"] == "group_direct"
    assert trace["success"] is False
    assert trace["error"] == "LiproApiError"
    assert trace["error_message"] == "LiproApiError(code=504)"
    assert trace["error_detail"] == "timeout"
    assert trace["error_code"] == 504
