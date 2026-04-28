"""Anonymous share report building helpers."""

from __future__ import annotations

from collections.abc import Mapping
from datetime import UTC, datetime
from typing import Any, Final

from ...const.base import VERSION
from .models import SharedDevice, SharedError
from .sanitize import sanitize_value

GENERATED_AT_PLACEHOLDER = "<generated_at>"
TIMESTAMP_PLACEHOLDER = "<timestamp>"
_CANONICAL_DYNAMIC_FIELDS = {
    "generated_at": GENERATED_AT_PLACEHOLDER,
    "timestamp": TIMESTAMP_PLACEHOLDER,
}
_DEVELOPER_FEEDBACK_LABEL_PLACEHOLDERS: Final[dict[str, str]] = {
    "name": "[user_label]",
    "deviceName": "[user_device_label]",
    "device_name": "[user_device_label]",
    "roomName": "[user_room_label]",
    "room_name": "[user_room_label]",
    "productName": "[user_product_label]",
    "product_name": "[user_product_label]",
    "keyName": "[user_panel_key_label]",
    "key_name": "[user_panel_key_label]",
}


def _canonicalize_payload(value: Any) -> Any:
    if isinstance(value, dict):
        return {
            key: _CANONICAL_DYNAMIC_FIELDS.get(key, _canonicalize_payload(item))
            for key, item in value.items()
        }
    if isinstance(value, list):
        return [_canonicalize_payload(item) for item in value]
    return value


def canonicalize_generated_payload(payload: Mapping[str, Any]) -> dict[str, Any]:
    """Normalize dynamic generated fields for fixture/snapshot comparisons."""
    canonical = _canonicalize_payload(dict(payload))
    if not isinstance(canonical, dict):
        msg = "Generated payload canonicalization must return a mapping"
        raise TypeError(msg)
    return canonical


def project_developer_feedback_upload(value: Any) -> Any:
    """Project developer-feedback payloads to the upload privacy contract."""
    if isinstance(value, dict):
        projected: dict[str, Any] = {}
        for key, item in value.items():
            placeholder = _DEVELOPER_FEEDBACK_LABEL_PLACEHOLDERS.get(key)
            if placeholder is not None and isinstance(item, str):
                normalized = item.strip()
                projected[key] = placeholder if normalized else item
                continue
            projected[key] = project_developer_feedback_upload(item)
        return projected
    if isinstance(value, list):
        return [project_developer_feedback_upload(item) for item in value]
    return value


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
        "devices": [device.to_dict() for device in devices.values()],
        "errors": [error.to_dict() for error in errors],
    }


def build_developer_feedback_report(
    *,
    installation_id: str | None,
    ha_version: str | None,
    feedback: dict[str, Any],
) -> dict[str, Any]:
    """Build one developer-feedback report payload."""
    projected_feedback = project_developer_feedback_upload(feedback)
    sanitized_feedback = sanitize_value(projected_feedback, preserve_structure=True)
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
        lite["errors"] = [error for error in errors[:10] if isinstance(error, dict)]

    if "developer_feedback" in report:
        feedback = report.get("developer_feedback")
        if isinstance(feedback, str):
            lite["developer_feedback"] = feedback[:2000]
        else:
            lite["developer_feedback"] = feedback

    return lite
