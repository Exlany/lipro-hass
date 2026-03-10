"""Adaptive tuning and connect-status strategy for the coordinator."""

from __future__ import annotations

import logging
from time import monotonic
from typing import Any, Final

from ...const.api import MAX_DEVICES_PER_QUERY
from ...const.config import (
    CONF_SCAN_INTERVAL,
    DEFAULT_SCAN_INTERVAL,
    MAX_SCAN_INTERVAL,
    MIN_SCAN_INTERVAL,
)
from ...const.properties import PROP_CONNECT_STATE
from .base import _CoordinatorBase
from .mqtt.polling import resolve_base_scan_interval_seconds
from .runtime.connect_status_runtime import (
    adapt_connect_status_stale_window as adapt_connect_status_stale_window_runtime,
    resolve_connect_status_query_interval_seconds as resolve_connect_status_query_interval_seconds_runtime,
)
from .runtime.state_batch_runtime import (
    normalize_state_batch_metric,
    summarize_recent_state_batch_metrics,
)
from .runtime.status_strategy import (
    ConnectStatusQueryDecision,
    compute_adaptive_state_batch_size,
    resolve_connect_status_query_candidates,
)

_LOGGER = logging.getLogger(__name__)

# Query connect status less frequently than full status polling to reduce load.
_CONNECT_STATUS_QUERY_INTERVAL_SECONDS: Final[float] = 60.0
# When MQTT is unstable/disconnected, degrade to a shorter connect-status interval.
_CONNECT_STATUS_QUERY_INTERVAL_DEGRADED_SECONDS: Final[float] = 20.0
# When MQTT recently provided connectState, skip redundant REST connect-status.
_CONNECT_STATUS_MQTT_STALE_SECONDS: Final[float] = 180.0
_CONNECT_STATUS_MQTT_STALE_MIN_SECONDS: Final[float] = 90.0
_CONNECT_STATUS_MQTT_STALE_MAX_SECONDS: Final[float] = 300.0
_CONNECT_STATUS_STALE_ADJUST_STEP_SECONDS: Final[float] = 15.0
_CONNECT_STATUS_SKIP_RATIO_WINDOW: Final[int] = 20
_CONNECT_STATUS_SKIP_RATIO_LOW: Final[float] = 0.20
_CONNECT_STATUS_SKIP_RATIO_HIGH: Final[float] = 0.85

# Runtime adaptive state-batch tuning.
_STATE_STATUS_BATCH_SIZE_MIN: Final[int] = 16
_STATE_STATUS_BATCH_SIZE_MAX: Final[int] = 64
_STATE_STATUS_BATCH_ADJUST_STEP: Final[int] = 8
_STATE_STATUS_BATCH_METRICS_WINDOW: Final[int] = 24
_STATE_STATUS_BATCH_METRICS_SAMPLE_SIZE: Final[int] = 6
_STATE_STATUS_BATCH_LATENCY_LOW_SECONDS: Final[float] = 1.2
_STATE_STATUS_BATCH_LATENCY_HIGH_SECONDS: Final[float] = 3.5


class CoordinatorAdaptiveTuningRuntime(_CoordinatorBase):
    """Coordinator runtime methods for adaptive tuning and connect-status decisions."""

    def _resolve_direct_iot_query_ids(self) -> list[str]:
        """Return individual-query IDs that are not currently mapped to groups."""
        query_ids: list[str] = []
        for device_id in self._iot_ids_to_query:
            device = self.get_device_by_id(device_id)
            if device is not None and device.is_group:
                continue
            query_ids.append(device_id)
        return query_ids

    def _build_status_metrics_snapshot(self) -> dict[str, Any]:
        """Build current runtime status-query metrics snapshot."""
        sample_count = len(self._state_batch_metrics)
        avg_batch_size: float | None = None
        avg_duration_seconds: float | None = None
        avg_fallback_depth: float | None = None
        if sample_count:
            batch_size_sum = 0
            duration_sum = 0.0
            fallback_sum = 0
            for (
                batch_size,
                duration_seconds,
                fallback_depth,
            ) in self._state_batch_metrics:
                batch_size_sum += max(0, int(batch_size))
                duration_sum += max(0.0, float(duration_seconds))
                fallback_sum += max(0, int(fallback_depth))
            avg_batch_size = batch_size_sum / sample_count
            avg_duration_seconds = duration_sum / sample_count
            avg_fallback_depth = fallback_sum / sample_count

        connect_decisions = len(self._connect_status_skip_history)
        connect_skip_ratio = (
            sum(self._connect_status_skip_history) / connect_decisions
            if connect_decisions
            else None
        )
        return {
            "state_batch_size_current": self._state_status_batch_size,
            "state_batch_size_avg": avg_batch_size,
            "state_batch_duration_avg_seconds": avg_duration_seconds,
            "state_fallback_depth_avg": avg_fallback_depth,
            "state_metrics_samples": sample_count,
            "connect_skip_ratio": connect_skip_ratio,
            "connect_skip_samples": connect_decisions,
            "connect_mqtt_stale_window_seconds": self._connect_status_mqtt_stale_seconds,
        }

    @property
    def _base_scan_interval(self) -> int:
        """Get the configured base scan interval in seconds."""
        options = self.config_entry.options if self.config_entry else None
        return resolve_base_scan_interval_seconds(
            options=options,
            option_name=CONF_SCAN_INTERVAL,
            default=DEFAULT_SCAN_INTERVAL,
            min_value=MIN_SCAN_INTERVAL,
            max_value=MAX_SCAN_INTERVAL,
            logger=_LOGGER,
        )

    def _resolve_connect_status_query_ids(self) -> list[str]:
        """Resolve the connect-status query candidate IDs for this refresh cycle."""
        if not self._iot_ids_to_query:
            return []

        iot_ids = self._resolve_direct_iot_query_ids()

        force_refresh = self._force_connect_status_refresh
        now = monotonic()
        decision = self._compute_connect_status_query_decision(
            iot_ids=iot_ids,
            force_refresh=force_refresh,
            now=now,
        )
        self._apply_connect_status_query_decision(
            decision,
            force_refresh=force_refresh,
            iot_ids=iot_ids,
        )

        return decision.query_ids

    def _compute_connect_status_query_decision(
        self,
        *,
        iot_ids: list[str],
        force_refresh: bool,
        now: float,
    ) -> ConnectStatusQueryDecision:
        """Compute connect-status query decision for the refresh tick."""
        query_interval_seconds = self._resolve_connect_status_query_interval_seconds(
            now,
        )
        return resolve_connect_status_query_candidates(
            iot_ids=iot_ids,
            force_refresh=force_refresh,
            mqtt_enabled=self._mqtt_enabled,
            mqtt_connected=self._mqtt_connected,
            last_query_time=self._last_connect_status_query_time,
            now=now,
            priority_ids=self._connect_status_priority_ids,
            mqtt_recent_time_by_id=self._last_mqtt_connect_state_at,
            stale_window_seconds=self._connect_status_mqtt_stale_seconds,
            query_interval_seconds=query_interval_seconds,
            normalize=self._normalize_device_key,
        )

    def _apply_connect_status_query_decision(
        self,
        decision: ConnectStatusQueryDecision,
        *,
        force_refresh: bool,
        iot_ids: list[str],
    ) -> None:
        """Apply connect-status decision side effects to coordinator state."""
        self._last_connect_status_query_time = decision.next_last_query_time

        # Force-refresh flag should be consumed once candidates are evaluated.
        if force_refresh:
            self._force_connect_status_refresh = False

        if decision.record_skip is not None:
            self._record_connect_status_decision(skipped=decision.record_skip)
        if decision.record_skip:
            skip_ratio = (
                sum(self._connect_status_skip_history)
                / len(self._connect_status_skip_history)
                if self._connect_status_skip_history
                else 0.0
            )
            _LOGGER.debug(
                "Skipping connect-status query: MQTT connectState is fresh for all %d devices "
                "(stale_window=%.1fs, skip_ratio=%.2f)",
                len(iot_ids),
                self._connect_status_mqtt_stale_seconds,
                skip_ratio,
            )

    def _resolve_connect_status_query_interval_seconds(self, now: float) -> float:
        """Resolve connect-status polling interval with MQTT degradation fallback."""
        return resolve_connect_status_query_interval_seconds_runtime(
            mqtt_enabled=self._mqtt_enabled,
            mqtt_connected=self._mqtt_connected,
            mqtt_disconnect_time=self._mqtt_disconnect_time,
            backoff_allows_attempt=self._mqtt_setup_backoff.should_attempt(now),
            normal_interval_seconds=_CONNECT_STATUS_QUERY_INTERVAL_SECONDS,
            degraded_interval_seconds=_CONNECT_STATUS_QUERY_INTERVAL_DEGRADED_SECONDS,
        )

    def _record_connect_status_decision(self, *, skipped: bool) -> None:
        """Record one connect-status skip decision and tune stale window."""
        self._connect_status_skip_history.append(skipped)
        self._adapt_connect_status_stale_window()

    def _adapt_connect_status_stale_window(self) -> None:
        """Adapt MQTT stale window based on recent connect skip ratio."""
        history = self._connect_status_skip_history
        current = self._connect_status_mqtt_stale_seconds
        updated = adapt_connect_status_stale_window_runtime(
            history=history,
            current_stale_seconds=current,
            window_size=_CONNECT_STATUS_SKIP_RATIO_WINDOW,
            skip_ratio_low=_CONNECT_STATUS_SKIP_RATIO_LOW,
            skip_ratio_high=_CONNECT_STATUS_SKIP_RATIO_HIGH,
            adjust_step_seconds=_CONNECT_STATUS_STALE_ADJUST_STEP_SECONDS,
            min_stale_seconds=_CONNECT_STATUS_MQTT_STALE_MIN_SECONDS,
            max_stale_seconds=_CONNECT_STATUS_MQTT_STALE_MAX_SECONDS,
        )
        if updated == current:
            return

        self._connect_status_mqtt_stale_seconds = updated
        skip_ratio = sum(history) / len(history) if history else 0.0
        _LOGGER.debug(
            "Adaptive connect stale window changed: %.1fs -> %.1fs (skip_ratio=%.2f, window=%d)",
            current,
            updated,
            skip_ratio,
            len(history),
        )

    def _record_state_batch_metric(
        self,
        batch_size: int,
        duration_seconds: float,
        fallback_depth: int,
    ) -> None:
        """Record one state-batch metric sample for runtime adaptation."""
        sample = normalize_state_batch_metric(
            batch_size,
            duration_seconds,
            fallback_depth,
        )
        self._state_batch_metrics.append(sample)
        _LOGGER.debug(
            "State batch metric: size=%d duration=%.3fs fallback_depth=%d current_batch=%d",
            sample[0],
            sample[1],
            sample[2],
            self._state_status_batch_size,
        )

    def _adapt_state_batch_size(self) -> None:
        """Adapt state batch size using recent latency/fallback metrics."""
        if not self._state_batch_metrics:
            return

        current = self._state_status_batch_size
        upper = min(MAX_DEVICES_PER_QUERY, _STATE_STATUS_BATCH_SIZE_MAX)
        updated = compute_adaptive_state_batch_size(
            current_batch_size=current,
            recent_metrics=self._state_batch_metrics,
            batch_size_min=_STATE_STATUS_BATCH_SIZE_MIN,
            batch_size_max=upper,
            batch_adjust_step=_STATE_STATUS_BATCH_ADJUST_STEP,
            metrics_sample_size=_STATE_STATUS_BATCH_METRICS_SAMPLE_SIZE,
            latency_low_seconds=_STATE_STATUS_BATCH_LATENCY_LOW_SECONDS,
            latency_high_seconds=_STATE_STATUS_BATCH_LATENCY_HIGH_SECONDS,
        )
        if updated == current:
            return

        avg_latency, max_depth, sample_count = summarize_recent_state_batch_metrics(
            list(self._state_batch_metrics),
            sample_size=_STATE_STATUS_BATCH_METRICS_SAMPLE_SIZE,
        )

        self._state_status_batch_size = updated
        _LOGGER.debug(
            "Adaptive state batch size changed: %d -> %d (avg_latency=%.3fs, max_fallback_depth=%d, samples=%d)",
            current,
            updated,
            avg_latency,
            max_depth,
            sample_count,
        )

    async def _query_connect_status(self, device_ids: list[str] | None = None) -> None:
        """Query real-time connection status for devices.

        This provides more accurate online/offline status than the cached
        connectState property from device status queries.
        """
        query_ids = (
            list(device_ids) if device_ids is not None else self._iot_ids_to_query
        )
        if not query_ids:
            return

        connect_status = await self.client.query_connect_status(
            query_ids,
        )

        if not connect_status:
            return

        for device_id, is_online in connect_status.items():
            self._connect_status_priority_ids.discard(
                self._normalize_device_key(device_id)
            )
            device = self.get_device_by_id(device_id)
            if device:
                # Update connectState property (via _apply_properties_update
                # for consistent debounce protection handling)
                self._apply_properties_update(
                    device,
                    {PROP_CONNECT_STATE: "1" if is_online else "0"},
                )
                _LOGGER.debug(
                    "Updated connect status for %s: %s",
                    device.name,
                    "online" if is_online else "offline",
                )


__all__ = [
    "_CONNECT_STATUS_MQTT_STALE_SECONDS",
    "_CONNECT_STATUS_SKIP_RATIO_WINDOW",
    "_STATE_STATUS_BATCH_METRICS_WINDOW",
    "_STATE_STATUS_BATCH_SIZE_MAX",
    "CoordinatorAdaptiveTuningRuntime",
]
