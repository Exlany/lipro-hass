"""Tests for the coordinator protocol-facing service."""

from __future__ import annotations

from unittest.mock import AsyncMock, MagicMock

import pytest

from custom_components.lipro.core.coordinator.services.protocol_service import (
    CoordinatorProtocolService,
)


def _build_service(protocol: MagicMock) -> CoordinatorProtocolService:
    return CoordinatorProtocolService(protocol_getter=lambda: protocol)


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
async def test_protocol_service_resolves_protocol_getter_each_call_and_normalizes_none_mesh_members() -> None:
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
async def test_add_and_delete_schedule_forward_formal_arguments() -> None:
    protocol = MagicMock()
    protocol.add_device_schedule = AsyncMock(return_value=[{"id": 11}])
    protocol.delete_device_schedules = AsyncMock(return_value=[{"id": 12}])
    service = _build_service(protocol)

    added = await service.async_add_device_schedule(
        "device-1",
        1,
        [1, 2],
        [3600, 7200],
        [0, 1],
        mesh_gateway_id="gateway-1",
        mesh_member_ids=["member-1"],
    )
    deleted = await service.async_delete_device_schedules(
        "device-1",
        1,
        [11],
        mesh_gateway_id="gateway-1",
        mesh_member_ids=["member-1"],
    )

    assert added == [{"id": 11}]
    assert deleted == [{"id": 12}]
    protocol.add_device_schedule.assert_awaited_once_with(
        "device-1",
        1,
        [1, 2],
        [3600, 7200],
        [0, 1],
        mesh_gateway_id="gateway-1",
        mesh_member_ids=["member-1"],
    )
    protocol.delete_device_schedules.assert_awaited_once_with(
        "device-1",
        1,
        [11],
        mesh_gateway_id="gateway-1",
        mesh_member_ids=["member-1"],
    )


@pytest.mark.asyncio
async def test_get_city_and_user_cloud_return_detached_dicts() -> None:
    protocol = MagicMock()
    city_payload = {"city": "江门"}
    cloud_payload = {"success": True}
    protocol.get_city = AsyncMock(return_value=city_payload)
    protocol.query_user_cloud = AsyncMock(return_value=cloud_payload)
    service = _build_service(protocol)

    city = await service.async_get_city()
    cloud = await service.async_query_user_cloud()

    assert city == city_payload
    assert cloud == cloud_payload
    assert city is not city_payload
    assert cloud is not cloud_payload


@pytest.mark.asyncio
@pytest.mark.parametrize(
    ("method_name", "protocol_attr"),
    [
        ("async_fetch_body_sensor_history", "fetch_body_sensor_history"),
        ("async_fetch_door_sensor_history", "fetch_door_sensor_history"),
    ],
)
async def test_history_methods_return_detached_payload_dicts(
    method_name: str,
    protocol_attr: str,
) -> None:
    protocol = MagicMock()
    payload = {"rows": [1, 2, 3]}
    setattr(protocol, protocol_attr, AsyncMock(return_value=payload))
    service = _build_service(protocol)

    method = getattr(service, method_name)
    result = await method(
        device_id="device-1",
        device_type=1,
        sensor_device_id="sensor-1",
        mesh_type="mesh",
    )

    assert result == payload
    assert result is not payload


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
