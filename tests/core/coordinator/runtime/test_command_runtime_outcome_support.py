"""Direct tests for CommandRuntime outcome support helpers."""

from __future__ import annotations

from unittest.mock import AsyncMock, MagicMock

import pytest

from custom_components.lipro.core.api import (
    LiproApiError,
    LiproAuthError,
    LiproRefreshTokenExpiredError,
)
from custom_components.lipro.core.coordinator.runtime.command_runtime_outcome_support import (
    _finalize_success,
    _handle_api_error,
    _record_command_result_failure,
    _resolve_reauth_reason,
)
from custom_components.lipro.core.coordinator.runtime.command_runtime_support import (
    _CommandRequest,
)

pytest_plugins = ('tests.core.coordinator.runtime.test_command_runtime_support',)


def test_record_command_result_failure_marks_trace_and_uses_runtime_callback(mock_device) -> None:
    trace: dict[str, object] = {}
    record_failure = MagicMock(return_value={'reason': 'command_result_failed'})

    summary = _record_command_result_failure(
        trace=trace,
        route='iot',
        device_serial=mock_device.serial,
        reason='command_result_failed',
        error_type='CommandResultRejected',
        record_failure=record_failure,
    )

    assert summary == {'reason': 'command_result_failed'}
    assert trace['route'] == 'iot'
    assert trace['success'] is False
    assert trace['error'] == 'CommandResultRejected'
    record_failure.assert_called_once()


def test_finalize_success_updates_confirmation_and_clears_failure(mock_device) -> None:
    builder = MagicMock()
    builder.should_skip_immediate_refresh.return_value = True
    confirmation = MagicMock()
    record_trace = MagicMock()
    clear_failure_state = MagicMock()
    trace: dict[str, object] = {}
    request = _CommandRequest(
        device=mock_device,
        command='POWER_ON',
        properties=None,
        fallback_device_id=None,
    )

    _finalize_success(
        request=request,
        route='iot',
        trace=trace,
        builder=builder,
        confirmation=confirmation,
        record_trace=record_trace,
        clear_failure_state=clear_failure_state,
    )

    confirmation.track_command_expectation.assert_called_once_with(
        device_serial=mock_device.serial,
        command='POWER_ON',
        properties=None,
    )
    record_trace.assert_called_once_with(trace)
    clear_failure_state.assert_called_once_with()
    assert trace['route'] == 'iot'
    assert trace['success'] is True


def test_resolve_reauth_reason_matches_auth_errors() -> None:
    assert _resolve_reauth_reason(LiproRefreshTokenExpiredError('expired')) == 'auth_expired'
    assert _resolve_reauth_reason(LiproAuthError('auth')) == 'auth_error'
    assert _resolve_reauth_reason(LiproApiError('generic')) is None


@pytest.mark.asyncio
async def test_handle_api_error_records_failure_and_triggers_reauth(mock_device) -> None:
    trace: dict[str, object] = {}
    record_failure = MagicMock(return_value={'reason': 'api_error'})
    trigger_reauth = AsyncMock()
    request = _CommandRequest(
        device=mock_device,
        command='POWER_ON',
        properties=None,
        fallback_device_id=None,
    )

    await _handle_api_error(
        request=request,
        trace=trace,
        route='device_direct',
        err=LiproAuthError('boom'),
        record_failure=record_failure,
        trigger_reauth=trigger_reauth,
    )

    record_failure.assert_called_once()
    trigger_reauth.assert_awaited_once_with('auth_error')
    assert trace['route'] == 'device_direct'
    assert trace['success'] is False
