"""Command sender for executing commands via API."""

from __future__ import annotations

import asyncio
import logging
from typing import TYPE_CHECKING, Any

from ....command.dispatch import execute_command_plan_with_trace
from ....command.result import (
    classify_command_result_payload,
    query_command_result_once,
)
from ....utils.log_safety import safe_error_placeholder
from ....utils.redaction import redact_identifier as _redact_identifier

if TYPE_CHECKING:
    from ....api import LiproClient
    from ....device import LiproDevice

_LOGGER = logging.getLogger(__name__)


class CommandSender:
    """Send commands to devices via API with verification support."""

    def __init__(
        self, *, client: LiproClient, redact_identifier: Any = _redact_identifier
    ) -> None:
        """Initialize command sender."""
        self._client = client
        self._redact_identifier = redact_identifier

    async def send_command(
        self,
        *,
        device: LiproDevice,
        command: str,
        properties: list[dict[str, str]] | None,
        fallback_device_id: str | None,
        trace: dict[str, Any],
    ) -> tuple[Any, str]:
        """Send command to device and return result with route."""
        _plan, result, route = await execute_command_plan_with_trace(
            self._client,
            device=device,
            command=command,
            properties=properties,
            fallback_device_id=fallback_device_id,
            trace=trace,
            redact_identifier=self._redact_identifier,
        )
        return result, route

    async def verify_command_delivery(
        self,
        *,
        msg_sn: str,
        retry_delays: list[float],
        trace: dict[str, Any],
        device: Any,
    ) -> tuple[bool, str | None]:
        """Verify command delivery via result polling with retries."""
        attempt = 0
        for delay in retry_delays:
            await asyncio.sleep(delay)
            attempt += 1

            try:
                result = await query_command_result_once(
                    query_command_result=self._client.query_command_result,
                    lipro_api_error=Exception,
                    device_name=device.name,
                    device_serial=device.serial,
                    device_type_hex=getattr(device, "device_type_hex", "unknown"),
                    msg_sn=msg_sn,
                    attempt=attempt,
                    attempt_limit=len(retry_delays) + 1,
                    logger=_LOGGER,
                )
            except Exception as err:  # noqa: BLE001 - retry on any query error
                _LOGGER.debug(
                    "Command result query attempt %d failed: %s",
                    attempt,
                    safe_error_placeholder(err),
                )
                continue

            if result is None:
                continue

            classification = classify_command_result_payload(result)

            if classification == "pending":
                continue

            if classification == "confirmed":
                trace["verification_attempts"] = attempt
                trace["verification_result"] = "confirmed"
                return True, classification

            if classification == "failed":
                trace["verification_attempts"] = attempt
                trace["verification_result"] = "failed"
                trace["verification_classification"] = classification
                return False, classification

        trace["verification_attempts"] = attempt
        trace["verification_result"] = "timeout"
        return False, None


__all__ = ["CommandSender"]
