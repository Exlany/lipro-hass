"""MQTT reconnection backoff strategy."""

from __future__ import annotations

from time import monotonic

from ....mqtt.setup_backoff import MqttSetupBackoff


class MqttReconnectManager:
    """Manages MQTT reconnection backoff and retry logic."""

    def __init__(
        self,
        *,
        base_delay: float = 1.0,
        max_delay: float = 60.0,
    ) -> None:
        """Initialize reconnect manager.

        Args:
            base_delay: Base delay for exponential backoff in seconds
            max_delay: Maximum delay cap in seconds
        """
        self._backoff = MqttSetupBackoff(
            base_delay=base_delay,
            max_delay=max_delay,
        )
        self._backoff_gate_logged: bool = False

    def should_attempt_reconnect(self, *, current_time: float | None = None) -> bool:
        """Check if reconnection should be attempted now.

        Args:
            current_time: Current timestamp (defaults to monotonic())

        Returns:
            True if reconnection should be attempted, False if in backoff period
        """
        now = monotonic() if current_time is None else current_time
        return self._backoff.should_attempt(now)

    def on_reconnect_failure(self, *, current_time: float | None = None) -> None:
        """Record reconnection failure and update backoff state.

        Args:
            current_time: Current timestamp (defaults to monotonic())
        """
        now = monotonic() if current_time is None else current_time
        self._backoff.on_failure(now)
        self._backoff_gate_logged = False

    def on_reconnect_success(self) -> None:
        """Reset backoff state after successful reconnection."""
        self._backoff.on_success()
        self._backoff_gate_logged = False

    def mark_backoff_gate_logged(self) -> None:
        """Mark that backoff gate log message was emitted."""
        self._backoff_gate_logged = True

    @property
    def backoff_gate_logged(self) -> bool:
        """Return whether backoff gate was logged."""
        return self._backoff_gate_logged

    def reset(self) -> None:
        """Reset reconnection state."""
        self._backoff.on_success()
        self._backoff_gate_logged = False
