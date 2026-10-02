"""Child REST ports preserve arguments, results and errors at the facade edge."""

from unittest.mock import AsyncMock, MagicMock

import pytest

from custom_components.lipro.core.api.rest_facade import LiproRestFacade
from custom_components.lipro.core.protocol import rest_port_bindings as ports


@pytest.mark.parametrize(
    ("port_type", "method", "args", "kwargs", "forward_args", "forward_kwargs"),
    [
        (
            ports._BoundRestAuthPort,
            "login",
            ("phone", "hash"),
            {"password_is_hashed": True},
            ("phone", "hash"),
            {"password_is_hashed": True},
        ),
        (ports._BoundRestAuthPort, "refresh_access_token", (), {}, (), {}),
        (
            ports._BoundRestInventoryPort,
            "get_devices",
            (20, 50),
            {},
            (),
            {"offset": 20, "limit": 50},
        ),
        (ports._BoundRestInventoryPort, "get_product_configs", (), {}, (), {}),
        (
            ports._BoundRestStatusPort,
            "query_device_status",
            (["d"],),
            {"max_devices_per_query": 3},
            (["d"],),
            {"max_devices_per_query": 3, "on_batch_metric": None},
        ),
        (
            ports._BoundRestStatusPort,
            "query_mesh_group_status",
            (["g"],),
            {},
            (["g"],),
            {},
        ),
        (
            ports._BoundRestStatusPort,
            "query_connect_status",
            (["d"],),
            {},
            (["d"],),
            {},
        ),
        (
            ports._BoundRestCommandPort,
            "send_command",
            ("d", "on", 1),
            {},
            ("d", "on", 1, None, ""),
            {},
        ),
        (
            ports._BoundRestCommandPort,
            "send_group_command",
            ("g", "on", 1),
            {},
            ("g", "on", 1, None, ""),
            {},
        ),
        (
            ports._BoundRestCommandPort,
            "query_command_result",
            (),
            {"msg_sn": "sn", "device_id": "d", "device_type": 1},
            (),
            {"msg_sn": "sn", "device_id": "d", "device_type": 1},
        ),
        (ports._BoundRestMiscPort, "get_mqtt_config", (), {}, (), {}),
        (ports._BoundRestMiscPort, "get_city", (), {}, (), {}),
        (ports._BoundRestMiscPort, "query_user_cloud", (), {}, (), {}),
        (
            ports._BoundRestMiscPort,
            "query_ota_info",
            ("d", 1),
            {"iot_name": "iot", "allow_rich_v2_fallback": True},
            ("d", 1),
            {"iot_name": "iot", "allow_rich_v2_fallback": True},
        ),
        (
            ports._BoundRestMiscPort,
            "fetch_body_sensor_history",
            ("d", 1, "sensor", "mesh"),
            {},
            ("d", 1, "sensor", "mesh"),
            {},
        ),
        (
            ports._BoundRestMiscPort,
            "fetch_door_sensor_history",
            ("d", 1, "sensor", "mesh"),
            {},
            ("d", 1, "sensor", "mesh"),
            {},
        ),
        (
            ports._BoundRestSchedulePort,
            "get_device_schedules",
            ("d", 1),
            {"mesh_gateway_id": "g", "mesh_member_ids": ["m"]},
            ("d", 1),
            {"mesh_gateway_id": "g", "mesh_member_ids": ["m"]},
        ),
        (
            ports._BoundRestSchedulePort,
            "add_device_schedule",
            ("d", 1, [1], [2], [3], "g"),
            {},
            ("d", 1, [1], [2], [3], "g"),
            {"mesh_gateway_id": "", "mesh_member_ids": None},
        ),
        (
            ports._BoundRestSchedulePort,
            "delete_device_schedules",
            ("d", 1, [1], "g"),
            {},
            ("d", 1, [1], "g"),
            {"mesh_gateway_id": "", "mesh_member_ids": None},
        ),
    ],
)
async def test_port_preserves_facade_contract(
    port_type, method, args, kwargs, forward_args, forward_kwargs
):
    facade = MagicMock(spec=LiproRestFacade)
    result = {"sentinel": "response"}
    operation = AsyncMock(return_value=result)
    setattr(facade, method, operation)
    port = port_type(facade)
    assert await getattr(port, method)(*args, **kwargs) is result
    operation.assert_awaited_once_with(*forward_args, **forward_kwargs)
    operation.side_effect = TimeoutError("upstream timeout")
    with pytest.raises(TimeoutError, match="upstream timeout"):
        await getattr(port, method)(*args, **kwargs)


@pytest.mark.parametrize("result", [{"power": 12}, [{"power": 12}]])
async def test_outlet_results_are_detached_from_facade(result):
    facade = MagicMock(spec=LiproRestFacade)
    facade.fetch_outlet_power_info = AsyncMock(return_value=result)
    normalized = await ports._BoundRestCommandPort(facade).fetch_outlet_power_info("d")
    assert normalized == result
    assert normalized is not result
    if isinstance(normalized, list):
        assert normalized[0] is not result[0]
    facade.fetch_outlet_power_info.assert_awaited_once_with("d")
