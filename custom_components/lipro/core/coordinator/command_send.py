"""Command sending/verification for the coordinator."""

from __future__ import annotations

import logging
from time import monotonic
from typing import Any, Final

from ...const import PROP_BRIGHTNESS, PROP_FAN_GEAR, PROP_POSITION, PROP_TEMPERATURE
from ..api import LiproApiError, LiproAuthError, LiproRefreshTokenExpiredError
from ..command.dispatch import execute_command_plan_with_trace
from ..command.result import (
    apply_missing_msg_sn_failure,
    apply_push_failure,
    apply_successful_command_trace,
    build_command_api_error_failure,
    classify_command_result_payload,
    extract_msg_sn,
    is_command_push_failed,
    poll_command_result_state,
    query_command_result_once,
    resolve_polled_command_result,
    should_skip_immediate_post_refresh,
)
from ..command.trace import build_command_trace, update_trace_with_exception
from ..device import LiproDevice
from ..utils.redaction import redact_identifier as _redact_identifier
from .command_confirm import _CommandConfirmMixin

_LOGGER = logging.getLogger(__name__)

# Optional command-result verification tuning.
_COMMAND_RESULT_VERIFY_ATTEMPTS: Final[int] = 3
_COMMAND_RESULT_VERIFY_INTERVAL_SECONDS: Final[float] = 0.35

# Keep the latest command traces in memory for debug diagnostics.
_MAX_DEVELOPER_COMMAND_TRACES: Final[int] = 100

_SLIDER_LIKE_PROPERTIES: Final[frozenset[str]] = frozenset(
    {
        PROP_BRIGHTNESS,
        PROP_TEMPERATURE,
        PROP_FAN_GEAR,
        PROP_POSITION,
    }
)


class _CommandSendMixin(_CommandConfirmMixin):
    """Command send/verification mixin."""

    def _record_command_trace(self, trace: dict[str, Any]) -> None:
        """Record one command trace when debug mode is enabled."""
        if not self._debug_mode:
            return

        self._command_traces.append(trace)

    def _finalize_successful_command(
        self,
        *,
        device: LiproDevice,
        command: str,
        properties: list[dict[str, str]] | None,
        route: str,
        trace: dict[str, Any],
    ) -> None:
        """Finalize post-send refresh strategy and success trace fields."""
        skip_immediate_refresh = should_skip_immediate_post_refresh(
            command=command,
            properties=properties,
            slider_like_properties=_SLIDER_LIKE_PROPERTIES,
        )
        self._track_command_expectation(device.serial, command, properties)
        if not device.is_group:
            self._connect_status_priority_ids.add(
                self._normalize_device_key(device.serial)
            )
        self._force_connect_status_refresh = True
        adaptive_delay = self._get_adaptive_post_refresh_delay(device.serial)
        self._schedule_post_command_refresh(
            skip_immediate=skip_immediate_refresh,
            device_serial=device.serial,
        )
        apply_successful_command_trace(
            trace=trace,
            route=route,
            adaptive_delay_seconds=adaptive_delay,
            skip_immediate_refresh=skip_immediate_refresh,
        )
        self._record_command_trace(trace)
        self._last_command_failure = None

    async def _handle_command_api_error(
        self,
        *,
        device: LiproDevice,
        trace: dict[str, Any],
        route: str,
        err: LiproApiError,
    ) -> bool:
        """Handle command-send API errors with consistent trace and reauth flows."""
        self._last_command_failure = build_command_api_error_failure(
            trace=trace,
            route=route,
            device_serial=device.serial,
            err=err,
            update_trace_with_exception=update_trace_with_exception,
        )
        self._record_command_trace(trace)
        if isinstance(err, LiproRefreshTokenExpiredError):
            _LOGGER.warning(
                "Refresh token expired while sending command to %s",
                device.name,
            )
            await self._trigger_reauth("auth_expired")
            return False
        if isinstance(err, LiproAuthError):
            _LOGGER.warning(
                "Auth error sending command to %s, triggering reauth",
                device.name,
            )
            await self._trigger_reauth("auth_error")
            return False

        _LOGGER.warning("Failed to send command to %s: %s", device.name, err)
        return False

    @property
    def last_command_failure(self) -> dict[str, Any] | None:
        """Return the latest command failure summary for service-layer mapping."""
        if self._last_command_failure is None:
            return None
        return dict(self._last_command_failure)

    async def _verify_command_result_delivery(
        self,
        *,
        device: LiproDevice,
        msg_sn: str,
        route: str,
        trace: dict[str, Any],
    ) -> bool:
        """Verify command delivery result by polling query_command_result."""
        verify_started_at = monotonic()

        async def _query_once(attempt: int) -> dict[str, Any] | None:
            return await query_command_result_once(
                query_command_result=self.client.query_command_result,
                lipro_api_error=LiproApiError,
                device_name=device.name,
                device_serial=device.serial,
                device_type_hex=device.device_type_hex,
                msg_sn=msg_sn,
                attempt=attempt,
                attempt_limit=_COMMAND_RESULT_VERIFY_ATTEMPTS,
                logger=_LOGGER,
            )

        def _log_attempt(attempt: int, state: str) -> None:
            _LOGGER.debug(
                "query_command_result attempt=%s/%s (device=%s, msgSn=%s, route=%s) state=%s",
                attempt,
                _COMMAND_RESULT_VERIFY_ATTEMPTS,
                device.serial,
                msg_sn,
                route,
                state,
            )

        state, attempt, last_payload = await poll_command_result_state(
            query_once=_query_once,
            classify_payload=classify_command_result_payload,
            attempt_limit=_COMMAND_RESULT_VERIFY_ATTEMPTS,
            interval_seconds=_COMMAND_RESULT_VERIFY_INTERVAL_SECONDS,
            on_attempt=_log_attempt,
        )

        verified, failure = resolve_polled_command_result(
            state=state,
            trace=trace,
            route=route,
            msg_sn=msg_sn,
            device_serial=device.serial,
            attempt=attempt,
            attempt_limit=_COMMAND_RESULT_VERIFY_ATTEMPTS,
            last_payload=last_payload,
            elapsed_seconds=monotonic() - verify_started_at,
            logger=_LOGGER,
        )
        if verified:
            return True

        self._last_command_failure = failure
        self._record_command_trace(trace)
        return False

    async def _verify_delivery_if_enabled(
        self,
        *,
        trace: dict[str, Any],
        route: str,
        command: str,
        device: LiproDevice,
        result: Any,
    ) -> bool:
        """Run command-result verification when enabled."""
        if not self._command_result_verify:
            return True

        msg_sn = extract_msg_sn(result)
        if msg_sn is None:
            self._last_command_failure = apply_missing_msg_sn_failure(
                trace=trace,
                route=route,
                command=command,
                device_name=device.name,
                device_serial=device.serial,
                logger=_LOGGER,
            )
            self._record_command_trace(trace)
            return False

        verified = await self._verify_command_result_delivery(
            device=device,
            msg_sn=msg_sn,
            route=route,
            trace=trace,
        )
        if verified:
            return True

        _LOGGER.warning(
            "Command delivery not confirmed (command=%s, device=%s, route=%s, msgSn=%s, failure=%s)",
            command,
            device.name,
            route,
            msg_sn,
            self._last_command_failure,
        )
        return False

    async def async_send_command(
        self,
        device: LiproDevice,
        command: str,
        properties: list[dict[str, str]] | None = None,
        fallback_device_id: str | None = None,
    ) -> bool:
        """Send a command to a device."""
        trace = build_command_trace(
            device=device,
            command=command,
            properties=properties,
            fallback_device_id=fallback_device_id,
            redact_identifier=_redact_identifier,
        )
        route = "device_direct"

        try:
            await self._async_ensure_authenticated()

            success, route = await self._execute_command_flow(
                device=device,
                command=command,
                properties=properties,
                fallback_device_id=fallback_device_id,
                trace=trace,
            )
            return success

        except LiproApiError as err:
            return await self._handle_command_api_error(
                device=device,
                trace=trace,
                route=route,
                err=err,
            )

    async def _execute_command_flow(
        self,
        *,
        device: LiproDevice,
        command: str,
        properties: list[dict[str, str]] | None,
        fallback_device_id: str | None,
        trace: dict[str, Any],
    ) -> tuple[bool, str]:
        """Execute command dispatch/verification/finalization flow."""
        plan, result, route = await execute_command_plan_with_trace(
            self.client,
            device=device,
            command=command,
            properties=properties,
            fallback_device_id=fallback_device_id,
            trace=trace,
            redact_identifier=_redact_identifier,
        )
        if is_command_push_failed(result):
            self._last_command_failure = apply_push_failure(
                trace=trace,
                route=route,
                command=command,
                device_name=device.name,
                device_serial=device.serial,
                logger=_LOGGER,
            )
            self._record_command_trace(trace)
            return False, route

        if not await self._verify_delivery_if_enabled(
            trace=trace,
            route=route,
            command=command,
            device=device,
            result=result,
        ):
            return False, route

        self._finalize_successful_command(
            device=device,
            command=plan.command,
            properties=plan.properties,
            route=route,
            trace=trace,
        )
        return True, route


__all__ = [
    "_COMMAND_RESULT_VERIFY_ATTEMPTS",
    "_COMMAND_RESULT_VERIFY_INTERVAL_SECONDS",
    "_MAX_DEVELOPER_COMMAND_TRACES",
    "_SLIDER_LIKE_PROPERTIES",
    "_CommandSendMixin",
]
