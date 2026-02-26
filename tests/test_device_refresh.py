"""Tests for device refresh helpers."""

from __future__ import annotations

from unittest.mock import patch

from custom_components.lipro.const.categories import DeviceCategory
from custom_components.lipro.core.device import LiproDevice
from custom_components.lipro.core.device_refresh import (
    build_fetched_device_snapshot,
    plan_stale_device_reconciliation,
    register_lookup_id,
)


def _make_device(
    *,
    serial: str,
    is_group: bool = False,
    iot_name: str = "lipro_led",
    physical_model: str = "light",
) -> LiproDevice:
    return LiproDevice(
        device_number=1,
        serial=serial,
        name="Refresh Test Device",
        device_type=1,
        iot_name=iot_name,
        physical_model=physical_model,
        is_group=is_group,
    )


class _GatewayCategoryErrorDevice:
    serial = "03ab000000000010"
    name = "GatewayError"
    is_group = False
    has_valid_iot_id = True
    iot_device_id = serial

    @property
    def is_gateway(self) -> bool:
        raise ValueError("bad gateway payload")

    @property
    def category(self) -> DeviceCategory:
        return DeviceCategory.LIGHT


class _OutletCategoryErrorDevice:
    serial = "03ab000000000020"
    name = "CategoryError"
    is_group = False
    has_valid_iot_id = True
    iot_device_id = serial

    @property
    def is_gateway(self) -> bool:
        return False

    @property
    def category(self) -> DeviceCategory:
        raise ValueError("bad category payload")


def test_register_lookup_id_ignores_non_string_and_blank() -> None:
    device = _make_device(serial="03ab000000000001")
    mapping: dict[str, LiproDevice] = {}

    register_lookup_id(mapping, 1, device)
    register_lookup_id(mapping, "   ", device)

    assert mapping == {}


def test_build_fetched_device_snapshot_handles_malformed_rows() -> None:
    group = _make_device(serial="mesh_group_10001", is_group=True)
    outlet = _make_device(
        serial="03ab000000000030",
        iot_name="lipro_outlet",
        physical_model="outlet",
    )
    invalid_serial = _make_device(serial="  ")

    with patch(
        "custom_components.lipro.core.device_refresh.LiproDevice.from_api_data"
    ) as from_api:
        from_api.side_effect = [
            TypeError("malformed row"),
            invalid_serial,
            _GatewayCategoryErrorDevice(),
            group,
            _OutletCategoryErrorDevice(),
            outlet,
        ]
        snapshot = build_fetched_device_snapshot([{}, {}, {}, {}, {}, {}])

    assert set(snapshot.devices) == {
        "mesh_group_10001",
        "03ab000000000020",
        "03ab000000000030",
    }
    assert snapshot.group_ids == ["mesh_group_10001"]
    assert snapshot.iot_ids == ["03ab000000000020", "03ab000000000030"]
    assert snapshot.outlet_ids == ["03ab000000000030"]


def test_plan_stale_device_reconciliation_tracks_and_removes() -> None:
    plan = plan_stale_device_reconciliation(
        previous_serials={"dev_a", "dev_b"},
        current_serials={"dev_a"},
        missing_cycles={"dev_b": 2, "dev_c": 1, "dev_a": 5},
        remove_threshold=3,
    )

    assert plan.removable_serials == {"dev_b"}
    assert plan.missing_cycles == {"dev_b": 3, "dev_c": 2}
