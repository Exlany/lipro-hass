"""Command sending/verification for the coordinator."""

from __future__ import annotations

import logging
from time import monotonic
from typing import Any, Final

from ...const.properties import (
    PROP_BRIGHTNESS,
    PROP_FAN_GEAR,
    PROP_POSITION,
    PROP_TEMPERATURE,
)
from ..api import LiproApiError, LiproAuthError, LiproRefreshTokenExpiredError
from ..command.dispatch import execute_command_plan_with_trace
from ..command.result import (
    apply_missing_msg_sn_failure,
    apply_push_failure,
    apply_successful_command_trace,
    build_command_api_error_failure,
    build_progressive_retry_delays,
    classify_command_result_payload,
    extract_msg_sn,
    is_command_push_failed,
    poll_command_result_state,
    query_command_result_once,
    resolve_polled_command_result,
    should_skip_immediate_post_refresh,
)
from ..command.trace import update_trace_with_exception
from ..device import LiproDevice
from ..utils.log_safety import safe_error_placeholder
from ..utils.redaction import redact_identifier as _redact_identifier
from .command_confirm import _POST_COMMAND_REFRESH_DELAY_SECONDS, _CommandConfirmMixin

_LOGGER = logging.getLogger(__name__)

# Optional command-result verification tuning.
# Use the existing adaptive confirmation latency as retry budget, then fan out
# retries with bounded exponential backoff to avoid hammering the endpoint.
_COMMAND_RESULT_VERIFY_MAX_ATTEMPTS: Final[int] = 6
_COMMAND_RESULT_VERIFY_BASE_DELAY_SECONDS: Final[float] = 0.35

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

        _LOGGER.warning(
            "Failed to send command to %s (%s)",
            device.name,
            safe_error_placeholder(err),
        )
        return False

    @property
    def last_command_failure(self) -> dict[str, Any] | None:
        """Return the latest command failure summary for service-layer mapping."""
        if self._last_command_failure is None:
            return None
        return dict(self._last_command_failure)

    async def async_ensure_authenticated(self) -> None:
        """Ensure coordinator authentication before sending commands."""
        await self._async_ensure_authenticated()

    async def async_handle_command_api_error(
        self,
        *,
        device: LiproDevice,
        trace: dict[str, Any],
        route: str,
        err: LiproApiError,
    ) -> bool:
        """Bridge API-error handling for the command service."""
        return await self._handle_command_api_error(
            device=device,
            trace=trace,
            route=route,
            err=err,
        )

    async def async_execute_command_flow(
        self,
        *,
        device: LiproDevice,
        command: str,
        properties: list[dict[str, str]] | None,
        fallback_device_id: str | None,
        trace: dict[str, Any],
    ) -> tuple[bool, str]:
        """Bridge command execution flow for the command service."""
        return await self._execute_command_flow(
            device=device,
            command=command,
            properties=properties,
            fallback_device_id=fallback_device_id,
            trace=trace,
        )

    async def _verify_command_result_delivery(
        self,
        *,
        device: LiproDevice,
        msg_sn: str,
        route: str,
        trace: dict[str, Any],
    ) -> bool:
        """Poll query_command_result within a bounded confirmation budget."""
        verify_started_at = monotonic()
        safe_device_serial = _redact_identifier(device.serial) or "***"
        safe_msg_sn = _redact_identifier(msg_sn) or "***"

        adaptive_delay_seconds = max(
            _POST_COMMAND_REFRESH_DELAY_SECONDS,
            self._get_adaptive_post_refresh_delay(device.serial),
        )
        retry_delays_seconds = build_progressive_retry_delays(
            base_delay_seconds=_COMMAND_RESULT_VERIFY_BASE_DELAY_SECONDS,
            time_budget_seconds=adaptive_delay_seconds,
            max_attempts=_COMMAND_RESULT_VERIFY_MAX_ATTEMPTS,
        )
        attempt_limit = len(retry_delays_seconds) + 1

        async def _query_once(attempt: int) -> dict[str, Any] | None:
            return await query_command_result_once(
                query_command_result=self.client.query_command_result,
                lipro_api_error=LiproApiError,
                device_name=device.name,
                device_serial=device.serial,
                device_type_hex=device.device_type_hex,
                msg_sn=msg_sn,
                attempt=attempt,
                attempt_limit=attempt_limit,
                logger=_LOGGER,
            )

        def _log_attempt(attempt: int, state: str) -> None:
            _LOGGER.debug(
                "query_command_result attempt=%s/%s (device=%s, msgSn=%s, route=%s, budget=%.2fs) state=%s",
                attempt,
                attempt_limit,
                safe_device_serial,
                safe_msg_sn,
                route,
                adaptive_delay_seconds,
                state,
            )

        state, attempt, last_payload = await poll_command_result_state(
            query_once=_query_once,
            classify_payload=classify_command_result_payload,
            retry_delays_seconds=retry_delays_seconds,
            on_attempt=_log_attempt,
        )

        verified, failure = resolve_polled_command_result(
            state=state,
            trace=trace,
            route=route,
            msg_sn=msg_sn,
            device_serial=device.serial,
            attempt=attempt,
            attempt_limit=attempt_limit,
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
        """Run bounded command-result polling when enabled."""
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

        safe_msg_sn = _redact_identifier(msg_sn) or "***"
        failure_reason = None
        if isinstance(self._last_command_failure, dict):
            failure_reason = self._last_command_failure.get("reason")
        _LOGGER.warning(
            "Command delivery not confirmed (command=%s, device=%s, route=%s, msgSn=%s, reason=%s)",
            command,
            device.name,
            route,
            safe_msg_sn,
            failure_reason,
        )
        return False

    async def async_send_command(
        self,
        device: LiproDevice,
        command: str,
        properties: list[dict[str, str]] | None = None,
        fallback_device_id: str | None = None,
    ) -> bool:
        """Send one command through the injected command service."""
        return await self.command_service.async_send_command(
            device,
            command,
            properties,
            fallback_device_id,
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
    "_COMMAND_RESULT_VERIFY_BASE_DELAY_SECONDS",
    "_COMMAND_RESULT_VERIFY_MAX_ATTEMPTS",
    "_MAX_DEVELOPER_COMMAND_TRACES",
    "_SLIDER_LIKE_PROPERTIES",
    "_CommandSendMixin",
]
