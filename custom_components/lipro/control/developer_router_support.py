"""Focused private helpers shared by developer-facing service-router handlers."""

from __future__ import annotations

from collections.abc import Awaitable, Callable, Iterator
import logging
from typing import TYPE_CHECKING, Any, NoReturn, TypeVar

from homeassistant.core import HomeAssistant, ServiceCall
from homeassistant.exceptions import ServiceValidationError

from ..const.base import DOMAIN
from ..core import LiproApiError
from ..runtime_types import LiproCoordinator
from ..services import contracts as _contracts
from ..services.diagnostics import (
    async_call_optional_capability as _async_call_optional_capability_service,
    build_sensor_history_result as _build_sensor_history_result_service,
    collect_developer_reports as _collect_developer_reports_service,
    raise_optional_capability_error as _raise_optional_capability_error_service,
)
from ..services.diagnostics.types import (
    DeveloperReport,
    GetDeviceAndCoordinator,
    RuntimeCoordinatorIterator,
    SensorHistoryResponse,
)
from ..services.errors import raise_service_error as _raise_service_error
from . import telemetry_surface as _telemetry_surface
from .runtime_access import (
    find_runtime_entry_for_coordinator as _find_runtime_entry_for_coordinator,
    is_debug_mode_enabled_for_entry as _is_debug_mode_enabled_for_entry,
    is_developer_runtime_coordinator as _is_developer_runtime_coordinator,
    iter_developer_runtime_coordinators as _iter_developer_runtime_coordinators,
    iter_runtime_entry_coordinators as _iter_runtime_entry_coordinators,
)

if TYPE_CHECKING:
    from ..core.device import LiproDevice

_LOGGER = logging.getLogger(__name__)
_ResultT = TypeVar("_ResultT")
type _RuntimeDeviceAndCoordinatorGetter = Callable[
    [HomeAssistant, ServiceCall],
    Awaitable[tuple[LiproDevice, LiproCoordinator]],
]



def build_single_runtime_coordinator_iterator(
    coordinator: LiproCoordinator,
) -> RuntimeCoordinatorIterator:
    """Build a stable iterator factory for one runtime coordinator."""

    def _iter_single_runtime_coordinator(
        _hass: HomeAssistant,
    ) -> Iterator[LiproCoordinator]:
        return iter((coordinator,))

    return _iter_single_runtime_coordinator


def build_developer_runtime_coordinator_iterator(
    hass: HomeAssistant,
) -> RuntimeCoordinatorIterator:
    """Freeze the current debug-enabled coordinators into one iterator factory."""
    coordinators = list(_iter_developer_runtime_coordinators(hass))

    def _iter_runtime_coordinators(
        _hass: HomeAssistant,
    ) -> Iterator[LiproCoordinator]:
        return iter(coordinators)

    return _iter_runtime_coordinators


async def get_developer_device_and_coordinator(
    hass: HomeAssistant,
    call: ServiceCall,
    *,
    get_device_and_coordinator: _RuntimeDeviceAndCoordinatorGetter,
) -> tuple[LiproDevice, LiproCoordinator]:
    """Resolve one runtime device/coordinator pair and require debug opt-in."""
    device, coordinator = await get_device_and_coordinator(hass, call)
    if not _is_developer_runtime_coordinator(hass, coordinator):
        entry = _find_runtime_entry_for_coordinator(hass, coordinator)
        raise_developer_mode_not_enabled(
            entry_id=entry.entry_id if entry is not None else None
        )
    return device, coordinator


def raise_developer_mode_not_enabled(*, entry_id: str | None = None) -> NoReturn:
    """Raise a consistent validation error for disabled developer services."""
    del entry_id
    raise ServiceValidationError(
        translation_domain=DOMAIN,
        translation_key="developer_mode_not_enabled",
    )


def collect_developer_reports(
    hass: HomeAssistant,
    *,
    requested_entry_id: str | None = None,
) -> list[DeveloperReport]:
    """Collect developer reports from debug-enabled runtime entries only."""
    if requested_entry_id is not None:
        entry_and_coordinator = next(
            iter(_iter_runtime_entry_coordinators(hass, entry_id=requested_entry_id)),
            None,
        )
        if entry_and_coordinator is None:
            raise ServiceValidationError(
                translation_domain=DOMAIN,
                translation_key="entry_not_found",
                translation_placeholders={"entry_id": requested_entry_id},
            )
        entry, coordinator = entry_and_coordinator
        if entry.entry_id != requested_entry_id:
            raise ServiceValidationError(
                translation_domain=DOMAIN,
                translation_key="entry_not_found",
                translation_placeholders={"entry_id": requested_entry_id},
            )
        if not _is_debug_mode_enabled_for_entry(entry):
            raise_developer_mode_not_enabled(entry_id=requested_entry_id)
        return _collect_developer_reports_service(
            hass,
            iter_runtime_coordinators=build_single_runtime_coordinator_iterator(
                coordinator
            ),
            find_runtime_entry_for_coordinator=_find_runtime_entry_for_coordinator,
            get_entry_telemetry_view=_telemetry_surface.get_entry_telemetry_view,
        )

    return _collect_developer_reports_service(
        hass,
        iter_runtime_coordinators=build_developer_runtime_coordinator_iterator(hass),
        find_runtime_entry_for_coordinator=_find_runtime_entry_for_coordinator,
        get_entry_telemetry_view=_telemetry_surface.get_entry_telemetry_view,
    )


def raise_optional_capability_error(capability: str, err: LiproApiError) -> NoReturn:
    """Raise a concise service-layer error for optional diagnostic capabilities."""
    _raise_optional_capability_error_service(capability, err, logger=_LOGGER)


async def async_call_optional_capability(
    capability: str,
    method: Callable[..., Awaitable[_ResultT]],
    **kwargs: Any,
) -> _ResultT:
    """Call optional capability API and map auth/API failures to service errors."""
    return await _async_call_optional_capability_service(
        capability,
        method,
        raise_optional_error=raise_optional_capability_error,
        raise_service_error=_raise_service_error,
        **kwargs,
    )


async def async_handle_fetch_sensor_history(
    hass: HomeAssistant,
    call: ServiceCall,
    *,
    service_handler: Callable[..., Awaitable[SensorHistoryResponse]],
    service_name_kw: str,
    service_name: str,
    get_device_and_coordinator: GetDeviceAndCoordinator,
) -> SensorHistoryResponse:
    """Shared wrapper for body/door sensor-history service handlers."""
    return await service_handler(
        hass,
        call,
        get_device_and_coordinator=get_device_and_coordinator,
        async_call_optional_capability=async_call_optional_capability,
        build_sensor_history_result=_build_sensor_history_result_service,
        attr_sensor_device_id=_contracts.ATTR_SENSOR_DEVICE_ID,
        attr_mesh_type=_contracts.ATTR_MESH_TYPE,
        **{service_name_kw: service_name},
    )


__all__ = [
    "async_call_optional_capability",
    "async_handle_fetch_sensor_history",
    "build_developer_runtime_coordinator_iterator",
    "build_single_runtime_coordinator_iterator",
    "collect_developer_reports",
    "get_developer_device_and_coordinator",
    "raise_developer_mode_not_enabled",
    "raise_optional_capability_error",
]
