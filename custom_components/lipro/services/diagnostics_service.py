"""Developer/diagnostic service handlers for Lipro integration."""

from __future__ import annotations

from collections.abc import Awaitable, Callable, Iterator, Mapping
from datetime import UTC, datetime
import logging
from typing import NoReturn, Protocol, TypedDict, TypeVar, cast

from homeassistant.core import HomeAssistant, ServiceCall
from homeassistant.exceptions import HomeAssistantError

from ..const.base import DOMAIN
from ..core import LiproApiError
from ..core.api.types import DiagnosticsApiResponse
from ..core.command.result import (
    CommandResultPayload,
    build_progressive_retry_delays,
    classify_command_result_payload,
    poll_command_result_state,
    query_command_result_once,
)
from ..core.utils.log_safety import safe_error_placeholder
from .execution import (
    AuthenticatedCoordinator,
    ServiceErrorRaiser,
    async_execute_coordinator_call,
)

_LOGGER = logging.getLogger(__name__)
_ResultT = TypeVar("_ResultT")
_CoordinatorT = TypeVar("_CoordinatorT")
_QUERY_COMMAND_RESULT_DIAGNOSTIC_BASE_DELAY_SECONDS = 0.35
_DEFAULT_QUERY_COMMAND_RESULT_MAX_ATTEMPTS = 6
_DEFAULT_QUERY_COMMAND_RESULT_TIME_BUDGET_SECONDS = 3.0

type DeveloperReport = dict[str, object]
type CapabilityPayload = dict[str, object]
type SensorHistoryClientMethod = Callable[..., Awaitable[DiagnosticsApiResponse]]
type DeveloperReportCollector = Callable[..., list[DeveloperReport]]
type RuntimeCoordinatorIterator = Callable[[HomeAssistant], Iterator[object]]
type AnonymousShareManagerFactory = Callable[..., object]
type ClientSessionGetter = Callable[[HomeAssistant], object]
type GetDeviceAndCoordinator = Callable[
    [HomeAssistant, ServiceCall],
    Awaitable[tuple[object, object]],
]
type OptionalCapabilityCaller = Callable[..., Awaitable[DiagnosticsApiResponse]]
type SensorHistoryResultBuilder = Callable[..., dict[str, object]]


class DeveloperReportResponse(TypedDict, total=False):
    """Response payload returned by the developer-report service."""

    entry_count: int
    reports: list[DeveloperReport]
    requested_entry_id: str


class DeveloperFeedbackResponse(TypedDict, total=False):
    """Response payload returned by developer-feedback submission."""

    success: bool
    message: str
    submitted_entries: int
    requested_entry_id: str


class CapabilityResponse(TypedDict):
    """Envelope used by optional diagnostics capabilities."""

    result: CapabilityPayload


class SensorHistoryResponse(TypedDict):
    """Structured sensor-history response payload."""

    serial: str
    sensor_device_id: str
    mesh_type: str
    result: DiagnosticsApiResponse


class LastErrorPayload(TypedDict, total=False):
    """Serializable API error details for diagnostics output."""

    code: int | str
    message: str


class QueryCommandResultResponse(TypedDict, total=False):
    """Response payload for query_command_result diagnostics."""

    serial: str
    msg_sn: str
    max_attempts: int
    time_budget_seconds: float
    state: str
    attempts: int
    attempt_limit: int
    retry_delays_seconds: list[float]
    result: CommandResultPayload | None
    last_error: LastErrorPayload


class DiagnosticsClientProtocol(Protocol):
    """Client surface required by diagnostics services."""

    async def query_command_result(
        self,
        *,
        msg_sn: str,
        device_id: str,
        device_type: str | int,
    ) -> CommandResultPayload:
        """Query one command-result payload."""

    async def get_city(self) -> CapabilityPayload:
        """Return city metadata from the backend."""

    async def query_user_cloud(self) -> CapabilityPayload:
        """Return user-cloud metadata from the backend."""

    async def fetch_body_sensor_history(
        self,
        *,
        device_id: str,
        device_type: str | int,
        sensor_device_id: str,
        mesh_type: str,
    ) -> DiagnosticsApiResponse:
        """Fetch body-sensor history diagnostics."""

    async def fetch_door_sensor_history(
        self,
        *,
        device_id: str,
        device_type: str | int,
        sensor_device_id: str,
        mesh_type: str,
    ) -> DiagnosticsApiResponse:
        """Fetch door-sensor history diagnostics."""


class DiagnosticsCoordinator(AuthenticatedCoordinator, Protocol):
    """Coordinator contract used by diagnostics services."""

    client: DiagnosticsClientProtocol


class DeveloperReportCoordinator(DiagnosticsCoordinator, Protocol):
    """Coordinator contract that can build developer reports."""

    def build_developer_report(self) -> DeveloperReport:
        """Build one serialized developer report."""


class DiagnosticsDevice(Protocol):
    """Device contract required by diagnostics services."""

    serial: str
    name: str
    device_type: int | str
    device_type_hex: str

class DeveloperFeedbackShareManager(Protocol):
    """Share manager surface needed by developer-feedback submission."""

    async def submit_developer_feedback(
        self,
        session: object,
        payload: Mapping[str, object],
    ) -> bool:
        """Submit the serialized developer-feedback payload."""



def _get_optional_service_string(call: ServiceCall, key: str) -> str | None:
    """Return one optional string service field after light normalization."""
    value = cast(object, call.data.get(key))
    if not isinstance(value, str):
        return None
    normalized = value.strip()
    return normalized or None


def _get_required_service_string(call: ServiceCall, key: str) -> str:
    """Return one required string service field validated by the schema layer."""
    return cast(str, call.data[key])


def _get_optional_note(call: ServiceCall, key: str) -> str:
    """Return one optional note field while preserving caller formatting."""
    value = cast(object, call.data.get(key, ""))
    return value if isinstance(value, str) else ""


def _coerce_service_int(call: ServiceCall, key: str, default: int) -> int:
    """Coerce one optional numeric service field to int."""
    value = cast(object, call.data.get(key, default))
    if isinstance(value, bool):
        return int(value)
    if isinstance(value, (int, float, str)):
        return int(value)
    return default


def _coerce_service_float(call: ServiceCall, key: str, default: float) -> float:
    """Coerce one optional numeric service field to float."""
    value = cast(object, call.data.get(key, default))
    if isinstance(value, bool):
        return float(value)
    if isinstance(value, (int, float, str)):
        return float(value)
    return default


def _collect_coordinator_capability_results(
    coordinators: Iterator[_CoordinatorT],
    *,
    capability: str,
    collector: Callable[[_CoordinatorT], _ResultT],
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
    coordinators: Iterator[DiagnosticsCoordinator],
    *,
    capability: str,
    collector: Callable[[DiagnosticsCoordinator], Awaitable[_ResultT]],
) -> tuple[bool, _ResultT | None, LiproApiError | None]:
    """Return the first successful capability result and retain the last API error."""
    last_api_error: LiproApiError | None = None
    for coordinator in coordinators:
        try:
            return True, await collector(coordinator), None
        except HomeAssistantError:
            raise
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
    iter_runtime_coordinators: RuntimeCoordinatorIterator,
) -> list[DeveloperReport]:
    """Collect developer reports from active config entries."""
    return _collect_coordinator_capability_results(
        (
            cast(DeveloperReportCoordinator, coordinator)
            for coordinator in iter_runtime_coordinators(hass)
            if callable(getattr(coordinator, "build_developer_report", None))
        ),
        capability="coordinator developer report",
        collector=lambda coordinator: coordinator.build_developer_report(),
    )


async def async_handle_get_developer_report(
    hass: HomeAssistant,
    call: ServiceCall,
    *,
    collect_reports: DeveloperReportCollector,
    attr_entry_id: str,
) -> dict[str, object]:
    """Handle the get_developer_report service."""
    requested_entry_id = _get_optional_service_string(call, attr_entry_id)
    result: DeveloperReportResponse = {
        "entry_count": 0,
        "reports": [],
    }
    reports = collect_reports(hass, requested_entry_id=requested_entry_id)
    result["entry_count"] = len(reports)
    result["reports"] = reports
    if requested_entry_id is not None:
        result["requested_entry_id"] = requested_entry_id
    return cast(dict[str, object], result)


async def async_handle_submit_developer_feedback(
    hass: HomeAssistant,
    call: ServiceCall,
    *,
    collect_reports: DeveloperReportCollector,
    get_anonymous_share_manager: AnonymousShareManagerFactory,
    get_client_session: ClientSessionGetter,
    domain: str,
    service_submit_developer_feedback: str,
    attr_note: str,
    attr_entry_id: str,
    raise_service_error: ServiceErrorRaiser,
) -> dict[str, object]:
    """Handle the submit_developer_feedback service."""
    requested_entry_id = _get_optional_service_string(call, attr_entry_id)
    reports = collect_reports(hass, requested_entry_id=requested_entry_id)
    if not reports:
        result: DeveloperFeedbackResponse = {
            "success": False,
            "message": "No active Lipro config entries",
            "submitted_entries": 0,
        }
        if requested_entry_id is not None:
            result["requested_entry_id"] = requested_entry_id
        return cast(dict[str, object], result)

    feedback_payload: dict[str, object] = {
        "source": "home_assistant_service",
        "service": f"{domain}.{service_submit_developer_feedback}",
        "generated_at": datetime.now(UTC).isoformat(),
        "entry_count": len(reports),
        "note": _get_optional_note(call, attr_note),
        "reports": reports,
    }
    if requested_entry_id is not None:
        feedback_payload["requested_entry_id"] = requested_entry_id

    share_manager = cast(
        DeveloperFeedbackShareManager,
        get_anonymous_share_manager(hass, entry_id=requested_entry_id),
    )
    success = await share_manager.submit_developer_feedback(
        get_client_session(hass),
        feedback_payload,
    )
    if not success:
        raise_service_error("developer_feedback_submit_failed")

    success_result: DeveloperFeedbackResponse = {
        "success": True,
        "submitted_entries": len(reports),
    }
    if requested_entry_id is not None:
        success_result["requested_entry_id"] = requested_entry_id
    return cast(dict[str, object], success_result)


def raise_optional_capability_error(
    capability: str,
    err: LiproApiError,
    *,
    logger: logging.Logger,
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
    method: Callable[..., Awaitable[_ResultT]],
    *,
    coordinator: AuthenticatedCoordinator | None = None,
    raise_optional_error: Callable[[str, LiproApiError], NoReturn],
    raise_service_error: ServiceErrorRaiser | None = None,
    **kwargs: object,
) -> _ResultT:
    """Call one optional capability and optionally route through the auth facade."""

    def _handle_api_error(err: LiproApiError) -> NoReturn:
        raise_optional_error(capability, err)

    if coordinator is not None and raise_service_error is not None:
        return await async_execute_coordinator_call(
            coordinator,
            call=lambda: method(**kwargs),
            raise_service_error=raise_service_error,
            handle_api_error=_handle_api_error,
        )

    try:
        return await method(**kwargs)
    except LiproApiError as err:
        raise_optional_error(capability, err)


def build_sensor_history_result(
    serial: str,
    sensor_device_id: str,
    mesh_type: str,
    result: DiagnosticsApiResponse,
) -> dict[str, object]:
    """Build the common response payload for sensor-history diagnostics."""
    return {
        "serial": serial,
        "sensor_device_id": sensor_device_id,
        "mesh_type": mesh_type,
        "result": result,
    }


def _build_last_error_payload(err: LiproApiError | None) -> LastErrorPayload | None:
    """Build serializable last-error details for diagnostics output."""
    if err is None:
        return None
    payload: LastErrorPayload = {}
    if err.code is not None:
        payload["code"] = err.code
    message = str(err).strip()
    if message:
        payload["message"] = message
    return payload or None


async def _async_query_command_result_with_optional_polling(
    *,
    coordinator: DiagnosticsCoordinator,
    device: DiagnosticsDevice,
    msg_sn: str,
    max_attempts: int,
    time_budget_seconds: float,
    raise_service_error: ServiceErrorRaiser,
) -> dict[str, object]:
    """Query command-result diagnostics with bounded polling."""
    retry_delays_seconds = build_progressive_retry_delays(
        base_delay_seconds=_QUERY_COMMAND_RESULT_DIAGNOSTIC_BASE_DELAY_SECONDS,
        time_budget_seconds=time_budget_seconds,
        max_attempts=max_attempts,
    )
    attempt_limit = len(retry_delays_seconds) + 1
    last_error: LiproApiError | None = None

    async def _authenticated_query_command_result(
        *,
        msg_sn: str,
        device_id: str,
        device_type: str,
    ) -> CommandResultPayload:
        nonlocal last_error
        try:
            payload = await async_execute_coordinator_call(
                coordinator,
                call=lambda: coordinator.client.query_command_result(
                    msg_sn=msg_sn,
                    device_id=device_id,
                    device_type=device_type,
                ),
                raise_service_error=raise_service_error,
            )
        except LiproApiError as err:
            last_error = err
            raise
        last_error = None
        return payload

    async def _query_once(attempt: int) -> CommandResultPayload | None:
        return await query_command_result_once(
            query_command_result=_authenticated_query_command_result,
            lipro_api_error=LiproApiError,
            device_name=device.name,
            device_serial=device.serial,
            device_type_hex=device.device_type_hex,
            msg_sn=msg_sn,
            attempt=attempt,
            attempt_limit=attempt_limit,
            logger=_LOGGER,
        )

    state, attempts, result = await poll_command_result_state(
        query_once=_query_once,
        classify_payload=classify_command_result_payload,
        retry_delays_seconds=retry_delays_seconds,
    )
    response: QueryCommandResultResponse = {
        "serial": device.serial,
        "msg_sn": msg_sn,
        "max_attempts": max_attempts,
        "time_budget_seconds": time_budget_seconds,
        "state": state,
        "attempts": attempts,
        "attempt_limit": attempt_limit,
        "retry_delays_seconds": list(retry_delays_seconds),
        "result": result,
    }
    last_error_payload = _build_last_error_payload(last_error)
    if result is None and last_error_payload is not None:
        response["last_error"] = last_error_payload
    return cast(dict[str, object], response)


async def async_handle_query_command_result(
    hass: HomeAssistant,
    call: ServiceCall,
    *,
    get_device_and_coordinator: GetDeviceAndCoordinator,
    attr_msg_sn: str,
    attr_max_attempts: str,
    attr_time_budget_seconds: str,
    raise_service_error: ServiceErrorRaiser,
) -> dict[str, object]:
    """Handle the query_command_result service."""
    raw_device, raw_coordinator = await get_device_and_coordinator(hass, call)
    device = cast(DiagnosticsDevice, raw_device)
    coordinator = cast(DiagnosticsCoordinator, raw_coordinator)
    return await _async_query_command_result_with_optional_polling(
        coordinator=coordinator,
        device=device,
        msg_sn=_get_required_service_string(call, attr_msg_sn),
        max_attempts=_coerce_service_int(
            call,
            attr_max_attempts,
            _DEFAULT_QUERY_COMMAND_RESULT_MAX_ATTEMPTS,
        ),
        time_budget_seconds=_coerce_service_float(
            call,
            attr_time_budget_seconds,
            _DEFAULT_QUERY_COMMAND_RESULT_TIME_BUDGET_SECONDS,
        ),
        raise_service_error=raise_service_error,
    )


async def async_handle_get_city(
    hass: HomeAssistant,
    call: ServiceCall,
    *,
    iter_runtime_coordinators: RuntimeCoordinatorIterator,
    raise_optional_error: Callable[[str, LiproApiError], NoReturn],
    service_get_city: str,
) -> dict[str, object]:
    """Handle the get_city service."""
    del call
    has_result, result, last_err = await _async_get_first_coordinator_capability_result(
        (cast(DiagnosticsCoordinator, coordinator) for coordinator in iter_runtime_coordinators(hass)),
        capability="get_city",
        collector=lambda coordinator: coordinator.client.get_city(),
    )
    if has_result:
        return {"result": cast(CapabilityPayload, result)}
    if last_err is not None:
        raise_optional_error(service_get_city, last_err)
    return {"result": {}}


async def async_handle_query_user_cloud(
    hass: HomeAssistant,
    call: ServiceCall,
    *,
    iter_runtime_coordinators: RuntimeCoordinatorIterator,
    raise_optional_error: Callable[[str, LiproApiError], NoReturn],
    service_query_user_cloud: str,
) -> dict[str, object]:
    """Handle the query_user_cloud service."""
    del call
    has_result, result, last_err = await _async_get_first_coordinator_capability_result(
        (cast(DiagnosticsCoordinator, coordinator) for coordinator in iter_runtime_coordinators(hass)),
        capability="query_user_cloud",
        collector=lambda coordinator: coordinator.client.query_user_cloud(),
    )
    if has_result:
        return {"result": cast(CapabilityPayload, result)}
    if last_err is not None:
        raise_optional_error(service_query_user_cloud, last_err)
    return {"result": {}}


async def _async_handle_fetch_sensor_history(
    hass: HomeAssistant,
    call: ServiceCall,
    *,
    get_device_and_coordinator: GetDeviceAndCoordinator,
    async_call_optional_capability: OptionalCapabilityCaller,
    build_sensor_history_result: SensorHistoryResultBuilder,
    attr_sensor_device_id: str,
    attr_mesh_type: str,
    service_name: str,
    get_client_method: Callable[[DiagnosticsCoordinator], SensorHistoryClientMethod],
) -> dict[str, object]:
    """Shared handler for sensor-history diagnostics services."""
    raw_device, raw_coordinator = await get_device_and_coordinator(hass, call)
    device = cast(DiagnosticsDevice, raw_device)
    coordinator = cast(DiagnosticsCoordinator, raw_coordinator)
    sensor_device_id = _get_required_service_string(call, attr_sensor_device_id)
    mesh_type = _get_required_service_string(call, attr_mesh_type)
    result = await async_call_optional_capability(
        service_name,
        get_client_method(coordinator),
        coordinator=coordinator,
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
    get_device_and_coordinator: GetDeviceAndCoordinator,
    async_call_optional_capability: OptionalCapabilityCaller,
    build_sensor_history_result: SensorHistoryResultBuilder,
    attr_sensor_device_id: str,
    attr_mesh_type: str,
    service_fetch_body_sensor_history: str,
) -> dict[str, object]:
    """Handle the fetch_body_sensor_history service."""
    return await _async_handle_fetch_sensor_history(
        hass,
        call,
        get_device_and_coordinator=get_device_and_coordinator,
        async_call_optional_capability=async_call_optional_capability,
        build_sensor_history_result=build_sensor_history_result,
        attr_sensor_device_id=attr_sensor_device_id,
        attr_mesh_type=attr_mesh_type,
        service_name=service_fetch_body_sensor_history,
        get_client_method=lambda coordinator: coordinator.client.fetch_body_sensor_history,
    )


async def async_handle_fetch_door_sensor_history(
    hass: HomeAssistant,
    call: ServiceCall,
    *,
    get_device_and_coordinator: GetDeviceAndCoordinator,
    async_call_optional_capability: OptionalCapabilityCaller,
    build_sensor_history_result: SensorHistoryResultBuilder,
    attr_sensor_device_id: str,
    attr_mesh_type: str,
    service_fetch_door_sensor_history: str,
) -> dict[str, object]:
    """Handle the fetch_door_sensor_history service."""
    return await _async_handle_fetch_sensor_history(
        hass,
        call,
        get_device_and_coordinator=get_device_and_coordinator,
        async_call_optional_capability=async_call_optional_capability,
        build_sensor_history_result=build_sensor_history_result,
        attr_sensor_device_id=attr_sensor_device_id,
        attr_mesh_type=attr_mesh_type,
        service_name=service_fetch_door_sensor_history,
        get_client_method=lambda coordinator: coordinator.client.fetch_door_sensor_history,
    )
