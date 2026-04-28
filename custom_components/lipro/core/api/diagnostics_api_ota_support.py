"""Internal OTA diagnostics mechanics kept behind the diagnostics API outward home."""

from __future__ import annotations

from collections.abc import Awaitable, Callable, Sequence
from dataclasses import dataclass
import logging
from typing import cast

from ...const.api import PATH_QUERY_CONTROLLER_OTA, PATH_QUERY_OTA_INFO_V2
from ..telemetry.models import (
    OperationOutcome,
    OutcomeKind,
    build_operation_outcome,
    build_operation_outcome_from_exception,
)
from ..utils.log_safety import safe_error_placeholder
from .types import JsonValue, OtaInfoRow

_LOGGER = logging.getLogger(__name__)
_OTA_FAILURE_ORIGIN = "diagnostics.query_ota_info"

IotRequest = Callable[..., Awaitable[JsonValue]]
ExtractDataList = Callable[[object], Sequence[object]]
DeviceTypeHexResolver = Callable[[int | str], str]
InvalidParamCodeChecker = Callable[[object], bool]


@dataclass(frozen=True, slots=True)
class PrimaryOtaQueryResult:
    """Primary OTA probes plus the fallback outcome signals they produced."""

    rows: list[OtaInfoRow]
    error: Exception | None
    success: bool
    primary_failure_recovered: bool
    rich_v2_recovered: bool
    rich_v2_outcome: OperationOutcome | None


def _valid_rows(rows: Sequence[object]) -> list[OtaInfoRow]:
    """Keep OTA rows that are valid mapping objects."""
    return [cast(OtaInfoRow, row) for row in rows if isinstance(row, dict)]


def build_ota_api_error_outcome(
    err: Exception,
    *,
    kind: OutcomeKind,
    reason_code: str,
) -> OperationOutcome:
    """Build one typed OTA diagnostics outcome from one API failure."""
    code = getattr(err, "code", None)
    return build_operation_outcome_from_exception(
        err,
        kind=kind,
        reason_code=reason_code,
        failure_origin=_OTA_FAILURE_ORIGIN,
        failure_category="protocol",
        handling_policy="inspect",
        http_status=code if isinstance(code, int) else None,
    )


def resolve_ota_query_outcome(
    *,
    primary_failure_recovered: bool,
    rich_v2_recovered: bool,
    rich_v2_outcome: OperationOutcome | None,
    controller_outcome: OperationOutcome | None,
) -> OperationOutcome:
    """Resolve the outward OTA outcome with recovery precedence."""
    for outcome in (
        build_operation_outcome(
            kind="degraded", reason_code="primary_endpoint_recovered"
        )
        if primary_failure_recovered
        else None,
        build_operation_outcome(kind="degraded", reason_code="rich_v2_recovered")
        if rich_v2_recovered
        else None,
        rich_v2_outcome,
        controller_outcome,
    ):
        if outcome is not None:
            return outcome
    return build_operation_outcome(kind="success", reason_code="ota_query_complete")


async def query_ota_rows_with_payload(
    *,
    iot_request: IotRequest,
    extract_data_list: ExtractDataList,
    lipro_api_error: type[Exception],
    path: str,
    payload: dict[str, JsonValue],
) -> tuple[list[OtaInfoRow], Exception | None]:
    """Query one OTA endpoint with one explicit payload."""
    try:
        result = await iot_request(path, payload)
    except lipro_api_error as err:
        _LOGGER.debug("OTA endpoint %s failed (%s)", path, safe_error_placeholder(err))
        return [], err
    return _valid_rows(extract_data_list(result)), None


async def query_rich_v2_ota_rows(
    *,
    iot_request: IotRequest,
    extract_data_list: ExtractDataList,
    is_invalid_param_error_code: InvalidParamCodeChecker,
    lipro_api_error: type[Exception],
    payload: dict[str, JsonValue],
) -> tuple[list[OtaInfoRow], OperationOutcome | None, Exception | None]:
    """Query the richer OTA v2 payload and classify degraded outcomes."""
    try:
        result = await iot_request(PATH_QUERY_OTA_INFO_V2, payload)
    except lipro_api_error as err:
        code = getattr(err, "code", None)
        if is_invalid_param_error_code(code):
            _LOGGER.debug(
                "OTA endpoint %s rejected richer payload (code=%s, err=%s)",
                PATH_QUERY_OTA_INFO_V2,
                code,
                safe_error_placeholder(err),
            )
            return (
                [],
                build_ota_api_error_outcome(
                    err,
                    kind="degraded",
                    reason_code="rich_v2_invalid_param",
                ),
                err,
            )
        _LOGGER.debug(
            "OTA endpoint %s richer payload failed (%s)",
            PATH_QUERY_OTA_INFO_V2,
            safe_error_placeholder(err),
        )
        return (
            [],
            build_ota_api_error_outcome(
                err,
                kind="degraded",
                reason_code="rich_v2_failed",
            ),
            err,
        )
    return _valid_rows(extract_data_list(result)), None, None


async def query_controller_ota_rows(
    *,
    iot_request: IotRequest,
    extract_data_list: ExtractDataList,
    is_invalid_param_error_code: InvalidParamCodeChecker,
    lipro_api_error: type[Exception],
) -> tuple[list[OtaInfoRow], OperationOutcome | None]:
    """Query controller OTA rows and classify degraded fallback outcomes."""
    try:
        controller_result = await iot_request(PATH_QUERY_CONTROLLER_OTA, {})
    except lipro_api_error as err:
        code = getattr(err, "code", None)
        if is_invalid_param_error_code(code):
            _LOGGER.debug(
                "Controller OTA endpoint rejected payload (code=%s, err=%s)",
                code,
                safe_error_placeholder(err),
            )
            return [], build_ota_api_error_outcome(
                err,
                kind="degraded",
                reason_code="controller_invalid_param",
            )
        _LOGGER.debug(
            "Controller OTA endpoint %s failed (%s)",
            PATH_QUERY_CONTROLLER_OTA,
            safe_error_placeholder(err),
        )
        return [], build_ota_api_error_outcome(
            err,
            kind="degraded",
            reason_code="controller_failed",
        )
    return _valid_rows(extract_data_list(controller_result)), None


__all__ = [
    "DeviceTypeHexResolver",
    "ExtractDataList",
    "InvalidParamCodeChecker",
    "IotRequest",
    "PrimaryOtaQueryResult",
    "build_ota_api_error_outcome",
    "query_controller_ota_rows",
    "query_ota_rows_with_payload",
    "query_rich_v2_ota_rows",
    "resolve_ota_query_outcome",
]
