"""Focused tests for runtime snapshot support helpers."""

from __future__ import annotations

from typing import cast
from unittest.mock import Mock

import pytest

from custom_components.lipro.core.coordinator.runtime.device.snapshot_support import (
    DeviceRow,
    SnapshotAssembly,
    build_index_identity_aliases,
    canonical_page_has_more,
    canonicalize_device_row,
    coerce_total_count,
    device_ref_from_row,
    record_snapshot_device,
)
from custom_components.lipro.core.protocol.contracts import CanonicalDeviceListItem


@pytest.mark.parametrize(
    ("total", "expected"),
    [
        (3, 3),
        (3.0, 3),
        ("3", 3),
        (-1, 0),
        (True, 1),
        ("invalid", 1),
        (None, 1),
    ],
)
def test_coerce_total_count_handles_supported_inputs(
    total: object, expected: int
) -> None:
    """Coercion keeps canonical total boundaries stable."""
    result = coerce_total_count(
        offset=0,
        devices_data=[{"serial": "03ab000000000001"}],
        total=total,
    )
    assert result == expected


@pytest.mark.parametrize(
    ("offset", "count", "total", "expected"),
    [
        (0, 1, 2, True),
        (0, 1, 1, False),
        (100, 1, "101", False),
        (100, 1, "102", True),
        (0, 1, "invalid", False),
    ],
)
def test_canonical_page_has_more(
    offset: int, count: int, total: object, expected: bool
) -> None:
    """Canonical page boundary logic should remain deterministic."""
    devices_data = [
        cast(CanonicalDeviceListItem, {"serial": "03ab000000000001"})
        for _ in range(count)
    ]
    assert (
        canonical_page_has_more(
            offset=offset,
            devices_data=devices_data,
            total=total,
        )
        is expected
    )


def test_canonicalize_device_row_derives_identity_aliases() -> None:
    """Rows without aliases should derive serial and iot aliases."""
    row = canonicalize_device_row(
        {
            "serial": "03ab000000000001",
            "iotDeviceId": "dev-001",
            "deviceName": "Test Device",
        }
    )
    assert row["identityAliases"] == ["03ab000000000001", "dev-001"]


def test_canonicalize_device_row_preserves_existing_aliases() -> None:
    """Rows with explicit aliases should not be rewritten."""
    row = canonicalize_device_row(
        {
            "serial": "03ab000000000001",
            "iotDeviceId": "dev-001",
            "identityAliases": ["custom"],
        }
    )
    assert row["identityAliases"] == ["custom"]


@pytest.mark.parametrize(
    ("payload", "expected"),
    [
        ({"serial": "s1"}, "s1"),
        ({"serial": " ", "iotDeviceId": "dev-1"}, "dev-1"),
        ({"serial": " ", "iotDeviceId": " ", "deviceId": "d-1"}, "d-1"),
        ({"serial": " ", "iotDeviceId": " ", "deviceId": " "}, None),
    ],
)
def test_device_ref_from_row_uses_priority_order(
    payload: dict[str, object], expected: str | None
) -> None:
    """Device refs should prefer serial, then iotDeviceId, then deviceId."""
    assert device_ref_from_row(payload) == expected


def test_build_index_identity_aliases_merges_runtime_aliases(make_device) -> None:
    """Identity alias list should always include serial and iot id."""
    device = make_device("light", serial="03ab000000000001")
    row = cast(
        DeviceRow,
        {
            "identityAliases": ["custom", "03ab000000000001"],
            "serial": "03ab000000000001",
            "iotDeviceId": "dev-001",
        },
    )

    aliases = build_index_identity_aliases(row, device)

    assert aliases == ("03ab000000000001", "custom")


def test_record_snapshot_device_populates_indexes_and_categories(make_device) -> None:
    """Recording a normal light should populate runtime indexes and iot ids."""
    assembly = SnapshotAssembly()
    device = make_device("light", serial="03ab000000000001")
    row = cast(
        DeviceRow,
        {
            "serial": "03ab000000000001",
            "iotDeviceId": "dev-001",
        },
    )

    record_snapshot_device(normalized_row=row, device=device, assembly=assembly)

    assert assembly.devices["03ab000000000001"] is device
    assert assembly.device_by_id["03ab000000000001"] is device
    assert assembly.identity_mapping["03ab000000000001"] is device
    assert assembly.identity_aliases_by_serial["03ab000000000001"] == (
        "03ab000000000001",
    )
    assert assembly.iot_ids == ["03ab000000000001"]
    assert assembly.group_ids == []
    assert assembly.outlet_ids == []


def test_record_snapshot_device_splits_group_outlet_and_gateway(make_device) -> None:
    """Special device categories should be routed to the right assembly buckets."""
    assembly = SnapshotAssembly()
    group_device = make_device("light", serial="group1", is_group=True)
    outlet_device = make_device("outlet", serial="outlet1")
    gateway_device = Mock()
    gateway_device.serial = "gateway1"
    gateway_device.iot_device_id = "gateway-iot"
    gateway_device.is_group = False
    gateway_device.capabilities = Mock(is_gateway=True, is_outlet=False)

    record_snapshot_device(
        normalized_row=cast(
            DeviceRow, {"serial": "group1", "iotDeviceId": "group-iot"}
        ),
        device=group_device,
        assembly=assembly,
    )
    record_snapshot_device(
        normalized_row=cast(
            DeviceRow, {"serial": "outlet1", "iotDeviceId": "outlet-iot"}
        ),
        device=outlet_device,
        assembly=assembly,
    )
    record_snapshot_device(
        normalized_row=cast(
            DeviceRow, {"serial": "gateway1", "iotDeviceId": "gateway-iot"}
        ),
        device=gateway_device,
        assembly=assembly,
    )

    assert assembly.group_ids == ["group1"]
    assert assembly.outlet_ids == ["outlet1"]
    assert assembly.iot_ids == []
    assert assembly.diagnostic_gateway_devices["gateway1"] is gateway_device
    assert "gateway1" not in assembly.devices
