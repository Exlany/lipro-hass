"""Request payload codec helpers for Lipro APIs."""

from __future__ import annotations

from collections.abc import Mapping
import json

from .types import JsonObject, JsonValue


def build_smart_home_request_data(
    *,
    sign: str,
    phone_id: str,
    timestamp_ms: int,
    app_version_name: str,
    app_version_code: int | str,
    data: Mapping[str, JsonValue],
    access_token: str | None = None,
) -> JsonObject:
    """Build Smart Home API form payload."""
    request_data: JsonObject = {
        "sign": sign,
        "optFrom": phone_id,
        "optAt": timestamp_ms,
        "vn": app_version_name,
        "vc": app_version_code,
    }
    request_data.update(data)
    if access_token is not None:
        request_data["accessToken"] = access_token
    return request_data


def extract_smart_home_success_payload(result: Mapping[str, JsonValue]) -> JsonValue:
    """Extract Smart Home API success payload from response envelope."""
    for key in ("value", "typedValue"):
        if key in result:
            payload = result.get(key)
            return {} if payload is None else payload
    return {}


def encode_iot_request_body(body_data: Mapping[str, JsonValue]) -> str:
    """Encode IoT API request body with stable compact JSON."""
    return json.dumps(dict(body_data), separators=(",", ":"), ensure_ascii=False)
