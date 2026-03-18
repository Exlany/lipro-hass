"""Typed models and rejection contracts for runtime device snapshots."""

from __future__ import annotations

from dataclasses import dataclass, field

from custom_components.lipro.core.device import LiproDevice
from custom_components.lipro.core.exceptions import LiproError

type SnapshotFailureStage = str


@dataclass(frozen=True, slots=True)
class RuntimeSnapshotRefreshFailure:
    """Structured refresh failure payload retained by DeviceRuntime."""

    stage: SnapshotFailureStage
    error_type: str | None
    page: int | None = None
    device_ref: str | None = None
    kept_last_known_good: bool = False


class RuntimeSnapshotRefreshRejectedError(LiproError):
    """Raised when a full snapshot refresh must be rejected atomically."""

    def __init__(
        self,
        *,
        stage: SnapshotFailureStage,
        cause_type: str | None,
        page: int | None = None,
        device_ref: str | None = None,
        kept_last_known_good: bool = False,
    ) -> None:
        """Store structured rejection metadata for one refresh attempt."""
        self.stage = stage
        self.cause_type = cause_type
        self.page = page
        self.device_ref = device_ref
        self.kept_last_known_good = kept_last_known_good
        super().__init__(self._build_message())

    def _build_message(self) -> str:
        details = [f"stage={self.stage}"]
        if self.page is not None:
            details.append(f"page={self.page}")
        if self.device_ref is not None:
            details.append(f"device_ref={self.device_ref}")
        if self.cause_type is not None:
            details.append(f"cause_type={self.cause_type}")
        details.append(
            "kept_last_known_good=true"
            if self.kept_last_known_good
            else "kept_last_known_good=false"
        )
        return "runtime snapshot refresh rejected (" + ", ".join(details) + ")"

    @property
    def failure(self) -> RuntimeSnapshotRefreshFailure:
        """Return the structured failure payload for the rejection."""
        return RuntimeSnapshotRefreshFailure(
            stage=self.stage,
            error_type=self.cause_type,
            page=self.page,
            device_ref=self.device_ref,
            kept_last_known_good=self.kept_last_known_good,
        )

    def with_retained_last_known_good(self) -> RuntimeSnapshotRefreshRejectedError:
        """Return a copy marked as retaining the previous snapshot."""
        return RuntimeSnapshotRefreshRejectedError(
            stage=self.stage,
            cause_type=self.cause_type,
            page=self.page,
            device_ref=self.device_ref,
            kept_last_known_good=True,
        )


@dataclass(frozen=True)
class FetchedDeviceSnapshot:
    """Atomic container for refreshed device indexes."""

    devices: dict[str, LiproDevice]
    device_by_id: dict[str, LiproDevice]
    iot_ids: list[str]
    group_ids: list[str]
    outlet_ids: list[str]
    cloud_serials: set[str] = field(default_factory=set)
    diagnostic_gateway_devices: dict[str, LiproDevice] = field(default_factory=dict)


__all__ = [
    "FetchedDeviceSnapshot",
    "RuntimeSnapshotRefreshFailure",
    "RuntimeSnapshotRefreshRejectedError",
    "SnapshotFailureStage",
]
