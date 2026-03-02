"""Command confirmation tracking for coordinator reconciliation.

This module encapsulates the pending-expectation and adaptive latency learning
used to reconcile command pushes with eventual device state updates.
"""

from __future__ import annotations

from dataclasses import dataclass
from time import monotonic
from typing import Any

from .command_expectation import PendingCommandExpectation
from .command_result import compute_adaptive_post_refresh_delay


@dataclass(slots=True)
class CommandConfirmationTracker:
    """Track per-device pending expectations and learned confirmation latency."""

    default_post_command_refresh_delay_seconds: float
    min_post_command_refresh_delay_seconds: float
    max_post_command_refresh_delay_seconds: float
    state_latency_margin_seconds: float
    state_latency_ewma_alpha: float
    state_confirm_timeout_seconds: float

    def filter_pending_command_mismatches(
        self,
        *,
        pending_expectations: dict[str, PendingCommandExpectation],
        device_serial: str,
        properties: dict[str, Any],
    ) -> tuple[dict[str, Any], set[str]]:
        """Filter stale mismatched values while waiting for confirmation.

        Returns a tuple of (filtered_properties, blocked_keys). When nothing is
        blocked, blocked_keys will be empty.
        """
        pending = pending_expectations.get(device_serial)
        if not pending:
            return properties, set()

        now = monotonic()
        if pending.is_expired(now, self.state_confirm_timeout_seconds):
            pending_expectations.pop(device_serial, None)
            return properties, set()

        blocked_keys = pending.stale_keys(properties)
        if not blocked_keys:
            return properties, set()

        filtered = {k: v for k, v in properties.items() if k not in blocked_keys}
        return filtered, blocked_keys

    def track_command_expectation(
        self,
        *,
        pending_expectations: dict[str, PendingCommandExpectation],
        device_serial: str,
        command: str,
        properties: list[dict[str, str]] | None,
    ) -> None:
        """Track expected CHANGE_STATE values for adaptive confirmation."""
        if command.upper() != "CHANGE_STATE" or not properties:
            pending_expectations.pop(device_serial, None)
            return

        expected: dict[str, str] = {}
        for item in properties:
            key = item.get("key")
            value = item.get("value")
            if isinstance(key, str):
                expected[key] = str(value)

        if not expected:
            pending_expectations.pop(device_serial, None)
            return

        pending_expectations[device_serial] = PendingCommandExpectation(
            sent_at=monotonic(),
            expected=expected,
        )

    def update_state_latency(
        self,
        *,
        device_state_latency_seconds: dict[str, float],
        device_serial: str,
        observed_latency: float,
    ) -> None:
        """Update per-device command->state latency EWMA."""
        bounded = max(
            self.min_post_command_refresh_delay_seconds,
            min(self.max_post_command_refresh_delay_seconds, observed_latency),
        )
        previous = device_state_latency_seconds.get(device_serial)
        if previous is None:
            device_state_latency_seconds[device_serial] = bounded
            return

        alpha = self.state_latency_ewma_alpha
        device_state_latency_seconds[device_serial] = (
            previous * (1 - alpha) + bounded * alpha
        )

    def observe_command_confirmation(
        self,
        *,
        pending_expectations: dict[str, PendingCommandExpectation],
        device_state_latency_seconds: dict[str, float],
        device_serial: str,
        properties: dict[str, Any],
    ) -> float | None:
        """Observe property updates and confirm pending expectations.

        Returns the observed latency (seconds) when confirmation happens, else None.
        """
        pending = pending_expectations.get(device_serial)
        if not pending:
            return None

        now = monotonic()
        if pending.is_expired(now, self.state_confirm_timeout_seconds):
            pending_expectations.pop(device_serial, None)
            return None

        if not pending.observe(properties):
            return None

        latency = now - pending.sent_at
        self.update_state_latency(
            device_state_latency_seconds=device_state_latency_seconds,
            device_serial=device_serial,
            observed_latency=latency,
        )
        pending_expectations.pop(device_serial, None)
        return latency

    def get_adaptive_post_refresh_delay(
        self,
        *,
        device_state_latency_seconds: dict[str, float],
        device_serial: str | None,
    ) -> float:
        """Get adaptive delayed-refresh seconds for a device."""
        learned_latency = (
            device_state_latency_seconds.get(device_serial)
            if isinstance(device_serial, str)
            else None
        )
        return compute_adaptive_post_refresh_delay(
            learned_latency_seconds=learned_latency,
            default_delay_seconds=self.default_post_command_refresh_delay_seconds,
            latency_margin_seconds=self.state_latency_margin_seconds,
            min_delay_seconds=self.min_post_command_refresh_delay_seconds,
            max_delay_seconds=self.max_post_command_refresh_delay_seconds,
        )

    @staticmethod
    def prune_runtime_state_for_devices(
        *,
        pending_expectations: dict[str, PendingCommandExpectation],
        device_state_latency_seconds: dict[str, float],
        active_serials: set[str],
    ) -> None:
        """Prune per-device runtime caches for removed devices."""
        stale_pending = set(pending_expectations) - active_serials
        for serial in stale_pending:
            pending_expectations.pop(serial, None)

        stale_latency = set(device_state_latency_seconds) - active_serials
        for serial in stale_latency:
            device_state_latency_seconds.pop(serial, None)

