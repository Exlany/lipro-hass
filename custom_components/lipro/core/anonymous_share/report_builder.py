"""Anonymous share report building helpers."""

from __future__ import annotations

from datetime import UTC, datetime
from typing import Any

from ...const.base import VERSION
from .models import SharedDevice, SharedError
from .sanitize import sanitize_value


def build_anonymous_share_report(
    *,
    installation_id: str | None,
    ha_version: str | None,
    devices: dict[str, SharedDevice],
    errors: list[SharedError],
) -> dict[str, Any]:
    """Build the anonymous share report payload."""
    return {
        "report_version": "1.1",
        "integration_version": VERSION,
        "ha_version": ha_version,
        "generated_at": datetime.now(UTC).isoformat(),
        "installation_id": installation_id,
        "device_count": len(devices),
        "error_count": len(errors),
        "devices": [d.to_dict() for d in devices.values()],
        "errors": [e.to_dict() for e in errors],
    }


def build_developer_feedback_report(
    *,
    installation_id: str | None,
    ha_version: str | None,
    feedback: dict[str, Any],
) -> dict[str, Any]:
    """Build one developer-feedback report payload."""
    sanitized_feedback = sanitize_value(feedback, preserve_structure=True)
    if not isinstance(sanitized_feedback, dict):
        sanitized_feedback = {"value": sanitized_feedback}

    return {
        "report_version": "1.2",
        "integration_version": VERSION,
        "ha_version": ha_version,
        "generated_at": datetime.now(UTC).isoformat(),
        "installation_id": installation_id or "manual",
        "device_count": 0,
        "error_count": 0,
        "devices": [],
        "errors": [],
        "developer_feedback": sanitized_feedback,
    }


def build_lite_report(report: dict[str, Any]) -> dict[str, Any]:
    """Build a smaller report variant for 413 retries."""
    lite: dict[str, Any] = {
        "report_version": report.get("report_version"),
        "integration_version": report.get("integration_version"),
        "ha_version": report.get("ha_version"),
        "generated_at": report.get("generated_at"),
        "installation_id": report.get("installation_id"),
        "device_count": report.get("device_count"),
        "error_count": report.get("error_count"),
    }

    devices = report.get("devices")
    if isinstance(devices, list):
        compact_devices: list[dict[str, Any]] = []
        for item in devices[:10]:
            if not isinstance(item, dict):
                continue
            compact_devices.append(
                {
                    "physical_model": item.get("physical_model"),
                    "iot_name": item.get("iot_name"),
                    "device_type": item.get("device_type"),
                    "product_id": item.get("product_id"),
                    "is_group": item.get("is_group"),
                    "category": item.get("category"),
                    "firmware_version": item.get("firmware_version"),
                    "capabilities": item.get("capabilities"),
                    "has_gear_presets": item.get("has_gear_presets"),
                    "gear_count": item.get("gear_count"),
                    "min_color_temp_kelvin": item.get("min_color_temp_kelvin"),
                    "max_color_temp_kelvin": item.get("max_color_temp_kelvin"),
                }
            )
        lite["devices"] = compact_devices

    errors = report.get("errors")
    if isinstance(errors, list):
        lite["errors"] = [e for e in errors[:10] if isinstance(e, dict)]

    if "developer_feedback" in report:
        feedback = report.get("developer_feedback")
        if isinstance(feedback, str):
            lite["developer_feedback"] = feedback[:2000]
        else:
            lite["developer_feedback"] = feedback

    return lite
