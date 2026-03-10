"""Snapshot coverage for API typed payload contracts."""

from __future__ import annotations

from syrupy.assertion import SnapshotAssertion

from custom_components.lipro.core.api.types import (
    CommandResultApiResponse,
    DiagnosticsApiResponse,
    ScheduleApiResponse,
)


def test_api_payload_snapshots(snapshot: SnapshotAssertion) -> None:
    command_payload: CommandResultApiResponse = {
        "code": 0,
        "message": "ok",
        "success": True,
        "msgSn": "abc123",
    }
    diagnostics_payload: DiagnosticsApiResponse = {
        "code": 0,
        "success": True,
        "data": [{"event": "connected", "count": 2}],
    }
    schedule_payload: ScheduleApiResponse = {
        "success": True,
        "data": [{"id": "1", "hour": 8, "minute": 30, "enable": True}],
    }

    assert {
        "command": command_payload,
        "diagnostics": diagnostics_payload,
        "schedule": schedule_payload,
    } == snapshot
