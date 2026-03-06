"""Tests for device-registry sync helpers."""

from __future__ import annotations

from types import SimpleNamespace
from unittest.mock import MagicMock, call, patch

from custom_components.lipro.core.coordinator.device_registry_sync import (
    collect_registry_serials_for_entry,
    remove_stale_registry_devices,
    sync_device_room_assignments,
)
from custom_components.lipro.core.coordinator.runtime.room_sync_runtime import (
    normalize_room_name,
    resolve_room_area_target_name,
)
from custom_components.lipro.core.device import LiproDevice


def _make_device(*, serial: str, room_name: str | None) -> LiproDevice:
    return LiproDevice(
        device_number=1,
        serial=serial,
        name="Registry Sync Test Device",
        device_type=1,
        iot_name="lipro_led",
        room_name=room_name,
        physical_model="light",
    )


def test_collect_registry_serials_for_entry_filters_domain_and_empty_ids() -> None:
    device_registry = MagicMock()
    entries = [
        SimpleNamespace(
            identifiers={
                ("lipro", "03ab5ccd7c000001"),
                ("other", "dev-1"),
                ("lipro", " "),
                ("lipro", 12345),
            }
        ),
        SimpleNamespace(
            identifiers={
                ("lipro", "03ab5ccd7c000002"),
            }
        ),
    ]

    with patch(
        "custom_components.lipro.core.coordinator.device_registry_sync.dr.async_entries_for_config_entry",
        return_value=entries,
    ):
        serials = collect_registry_serials_for_entry(
            device_registry=device_registry,
            config_entry_id="entry-1",
            domain="lipro",
        )

    assert serials == {"03ab5ccd7c000001", "03ab5ccd7c000002"}


def test_sync_device_room_assignments_updates_when_cloud_room_changes() -> None:
    previous_devices = {
        "03ab5ccd7c111111": _make_device(
            serial="03ab5ccd7c111111",
            room_name="主卧",
        )
    }
    devices = {
        "03ab5ccd7c111111": _make_device(
            serial="03ab5ccd7c111111",
            room_name="儿童房",
        )
    }

    device_registry = MagicMock()
    device_registry.async_get_device.return_value = SimpleNamespace(
        id="dev-entry-1",
        area_id="area-old",
    )
    area_registry = MagicMock()
    area_registry.async_get_area.return_value = SimpleNamespace(name="主卧")
    area_registry.async_get_or_create.return_value = SimpleNamespace(id="area-kids")

    sync_device_room_assignments(
        devices=devices,
        previous_devices=previous_devices,
        room_area_sync_force=False,
        domain="lipro",
        device_registry=device_registry,
        area_registry=area_registry,
        normalize_room_name=normalize_room_name,
        resolve_room_area_target_name=resolve_room_area_target_name,
        logger=MagicMock(),
    )

    device_registry.async_update_device.assert_called_once_with(
        "dev-entry-1",
        suggested_area="儿童房",
        area_id="area-kids",
    )


def test_sync_device_room_assignments_force_sync_when_room_name_unchanged() -> None:
    previous_devices = {
        "03ab5ccd7c111111": _make_device(
            serial="03ab5ccd7c111111",
            room_name="主卧",
        )
    }
    devices = {
        "03ab5ccd7c111111": _make_device(
            serial="03ab5ccd7c111111",
            room_name="主卧",
        )
    }

    device_registry = MagicMock()
    device_registry.async_get_device.return_value = SimpleNamespace(
        id="dev-entry-1",
        area_id="area-custom",
    )
    area_registry = MagicMock()
    area_registry.async_get_area.return_value = SimpleNamespace(name="手动区域")
    area_registry.async_get_or_create.return_value = SimpleNamespace(id="area-bedroom")

    sync_device_room_assignments(
        devices=devices,
        previous_devices=previous_devices,
        room_area_sync_force=True,
        domain="lipro",
        device_registry=device_registry,
        area_registry=area_registry,
        normalize_room_name=normalize_room_name,
        resolve_room_area_target_name=resolve_room_area_target_name,
        logger=MagicMock(),
    )

    device_registry.async_update_device.assert_called_once_with(
        "dev-entry-1",
        suggested_area="主卧",
        area_id="area-bedroom",
    )


def test_sync_device_room_assignments_force_sync_skips_aligned_mapping() -> None:
    previous_devices = {
        "03ab5ccd7c111111": _make_device(
            serial="03ab5ccd7c111111",
            room_name="主卧",
        )
    }
    devices = {
        "03ab5ccd7c111111": _make_device(
            serial="03ab5ccd7c111111",
            room_name="主卧",
        )
    }

    device_registry = MagicMock()
    device_registry.async_get_device.return_value = SimpleNamespace(
        id="dev-entry-1",
        area_id="area-bedroom",
    )
    area_registry = MagicMock()
    area_registry.async_get_area.return_value = SimpleNamespace(name=" 主卧 ")
    resolve_target = MagicMock(return_value=(True, "主卧"))

    sync_device_room_assignments(
        devices=devices,
        previous_devices=previous_devices,
        room_area_sync_force=True,
        domain="lipro",
        device_registry=device_registry,
        area_registry=area_registry,
        normalize_room_name=normalize_room_name,
        resolve_room_area_target_name=resolve_target,
        logger=MagicMock(),
    )

    device_registry.async_update_device.assert_not_called()
    resolve_target.assert_not_called()


def test_sync_device_room_assignments_reuses_cached_area_id_for_same_target() -> None:
    previous_devices = {
        "03ab5ccd7c111111": _make_device(
            serial="03ab5ccd7c111111",
            room_name="主卧",
        ),
        "03ab5ccd7c222222": _make_device(
            serial="03ab5ccd7c222222",
            room_name="书房",
        ),
    }
    devices = {
        "03ab5ccd7c111111": _make_device(
            serial="03ab5ccd7c111111",
            room_name="客厅",
        ),
        "03ab5ccd7c222222": _make_device(
            serial="03ab5ccd7c222222",
            room_name="客厅",
        ),
    }

    device_registry = MagicMock()

    def _lookup(*, identifiers: set[tuple[str, str]]) -> SimpleNamespace | None:
        if ("lipro", "03ab5ccd7c111111") in identifiers:
            return SimpleNamespace(id="dev-entry-1", area_id="area-old-1")
        if ("lipro", "03ab5ccd7c222222") in identifiers:
            return SimpleNamespace(id="dev-entry-2", area_id="area-old-2")
        return None

    device_registry.async_get_device.side_effect = _lookup
    area_registry = MagicMock()
    area_registry.async_get_area.side_effect = [
        SimpleNamespace(name="主卧"),
        SimpleNamespace(name="书房"),
    ]
    area_registry.async_get_or_create.return_value = SimpleNamespace(id="area-living")

    sync_device_room_assignments(
        devices=devices,
        previous_devices=previous_devices,
        room_area_sync_force=False,
        domain="lipro",
        device_registry=device_registry,
        area_registry=area_registry,
        normalize_room_name=normalize_room_name,
        resolve_room_area_target_name=resolve_room_area_target_name,
        logger=MagicMock(),
    )

    area_registry.async_get_or_create.assert_called_once_with("客厅")
    device_registry.async_update_device.assert_has_calls(
        [
            call("dev-entry-1", suggested_area="客厅", area_id="area-living"),
            call("dev-entry-2", suggested_area="客厅", area_id="area-living"),
        ],
        any_order=False,
    )


def test_remove_stale_registry_devices_removes_only_present_devices() -> None:
    present_entry = SimpleNamespace(id="reg-id", name="Stale Device")
    device_registry = MagicMock()

    def _lookup(*, identifiers: set[tuple[str, str]]) -> SimpleNamespace | None:
        return present_entry if ("lipro", "03ab5ccd7cdead") in identifiers else None

    device_registry.async_get_device.side_effect = _lookup

    remove_stale_registry_devices(
        stale_serials={"03ab5ccd7cdead", "03ab5ccd7cnotfound"},
        domain="lipro",
        device_registry=device_registry,
        logger=MagicMock(),
    )

    assert device_registry.async_get_device.call_count == 2
    device_registry.async_remove_device.assert_called_once_with("reg-id")
    device_registry.async_get_device.assert_has_calls(
        [
            call(identifiers={("lipro", "03ab5ccd7cdead")}),
            call(identifiers={("lipro", "03ab5ccd7cnotfound")}),
        ],
        any_order=True,
    )
