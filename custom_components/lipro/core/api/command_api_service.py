"""Command endpoint helpers for Lipro API client."""

from __future__ import annotations

from collections.abc import Awaitable, Callable
from typing import Any, Protocol

from .request_policy import compute_exponential_retry_wait_time

type MappingPayload = dict[str, Any]
type MappingRows = list[MappingPayload]
type ToDeviceTypeHex = Callable[[int | str], str]
type IoTRequest = Callable[[str, MappingPayload], Awaitable[Any]]
type SleepFn = Callable[[float], Awaitable[Any]]
type IsCommandBusyError = Callable[[Exception], bool]


class BusyRetryRequest(Protocol):
    """Protocol for LiproClient._iot_request_with_busy_retry-compatible call."""

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


async def iot_request_with_busy_retry(
    *,
    path: str,
    body_data: MappingPayload,
    target_id: str,
    command: str,
    attempt_limit: int,
    base_delay_seconds: float,
    iot_request: IoTRequest,
    throttle_change_state: Callable[[str, str], Awaitable[None]],
    record_change_state_success: Callable[[str, str], Awaitable[None]],
    is_command_busy_error: IsCommandBusyError,
    lipro_api_error: type[Exception],
    record_change_state_busy: Callable[[str, str], Awaitable[tuple[float, int]]],
    sleep: SleepFn,
    logger: Any,
) -> MappingPayload:
    """Send IoT command request with retry for transient busy errors."""
    for attempt in range(attempt_limit + 1):
        await throttle_change_state(target_id, command)
        try:
            result = await iot_request(path, body_data)
            await record_change_state_success(target_id, command)
            if isinstance(result, dict):
                return result
            return {}
        except lipro_api_error as err:
            if not is_command_busy_error(err):
                raise

            adaptive_interval, busy_count = await record_change_state_busy(
                target_id,
                command,
            )
            if attempt >= attempt_limit:
                raise

            wait_time = compute_exponential_retry_wait_time(
                retry_count=attempt,
                base_delay_seconds=base_delay_seconds,
            )
            logger.debug(
                (
                    "Command %s to %s busy (code=%s), retrying in %.2fs "
                    "(%d/%d), adaptive_interval=%.2fs busy_count=%d"
                ),
                command,
                target_id,
                getattr(err, "code", None),
                wait_time,
                attempt + 1,
                attempt_limit,
                adaptive_interval,
                busy_count,
            )
            await sleep(wait_time)

    # Defensive fallback, loop should return or raise earlier.
    return {}
