"""Tests for anonymous-share report builder edge branches."""

from __future__ import annotations

from unittest.mock import patch

from custom_components.lipro.core.anonymous_share.models import (
    SharedDevice,
    SharedError,
)
from custom_components.lipro.core.anonymous_share.report_builder import (
    build_anonymous_share_report,
    build_developer_feedback_report,
    build_lite_report,
    canonicalize_generated_payload,
)
from tests.helpers.external_boundary_fixtures import load_external_boundary_fixture


def test_build_anonymous_share_report_matches_boundary_fixture() -> None:
    report = build_anonymous_share_report(
        installation_id="install-001",
        ha_version="2026.3.0",
        devices={
            "device-1": SharedDevice(
                physical_model="light",
                iot_name="lipro_led",
                device_type=1,
                product_id=100,
                is_group=False,
                category="light",
                firmware_version="1.0.0",
                property_keys=["powerState"],
                properties={"powerState": "1"},
                min_color_temp_kelvin=2700,
                max_color_temp_kelvin=6500,
                capabilities=["on", "brightness"],
            )
        },
        errors=[
            SharedError(
                error_type="api_error",
                message="timeout",
                endpoint="/device/list",
                iot_name="lipro_led",
                device_type="ff000001",
            )
        ],
    )

    assert canonicalize_generated_payload(report) == load_external_boundary_fixture(
        "share_worker",
        "anonymous_share_report.canonical.json",
    )


def test_build_developer_feedback_report_wraps_non_dict_sanitized_feedback() -> None:
    with patch(
        "custom_components.lipro.core.anonymous_share.report_builder.sanitize_value",
        return_value="masked feedback",
    ):
        report = build_developer_feedback_report(
            installation_id="install-001",
            ha_version="2026.3.0",
            feedback={"raw": "value"},
        )

    assert report["developer_feedback"] == {"value": "masked feedback"}


def test_build_lite_report_matches_boundary_fixture() -> None:
    report = {
        "report_version": "1.1",
        "integration_version": load_external_boundary_fixture(
            "share_worker",
            "anonymous_share_report.canonical.json",
        )["integration_version"],
        "ha_version": "2026.3.0",
        "generated_at": "2026-03-04T00:00:00+00:00",
        "installation_id": "install-001",
        "device_count": 2,
        "error_count": 1,
        "devices": [
            {
                "physical_model": "light",
                "iot_name": "lipro_led",
                "device_type": 1,
                "product_id": 100,
                "is_group": False,
                "category": "light",
                "firmware_version": "1.0.0",
                "capabilities": ["on", "brightness"],
                "has_gear_presets": False,
                "gear_count": 0,
                "min_color_temp_kelvin": 2700,
                "max_color_temp_kelvin": 6500,
            },
            "invalid-device-row",
        ],
        "errors": [
            {
                "type": "api_error",
                "message": "timeout",
                "endpoint": "/device/list",
                "iot_name": "lipro_led",
                "device_type": "ff000001",
                "timestamp": "2026-03-04T00:00:00+00:00",
            }
        ],
    }

    assert canonicalize_generated_payload(build_lite_report(report)) == (
        load_external_boundary_fixture("share_worker", "lite_report.canonical.json")
    )


def test_build_lite_report_truncates_string_developer_feedback() -> None:
    long_feedback = "x" * 2500
    report = {"developer_feedback": long_feedback}

    lite = build_lite_report(report)

    assert lite["developer_feedback"] == long_feedback[:2000]
