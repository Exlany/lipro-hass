"""Payload-shape services.diagnostics assertions."""

from __future__ import annotations

from typing import cast
from unittest.mock import MagicMock

from custom_components.lipro.core import LiproApiError
from custom_components.lipro.services.diagnostics import (
    build_developer_feedback_payload,
)
from custom_components.lipro.services.diagnostics.handlers import (
    _build_last_error_payload,
)
from custom_components.lipro.services.diagnostics.helpers import (
    _coerce_service_float,
    _coerce_service_int,
)
from homeassistant.core import HomeAssistant
from tests.helpers.service_call import service_call

from .test_services_diagnostics_support import _developer_feedback_report_fixture


def test_service_number_coercion_handles_bool_and_default() -> None:
    """Numeric coercion should preserve schema-friendly bool and fallback behavior."""
    hass = cast(HomeAssistant, MagicMock())
    call = service_call(
        hass, {"int_value": True, "float_value": False, "bad": object()}
    )

    assert _coerce_service_int(call, "int_value", 7) == 1
    assert _coerce_service_int(call, "bad", 7) == 7
    assert _coerce_service_float(call, "float_value", 1.5) == 0.0
    assert _coerce_service_float(call, "missing", 1.5) == 1.5


def test_build_last_error_payload_omits_empty_message_and_none_code() -> None:
    """Serializable last-error payload should only include meaningful fields."""
    assert _build_last_error_payload(None) is None
    assert _build_last_error_payload(LiproApiError("   ", code=None)) == {
        "failure_summary": {
            "failure_category": "protocol",
            "failure_origin": "service.api",
            "handling_policy": "inspect",
            "error_type": "LiproApiError",
        }
    }
    assert _build_last_error_payload(LiproApiError("bad gateway", code=502)) == {
        "code": 502,
        "message": "bad gateway",
        "failure_summary": {
            "failure_category": "network",
            "failure_origin": "service.api",
            "handling_policy": "retry",
            "error_type": "LiproApiError",
        },
    }


def test_build_developer_feedback_payload_matches_boundary_fixture() -> None:
    from custom_components.lipro.core.anonymous_share.report_builder import (
        canonicalize_generated_payload,
    )
    from tests.helpers.external_boundary_fixtures import load_external_boundary_fixture

    payload = build_developer_feedback_payload(
        reports=[_developer_feedback_report_fixture()],
        note="manual run",
        domain="lipro",
        service_name="submit_developer_feedback",
        requested_entry_id="entry-2",
    )

    assert canonicalize_generated_payload(payload) == load_external_boundary_fixture(
        "support_payload",
        "developer_feedback_service.canonical.json",
    )
