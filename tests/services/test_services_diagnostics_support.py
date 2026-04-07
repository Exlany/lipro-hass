"""Local support helpers for topicized services.diagnostics suites."""

from __future__ import annotations

from typing import Any
from unittest.mock import AsyncMock, MagicMock


def _developer_feedback_report_fixture() -> dict[str, object]:
    return {
        "name": "Bedroom Gateway",
        "iotName": "lipro_gateway",
        "deviceName": "Bedroom Gateway Alias",
        "roomName": "Master Bedroom",
        "productName": "Evening Scene",
        "panel_capability_snapshot": {
            "panels": [
                {
                    "name": "Wall Panel",
                    "iot_name": "21JD",
                    "panel_info": [{"keyName": "Bedside"}],
                }
            ]
        },
        "ir_remote_inventory_snapshot": {
            "gateways": [
                {
                    "name": "Main Gateway",
                    "rc_list": [
                        {
                            "name": "Fan Light Remote",
                            "address": "masked-remote-address",
                        }
                    ],
                }
            ],
            "ir_remote_devices": [
                {"name": "TV Remote", "gateway_device_id": "masked-gateway-id"}
            ],
        },
    }


def _attach_auth_service(coordinator: MagicMock) -> MagicMock:
    coordinator.auth_service = MagicMock(
        async_ensure_authenticated=AsyncMock(),
        async_trigger_reauth=AsyncMock(),
    )
    return coordinator


def _build_city_coordinator(
    behavior: dict[str, Any] | Exception,
) -> MagicMock:
    """Create a coordinator mock for get_city capability."""
    coordinator = _attach_auth_service(MagicMock())
    coordinator.protocol_service.async_get_city = AsyncMock()
    if isinstance(behavior, Exception):
        coordinator.protocol_service.async_get_city.side_effect = behavior
    else:
        coordinator.protocol_service.async_get_city.return_value = behavior
    return coordinator


def _build_query_user_cloud_coordinator(
    behavior: dict[str, Any] | Exception,
) -> MagicMock:
    """Create a coordinator mock for query_user_cloud capability."""
    coordinator = _attach_auth_service(MagicMock())
    coordinator.protocol_service.async_query_user_cloud = AsyncMock()
    if isinstance(behavior, Exception):
        coordinator.protocol_service.async_query_user_cloud.side_effect = behavior
    else:
        coordinator.protocol_service.async_query_user_cloud.return_value = behavior
    return coordinator
