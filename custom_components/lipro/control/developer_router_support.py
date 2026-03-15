"""Focused private helpers shared by developer-facing service-router handlers."""

from __future__ import annotations

from collections.abc import Awaitable, Callable, Iterator
import logging
from typing import Any, NoReturn, TypeVar

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
    DeveloperReportCoordinatorIterator,
    GetDeviceAndCoordinator,
)
from ..services.errors import raise_service_error as _raise_service_error
from .runtime_access import (
    get_entry_runtime_coordinator as _get_entry_runtime_coordinator,
    is_debug_mode_enabled_for_entry as _is_debug_mode_enabled_for_entry,
    iter_developer_runtime_coordinators as _iter_developer_runtime_coordinators,
    iter_runtime_entries as _iter_runtime_entries,
)

_LOGGER = logging.getLogger(__name__)
_ResultT = TypeVar("_ResultT")


def build_single_runtime_coordinator_iterator(
    coordinator: LiproCoordinator,
) -> DeveloperReportCoordinatorIterator:
    """Build a stable iterator factory for one runtime coordinator."""

    def _iter_single_runtime_coordinator(
        _hass: HomeAssistant,
    ) -> Iterator[LiproCoordinator]:
        return iter((coordinator,))

    return _iter_single_runtime_coordinator



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
        for entry in _iter_runtime_entries(hass, entry_id=requested_entry_id):
            if entry.entry_id != requested_entry_id:
                continue
            coordinator = _get_entry_runtime_coordinator(entry)
            if coordinator is None:
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
            )

        raise ServiceValidationError(
            translation_domain=DOMAIN,
            translation_key="entry_not_found",
            translation_placeholders={"entry_id": requested_entry_id},
        )

    coordinators = list(_iter_developer_runtime_coordinators(hass))
    return _collect_developer_reports_service(
        hass,
        iter_runtime_coordinators=lambda _hass: iter(coordinators),
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
    service_handler: Callable[..., Awaitable[dict[str, object]]],
    service_name_kw: str,
    service_name: str,
    get_device_and_coordinator: GetDeviceAndCoordinator,
) -> dict[str, object]:
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
    "build_single_runtime_coordinator_iterator",
    "collect_developer_reports",
    "raise_developer_mode_not_enabled",
    "raise_optional_capability_error",
]
