"""Tests for anonymous-share report builder edge branches."""

from __future__ import annotations

from unittest.mock import patch

from custom_components.lipro.core.anonymous_share.report_builder import (
    build_developer_feedback_report,
    build_lite_report,
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


def test_build_lite_report_skips_non_dict_devices() -> None:
    report = {
        "report_version": "1.1",
        "integration_version": "1.0.0",
        "ha_version": "2026.3.0",
        "generated_at": "2026-03-04T00:00:00+00:00",
        "installation_id": "install-001",
        "device_count": 2,
        "error_count": 0,
        "devices": [
            "invalid-device-row",
            {"physical_model": "light", "iot_name": "lipro_led"},
        ],
        "errors": [],
    }

    lite = build_lite_report(report)

    assert len(lite["devices"]) == 1
    assert lite["devices"][0]["physical_model"] == "light"


def test_build_lite_report_truncates_string_developer_feedback() -> None:
    long_feedback = "x" * 2500
    report = {"developer_feedback": long_feedback}

    lite = build_lite_report(report)

    assert lite["developer_feedback"] == long_feedback[:2000]
