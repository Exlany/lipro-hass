"""Command endpoint helpers for Lipro API client."""

from __future__ import annotations

from collections.abc import Callable
from typing import Any, Protocol

type MappingPayload = dict[str, Any]
type ToDeviceTypeHex = Callable[[int | str], str]


class BusyRetryRequest(Protocol):
    """Protocol for REST facade busy-retry execution callbacks."""

    async def __call__(
        self,
        path: str,
        body_data: MappingPayload,
        *,
        target_id: str,
        command: str,
    ) -> MappingPayload:
        """Execute one busy-retry protected command request."""


def build_command_request_body(
    *,
    target_id: str,
    command: str,
    device_type: int | str,
    properties: list[dict[str, str]] | None,
    iot_name: str,
    to_device_type_hex: ToDeviceTypeHex,
    group_id: str = "",
) -> MappingPayload:
    """Build a command request payload shared by device/group endpoints."""
    body: MappingPayload = {
        "command": command,
        "deviceId": target_id,
        "deviceType": to_device_type_hex(device_type),
        "iotName": iot_name,
        "properties": properties or [],
        "skuId": "",
        "hasMacRule": False,
    }
    if group_id:
        body["groupId"] = group_id
    return body


async def send_command_to_target(
    *,
    path: str,
    target_id: str,
    command: str,
    device_type: int | str,
    properties: list[dict[str, str]] | None,
    iot_name: str,
    group_id: str = "",
    to_device_type_hex: ToDeviceTypeHex,
    iot_request_with_busy_retry: BusyRetryRequest,
) -> MappingPayload:
    """Build and send command payload to a specific endpoint target."""
    body = build_command_request_body(
        target_id=target_id,
        command=command,
        device_type=device_type,
        properties=properties,
        iot_name=iot_name,
        to_device_type_hex=to_device_type_hex,
        group_id=group_id,
    )
    return await iot_request_with_busy_retry(
        path,
        body,
        target_id=target_id,
        command=command,
    )
