"""Tests for request payload codec helpers."""

from __future__ import annotations

from custom_components.lipro.core.request_codec import (
    build_smart_home_request_data,
    encode_iot_request_body,
    extract_smart_home_success_payload,
)


def test_build_smart_home_request_data_adds_optional_access_token() -> None:
    payload = build_smart_home_request_data(
        sign="abc",
        phone_id="phone-id",
        timestamp_ms=123,
        app_version_name="2.24.3",
        app_version_code=20240003,
        data={"key": "value"},
        access_token="token",
    )

    assert payload["sign"] == "abc"
    assert payload["optFrom"] == "phone-id"
    assert payload["optAt"] == 123
    assert payload["vn"] == "2.24.3"
    assert payload["vc"] == 20240003
    assert payload["key"] == "value"
    assert payload["accessToken"] == "token"


def test_build_smart_home_request_data_without_access_token() -> None:
    payload = build_smart_home_request_data(
        sign="abc",
        phone_id="phone-id",
        timestamp_ms=123,
        app_version_name="2.24.3",
        app_version_code=20240003,
        data={},
        access_token=None,
    )

    assert "accessToken" not in payload


def test_extract_smart_home_success_payload_variants() -> None:
    assert extract_smart_home_success_payload({"value": {"x": 1}}) == {"x": 1}
    assert extract_smart_home_success_payload({"value": None}) == {}
    assert extract_smart_home_success_payload({"typedValue": {"y": 2}}) == {"y": 2}
    assert extract_smart_home_success_payload({"typedValue": None}) == {}
    assert extract_smart_home_success_payload({"code": "0000"}) == {}


def test_encode_iot_request_body_is_compact_json() -> None:
    encoded = encode_iot_request_body({"name": "灯", "value": 1})

    assert encoded == '{"name":"灯","value":1}'
