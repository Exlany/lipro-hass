"""Command sender for executing commands via the protocol façade."""

from __future__ import annotations

import asyncio
from collections.abc import Callable
from dataclasses import dataclass
import logging
from typing import TYPE_CHECKING

from ....api import LiproApiError, LiproAuthError, LiproConnectionError
from ....command.dispatch import (
    execute_command_dispatch,
    resolve_command_plan_with_trace,
)
from ....command.result import (
    COMMAND_RESULT_STATE_CONFIRMED,
    COMMAND_RESULT_STATE_FAILED,
    COMMAND_RESULT_STATE_PENDING,
    COMMAND_VERIFICATION_RESULT_CONFIRMED,
    COMMAND_VERIFICATION_RESULT_FAILED,
    COMMAND_VERIFICATION_RESULT_TIMEOUT,
    CommandResultPayload,
    CommandResultState,
    classify_command_result_payload,
    query_command_result_once,
)
from ....command.trace import update_trace_with_response
from ....utils.log_safety import safe_error_placeholder
from ....utils.redaction import redact_identifier as _redact_identifier
from ...types import CommandTrace

if TYPE_CHECKING:
    from ....device import LiproDevice
    from ....protocol import LiproProtocolFacade

_LOGGER = logging.getLogger(__name__)
_NON_FATAL_VERIFICATION_QUERY_EXCEPTIONS = (
    LiproConnectionError,
    OSError,
    RuntimeError,
    TimeoutError,
    ValueError,
)


@dataclass(slots=True)
class CommandDispatchApiError(Exception):
    """Protocol API error annotated with the resolved command route."""

    route: str
    error: LiproApiError


class CommandSender:
    """Send commands to devices via the protocol façade with verification support."""

    def __init__(
        self,
        *,
        protocol: LiproProtocolFacade,
        redact_identifier: Callable[[str | None], str | None] = _redact_identifier,
    ) -> None:
        """Initialize command sender."""
        self._protocol = protocol
        self._redact_identifier = redact_identifier

    async def send_command(
        self,
        *,
        device: LiproDevice,
        command: str,
        properties: list[dict[str, str]] | None,
        fallback_device_id: str | None,
        trace: CommandTrace,
    ) -> tuple[CommandResultPayload, str]:
        """Send command to device and return result with route.

        Returns:
            Tuple of (api_result, route_name)
        """
        plan = resolve_command_plan_with_trace(
            device=device,
            command=command,
            properties=properties,
            fallback_device_id=fallback_device_id,
            trace=trace,
            redact_identifier=self._redact_identifier,
        )
        try:
            result, route = await execute_command_dispatch(
                self._protocol,
                device=device,
                plan=plan,
            )
        except LiproApiError as err:
            raise CommandDispatchApiError(route=plan.route, error=err) from err
        update_trace_with_response(trace, result)
        return result, route

    def _record_verification_terminal_state(
        self,
        *,
        trace: CommandTrace,
        attempt: int,
        verification_result: str,
        classification: CommandResultState | None = None,
    ) -> None:
        """Record one terminal command-verification state into the trace."""
        trace["verification_attempts"] = attempt
        trace["verification_result"] = verification_result
        if classification is not None:
            trace["verification_classification"] = classification

    async def _query_verification_result(
        self,
        *,
        msg_sn: str,
        attempt: int,
        attempt_limit: int,
        device: LiproDevice,
    ) -> CommandResultPayload | None:
        """Query one command-result attempt while downgrading non-fatal transport errors."""
        try:
            return await query_command_result_once(
                query_command_result=self._protocol.query_command_result,
                lipro_api_error=LiproApiError,
                device_name=device.name,
                device_serial=device.serial,
                device_type_hex=getattr(device, "device_type_hex", "unknown"),
                msg_sn=msg_sn,
                attempt=attempt,
                attempt_limit=attempt_limit,
                logger=_LOGGER,
                should_reraise=lambda err: isinstance(err, LiproAuthError),
            )
        except _NON_FATAL_VERIFICATION_QUERY_EXCEPTIONS as err:
            _LOGGER.debug(
                "Command result query attempt %d failed: %s",
                attempt,
                safe_error_placeholder(err),
            )
            return None

    def _resolve_verification_outcome(
        self,
        *,
        result: CommandResultPayload,
        attempt: int,
        trace: CommandTrace,
    ) -> tuple[bool, CommandResultState | None] | None:
        """Return one terminal verification outcome when polling result is decisive."""
        classification = classify_command_result_payload(result)
        if classification == COMMAND_RESULT_STATE_PENDING:
            return None
        if classification == COMMAND_RESULT_STATE_CONFIRMED:
            self._record_verification_terminal_state(
                trace=trace,
                attempt=attempt,
                verification_result=COMMAND_VERIFICATION_RESULT_CONFIRMED,
            )
            return True, classification
        if classification == COMMAND_RESULT_STATE_FAILED:
            self._record_verification_terminal_state(
                trace=trace,
                attempt=attempt,
                verification_result=COMMAND_VERIFICATION_RESULT_FAILED,
                classification=classification,
            )
            return False, classification
        return None

    async def verify_command_delivery(
        self,
        *,
        msg_sn: str,
        retry_delays: list[float],
        trace: CommandTrace,
        device: LiproDevice,
    ) -> tuple[bool, CommandResultState | None]:
        """Verify command delivery via result polling with retries."""
        attempt = 0
        attempt_limit = len(retry_delays) + 1
        for delay in retry_delays:
            await asyncio.sleep(delay)
            attempt += 1
            result = await self._query_verification_result(
                msg_sn=msg_sn,
                attempt=attempt,
                attempt_limit=attempt_limit,
                device=device,
            )
            if result is None:
                continue
            outcome = self._resolve_verification_outcome(
                result=result,
                attempt=attempt,
                trace=trace,
            )
            if outcome is not None:
                return outcome

        self._record_verification_terminal_state(
            trace=trace,
            attempt=attempt,
            verification_result=COMMAND_VERIFICATION_RESULT_TIMEOUT,
        )
        return False, None


__all__ = ["CommandDispatchApiError", "CommandSender"]
