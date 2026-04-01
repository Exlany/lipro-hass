"""Topical tests for the formal runtime_access surface."""

from __future__ import annotations

from collections.abc import Mapping
from types import SimpleNamespace
from typing import cast
from unittest.mock import MagicMock, patch

from pytest_homeassistant_custom_component.common import MockConfigEntry

from custom_components.lipro.const.base import DOMAIN
from custom_components.lipro.control.runtime_access import (
    build_runtime_diagnostics_projection,
    build_runtime_entry_view,
    find_runtime_device,
    find_runtime_device_and_coordinator,
    iter_runtime_entry_coordinators,
    iter_runtime_entry_views,
)
from custom_components.lipro.control.runtime_access_types import RuntimeEntryPort
from custom_components.lipro.runtime_types import LiproCoordinator


def test_build_runtime_entry_view_materializes_typed_read_model() -> None:
    protocol = SimpleNamespace()
    telemetry_service = SimpleNamespace(build_snapshot=lambda: {"runtime": "ok"})
    coordinator = SimpleNamespace(
        update_interval=None,
        last_update_success=True,
        mqtt_service=SimpleNamespace(connected=False),
        protocol=protocol,
        telemetry_service=telemetry_service,
        devices={"device-1": object()},
    )
    entry = SimpleNamespace(
        entry_id="entry-1",
        options={"debug_mode": True},
        runtime_data=cast(LiproCoordinator, coordinator),
    )

    view = build_runtime_entry_view(entry)

    assert view is not None
    assert view.entry is entry
    assert view.entry_id == "entry-1"
    assert view.options == {"debug_mode": True}
    assert view.coordinator is not None
    assert view.coordinator.runtime_coordinator is coordinator
    assert view.coordinator.last_update_success is True
    assert view.coordinator.mqtt_connected is False
    assert view.coordinator.runtime_telemetry_snapshot == {"runtime": "ok"}


def test_build_runtime_entry_view_accepts_slots_backed_runtime_ports() -> None:
    class SlotBackedEntry(RuntimeEntryPort):
        __slots__ = ("entry_id", "options", "runtime_data")

        entry_id: str
        options: Mapping[str, object]
        runtime_data: LiproCoordinator | None

        def __init__(
            self,
            *,
            entry_id: str,
            options: Mapping[str, object],
            runtime_data: LiproCoordinator | None,
        ) -> None:
            self.entry_id = entry_id
            self.options = options
            self.runtime_data = runtime_data

    coordinator = SimpleNamespace(
        update_interval=None,
        last_update_success=True,
        mqtt_service=SimpleNamespace(connected=True),
        protocol=None,
        telemetry_service=SimpleNamespace(build_snapshot=lambda: {"slot": "ok"}),
        devices={},
    )
    entry: RuntimeEntryPort = SlotBackedEntry(
        entry_id="entry-slot",
        options={"debug_mode": False},
        runtime_data=cast(LiproCoordinator, coordinator),
    )

    view = build_runtime_entry_view(entry)

    assert view is not None
    assert view.entry is entry
    assert view.entry_id == "entry-slot"
    assert view.coordinator is not None
    assert view.coordinator.mqtt_connected is True
    assert view.coordinator.runtime_telemetry_snapshot == {"slot": "ok"}


def test_iter_runtime_entry_views_rejects_dynamic_probe_only_entries() -> None:
    class ProbeOnlyEntry:
        def __getattr__(self, name: str) -> object:
            return {
                "entry_id": "ghost-entry",
                "options": {},
                "runtime_data": SimpleNamespace(),
            }[name]

    hass = MagicMock()
    hass.config_entries.async_entries.return_value = [
        ProbeOnlyEntry(),
        SimpleNamespace(entry_id="entry-1", options={}, runtime_data=None),
    ]

    views = iter_runtime_entry_views(hass)

    assert [view.entry_id for view in views] == ["entry-1"]


def test_build_runtime_entry_view_degrades_underspecified_runtime_data() -> None:
    entry = SimpleNamespace(
        entry_id="entry-bad",
        options={},
        runtime_data=cast(LiproCoordinator, SimpleNamespace()),
    )

    view = build_runtime_entry_view(entry)

    assert view is not None
    assert view.coordinator is not None
    assert view.coordinator.last_update_success is False
    assert view.coordinator.mqtt_connected is None
    assert view.coordinator.runtime_telemetry_snapshot == {}
    assert view.coordinator.devices is None


def test_iter_runtime_entry_coordinators_skips_entries_without_runtime_data(hass) -> None:
    coordinator = MagicMock()
    missing_runtime = MockConfigEntry(domain=DOMAIN, options={})
    loaded_entry = MockConfigEntry(domain=DOMAIN, options={})
    missing_runtime.add_to_hass(hass)
    loaded_entry.add_to_hass(hass)
    loaded_entry.runtime_data = coordinator

    targets = iter_runtime_entry_coordinators(hass)

    assert targets == [(loaded_entry, coordinator)]


def test_find_runtime_device_prefers_formal_lookup_helpers(hass) -> None:
    device = object()
    entry = MockConfigEntry(domain=DOMAIN, options={})
    get_device = MagicMock(return_value=None)
    get_device_by_id = MagicMock(return_value=device)
    coordinator = SimpleNamespace(
        config_entry=entry,
        get_device=get_device,
        get_device_by_id=get_device_by_id,
        devices={},
    )
    entry.runtime_data = coordinator
    entry.add_to_hass(hass)

    assert find_runtime_device(coordinator, "alias") is device
    assert find_runtime_device_and_coordinator(hass, device_id="alias") == (
        device,
        coordinator,
    )


def test_build_runtime_diagnostics_projection_marks_missing_device_cache() -> None:
    coordinator = SimpleNamespace(
        update_interval=None,
        last_update_success=True,
        mqtt_service=SimpleNamespace(connected=True),
        protocol=None,
        telemetry_service=SimpleNamespace(build_snapshot=dict),
        devices=None,
    )
    entry = SimpleNamespace(
        entry_id="entry-1",
        options={},
        runtime_data=cast(LiproCoordinator, coordinator),
    )

    projection = build_runtime_diagnostics_projection(entry)

    assert projection is not None
    assert projection.snapshot.entry_id == "entry-1"
    assert projection.snapshot.device_count == 0
    assert projection.degraded_fields == ("devices",)


def test_build_runtime_diagnostics_projection_rejects_empty_entry_id() -> None:
    coordinator = SimpleNamespace(
        update_interval=None,
        last_update_success=True,
        mqtt_service=SimpleNamespace(connected=True),
        protocol=None,
        telemetry_service=SimpleNamespace(build_snapshot=dict),
        devices={},
    )
    entry = SimpleNamespace(
        entry_id="",
        options={},
        runtime_data=cast(LiproCoordinator, coordinator),
    )

    assert build_runtime_diagnostics_projection(entry) is None

def test_build_runtime_diagnostics_projection_uses_formal_mapping_helpers() -> None:
    coordinator = SimpleNamespace(
        update_interval=None,
        last_update_success=True,
        mqtt_service=SimpleNamespace(connected=True),
        protocol=None,
        telemetry_service=SimpleNamespace(build_snapshot=dict),
        devices=None,
    )
    entry = SimpleNamespace(
        entry_id="entry-1",
        options={},
        runtime_data=cast(LiproCoordinator, coordinator),
    )

    with (
        patch(
            "custom_components.lipro.control.runtime_access.get_runtime_device_mapping",
            return_value={"device-1": object()},
        ) as mock_mapping,
        patch(
            "custom_components.lipro.control.runtime_access.is_runtime_device_mapping_degraded",
            return_value=True,
        ) as mock_degraded,
    ):
        projection = build_runtime_diagnostics_projection(entry)

    assert projection is not None
    assert projection.snapshot.device_count == 1
    assert projection.degraded_fields == ("devices",)
    mock_mapping.assert_called_once_with(coordinator)
    mock_degraded.assert_called_once_with(coordinator)

