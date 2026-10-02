"""Malformed telemetry degrades safely without losing coordinator facts."""

from types import SimpleNamespace
from typing import cast

import pytest

from custom_components.lipro.control import (
    runtime_access_support_telemetry as telemetry,
)
from custom_components.lipro.control.runtime_access_types import (
    RuntimeAccessCoordinator,
    RuntimeAccessProtocol,
    RuntimeCoordinatorView,
    RuntimeEntryPort,
    RuntimeEntryView,
)


@pytest.mark.parametrize(
    "protocol",
    [
        SimpleNamespace(),
        SimpleNamespace(diagnostics_context=None),
        SimpleNamespace(diagnostics_context=SimpleNamespace()),
        SimpleNamespace(diagnostics_context=SimpleNamespace(snapshot=list)),
        SimpleNamespace(protocol_diagnostics_snapshot=list, diagnostics_context=None),
    ],
)
def test_unavailable_protocol_snapshot_is_empty(protocol):
    source = telemetry._ProtocolFacadeTelemetrySource(
        cast(RuntimeAccessProtocol, protocol)
    )
    assert source.get_protocol_telemetry_snapshot() == {}


def test_legacy_context_snapshot_filters_non_json_values():
    protocol = SimpleNamespace(
        diagnostics_context=SimpleNamespace(
            snapshot=lambda: {
                "nested": {"ok": [1, None, {"flag": True}], "bad": object()},
                "bad_list": [object()],
                "none": None,
            }
        )
    )
    source = telemetry._ProtocolFacadeTelemetrySource(
        cast(RuntimeAccessProtocol, protocol)
    )
    assert source.get_protocol_telemetry_snapshot() == {
        "nested": {"ok": [1, None, {"flag": True}]},
        "none": None,
    }


def test_snapshot_and_projection_handle_partial_entry_views():
    coordinator = RuntimeCoordinatorView(None, False, True, None, {"ok": True}, None)
    entry = cast(RuntimeEntryPort, SimpleNamespace())
    missing = RuntimeEntryView(entry, "entry", {}, None)
    unnamed = RuntimeEntryView(entry, "", {}, coordinator)
    complete = RuntimeEntryView(entry, "entry", {}, coordinator)
    for view in (None, missing, unnamed):
        assert telemetry.build_runtime_snapshot_from_view_support(view) is None
        assert (
            telemetry.build_runtime_diagnostics_projection_from_view_support(view)
            is None
        )
    projection = telemetry.build_runtime_diagnostics_projection_from_view_support(
        complete
    )
    assert projection is not None
    assert projection.degraded_fields == ("devices",)
    assert projection.update_interval == ""
    assert projection.snapshot.device_count == 0
    assert projection.snapshot.mqtt_connected is True
    assert telemetry._CoordinatorTelemetrySource(
        coordinator, entry_id=None
    ).get_runtime_telemetry_snapshot() == {"ok": True}


class UnavailableTelemetry:
    @property
    def telemetry_service(self):
        raise AttributeError("not ready")


class UnavailableSnapshot:
    @property
    def build_snapshot(self):
        raise AttributeError("not ready")


@pytest.mark.parametrize(
    "coordinator",
    [
        SimpleNamespace(),
        UnavailableTelemetry(),
        SimpleNamespace(telemetry_service=SimpleNamespace()),
        SimpleNamespace(telemetry_service=UnavailableSnapshot()),
        SimpleNamespace(telemetry_service=SimpleNamespace(build_snapshot=0)),
        SimpleNamespace(telemetry_service=SimpleNamespace(build_snapshot=list)),
    ],
)
def test_missing_or_invalid_runtime_snapshot_is_empty(coordinator):
    assert (
        telemetry._build_runtime_telemetry_snapshot(
            cast(RuntimeAccessCoordinator, coordinator)
        )
        == {}
    )
