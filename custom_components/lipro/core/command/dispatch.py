"""Command routing and dispatch helpers for the coordinator."""

from __future__ import annotations

from collections.abc import Callable, Mapping
from dataclasses import dataclass
from enum import StrEnum
import logging
from typing import TYPE_CHECKING

from ...const.device_types import DEVICE_TYPE_PANEL
from ..api import LiproApiError
from ..device import LiproDevice
from ..utils.identifiers import is_valid_iot_device_id
from .result import CommandResultPayload, is_command_push_failed
from .trace import update_trace_with_resolved_request, update_trace_with_response

if TYPE_CHECKING:
    from ..protocol import LiproProtocolFacade

_LOGGER = logging.getLogger(__name__)

type RedactIdentifier = Callable[[str | None], str | None]
type CommandTracePayload = dict[str, object]


def _as_command_result_payload(result: Mapping[str, object]) -> CommandResultPayload:
    """Widen one JSON-like mapping into the canonical command-result payload alias."""
    return dict(result)


class CommandRoute(StrEnum):
    """Command routing strategies."""

    DEVICE_DIRECT = "device_direct"
    PANEL_DIRECT = "panel_direct_via_group_endpoint"
    GROUP_DIRECT = "group_direct"
    GROUP_ERROR_FALLBACK = "group_error_fallback_member"
    GROUP_PUSH_FAIL_FALLBACK = "group_push_fail_fallback_member"


@dataclass(frozen=True)
class CommandDispatchPlan:
    """Resolved command route and payload for one send operation."""

    route: str
    command: str
    properties: list[dict[str, str]] | None
    member_fallback_id: str | None


def normalize_group_power_command(
    command: str,
    properties: list[dict[str, str]] | None,
) -> tuple[str, list[dict[str, str]] | None]:
    """Normalize group power CHANGE_STATE to POWER_ON/OFF for backend compatibility."""
    if command.upper() != "CHANGE_STATE" or not properties:
        return command, properties

    power_value: str | None = None
    has_non_power_properties = False
    for prop in properties:
        key = prop.get("key")
        if not isinstance(key, str):
            has_non_power_properties = True
            continue
        if key != "powerState":
            has_non_power_properties = True
            continue
        value = prop.get("value")
        if isinstance(value, str):
            normalized = value.strip().lower()
            if normalized in {"1", "true", "on"}:
                power_value = "1"
            elif normalized in {"0", "false", "off"}:
                power_value = "0"

    # Only collapse into POWER_ON/OFF when the payload is power-only.
    # Mixed updates (e.g., power + brightness/colorTemp) must preserve
    # CHANGE_STATE properties to avoid dropping non-power settings.
    if has_non_power_properties:
        return command, properties

    if power_value == "1":
        return "POWER_ON", None
    if power_value == "0":
        return "POWER_OFF", None
    return command, properties


def resolve_group_fallback_member_id(
    device: LiproDevice,
    fallback_device_id: str | None,
) -> str | None:
    """Resolve fallback target for single-member mesh groups only."""
    if not device.is_group or not isinstance(fallback_device_id, str):
        return None

    candidate = fallback_device_id.strip().lower()
    if (
        not candidate
        or candidate == device.serial.lower()
        or not is_valid_iot_device_id(candidate)
    ):
        return None

    member_ids = device.mesh_group_member_ids
    if len(member_ids) != 1:
        return None

    only_member = member_ids[0]
    member_id = only_member.strip().lower()
    if not member_id or not is_valid_iot_device_id(member_id):
        return None

    if candidate != member_id:
        return None

    return candidate


def plan_command_dispatch(
    device: LiproDevice,
    command: str,
    properties: list[dict[str, str]] | None,
    fallback_device_id: str | None,
) -> CommandDispatchPlan:
    """Resolve command payload and route policy for one command call."""
    member_fallback_id = resolve_group_fallback_member_id(device, fallback_device_id)
    if not device.is_group:
        route = CommandRoute.DEVICE_DIRECT
        if (
            device.device_type_hex == DEVICE_TYPE_PANEL
            and command.upper().startswith("PANEL_")
        ):
            route = CommandRoute.PANEL_DIRECT
        return CommandDispatchPlan(
            route=route,
            command=command,
            properties=properties,
            member_fallback_id=member_fallback_id,
        )

    route = CommandRoute.GROUP_DIRECT
    if (
        isinstance(fallback_device_id, str)
        and fallback_device_id.strip()
        and fallback_device_id.strip().lower() != device.serial.lower()
        and member_fallback_id is None
    ):
        _LOGGER.debug(
            "Ignoring member fallback %s for group %s "
            "(requires single-member mesh group)",
            fallback_device_id,
            device.serial,
        )

    actual_command, actual_properties = normalize_group_power_command(
        command, properties
    )
    if actual_command != command:
        _LOGGER.debug(
            "Normalized group command %s to %s for %s",
            command,
            actual_command,
            device.serial,
        )
    return CommandDispatchPlan(
        route=route,
        command=actual_command,
        properties=actual_properties,
        member_fallback_id=member_fallback_id,
    )


async def _send_member_command(
    client: LiproProtocolFacade,
    *,
    member_id: str,
    device: LiproDevice,
    command: str,
    properties: list[dict[str, str]] | None,
) -> CommandResultPayload:
    """Send a command to a specific member device."""
    return _as_command_result_payload(
        await client.send_command(
            member_id,
            command,
            device.device_type_hex,
            properties,
            device.iot_name,
        )
    )


async def _fallback_to_member(
    client: LiproProtocolFacade,
    *,
    member_id: str,
    device: LiproDevice,
    command: str,
    properties: list[dict[str, str]] | None,
    route: CommandRoute,
    log_message: str,
    log_args: tuple[object, ...],
) -> tuple[CommandResultPayload, str]:
    """Run one fallback send to the resolved member and return updated route."""
    _LOGGER.warning(log_message, *log_args)
    result = await _send_member_command(
        client,
        member_id=member_id,
        device=device,
        command=command,
        properties=properties,
    )
    return result, route


async def _send_group_with_error_fallback(
    client: LiproProtocolFacade,
    *,
    device: LiproDevice,
    plan: CommandDispatchPlan,
) -> tuple[CommandResultPayload, str]:
    """Send group command and fallback on group API error when allowed."""
    try:
        result = _as_command_result_payload(
            await client.send_group_command(
                device.serial,
                plan.command,
                device.device_type_hex,
                plan.properties,
                device.iot_name,
            )
        )
        return result, plan.route
    except LiproApiError as err:
        if not plan.member_fallback_id:
            raise
        return await _fallback_to_member(
            client,
            device=device,
            member_id=plan.member_fallback_id,
            command=plan.command,
            properties=plan.properties,
            route=CommandRoute.GROUP_ERROR_FALLBACK,
            log_message="Group command %s to %s failed (%s), fallback to member %s",
            log_args=(
                plan.command,
                device.serial,
                err,
                plan.member_fallback_id,
            ),
        )


def _should_fallback_after_group_result(
    *,
    member_fallback_id: str | None,
    result: object,
) -> bool:
    """Return whether group push result should fallback to member command."""
    return member_fallback_id is not None and is_command_push_failed(result)


async def _execute_panel_command(
    client: LiproProtocolFacade,
    *,
    device: LiproDevice,
    plan: CommandDispatchPlan,
) -> tuple[CommandResultPayload, str]:
    """Execute panel command via group endpoint."""
    result = _as_command_result_payload(
        await client.send_group_command(
            device.serial,
            plan.command,
            device.device_type_hex,
            plan.properties,
            device.iot_name,
        )
    )
    return result, plan.route


async def _execute_device_command(
    client: LiproProtocolFacade,
    *,
    device: LiproDevice,
    plan: CommandDispatchPlan,
) -> tuple[CommandResultPayload, str]:
    """Execute direct device command."""
    result = await _send_member_command(
        client,
        member_id=device.serial,
        device=device,
        command=plan.command,
        properties=plan.properties,
    )
    return result, plan.route


async def _execute_group_command(
    client: LiproProtocolFacade,
    *,
    device: LiproDevice,
    plan: CommandDispatchPlan,
) -> tuple[CommandResultPayload, str]:
    """Execute group command with fallback logic."""
    result, route = await _send_group_with_error_fallback(
        client,
        device=device,
        plan=plan,
    )
    member_fallback_id = plan.member_fallback_id
    if member_fallback_id is not None and _should_fallback_after_group_result(
        member_fallback_id=member_fallback_id,
        result=result,
    ):
        result, route = await _fallback_to_member(
            client,
            device=device,
            member_id=member_fallback_id,
            command=plan.command,
            properties=plan.properties,
            route=CommandRoute.GROUP_PUSH_FAIL_FALLBACK,
            log_message=(
                "Group command %s to %s returned pushSuccess=false, "
                "fallback to member %s"
            ),
            log_args=(
                plan.command,
                device.serial,
                member_fallback_id,
            ),
        )

    return result, route


async def execute_command_dispatch(
    client: LiproProtocolFacade,
    *,
    device: LiproDevice,
    plan: CommandDispatchPlan,
) -> tuple[CommandResultPayload, str]:
    """Execute direct/group command send with fallback routing."""
    if plan.route == CommandRoute.PANEL_DIRECT:
        return await _execute_panel_command(client, device=device, plan=plan)

    if not device.is_group:
        return await _execute_device_command(client, device=device, plan=plan)

    return await _execute_group_command(client, device=device, plan=plan)


def resolve_command_plan_with_trace(
    *,
    device: LiproDevice,
    command: str,
    properties: list[dict[str, str]] | None,
    fallback_device_id: str | None,
    trace: CommandTracePayload,
    redact_identifier: RedactIdentifier,
) -> CommandDispatchPlan:
    """Resolve one dispatch plan and append resolved request fields to trace."""
    plan: CommandDispatchPlan = plan_command_dispatch(
        device,
        command,
        properties,
        fallback_device_id,
    )
    update_trace_with_resolved_request(
        trace,
        command=plan.command,
        properties=plan.properties,
        fallback_device_id=plan.member_fallback_id,
        redact_identifier=redact_identifier,
    )
    return plan


async def execute_command_plan_with_trace(
    client: LiproProtocolFacade,
    *,
    device: LiproDevice,
    command: str,
    properties: list[dict[str, str]] | None,
    fallback_device_id: str | None,
    trace: CommandTracePayload,
    redact_identifier: RedactIdentifier,
) -> tuple[CommandDispatchPlan, CommandResultPayload, str]:
    """Plan command dispatch and append resolved request/response trace fields.

    Returns:
        Tuple of (dispatch_plan, api_result, route_name)
    """
    plan = resolve_command_plan_with_trace(
        device=device,
        command=command,
        properties=properties,
        fallback_device_id=fallback_device_id,
        trace=trace,
        redact_identifier=redact_identifier,
    )
    route = plan.route
    result, route = await execute_command_dispatch(
        client,
        device=device,
        plan=plan,
    )
    update_trace_with_response(trace, result)
    return plan, result, route
