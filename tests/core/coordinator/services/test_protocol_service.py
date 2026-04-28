"""Tests for the coordinator protocol-facing service."""

from __future__ import annotations

from dataclasses import dataclass, field
from unittest.mock import AsyncMock, MagicMock

import pytest

from custom_components.lipro.core.coordinator.services.protocol_service import (
    CoordinatorProtocolService,
    build_schedule_mesh_context,
)


@dataclass
class _ScheduleDeviceDouble:
    iot_device_id: str = "03ab0000000000a1"
    device_type_hex: str = "ff000001"
    mesh_gateway_device_id: str | None = ""
    mesh_group_member_ids: list[str] = field(default_factory=list)
    ir_remote_gateway_device_id: str | None = None


def _build_service(protocol: MagicMock) -> CoordinatorProtocolService:
    return CoordinatorProtocolService(protocol_getter=lambda: protocol)


def _make_schedule_device(
    *,
    iot_device_id: str = "03ab0000000000a1",
    device_type_hex: str = "ff000001",
    mesh_gateway_device_id: str | None = "",
    mesh_group_member_ids: list[str] | None = None,
    ir_remote_gateway_device_id: str | None = None,
) -> _ScheduleDeviceDouble:
    return _ScheduleDeviceDouble(
        iot_device_id=iot_device_id,
        device_type_hex=device_type_hex,
        mesh_gateway_device_id=mesh_gateway_device_id,
        mesh_group_member_ids=list(mesh_group_member_ids or []),
        ir_remote_gateway_device_id=ir_remote_gateway_device_id,
    )


def test_build_schedule_mesh_context_normalizes_member_ids_and_gateway() -> None:
    device = _make_schedule_device(
        mesh_gateway_device_id=" 03AB0000000000A1 ",
        mesh_group_member_ids=["03ab0000000000a2", " 03AB0000000000A2 ", "bad"],
        ir_remote_gateway_device_id=None,
    )

    assert build_schedule_mesh_context(device) == (
        "03ab0000000000a1",
        ["03ab0000000000a2"],
    )


def test_build_schedule_mesh_context_falls_back_to_ir_remote_gateway_property() -> None:
    device = _make_schedule_device(
        mesh_gateway_device_id=None,
        mesh_group_member_ids=[],
        ir_remote_gateway_device_id=" 03AB0000000000A9 ",
    )

    assert build_schedule_mesh_context(device) == ("03ab0000000000a9", [])


def test_build_schedule_mesh_context_preserves_blank_mesh_gateway_without_ir_override() -> (
    None
):
    device = _make_schedule_device(
        mesh_gateway_device_id="",
        mesh_group_member_ids=[],
        ir_remote_gateway_device_id=" 03AB0000000000A9 ",
    )

    assert build_schedule_mesh_context(device) == ("", [])


@pytest.mark.asyncio
async def test_get_device_schedules_copies_mesh_member_ids_before_forwarding() -> None:
    protocol = MagicMock()
    protocol.get_device_schedules = AsyncMock(return_value=[{"id": 1}])
    service = _build_service(protocol)
    mesh_member_ids = ["member-1"]

    result = await service.async_get_device_schedules(
        "device-1",
        "ff000001",
        mesh_gateway_id="gateway-1",
        mesh_member_ids=mesh_member_ids,
    )
    mesh_member_ids.append("member-2")

    assert result == [{"id": 1}]
    assert protocol.get_device_schedules.await_args.kwargs["mesh_member_ids"] == [
        "member-1"
    ]


@pytest.mark.asyncio
async def test_protocol_service_resolves_protocol_getter_each_call_and_normalizes_none_mesh_members() -> (
    None
):
    protocol = MagicMock()
    protocol.get_device_schedules = AsyncMock(return_value=[])
    getter = MagicMock(return_value=protocol)
    service = CoordinatorProtocolService(protocol_getter=getter)

    await service.async_get_device_schedules("device-1", 1)
    await service.async_get_device_schedules("device-2", 2, mesh_member_ids=None)

    assert getter.call_count == 2
    first_kwargs = protocol.get_device_schedules.await_args_list[0].kwargs
    second_kwargs = protocol.get_device_schedules.await_args_list[1].kwargs
    assert first_kwargs["mesh_member_ids"] == []
    assert second_kwargs["mesh_member_ids"] == []


@pytest.mark.asyncio
async def test_device_schedule_methods_resolve_mesh_context_from_device() -> None:
    protocol = MagicMock()
    protocol.get_device_schedules = AsyncMock(return_value=[{"id": 1}])
    protocol.add_device_schedule = AsyncMock(return_value=[{"id": 11}])
    protocol.delete_device_schedules = AsyncMock(return_value=[{"id": 12}])
    service = _build_service(protocol)
    device = _make_schedule_device(
        iot_device_id="device-1",
        device_type_hex="ff000001",
        mesh_gateway_device_id="gateway-1",
        mesh_group_member_ids=["member-1"],
    )

    schedules = await service.async_get_device_schedules_for_device(device)
    added = await service.async_add_device_schedule_for_device(
        device,
        [1, 2],
        [3600, 7200],
        [0, 1],
    )
    deleted = await service.async_delete_device_schedules_for_device(device, [11])

    assert schedules == [{"id": 1}]
    assert added == [{"id": 11}]
    assert deleted == [{"id": 12}]
    protocol.get_device_schedules.assert_awaited_once_with(
        "device-1",
        "ff000001",
        mesh_gateway_id="",
        mesh_member_ids=[],
    )
    protocol.add_device_schedule.assert_awaited_once_with(
        "device-1",
        "ff000001",
        [1, 2],
        [3600, 7200],
        [0, 1],
        mesh_gateway_id="",
        mesh_member_ids=[],
    )
    protocol.delete_device_schedules.assert_awaited_once_with(
        "device-1",
        "ff000001",
        [11],
        mesh_gateway_id="",
        mesh_member_ids=[],
    )


@pytest.mark.asyncio
async def test_query_command_result_and_outlet_power_info_use_protocol_home() -> None:
    protocol = MagicMock()
    protocol.query_command_result = AsyncMock(return_value={"msgSn": "123"})
    protocol.fetch_outlet_power_info = AsyncMock(return_value={"nowPower": 12.3})
    service = _build_service(protocol)

    command_result = await service.async_query_command_result(
        msg_sn="123",
        device_id="device-1",
        device_type=1,
    )
    power_info = await service.async_fetch_outlet_power_info("device-1")

    assert command_result == {"msgSn": "123"}
    assert power_info == {"nowPower": 12.3}
    protocol.query_command_result.assert_awaited_once_with(
        msg_sn="123",
        device_id="device-1",
        device_type=1,
    )
    protocol.fetch_outlet_power_info.assert_awaited_once_with("device-1")
