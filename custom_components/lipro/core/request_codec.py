"""Request payload codec helpers for Lipro APIs."""

from __future__ import annotations

import json
from typing import Any


def build_smart_home_request_data(
    *,
    sign: str,
    phone_id: str,
    timestamp_ms: int,
    app_version_name: str,
    app_version_code: int | str,
    data: dict[str, Any],
    access_token: str | None = None,
) -> dict[str, Any]:
    """Build Smart Home API form payload."""
    request_data = {
        "sign": sign,
        "optFrom": phone_id,
        "optAt": timestamp_ms,
        "vn": app_version_name,
        "vc": app_version_code,
        **data,
    }
    if access_token is not None:
        request_data["accessToken"] = access_token
    return request_data


def extract_smart_home_success_payload(result: dict[str, Any]) -> dict[str, Any]:
    """Extract Smart Home API success payload from response envelope."""
    for key in ("value", "typedValue"):
        if key in result:
            payload = result.get(key)
            return {} if payload is None else payload
    return {}


def encode_iot_request_body(body_data: dict[str, Any]) -> str:
    """Encode IoT API request body with stable compact JSON."""
    return json.dumps(body_data, separators=(",", ":"), ensure_ascii=False)
