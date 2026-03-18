"""Adapter helpers that bridge runtime callback ports into message-handler contracts."""

from __future__ import annotations

from collections.abc import Callable
import logging
from typing import TYPE_CHECKING, Protocol, cast

from .message_handler import MqttMessageHandler

if TYPE_CHECKING:
    from ....device import LiproDevice
    from ...types import PropertyDict

    DeviceResolverCallable = Callable[[str], LiproDevice | None]
else:
    DeviceResolverCallable = Callable[[str], object]


class DeviceResolverProtocol(Protocol):
    """Protocol for device resolution."""

    def get_device_by_id(self, device_id: str) -> LiproDevice | None:
        """Resolve device by ID."""


class PropertyApplierProtocol(Protocol):
    """Protocol for property application."""

    async def __call__(
        self,
        device: LiproDevice,
        properties: PropertyDict,
        source: str,
    ) -> bool:
        """Apply properties update to device."""


class ListenerNotifierProtocol(Protocol):
    """Protocol for listener notification."""

    def schedule_listener_update(self) -> None:
        """Schedule a listener update."""


class ConnectStateTrackerProtocol(Protocol):
    """Protocol for connect state tracking."""

    def record_connect_state(
        self, device_serial: str, timestamp: float, is_online: bool
    ) -> None:
        """Record connect state observation."""


class GroupReconcilerProtocol(Protocol):
    """Protocol for group reconciliation."""

    def schedule_group_reconciliation(self, device_name: str, timestamp: float) -> None:
        """Schedule group online reconciliation."""


class DeviceResolverAdapter:
    """Adapter for callable-or-object device resolution ports."""

    def __init__(self, resolver: DeviceResolverProtocol) -> None:
        self._resolver = resolver

    def get_device_by_id(self, device_id: str) -> LiproDevice | None:
        resolver = self._resolver
        method = cast(
            DeviceResolverCallable | None,
            getattr(resolver, "get_device_by_id", None),
        )
        if method is not None:
            return method(device_id)
        return cast(DeviceResolverCallable, resolver)(device_id)


class PropertyApplierAdapter:
    """Adapter to convert bool-returning applier to dict-returning."""

    def __init__(self, applier: PropertyApplierProtocol) -> None:
        self._applier = applier

    async def apply_properties_update(
        self,
        device: LiproDevice,
        properties: PropertyDict,
    ) -> PropertyDict:
        """Apply properties and return applied dict."""
        success = await self._applier(device, properties, "mqtt")
        return properties if success else {}


class ListenerNotifierAdapter:
    """Adapter for callable-or-object listener notification ports."""

    def __init__(self, notifier: ListenerNotifierProtocol) -> None:
        self._notifier = notifier

    def schedule_listener_update(self) -> None:
        notifier = self._notifier
        method = cast(
            Callable[[], None] | None,
            getattr(notifier, "schedule_listener_update", None),
        )
        if method is not None:
            method()
            return
        cast(Callable[[], None], notifier)()


class ConnectStateTrackerAdapter:
    """Adapter for callable-or-object connect-state tracking ports."""

    def __init__(self, tracker: ConnectStateTrackerProtocol) -> None:
        self._tracker = tracker

    def record_connect_state(
        self, device_serial: str, timestamp: float, is_online: bool
    ) -> None:
        tracker = self._tracker
        method = cast(
            Callable[[str, float, bool], None] | None,
            getattr(tracker, "record_connect_state", None),
        )
        if method is not None:
            method(device_serial, timestamp, is_online)
            return
        cast(Callable[[str, float, bool], None], tracker)(
            device_serial,
            timestamp,
            is_online,
        )


class GroupReconcilerAdapter:
    """Adapter for callable-or-object group reconciliation ports."""

    def __init__(self, reconciler: GroupReconcilerProtocol) -> None:
        self._reconciler = reconciler

    def schedule_group_reconciliation(
        self, device_name: str, timestamp: float
    ) -> None:
        reconciler = self._reconciler
        method = cast(
            Callable[[str, float], None] | None,
            getattr(reconciler, "schedule_group_reconciliation", None),
        )
        if method is not None:
            method(device_name, timestamp)
            return
        cast(Callable[[str, float], None], reconciler)(
            device_name,
            timestamp,
        )


def build_mqtt_message_handler(
    *,
    device_resolver: DeviceResolverProtocol,
    property_applier: PropertyApplierProtocol,
    listener_notifier: ListenerNotifierProtocol,
    connect_state_tracker: ConnectStateTrackerProtocol,
    group_reconciler: GroupReconcilerProtocol,
    logger: logging.Logger,
) -> MqttMessageHandler:
    """Build the formal message handler from runtime callback ports."""
    return MqttMessageHandler(
        device_resolver=DeviceResolverAdapter(device_resolver),
        property_applier=PropertyApplierAdapter(property_applier),
        listener_notifier=ListenerNotifierAdapter(listener_notifier),
        connect_state_tracker=ConnectStateTrackerAdapter(connect_state_tracker),
        group_reconciler=GroupReconcilerAdapter(group_reconciler),
        logger=logger,
    )


__all__ = [
    "ConnectStateTrackerProtocol",
    "DeviceResolverProtocol",
    "GroupReconcilerProtocol",
    "ListenerNotifierProtocol",
    "PropertyApplierProtocol",
    "build_mqtt_message_handler",
]
