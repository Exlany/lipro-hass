"""Shared diagnostics helpers and cross-surface smoke tests."""

from __future__ import annotations

from collections.abc import Mapping
from datetime import timedelta
from types import MappingProxyType
from unittest.mock import MagicMock, patch

import pytest

from custom_components.lipro.const.base import DOMAIN
from custom_components.lipro.control.diagnostics_surface import (
    DiagnosticsPayload,
    DiagnosticsValue,
)
from custom_components.lipro.diagnostics import (
    _redact_device_properties,
    async_get_config_entry_diagnostics,
    async_get_device_diagnostics,
)

_USE_DEFAULT_GET_DEVICE = object()


def _diag_payload(value: DiagnosticsValue) -> DiagnosticsPayload:
    assert isinstance(value, dict)
    return value


def _diag_list(value: DiagnosticsValue) -> list[DiagnosticsValue]:
    assert isinstance(value, list)
    return value


def _diag_str(value: DiagnosticsValue) -> str:
    assert isinstance(value, str)
    return value


def _normalize_device_cache(devices):
    if devices is None:
        return None
    if isinstance(devices, Mapping):
        return MappingProxyType(dict(devices))
    return devices


def _make_coordinator(
    *,
    devices=None,
    last_update_success: bool = True,
    update_interval_seconds: int = 30,
    mqtt_connected=True,
    get_device=_USE_DEFAULT_GET_DEVICE,
):
    coordinator = MagicMock()
    device_cache = _normalize_device_cache(devices)
    coordinator.devices = device_cache
    coordinator.last_update_success = last_update_success
    coordinator.update_interval = timedelta(seconds=update_interval_seconds)
    coordinator.mqtt_service.connected = mqtt_connected

    if get_device is _USE_DEFAULT_GET_DEVICE:
        if isinstance(device_cache, Mapping):
            coordinator.get_device = MagicMock(
                side_effect=lambda device_id: device_cache.get(device_id)
            )
        else:
            coordinator.get_device = None
    else:
        coordinator.get_device = get_device

    return coordinator


def _make_entry(
    *,
    runtime_data,
    entry_id: str = "entry-1",
    title="Lipro (13800000000)",
    data: dict[str, object] | None = None,
    options: dict[str, object] | None = None,
):
    entry = MagicMock()
    entry.entry_id = entry_id
    entry.runtime_data = runtime_data
    entry.title = title
    entry.data = data or {}
    entry.options = options or {}
    return entry


def _make_device_entry(serial: str, *, domain: str = DOMAIN):
    device_entry = MagicMock()
    device_entry.identifiers = {(domain, serial)}
    return device_entry


def _make_share_manager(*, enabled: bool = False, pending_count=(0, 0)):
    share_manager = MagicMock()
    share_manager.is_enabled = enabled
    share_manager.pending_count = pending_count
    return share_manager


def _patch_share_manager(share_manager):
    return patch(
        "custom_components.lipro.diagnostics.get_anonymous_share_manager",
        return_value=share_manager,
    )


def test_redact_device_properties_rejects_non_mapping_inputs() -> None:
    """Diagnostics adapter should only pass typed property mappings downstream."""
    assert _redact_device_properties(["not", "a", "mapping"]) == {}


@pytest.mark.asyncio
@pytest.mark.parametrize("topic", ["config-entry", "device"])
async def test_diagnostics_surfaces_report_entry_not_loaded_consistently(
    hass, topic: str
) -> None:
    """Both diagnostics surfaces should expose the same entry-not-loaded contract."""
    entry = _make_entry(runtime_data=None)

    if topic == "config-entry":
        result = await async_get_config_entry_diagnostics(hass, entry)
    else:
        result = await async_get_device_diagnostics(
            hass,
            entry,
            _make_device_entry("03ab5ccd7c111111"),
        )

    assert result == {"error": "entry_not_loaded"}


@pytest.mark.asyncio
async def test_config_entry_diagnostics_redacts_ir_gateway_projection(
    hass, make_device
) -> None:
    """IR remote gateway projections should redact via the typed helper path."""
    device = make_device(
        "light",
        serial="rmt_id_appremote_realremote_03abdeadbeefcafe",
        physical_model="irRemote",
        properties={"powerState": "1"},
    )
    coordinator = _make_coordinator(devices={device.serial: device})
    entry = _make_entry(runtime_data=coordinator)

    with _patch_share_manager(_make_share_manager()):
        result = await async_get_config_entry_diagnostics(hass, entry)

    devices = _diag_list(result["devices"])
    first_device = _diag_payload(devices[0])
    extra_data = _diag_payload(first_device["extra_data"])
    assert extra_data == {"gateway_device_id": "**REDACTED**"}


@pytest.mark.asyncio
async def test_config_entry_diagnostics_redacts_mesh_group_projection_without_gateway(
    hass, make_device
) -> None:
    """Mesh-group diagnostics should preserve member-cardinality without leaking ids."""
    device = make_device(
        "light",
        serial="mesh_group_20001",
        extra_data={"group_member_ids": ["03ab111111111111", "03ab222222222222"]},
        properties={"powerState": "1"},
    )
    coordinator = _make_coordinator(devices={device.serial: device})
    entry = _make_entry(runtime_data=coordinator)

    with _patch_share_manager(_make_share_manager()):
        result = await async_get_config_entry_diagnostics(hass, entry)

    devices = _diag_list(result["devices"])
    first_device = _diag_payload(devices[0])
    extra_data = _diag_payload(first_device["extra_data"])
    assert extra_data == {
        "group_member_ids": ["**REDACTED**", "**REDACTED**"],
    }


@pytest.mark.asyncio
async def test_device_diagnostics_reports_degraded_runtime_device_cache(
    hass,
) -> None:
    """Device diagnostics should surface degraded cache state via runtime_access."""
    coordinator = _make_coordinator(
        devices=None,
        get_device=None,
    )
    coordinator.get_device_by_id = None
    entry = _make_entry(runtime_data=coordinator)

    result = await async_get_device_diagnostics(
        hass,
        entry,
        _make_device_entry("03ab5ccd7c111111"),
    )

    assert result == {"error": "device_cache_unavailable"}
