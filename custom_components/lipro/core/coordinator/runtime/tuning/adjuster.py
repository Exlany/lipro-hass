"""Parameter adjuster for applying tuning decisions."""

from __future__ import annotations

from typing import Any


class TuningAdjuster:
    """Apply tuning adjustments to runtime parameters."""

    def __init__(self) -> None:
        self._current_batch_size: int = 32
        self._adjustment_count: int = 0

    def apply_batch_size_adjustment(self, new_size: int) -> bool:
        if new_size == self._current_batch_size:
            return False
        self._current_batch_size = new_size
        self._adjustment_count += 1
        return True

    def get_current_batch_size(self) -> int:
        return self._current_batch_size

    def get_adjustment_count(self) -> int:
        return self._adjustment_count

    def reset_adjustments(self, *, batch_size: int) -> None:
        self._current_batch_size = batch_size
        self._adjustment_count = 0

    def get_adjuster_state(self) -> dict[str, Any]:
        return {
            "current_batch_size": self._current_batch_size,
            "adjustment_count": self._adjustment_count,
        }


__all__ = ["TuningAdjuster"]
