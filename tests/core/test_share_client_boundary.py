"""Topicized ShareWorkerClient external-boundary proof."""
# ruff: noqa: F403, I001

from __future__ import annotations

from .test_share_client_support import *

def test_build_lite_report_matches_external_boundary_fixture() -> None:
    from custom_components.lipro.core.anonymous_share.report_builder import (
        build_lite_report,
        canonicalize_generated_payload,
    )
    from tests.helpers.external_boundary_fixtures import load_external_boundary_fixture

    report = {
        "report_version": "1.1",
        "integration_version": load_external_boundary_fixture(
            "share_worker",
            "lite_report.canonical.json",
        )["integration_version"],
        "ha_version": "2026.3.0",
        "generated_at": "2026-03-12T00:00:00+00:00",
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
            }
        ],
        "errors": [
            {
                "type": "api_error",
                "message": "timeout",
                "endpoint": "/device/list",
                "iot_name": "lipro_led",
                "device_type": "ff000001",
                "timestamp": "2026-03-12T00:00:00+00:00",
            }
        ],
    }

    assert canonicalize_generated_payload(build_lite_report(report)) == (
        load_external_boundary_fixture("share_worker", "lite_report.canonical.json")
    )
