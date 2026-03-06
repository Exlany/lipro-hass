"""Developer/diagnostic service handlers for Lipro integration."""

from __future__ import annotations

from collections.abc import Awaitable, Callable, Iterator
from datetime import UTC, datetime
import logging
from typing import Any, NoReturn, TypeVar

from homeassistant.core import HomeAssistant, ServiceCall
from homeassistant.exceptions import HomeAssistantError

from ..const import DOMAIN
from ..core import LiproApiError
from ..core.utils.log_safety import safe_error_placeholder

_LOGGER = logging.getLogger(__name__)
_ResultT = TypeVar("_ResultT")


def _collect_coordinator_capability_results(
    coordinators: Iterator[Any],
    *,
    capability: str,
    collector: Callable[[Any], _ResultT],
) -> list[_ResultT]:
    """Collect capability results across coordinators with per-entry fault tolerance."""
    results: list[_ResultT] = []
    for coordinator in coordinators:
        try:
            results.append(collector(coordinator))
        except Exception as err:  # noqa: BLE001
            _LOGGER.warning(
                "Skip one %s capability due to error (%s)",
                capability,
                type(err).__name__,
            )
    return results


async def _async_get_first_coordinator_capability_result(
    coordinators: Iterator[Any],
    *,
    capability: str,
    collector: Callable[[Any], Awaitable[_ResultT]],
) -> tuple[bool, _ResultT | None, LiproApiError | None]:
    """Return first successful capability result and retain last API error."""
    last_api_error: LiproApiError | None = None
    for coordinator in coordinators:
        try:
            return True, await collector(coordinator), None
        except LiproApiError as err:
            last_api_error = err
        except Exception as err:  # noqa: BLE001
            _LOGGER.warning(
                "Skip one %s capability due to unexpected error (%s)",
                capability,
                type(err).__name__,
            )
    return False, None, last_api_error


def collect_developer_reports(
    hass: HomeAssistant,
    *,
    iter_runtime_coordinators: Callable[[HomeAssistant], Iterator[Any]],
) -> list[dict[str, Any]]:
    """Collect developer reports from active config entries."""
    return _collect_coordinator_capability_results(
        (
            coordinator
            for coordinator in iter_runtime_coordinators(hass)
            if hasattr(coordinator, "build_developer_report")
        ),
        capability="coordinator developer report",
        collector=lambda coordinator: coordinator.build_developer_report(),
    )


async def async_handle_get_developer_report(
    hass: HomeAssistant,
    call: ServiceCall,
    *,
    collect_reports: Callable[[HomeAssistant], list[dict[str, Any]]],
) -> dict[str, Any]:
    """Handle get_developer_report service."""
    del call
    reports = collect_reports(hass)
    return {
        "entry_count": len(reports),
        "reports": reports,
    }


async def async_handle_submit_developer_feedback(
    hass: HomeAssistant,
    call: ServiceCall,
    *,
    collect_reports: Callable[[HomeAssistant], list[dict[str, Any]]],
    get_anonymous_share_manager: Callable[[HomeAssistant], Any],
    get_client_session: Callable[[HomeAssistant], Any],
    domain: str,
    service_submit_developer_feedback: str,
    attr_note: str,
    raise_service_error: Callable[..., NoReturn],
) -> dict[str, Any]:
    """Handle submit_developer_feedback service."""
    reports = collect_reports(hass)
    if not reports:
        return {
            "success": False,
            "message": "No active Lipro config entries",
            "submitted_entries": 0,
        }

    feedback_payload = {
        "source": "home_assistant_service",
        "service": f"{domain}.{service_submit_developer_feedback}",
        "generated_at": datetime.now(UTC).isoformat(),
        "entry_count": len(reports),
        "note": call.data.get(attr_note, ""),
        "reports": reports,
    }

    share_manager = get_anonymous_share_manager(hass)
    session = get_client_session(hass)
    success = await share_manager.submit_developer_feedback(
        session,
        feedback_payload,
    )
    if not success:
        raise_service_error("developer_feedback_submit_failed")

    return {
        "success": True,
        "submitted_entries": len(reports),
    }


def raise_optional_capability_error(
    capability: str,
    err: LiproApiError,
    *,
    logger: Any,
) -> NoReturn:
    """Raise concise service-layer error for optional diagnostic capabilities."""
    safe_error = safe_error_placeholder(err)
    logger.warning("Optional capability %s failed (%s)", capability, safe_error)
    service_error = HomeAssistantError(
        f"{capability} failed ({safe_error})",
        translation_domain=DOMAIN,
        translation_key="optional_capability_failed",
        translation_placeholders={
            "capability": capability,
            "error": safe_error,
        },
    )
    raise service_error from err


async def async_call_optional_capability(
    capability: str,
    method: Callable[..., Awaitable[Any]],
    *,
    raise_optional_error: Callable[[str, LiproApiError], NoReturn],
    **kwargs: Any,
) -> Any:
    """Call optional capability API and map LiproApiError to service error."""
    try:
        return await method(**kwargs)
    except LiproApiError as err:
        raise_optional_error(capability, err)


def build_sensor_history_result(
    serial: str,
    sensor_device_id: str,
    mesh_type: str,
    result: dict[str, Any],
) -> dict[str, Any]:
    """Build common response payload for sensor history diagnostics."""
    return {
        "serial": serial,
        "sensor_device_id": sensor_device_id,
        "mesh_type": mesh_type,
        "result": result,
    }


async def async_handle_query_command_result(
    hass: HomeAssistant,
    call: ServiceCall,
    *,
    get_device_and_coordinator: Any,
    async_call_optional_capability: Any,
    attr_msg_sn: str,
    service_query_command_result: str,
) -> dict[str, Any]:
    """Handle query_command_result service."""
    device, coordinator = await get_device_and_coordinator(hass, call)
    msg_sn = call.data[attr_msg_sn]
    result = await async_call_optional_capability(
        service_query_command_result,
        coordinator.client.query_command_result,
        msg_sn=msg_sn,
        device_id=device.serial,
        device_type=device.device_type,
    )
    return {
        "serial": device.serial,
        "msg_sn": msg_sn,
        "result": result,
    }


async def async_handle_get_city(
    hass: HomeAssistant,
    call: ServiceCall,
    *,
    iter_runtime_coordinators: Callable[[HomeAssistant], Iterator[Any]],
    raise_optional_error: Callable[[str, LiproApiError], NoReturn],
    service_get_city: str,
) -> dict[str, Any]:
    """Handle get_city service."""
    del call
    has_result, result, last_err = await _async_get_first_coordinator_capability_result(
        iter_runtime_coordinators(hass),
        capability="get_city",
        collector=lambda coordinator: coordinator.client.get_city(),
    )
    if has_result:
        return {"result": result}
    if last_err is not None:
        raise_optional_error(service_get_city, last_err)
    return {"result": {}}


async def _async_handle_fetch_sensor_history(
    hass: HomeAssistant,
    call: ServiceCall,
    *,
    get_device_and_coordinator: Any,
    async_call_optional_capability: Any,
    build_sensor_history_result: Callable[..., dict[str, Any]],
    attr_sensor_device_id: str,
    attr_mesh_type: str,
    service_name: str,
    get_client_method: Callable[[Any], Callable[..., Awaitable[Any]]],
) -> dict[str, Any]:
    """Shared handler for sensor-history diagnostics services."""
    device, coordinator = await get_device_and_coordinator(hass, call)
    sensor_device_id = call.data[attr_sensor_device_id]
    mesh_type = call.data[attr_mesh_type]
    result = await async_call_optional_capability(
        service_name,
        get_client_method(coordinator),
        device_id=device.serial,
        device_type=device.device_type,
        sensor_device_id=sensor_device_id,
        mesh_type=mesh_type,
    )
    return build_sensor_history_result(
        device.serial,
        sensor_device_id,
        mesh_type,
        result,
    )


async def async_handle_fetch_body_sensor_history(
    hass: HomeAssistant,
    call: ServiceCall,
    *,
    get_device_and_coordinator: Any,
    async_call_optional_capability: Any,
    build_sensor_history_result: Callable[..., dict[str, Any]],
    attr_sensor_device_id: str,
    attr_mesh_type: str,
    service_fetch_body_sensor_history: str,
) -> dict[str, Any]:
    """Handle fetch_body_sensor_history service."""
    return await _async_handle_fetch_sensor_history(
        hass,
        call,
        get_device_and_coordinator=get_device_and_coordinator,
        async_call_optional_capability=async_call_optional_capability,
        build_sensor_history_result=build_sensor_history_result,
        attr_sensor_device_id=attr_sensor_device_id,
        attr_mesh_type=attr_mesh_type,
        service_name=service_fetch_body_sensor_history,
        get_client_method=lambda coordinator: (
            coordinator.client.fetch_body_sensor_history
        ),
    )


async def async_handle_fetch_door_sensor_history(
    hass: HomeAssistant,
    call: ServiceCall,
    *,
    get_device_and_coordinator: Any,
    async_call_optional_capability: Any,
    build_sensor_history_result: Callable[..., dict[str, Any]],
    attr_sensor_device_id: str,
    attr_mesh_type: str,
    service_fetch_door_sensor_history: str,
) -> dict[str, Any]:
    """Handle fetch_door_sensor_history service."""
    return await _async_handle_fetch_sensor_history(
        hass,
        call,
        get_device_and_coordinator=get_device_and_coordinator,
        async_call_optional_capability=async_call_optional_capability,
        build_sensor_history_result=build_sensor_history_result,
        attr_sensor_device_id=attr_sensor_device_id,
        attr_mesh_type=attr_mesh_type,
        service_name=service_fetch_door_sensor_history,
        get_client_method=lambda coordinator: (
            coordinator.client.fetch_door_sensor_history
        ),
    )
